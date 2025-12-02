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
from .voltage_controller import get_voltage_controller, VoltageProfile
from .intent_tech_layer import get_intent_layer

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

        # Voltage Controller & Intent-Tech Layer (global singletons)
        self.voltage_controller = get_voltage_controller()
        self.intent_layer = get_intent_layer()

        logger.info(f"TibetBettiClient initialized")
        logger.info(f"  BETTI Router: {self.betti_url}")
        if self.kit_url:
            logger.info(f"  KIT API: {self.kit_url}")
        logger.info(f"  Voltage Controller: Available ({self.voltage_controller.current_profile.value} profile)")
        logger.info(f"  Intent-Tech Layer: Available")

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

    # ========================================================================
    # BETTI INTENT EXECUTION (with BALANS Security Pipeline)
    # ========================================================================

    def execute_intent(
        self,
        intent: str,
        context: Dict[str, Any],
        user_id: str,
        fira_id: Optional[str] = None,
        urgency: int = 5,
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute intent through BETTI security pipeline

        Pipeline: SNAFT → BALANS → Complexity → Execute → Flag2Fail

        Args:
            intent: Intent to execute (e.g., "turn_on_lights")
            context: Intent context/parameters
            user_id: User ID
            fira_id: Optional FIR/A trust token
            urgency: User urgency (1-10, default 5)
            deadline: Optional ISO datetime deadline

        Returns:
            Response with status and result

        Status codes:
            - executed: Successfully executed
            - snaft_blocked: SNAFT factory firewall blocked
            - clarification_needed: BALANS needs clarification
            - awaiting_resources: Robot requests permission (Internal TIBET)
            - delayed: BALANS suggests waiting
            - rejected: Cannot safely execute
            - split_required: Task too complex, needs splitting

        Example:
            >>> result = client.execute_intent(
            ...     intent="upload_file",
            ...     context={
            ...         "file_size_mb": 500,
            ...         "did": "phone_001",
            ...         "device_type": "phone"
            ...     },
            ...     user_id="jasper@jtel.nl",
            ...     urgency=7,
            ...     deadline="2025-11-28T18:00:00Z"
            ... )
            >>>
            >>> if result['status'] == 'awaiting_resources':
            ...     print(f"🔋 {result['result']['robot_request']}")
            ...     # "May I charge for 20 minutes first?"
            >>> elif result['status'] == 'clarification_needed':
            ...     print(f"❓ {result['result']['clarification_question']}")
            >>> elif result['status'] == 'executed':
            ...     print(f"✓ {result['result']['message']}")
            ...     print(f"Warmth: {result['result']['warmth']}, Color: {result['result']['color']}")
        """
        if not self.kit_url:
            raise ValueError("KIT URL required for intent execution")

        # Build payload
        payload = {
            "intent": intent,
            "context": {
                **context,
                "urgency": urgency
            },
            "user_id": user_id
        }

        if fira_id:
            payload["fira_id"] = fira_id

        if deadline:
            payload["context"]["deadline"] = deadline

        logger.info(f"Executing intent: {intent} (urgency={urgency})")

        response = self._request(
            "POST",
            f"{self.kit_url}/betti/intent/execute",
            payload
        )

        # Log BALANS decision
        status = response.get("status")
        result = response.get("result", {})

        if status == "snaft_blocked":
            logger.warning(f"🚫 SNAFT blocked: {result.get('reason')}")
        elif status == "clarification_needed":
            logger.info(f"❓ Clarification needed: {result.get('message')}")
        elif status == "awaiting_resources":
            logger.info(f"🔋 Awaiting resources: {result.get('robot_request')}")
        elif status == "delayed":
            logger.info(f"⏰ Delayed: {result.get('message')}")
        elif status == "rejected":
            logger.warning(f"❌ Rejected: {result.get('message')}")
        elif status == "split_required":
            logger.info(f"📋 Split required (complexity: {result.get('complexity', {}).get('score')})")
        elif status == "executed":
            warmth = result.get('warmth', 'neutral')
            color = result.get('color', 'green')
            logger.info(f"✓ Executed (warmth={warmth}, color={color})")

        return response

    def clarify_intent(
        self,
        intent: str,
        clarification: str,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Provide clarification for ambiguous intent

        Use this after receiving clarification_needed status.

        Args:
            intent: Original intent
            clarification: User's clarification/answer
            context: Updated context with clarification
            user_id: User ID

        Returns:
            New execution result

        Example:
            >>> # Initial request was ambiguous
            >>> result = client.execute_intent("turn_on_living_lights", {}, "user_123")
            >>> if result['status'] == 'clarification_needed':
            ...     # User clarifies: "huiskamer"
            ...     result = client.clarify_intent(
            ...         intent="turn_on_lights",
            ...         clarification="huiskamer",
            ...         context={"location": "huiskamer"},
            ...         user_id="user_123"
            ...     )
        """
        updated_context = {
            **context,
            "clarification": clarification,
            "clarified": True
        }

        return self.execute_intent(
            intent=intent,
            context=updated_context,
            user_id=user_id
        )

    def approve_resource_request(
        self,
        intent: str,
        context: Dict[str, Any],
        user_id: str,
        approved: bool
    ) -> Dict[str, Any]:
        """
        Approve or deny robot's resource request (Internal TIBET)

        Use this after receiving awaiting_resources status.

        Args:
            intent: Original intent
            context: Original context
            user_id: User ID
            approved: True to approve, False to deny

        Returns:
            New execution result if approved, or cancellation if denied

        Example:
            >>> result = client.execute_intent("upload_large_file", {...}, "user_123")
            >>> if result['status'] == 'awaiting_resources':
            ...     # Robot: "May I charge for 20 minutes first?"
            ...     user_approves = ask_user("Approve charging?")
            ...
            ...     result = client.approve_resource_request(
            ...         intent="upload_large_file",
            ...         context={...},
            ...         user_id="user_123",
            ...         approved=user_approves
            ...     )
        """
        if approved:
            # Re-execute after approval
            updated_context = {
                **context,
                "resource_request_approved": True,
                "retry_after_resources": True
            }
            return self.execute_intent(
                intent=intent,
                context=updated_context,
                user_id=user_id
            )
        else:
            # User denied - return cancellation
            return {
                "status": "cancelled",
                "result": {
                    "message": "User denied resource request",
                    "warmth": "neutral",
                    "color": "blue"
                }
            }

    # ========================================================================
    # BALANS ANALYTICS & MONITORING
    # ========================================================================

    def get_balans_decisions(
        self,
        did: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get BALANS decision history for device

        Args:
            did: Device ID
            limit: Max number of decisions to return

        Returns:
            List of BALANS decisions with warmth/color

        Example:
            >>> decisions = client.get_balans_decisions("phone_001", limit=20)
            >>> for d in decisions:
            ...     print(f"{d['decision']} - {d['response_warmth']} - {d['decision_reasoning']}")
        """
        if not self.kit_url:
            raise ValueError("KIT URL required")

        response = self._request(
            "GET",
            f"{self.kit_url}/betti/balans/decisions/{did}?limit={limit}"
        )

        return response.get("decisions", [])

    def get_balans_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """
        Get BALANS analytics dashboard

        Args:
            days: Number of days to analyze

        Returns:
            Dashboard with decision distributions, warmth/color trends

        Example:
            >>> dashboard = client.get_balans_dashboard(days=7)
            >>> print("Decision Distribution:")
            >>> for decision in dashboard['decision_distribution']:
            ...     print(f"  {decision['decision']}: {decision['count']} times")
            >>> print("Warmth/Color Distribution:")
            >>> for wc in dashboard['warmth_color_distribution']:
            ...     print(f"  {wc['response_warmth']} + {wc['response_color']}: {wc['count']}")
        """
        if not self.kit_url:
            raise ValueError("KIT URL required")

        response = self._request(
            "GET",
            f"{self.kit_url}/betti/balans/dashboard?days={days}"
        )

        return response

    # ========================================================================
    # SNAFT - Factory Firewall
    # ========================================================================

    def get_snaft_rules(
        self,
        device_type: Optional[str] = None,
        manufacturer: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get SNAFT factory firewall rules

        Args:
            device_type: Filter by device type (robot/drone/car/phone/iot)
            manufacturer: Filter by manufacturer

        Returns:
            List of SNAFT rules

        Example:
            >>> # Get all drone rules
            >>> rules = client.get_snaft_rules(device_type="drone")
            >>> for rule in rules:
            ...     print(f"{rule['rule_type']}: {rule['reason']}")
            >>>
            >>> # Get Boston Dynamics robot rules
            >>> rules = client.get_snaft_rules(
            ...     device_type="robot",
            ...     manufacturer="Boston Dynamics"
            ... )
        """
        if not self.kit_url:
            raise ValueError("KIT URL required")

        params = []
        if device_type:
            params.append(f"device_type={device_type}")
        if manufacturer:
            params.append(f"manufacturer={manufacturer}")

        query = f"?{'&'.join(params)}" if params else ""

        response = self._request(
            "GET",
            f"{self.kit_url}/betti/snaft/rules{query}"
        )

        return response.get("rules", [])

    def get_snaft_violations(
        self,
        did: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get SNAFT violation history for device

        Args:
            did: Device ID
            limit: Max violations to return

        Returns:
            List of SNAFT violations

        Example:
            >>> violations = client.get_snaft_violations("drone_dji_001")
            >>> for v in violations:
            ...     print(f"{v['timestamp']}: {v['intent']} - {v['reason']}")
        """
        if not self.kit_url:
            raise ValueError("KIT URL required")

        response = self._request(
            "GET",
            f"{self.kit_url}/betti/snaft/violations/{did}?limit={limit}"
        )

        return response.get("violations", [])

    def get_snaft_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """
        Get SNAFT violation analytics

        Args:
            days: Number of days to analyze

        Returns:
            Dashboard with violation trends, device awareness

        Example:
            >>> dashboard = client.get_snaft_dashboard(days=7)
            >>> print("Top Violations:")
            >>> for v in dashboard['top_violations']:
            ...     print(f"  {v['device_type']} - {v['reason']}: {v['violation_count']} times")
            >>> print("Device Awareness:")
            >>> for d in dashboard['device_awareness']:
            ...     print(f"  {d['did']}: awareness level {d['self_awareness_level']}/10")
        """
        if not self.kit_url:
            raise ValueError("KIT URL required")

        response = self._request(
            "GET",
            f"{self.kit_url}/betti/snaft/dashboard?days={days}"
        )

        return response

    # ========================================================================
    # BETTI COMPLEXITY ANALYSIS
    # ========================================================================

    def analyze_complexity(
        self,
        intent: str,
        context: Dict[str, Any],
        threshold_profile: str = "default"
    ) -> Dict[str, Any]:
        """
        Analyze complexity of intent WITHOUT executing

        Useful for testing and what-if analysis.

        Args:
            intent: Intent to analyze
            context: Intent context
            threshold_profile: Complexity profile (default/strict/relaxed)

        Returns:
            Complexity analysis with B0-B5 dimensions

        Example:
            >>> analysis = client.analyze_complexity(
            ...     intent="organize_smart_home",
            ...     context={
            ...         "humans": 5,
            ...         "devices": 50,
            ...         "operations": 200
            ...     }
            ... )
            >>> print(f"Complexity Score: {analysis['complexity']['score']}")
            >>> print(f"B0 (Humans): {analysis['complexity']['b0_humans']}")
            >>> print(f"Split Required: {analysis['complexity']['split_required']}")
        """
        if not self.kit_url:
            raise ValueError("KIT URL required")

        payload = {
            "intent": intent,
            "context": context,
            "threshold_profile": threshold_profile
        }

        response = self._request(
            "POST",
            f"{self.kit_url}/betti/complexity/analyze",
            payload
        )

        return response

    async def process_raw_input(
        self,
        raw_input: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process raw input through Intent-Tech Layer with automatic voltage scaling

        This method:
        1. Parses raw input to structured intent
        2. Automatically adjusts voltage profile based on urgency (1-10 scale)
        3. Routes intent to appropriate subsystem (BETTI/KIT/DIRECT)
        4. Returns processed result

        Args:
            raw_input: Raw text input (e.g., "call john", "schedule meeting tomorrow")
            context: Additional context dict (user_id, device, etc.)
            session_id: Session ID for state management

        Returns:
            Dict with:
                - intent: ParsedIntent object
                - response: Response from routed handler
                - voltage_profile: Current voltage profile (if changed)

        Example:
            >>> result = await client.process_raw_input(
            ...     raw_input="send urgent message to team",
            ...     context={"user_id": "user_123"}
            ... )
            >>> print(f"Urgency: {result['intent'].urgency}")
            >>> print(f"Voltage: {result.get('voltage_profile')}")
        """
        # 1. Parse intent through Intent-Tech Layer
        parsed = await self.intent_layer.process(
            raw_input=raw_input,
            context=context,
            session_id=session_id
        )

        # 2. Auto-adjust voltage based on urgency (1-10 → voltage profile)
        intent_data = parsed["intent"]
        target_profile = await self.voltage_controller.profile_for_urgency(
            intent_data.urgency
        )

        # 3. Apply voltage profile if different from current
        if target_profile != self.voltage_controller.current_profile:
            success = await self.voltage_controller.set_profile(target_profile)
            if success:
                parsed["voltage_profile_changed"] = {
                    "from": self.voltage_controller.current_profile.value,
                    "to": target_profile.value,
                    "urgency": intent_data.urgency
                }
                logger.info(
                    f"Voltage adjusted: {self.voltage_controller.current_profile.value} "
                    f"→ {target_profile.value} (urgency {intent_data.urgency})"
                )

        # 4. Add current voltage profile to response
        parsed["voltage_profile"] = self.voltage_controller.current_profile.value

        return parsed
