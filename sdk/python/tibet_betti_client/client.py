"""
TIBET-BETTI Main Client

Integrates with:
1. BETTI Router (JIS) - For trust tokens and intent routing
2. KIT API - For context/sense and AI control
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import requests

from .tibet import Tibet, TimeWindow, Constraints
from .context import Context, SenseRule
from .trust_token import TrustToken, FIRARelationship
from .websocket import TibetWebSocket

logger = logging.getLogger(__name__)

# Optional crypto imports - only needed if generating keys
DIDKey = None
HIDKey = None

def _import_crypto():
    """Lazy import crypto modules"""
    global DIDKey, HIDKey
    if DIDKey is None:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'jis_client'))
            from crypto import DIDKey as _DIDKey, HIDKey as _HIDKey
            DIDKey = _DIDKey
            HIDKey = _HIDKey
        except ImportError as e:
            logger.warning(f"Crypto modules not available: {e}")
            logger.warning("Key generation will be disabled. Install cryptography package if needed.")
    return DIDKey, HIDKey


class TibetBettiClient:
    """
    Complete TIBET-BETTI Client

    Combines:
    - BETTI Router: Trust tokens, intent routing, loop prevention
    - KIT API: Context management, sense rules, AI control

    Example:
        >>> client = TibetBettiClient(
        ...     betti_url="http://localhost:18081",
        ...     kit_url="http://localhost:8000",
        ...     secret="your-secret"
        ... )
        >>>
        >>> # Establish trust
        >>> relationship = client.establish_trust("my_app", "user_ai")
        >>>
        >>> # Send TIBET with context
        >>> client.send_tibet(
        ...     relationship_id=relationship.id,
        ...     intent="schedule_meeting",
        ...     context={"user_id": "user_123", "preference": "morning"},
        ...     time_window=TimeWindow.from_now(hours=24)
        ... )
    """

    def __init__(
        self,
        betti_url: str,
        kit_url: Optional[str] = None,
        secret: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize TIBET-BETTI Client

        Args:
            betti_url: URL of BETTI router (JIS)
            kit_url: URL of KIT API (your context/sense system)
            secret: Shared secret for authentication
            jwt_token: JWT token (alternative to secret)
            timeout: Request timeout in seconds
        """
        self.betti_url = betti_url.rstrip('/')
        self.kit_url = kit_url.rstrip('/') if kit_url else None
        self.secret = secret
        self.jwt_token = jwt_token
        self.timeout = timeout

        # HTTP session
        self.session = requests.Session()

        # Track continuity hashes for FIR/As
        self._continuity_hashes: Dict[str, str] = {}

        # WebSocket connection (lazy init)
        self._ws: Optional[TibetWebSocket] = None

        logger.info(f"TibetBettiClient initialized")
        logger.info(f"  BETTI Router: {self.betti_url}")
        if self.kit_url:
            logger.info(f"  KIT API: {self.kit_url}")

    def _headers(self) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        elif self.secret:
            headers["X-JIS-SECRET"] = self.secret

        return headers

    def _request(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request"""
        response = self.session.request(
            method=method,
            url=url,
            json=json_data,
            headers=self._headers(),
            timeout=self.timeout
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            logger.error(f"Response: {response.text}")
            raise

        return response.json()

    # ========================================================================
    # TRUST TOKEN MANAGEMENT (FIR/A)
    # ========================================================================

    def establish_trust(
        self,
        initiator: str,
        responder: str,
        roles: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        trust_level: int = 1,
        generate_keys: bool = False
    ) -> FIRARelationship:
        """
        Establish trust relationship (FIR/A)

        This creates a "We know each other" relationship.

        Args:
            initiator: Name of initiating party (e.g., "my_app")
            responder: Name of responding party (e.g., "user_device")
            roles: Optional roles list
            context: Optional context info
            trust_level: Trust level (0-5)
            generate_keys: Auto-generate DID/HID keys (requires cryptography package)

        Returns:
            FIRARelationship with token

        Example:
            >>> rel = client.establish_trust("my_phone", "my_car")
            >>> print(rel.token)  # Trust token ID
        """
        # Generate keys if requested
        did = None
        hid = None

        if generate_keys:
            DIDKey_cls, HIDKey_cls = _import_crypto()
            if DIDKey_cls and HIDKey_cls:
                did = DIDKey_cls.generate()
                hid = HIDKey_cls.generate()
            else:
                logger.warning("Cannot generate keys - crypto modules not available")

        # Build payload
        payload = {
            "initiator": initiator,
            "responder": responder,
            "roles": roles or ["client", "service"],
            "context": {
                **(context or {}),
                "trust_level": trust_level,
                "established_at": datetime.utcnow().isoformat()
            }
        }

        # Add DID if generated
        if did:
            payload["initiator_did"] = {
                "did_public": did.export_public()
            }

            if hid:
                payload["initiator_did"]["hid_did_binding"] = hid.derive_did_binding(did)

        logger.info(f"Establishing trust: {initiator} ←→ {responder}")

        # Create FIR/A via BETTI router
        response = self._request(
            "POST",
            f"{self.betti_url}/fira/init",
            payload
        )

        fir_a_id = response["fir_a_id"]
        continuity_hash = response["continuity_hash"]

        # Track hash
        self._continuity_hashes[fir_a_id] = continuity_hash

        logger.info(f"Trust established: {fir_a_id}")

        return FIRARelationship(
            id=fir_a_id,
            token=fir_a_id,  # Token is the FIR/A ID
            initiator=initiator,
            responder=responder,
            trust_level=trust_level,
            continuity_hash=continuity_hash,
            did_key=did,
            hid_key=hid
        )

    def get_relationship(self, fir_a_id: str) -> FIRARelationship:
        """Get existing relationship details"""
        response = self._request(
            "GET",
            f"{self.betti_url}/relation/{fir_a_id}"
        )

        return FIRARelationship(
            id=response["fir_a_id"],
            token=response["fir_a_id"],
            continuity_hash=response["continuity_hash"],
            initiator=response.get("initiator"),
            responder=response.get("responder")
        )

    # ========================================================================
    # TIBET INTENT SENDING
    # ========================================================================

    def send_tibet(
        self,
        relationship_id: str,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        time_window: Optional[TimeWindow] = None,
        constraints: Optional[Constraints] = None,
        humotica: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send TIBET intent

        Args:
            relationship_id: FIR/A relationship ID (trust token)
            intent: Intent identifier (e.g., "turn_on_lights")
            context: Context information
            time_window: Optional time window
            constraints: Optional constraints
            humotica: Optional human-readable explanation

        Returns:
            Response from BETTI router

        Example:
            >>> client.send_tibet(
            ...     relationship_id=rel.id,
            ...     intent="schedule_meeting",
            ...     context={"attendees": 5, "duration": 60},
            ...     time_window=TimeWindow.from_now(hours=24),
            ...     constraints=Constraints(max_retries=3)
            ... )
        """
        # Build TIBET
        tibet = Tibet(
            intent=intent,
            context=context or {},
            time_window=time_window or TimeWindow.immediate(),
            constraints=constraints or Constraints(),
            humotica=humotica
        )

        # Get continuity hash
        continuity_hash_prev = self._continuity_hashes.get(relationship_id)

        # Build payload
        payload = {
            "fir_a_id": relationship_id,
            "intent": tibet.intent,
            "context": tibet.context,
            "timebox_seconds": tibet.time_window.duration_seconds(),
            "continuity_hash_prev": continuity_hash_prev
        }

        logger.info(f"Sending TIBET: {intent} via FIR/A {relationship_id}")

        # Send to BETTI router
        response = self._request(
            "POST",
            f"{self.betti_url}/ift",
            payload
        )

        # Update hash
        new_hash = response["continuity_hash"]
        self._continuity_hashes[relationship_id] = new_hash

        logger.info(f"TIBET accepted. New hash: {new_hash[:8]}...")

        return {
            "status": "accepted",
            "fir_a_id": response["fir_a_id"],
            "continuity_hash": new_hash,
            "events": response["events"]
        }

    # ========================================================================
    # KIT API INTEGRATION (Context & Sense)
    # ========================================================================

    def update_context(
        self,
        user_id: str,
        context_data: Dict[str, Any],
        evaluate_sense: bool = True
    ) -> Dict[str, Any]:
        """
        Update user context in KIT

        Args:
            user_id: User identifier
            context_data: Context data to update
            evaluate_sense: Run sense evaluation after update

        Returns:
            Response with sense evaluation results

        Example:
            >>> client.update_context(
            ...     user_id="user_123",
            ...     context_data={
            ...         "location": "home",
            ...         "time_of_day": "evening",
            ...         "activity": "relaxing"
            ...     }
            ... )
        """
        if not self.kit_url:
            raise ValueError("KIT URL not configured")

        payload = {
            "user_id": user_id,
            "context": context_data,
            "evaluate_sense": evaluate_sense
        }

        logger.info(f"Updating context for user {user_id}")

        response = self._request(
            "POST",
            f"{self.kit_url}/context/update",
            payload
        )

        return response

    def get_context(self, user_id: str) -> Context:
        """Get user context from KIT"""
        if not self.kit_url:
            raise ValueError("KIT URL not configured")

        response = self._request(
            "GET",
            f"{self.kit_url}/context/{user_id}"
        )

        return Context.from_dict(response)

    def create_sense_rule(
        self,
        name: str,
        conditions: Dict[str, Any],
        intent: str,
        priority: int = 5
    ) -> SenseRule:
        """
        Create sense rule in KIT

        Sense rules automatically trigger intents based on context.

        Args:
            name: Rule name
            conditions: Conditions to match (context patterns)
            intent: Intent to trigger when conditions match
            priority: Rule priority (higher = more important)

        Returns:
            Created sense rule

        Example:
            >>> client.create_sense_rule(
            ...     name="evening_lights",
            ...     conditions={
            ...         "time_of_day": "evening",
            ...         "location": "home",
            ...         "ambient_light": {"lt": 100}
            ...     },
            ...     intent="turn_on_lights",
            ...     priority=7
            ... )
        """
        if not self.kit_url:
            raise ValueError("KIT URL not configured")

        payload = {
            "name": name,
            "conditions": conditions,
            "intent": intent,
            "priority": priority
        }

        logger.info(f"Creating sense rule: {name} → {intent}")

        response = self._request(
            "POST",
            f"{self.kit_url}/sense/rules",
            payload
        )

        return SenseRule.from_dict(response)

    def evaluate_sense(
        self,
        user_id: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Evaluate sense rules for user

        Args:
            user_id: User identifier
            context_data: Optional context (uses current if not provided)

        Returns:
            List of triggered intents

        Example:
            >>> intents = client.evaluate_sense("user_123")
            >>> print(intents)  # ["turn_on_lights", "start_music"]
        """
        if not self.kit_url:
            raise ValueError("KIT URL not configured")

        payload = {
            "user_id": user_id,
            "context": context_data
        }

        response = self._request(
            "POST",
            f"{self.kit_url}/sense/evaluate",
            payload
        )

        return response.get("triggered_intents", [])

    # ========================================================================
    # COMBINED: Context → Sense → TIBET
    # ========================================================================

    def context_to_tibet(
        self,
        relationship_id: str,
        user_id: str,
        context_update: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Complete flow: Update context → Evaluate sense → Send TIBETs

        This is the magic integration!

        Args:
            relationship_id: Trust token (FIR/A ID)
            user_id: User ID in KIT
            context_update: New context data

        Returns:
            List of sent TIBET responses

        Example:
            >>> # User arrives home
            >>> results = client.context_to_tibet(
            ...     relationship_id=rel.id,
            ...     user_id="user_123",
            ...     context_update={"location": "home", "time": "18:30"}
            ... )
            >>> # Automatically triggers:
            >>> # - turn_on_lights
            >>> # - set_temperature
            >>> # - start_music
        """
        if not self.kit_url:
            raise ValueError("KIT URL required for context_to_tibet")

        # 1. Update context
        logger.info(f"Updating context for {user_id}")
        self.update_context(user_id, context_update, evaluate_sense=False)

        # 2. Evaluate sense rules
        logger.info(f"Evaluating sense rules")
        triggered_intents = self.evaluate_sense(user_id)

        # 3. Send TIBET for each triggered intent
        results = []
        for intent in triggered_intents:
            logger.info(f"Sending TIBET for triggered intent: {intent}")

            result = self.send_tibet(
                relationship_id=relationship_id,
                intent=intent,
                context={
                    "user_id": user_id,
                    "triggered_by": "sense_rule",
                    **context_update
                },
                humotica=f"Auto-triggered by sense rule based on context update: {context_update}"
            )

            results.append(result)

        logger.info(f"Sent {len(results)} TIBETs from sense evaluation")

        return results

    # ========================================================================
    # WEBSOCKET (Real-Time)
    # ========================================================================

    def connect_websocket(
        self,
        user_id: str,
        on_message: callable,
        on_tibet: Optional[callable] = None
    ) -> TibetWebSocket:
        """
        Connect to WebSocket for real-time updates

        Args:
            user_id: User ID
            on_message: Callback for any message
            on_tibet: Optional callback specifically for TIBET intents

        Returns:
            TibetWebSocket connection

        Example:
            >>> def handle_tibet(tibet_data):
            ...     print(f"Received TIBET: {tibet_data['intent']}")
            >>>
            >>> ws = client.connect_websocket(
            ...     user_id="user_123",
            ...     on_message=lambda msg: print(msg),
            ...     on_tibet=handle_tibet
            ... )
            >>> ws.start()  # Run in background
        """
        if not self.kit_url:
            raise ValueError("KIT URL required for WebSocket")

        ws_url = self.kit_url.replace('http://', 'ws://').replace('https://', 'wss://')

        self._ws = TibetWebSocket(
            url=f"{ws_url}/ws/{user_id}",
            on_message=on_message,
            on_tibet=on_tibet
        )

        return self._ws

    def close_websocket(self):
        """Close WebSocket connection"""
        if self._ws:
            self._ws.close()
            self._ws = None

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def health_check(self) -> Dict[str, Any]:
        """Check BETTI router health"""
        return self._request("GET", f"{self.betti_url}/health")

    def kit_health_check(self) -> Dict[str, Any]:
        """Check KIT API health"""
        if not self.kit_url:
            raise ValueError("KIT URL not configured")
        return self._request("GET", f"{self.kit_url}/health")
