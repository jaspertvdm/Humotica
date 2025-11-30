"""
Trust Token (FIR/A) classes
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrustToken:
    """
    Trust Token = "Wij Kennen Elkaar"

    A trust token represents an established relationship between two entities.
    It carries:
    - Identity (who are the parties)
    - History (how many interactions)
    - Context (what's the relationship about)
    - Constraints (what's allowed)
    """

    token_id: str
    initiator: str
    responder: str
    trust_level: int = 1  # 0-5
    established_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    total_interactions: int = 0

    def is_valid(self) -> bool:
        """Check if token is valid"""
        # TODO: Add expiry, revocation checks
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "token_id": self.token_id,
            "initiator": self.initiator,
            "responder": self.responder,
            "trust_level": self.trust_level,
            "established_at": self.established_at.isoformat() if self.established_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "total_interactions": self.total_interactions
        }


@dataclass
class FIRARelationship:
    """
    FIR/A = Formalized Intent Relationship Acknowledged

    Complete relationship information including continuity chain.
    """

    id: str
    token: str  # Token ID (often same as id)
    initiator: Optional[str] = None
    responder: Optional[str] = None
    trust_level: int = 1
    continuity_hash: Optional[str] = None
    did_key: Optional[Any] = None  # DIDKey object
    hid_key: Optional[Any] = None  # HIDKey object (never transmitted!)

    def to_trust_token(self) -> TrustToken:
        """Convert to TrustToken"""
        return TrustToken(
            token_id=self.token,
            initiator=self.initiator or "unknown",
            responder=self.responder or "unknown",
            trust_level=self.trust_level
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "id": self.id,
            "token": self.token,
            "initiator": self.initiator,
            "responder": self.responder,
            "trust_level": self.trust_level,
            "continuity_hash": self.continuity_hash
        }
