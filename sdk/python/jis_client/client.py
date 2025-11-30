"""
JIS Client - Main client class for interacting with JIS Router
"""
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from .crypto import DIDKey, HIDKey, KeyExchange, create_did_exchange_payload
from .models import (
    DIDKeyInfo,
    FIRARelationship,
    IntentResponse,
    NIRNotification,
    RelationshipEvent,
)

logger = logging.getLogger(__name__)


class JISClient:
    """
    Main client for JTel Identity Standard Router

    Handles:
    - FIR/A relationship initialization
    - Intent transmission (IFT)
    - NIR notifications
    - Continuity chain management
    - DID/HID key exchange

    Example:
        >>> client = JISClient("http://localhost:18081", secret="your-secret")
        >>> did = DIDKey.generate()
        >>> hid = HIDKey.generate()
        >>>
        >>> # Create relationship
        >>> fir_a = client.init_relationship(
        ...     initiator="my-app",
        ...     responder="server",
        ...     roles=["client"],
        ...     did_key=did,
        ...     hid_key=hid
        ... )
        >>>
        >>> # Send intent
        >>> result = client.send_intent(
        ...     fir_a_id=fir_a.id,
        ...     intent="unlock_door",
        ...     context={"location": "home"}
        ... )
    """

    def __init__(
        self,
        router_url: str,
        secret: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize JIS Client

        Args:
            router_url: Base URL of JIS Router (e.g., "http://localhost:18081")
            secret: Shared secret for authentication (X-JIS-SECRET header)
            jwt_token: JWT token for authentication (Bearer token)
            timeout: Request timeout in seconds

        Note: Provide either secret OR jwt_token, not both
        """
        self.router_url = router_url.rstrip('/')
        self.secret = secret
        self.jwt_token = jwt_token
        self.timeout = timeout
        self.session = requests.Session()

        # Track current continuity hash for each relationship
        self._continuity_hashes: Dict[str, str] = {}

    def _headers(self) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {"Content-Type": "application/json"}

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        elif self.secret:
            headers["X-JIS-SECRET"] = self.secret
        else:
            logger.warning("No authentication configured (secret or JWT)")

        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to router

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/fira/init")
            json_data: JSON payload for POST requests

        Returns:
            Response JSON

        Raises:
            requests.HTTPError: On HTTP errors
        """
        url = urljoin(self.router_url, endpoint)
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

    def init_relationship(
        self,
        initiator: str,
        responder: str,
        roles: List[str],
        context: Optional[Dict[str, Any]] = None,
        humotica: Optional[str] = None,
        did_key: Optional[DIDKey] = None,
        hid_key: Optional[HIDKey] = None,
        include_key_exchange: bool = True
    ) -> FIRARelationship:
        """
        Initialize new FIR/A relationship

        Args:
            initiator: Name of initiating entity (e.g., "my-app")
            responder: Name of responding entity (e.g., "server")
            roles: List of declared roles (e.g., ["client", "device"])
            context: Optional context information
            humotica: Optional human/intent trace
            did_key: DID key for this device (optional)
            hid_key: HID key for human binding (optional, never transmitted!)
            include_key_exchange: Include Diffie-Hellman key exchange

        Returns:
            FIRARelationship object with ID and continuity hash

        Example:
            >>> did = DIDKey.generate()
            >>> hid = HIDKey.generate()
            >>> fir_a = client.init_relationship(
            ...     initiator="mobile-app",
            ...     responder="api-server",
            ...     roles=["client"],
            ...     did_key=did,
            ...     hid_key=hid
            ... )
        """
        payload = {
            "initiator": initiator,
            "responder": responder,
            "roles": roles,
            "context": context or {},
            "humotica": humotica,
        }

        # Add DID key exchange if provided
        if did_key:
            exchange = KeyExchange() if include_key_exchange else None
            did_payload = create_did_exchange_payload(did_key, exchange) if exchange else {
                "did_public": did_key.export_public()
            }

            # Add HID-DID binding if HID provided
            if hid_key:
                did_payload["hid_did_binding"] = hid_key.derive_did_binding(did_key)

            payload["initiator_did"] = did_payload

        logger.info(f"Initializing FIR/A: {initiator} <-> {responder}")
        response = self._request("POST", "/fira/init", payload)

        # Store continuity hash
        fir_a_id = response["fir_a_id"]
        continuity_hash = response["continuity_hash"]
        self._continuity_hashes[fir_a_id] = continuity_hash

        logger.info(f"FIR/A created: {fir_a_id} (hash: {continuity_hash[:8]}...)")

        return FIRARelationship(
            id=fir_a_id,
            continuity_hash=continuity_hash,
            events=response["events"],
            initiator=initiator,
            responder=responder,
            roles=roles
        )

    def send_intent(
        self,
        fir_a_id: str,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        timebox_seconds: int = 30,
        continuity_hash_prev: Optional[str] = None
    ) -> IntentResponse:
        """
        Send Intent-First Transmission (IFT)

        Args:
            fir_a_id: FIR/A relationship ID
            intent: Intent identifier (e.g., "unlock_door", "send_message")
            context: Optional context information
            timebox_seconds: Time window for this intent
            continuity_hash_prev: Previous continuity hash (auto-tracked if None)

        Returns:
            IntentResponse with new continuity hash

        Raises:
            HTTPError: On hash mismatch (409) or other errors

        Example:
            >>> client.send_intent(
            ...     fir_a_id=fir_a.id,
            ...     intent="verify_identity",
            ...     context={"method": "biometric"}
            ... )
        """
        # Use tracked hash if not provided
        if continuity_hash_prev is None:
            continuity_hash_prev = self._continuity_hashes.get(fir_a_id)

        payload = {
            "fir_a_id": fir_a_id,
            "intent": intent,
            "context": context or {},
            "timebox_seconds": timebox_seconds,
            "continuity_hash_prev": continuity_hash_prev
        }

        logger.info(f"Sending intent '{intent}' for FIR/A {fir_a_id}")
        response = self._request("POST", "/ift", payload)

        # Update tracked hash
        new_hash = response["continuity_hash"]
        self._continuity_hashes[fir_a_id] = new_hash

        logger.debug(f"Intent accepted. New hash: {new_hash[:8]}...")

        return IntentResponse(
            fir_a_id=response["fir_a_id"],
            continuity_hash=new_hash,
            events=response["events"]
        )

    def notify_nir(
        self,
        fir_a_id: str,
        reason: str,
        suggested_method: Optional[str] = None,
        continuity_hash_prev: Optional[str] = None
    ) -> NIRNotification:
        """
        Send NIR notification (flag uncertainty)

        Args:
            fir_a_id: FIR/A relationship ID
            reason: Why the flag was raised
            suggested_method: Suggested resolution method
            continuity_hash_prev: Previous continuity hash (auto-tracked if None)

        Returns:
            NIRNotification with new continuity hash

        Example:
            >>> client.notify_nir(
            ...     fir_a_id=fir_a.id,
            ...     reason="unusual_location",
            ...     suggested_method="biometric_confirm"
            ... )
        """
        if continuity_hash_prev is None:
            continuity_hash_prev = self._continuity_hashes.get(fir_a_id)

        payload = {
            "fir_a_id": fir_a_id,
            "reason": reason,
            "suggested_method": suggested_method,
            "continuity_hash_prev": continuity_hash_prev
        }

        logger.warning(f"NIR notification for {fir_a_id}: {reason}")
        response = self._request("POST", "/nir/notify", payload)

        new_hash = response["continuity_hash"]
        self._continuity_hashes[fir_a_id] = new_hash

        return NIRNotification(
            fir_a_id=response["fir_a_id"],
            reason=reason,
            suggested_method=suggested_method,
            continuity_hash=new_hash
        )

    def confirm_nir(
        self,
        fir_a_id: str,
        method: str,
        result: str,
        continuity_hash_prev: Optional[str] = None
    ) -> IntentResponse:
        """
        Confirm NIR resolution

        Args:
            fir_a_id: FIR/A relationship ID
            method: Method used for resolution
            result: Result of resolution (e.g., "confirmed", "denied")
            continuity_hash_prev: Previous continuity hash (auto-tracked if None)

        Returns:
            IntentResponse with new continuity hash

        Example:
            >>> client.confirm_nir(
            ...     fir_a_id=fir_a.id,
            ...     method="biometric",
            ...     result="confirmed"
            ... )
        """
        if continuity_hash_prev is None:
            continuity_hash_prev = self._continuity_hashes.get(fir_a_id)

        payload = {
            "fir_a_id": fir_a_id,
            "method": method,
            "result": result,
            "continuity_hash_prev": continuity_hash_prev
        }

        logger.info(f"NIR confirmation for {fir_a_id}: {method} -> {result}")
        response = self._request("POST", "/nir/confirm", payload)

        new_hash = response["continuity_hash"]
        self._continuity_hashes[fir_a_id] = new_hash

        return IntentResponse(
            fir_a_id=response["fir_a_id"],
            continuity_hash=new_hash,
            events=response["events"]
        )

    def get_relationship(self, fir_a_id: str) -> FIRARelationship:
        """
        Get current state of a relationship

        Args:
            fir_a_id: FIR/A relationship ID

        Returns:
            FIRARelationship with current state

        Example:
            >>> info = client.get_relationship(fir_a.id)
            >>> print(f"Events: {info.events}")
        """
        response = self._request("GET", f"/relation/{fir_a_id}")

        # Update tracked hash
        continuity_hash = response["continuity_hash"]
        self._continuity_hashes[fir_a_id] = continuity_hash

        return FIRARelationship(
            id=response["fir_a_id"],
            continuity_hash=continuity_hash,
            events=response["events"]
        )

    def get_events(
        self,
        fir_a_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[RelationshipEvent]:
        """
        Get event history for a relationship

        Args:
            fir_a_id: FIR/A relationship ID
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of RelationshipEvent objects (newest first)

        Example:
            >>> events = client.get_events(fir_a.id, limit=10)
            >>> for event in events:
            ...     print(f"Event {event.seq}: {event.payload['type']}")
        """
        response = self._request(
            "GET",
            f"/relation/{fir_a_id}/events?limit={limit}&offset={offset}"
        )

        return [
            RelationshipEvent(
                seq=event["seq"],
                continuity_hash=event["continuity_hash"],
                payload=event["payload"],
                timestamp=event.get("timestamp")
            )
            for event in response["events"]
        ]

    def get_did_keys(self, fir_a_id: str) -> Dict[str, DIDKeyInfo]:
        """
        Get DID keys for a relationship

        Args:
            fir_a_id: FIR/A relationship ID

        Returns:
            Dict mapping entity name to DIDKeyInfo

        Example:
            >>> keys = client.get_did_keys(fir_a.id)
            >>> print(keys["initiator"].did_public_key)
        """
        response = self._request("GET", f"/relation/{fir_a_id}/keys")

        return {
            entity: DIDKeyInfo(
                did_public_key=info["did_public_key"],
                exchange_public_key=info.get("exchange_public_key"),
                hid_did_binding=info.get("hid_did_binding"),
                created_at=info.get("created_at")
            )
            for entity, info in response["keys"].items()
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check router health

        Returns:
            Health status dict

        Example:
            >>> health = client.health_check()
            >>> print(health["status"])  # "ok"
        """
        return self._request("GET", "/health")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get router metrics

        Returns:
            Metrics dict with relationship/event counts

        Example:
            >>> metrics = client.get_metrics()
            >>> print(f"Total relationships: {metrics['total_relationships']}")
        """
        return self._request("GET", "/metrics")
