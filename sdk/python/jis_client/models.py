"""
Data models for JIS Client SDK
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FIRARelationship:
    """
    Represents a FIR/A relationship between two entities

    Attributes:
        id: Unique FIR/A ID (UUID)
        continuity_hash: Current continuity hash
        events: Number of events in chain
        initiator: Initiating entity name
        responder: Responding entity name
        roles: List of declared roles
    """
    id: str
    continuity_hash: str
    events: int
    initiator: Optional[str] = None
    responder: Optional[str] = None
    roles: Optional[List[str]] = None

    @property
    def fir_a_id(self) -> str:
        """Alias for id (backwards compatibility)"""
        return self.id


@dataclass
class IntentResponse:
    """
    Response from sending an intent (IFT)

    Attributes:
        fir_a_id: FIR/A relationship ID
        continuity_hash: New continuity hash after this event
        events: Total number of events in chain
    """
    fir_a_id: str
    continuity_hash: str
    events: int


@dataclass
class NIRNotification:
    """
    NIR (Notify/Identify/Rectify) notification

    Represents a flag or uncertainty in the relationship
    Requires human intervention to resolve

    Attributes:
        fir_a_id: FIR/A relationship ID
        reason: Why the flag was raised
        suggested_method: Suggested resolution method
        continuity_hash: Continuity hash after notification
    """
    fir_a_id: str
    reason: str
    suggested_method: Optional[str] = None
    continuity_hash: Optional[str] = None


@dataclass
class RelationshipEvent:
    """
    Individual event in a relationship's continuity chain

    Attributes:
        seq: Sequence number (monotonically increasing)
        continuity_hash: Hash at this point in chain
        payload: Event data (type, context, etc.)
        timestamp: ISO timestamp
    """
    seq: int
    continuity_hash: str
    payload: Dict[str, Any]
    timestamp: Optional[str] = None


@dataclass
class DIDKeyInfo:
    """
    Information about DID keys in a relationship

    Attributes:
        did_public_key: Public DID key (PEM format)
        exchange_public_key: Key exchange public key (hex)
        hid_did_binding: HID-DID binding hash
        created_at: When this key was registered
    """
    did_public_key: str
    exchange_public_key: Optional[str] = None
    hid_did_binding: Optional[str] = None
    created_at: Optional[str] = None
