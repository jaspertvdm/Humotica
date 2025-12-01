"""
BETTI Token Chain (Law 13)

Implements HMAC-based token chaining for tamper-proof audit trails.
Each token is cryptographically linked to the previous one.

Usage:
    from token_chain import TokenChain

    chain = TokenChain(secret="your-secret")

    # Add tokens
    token1 = chain.add("user1|action1|timestamp1")
    token2 = chain.add("user2|action2|timestamp2")

    # Verify chain
    is_valid = chain.verify()

    # Get audit trail
    trail = chain.get_trail()
"""

import hmac
import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


@dataclass
class ChainToken:
    """Single token in the chain"""
    index: int
    data: str
    hash: str
    prev_hash: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "data": self.data,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp
        }


@dataclass
class TokenChain:
    """
    HMAC-based token chain for BETTI Law 13.

    Creates tamper-proof audit trails where each token
    is cryptographically linked to the previous one.
    """

    secret: str = "BETTI-JIS-TIBET-DEFAULT"
    tokens: List[ChainToken] = field(default_factory=list)
    genesis_hash: str = "genesis"

    def _hmac_sha256(self, data: str) -> str:
        """Generate HMAC-SHA256 hash"""
        return hmac.new(
            self.secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _sha256(self, data: str) -> str:
        """Generate SHA256 hash"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @property
    def last_hash(self) -> str:
        """Get the hash of the last token"""
        if not self.tokens:
            return self.genesis_hash
        return self.tokens[-1].hash

    @property
    def length(self) -> int:
        """Get chain length"""
        return len(self.tokens)

    def add(self, data: str) -> ChainToken:
        """
        Add a new token to the chain.

        Args:
            data: The data to include in the token

        Returns:
            The newly created ChainToken
        """
        prev_hash = self.last_hash
        index = len(self.tokens) + 1
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Create hash: HMAC(secret, data|prev_hash|index)
        hash_input = f"{data}|{prev_hash}|{index}"
        token_hash = self._hmac_sha256(hash_input)

        token = ChainToken(
            index=index,
            data=data,
            hash=token_hash,
            prev_hash=prev_hash,
            timestamp=timestamp
        )

        self.tokens.append(token)
        return token

    def verify(self) -> tuple[bool, List[str]]:
        """
        Verify the integrity of the entire chain.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.tokens:
            return True, []

        prev_hash = self.genesis_hash

        for token in self.tokens:
            # Verify prev_hash link
            if token.prev_hash != prev_hash:
                errors.append(f"Chain break at index {token.index}: prev_hash mismatch")

            # Verify token hash
            hash_input = f"{token.data}|{token.prev_hash}|{token.index}"
            expected_hash = self._hmac_sha256(hash_input)

            if token.hash != expected_hash:
                errors.append(f"Hash mismatch at index {token.index}")

            prev_hash = token.hash

        return len(errors) == 0, errors

    def get_trail(self) -> List[Dict[str, Any]]:
        """Get the full audit trail"""
        return [t.to_dict() for t in self.tokens]

    def get_token(self, index: int) -> Optional[ChainToken]:
        """Get token by index (1-based)"""
        if 1 <= index <= len(self.tokens):
            return self.tokens[index - 1]
        return None

    def save(self, filepath: str) -> None:
        """Save chain to JSON file"""
        data = {
            "genesis_hash": self.genesis_hash,
            "tokens": self.get_trail()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str, secret: str = "BETTI-JIS-TIBET-DEFAULT") -> 'TokenChain':
        """Load chain from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        chain = cls(secret=secret, genesis_hash=data.get("genesis_hash", "genesis"))

        for t in data.get("tokens", []):
            token = ChainToken(
                index=t["index"],
                data=t["data"],
                hash=t["hash"],
                prev_hash=t["prev_hash"],
                timestamp=t["timestamp"]
            )
            chain.tokens.append(token)

        return chain

    def to_dict(self) -> Dict[str, Any]:
        """Convert chain to dictionary"""
        return {
            "length": self.length,
            "last_hash": self.last_hash[:16] + "..." if self.last_hash != self.genesis_hash else self.genesis_hash,
            "genesis_hash": self.genesis_hash,
            "valid": self.verify()[0],
            "tokens": self.get_trail()
        }


class TibetTokenChain(TokenChain):
    """
    TIBET-specific token chain.

    Extends TokenChain with TIBET handshake semantics.
    """

    def add_propose(self, initiator: str, responder: str, intent: str, humotica: str = "") -> ChainToken:
        """Add a TIBET PROPOSE to the chain"""
        data = f"PROPOSE|{initiator}|{responder}|{intent}|{humotica}"
        return self.add(data)

    def add_accept(self, handshake_id: str, responder: str) -> ChainToken:
        """Add a TIBET ACCEPT to the chain"""
        data = f"ACCEPT|{handshake_id}|{responder}"
        return self.add(data)

    def add_reject(self, handshake_id: str, responder: str, reason: str = "") -> ChainToken:
        """Add a TIBET REJECT to the chain"""
        data = f"REJECT|{handshake_id}|{responder}|{reason}"
        return self.add(data)

    def add_revoke(self, session_token: str, revoker: str, reason: str = "") -> ChainToken:
        """Add a TIBET REVOKE to the chain"""
        data = f"REVOKE|{session_token}|{revoker}|{reason}"
        return self.add(data)


# Convenience function for quick verification
def verify_chain_file(filepath: str, secret: str = "BETTI-JIS-TIBET-DEFAULT") -> Dict[str, Any]:
    """
    Quick verification of a chain file.

    Returns dict with valid, length, errors.
    """
    try:
        chain = TokenChain.load(filepath, secret)
        valid, errors = chain.verify()
        return {
            "valid": valid,
            "length": chain.length,
            "errors": errors,
            "last_hash": chain.last_hash[:16] + "..."
        }
    except Exception as e:
        return {
            "valid": False,
            "length": 0,
            "errors": [str(e)],
            "last_hash": None
        }


if __name__ == "__main__":
    # Demo
    print("=== BETTI Token Chain Demo ===\n")

    chain = TibetTokenChain(secret="demo-secret")

    # Add some TIBET events
    t1 = chain.add_propose("1002", "3001", "zakelijk_gesprek", "Bellen over project")
    print(f"1. PROPOSE: index={t1.index}, hash={t1.hash[:16]}...")

    t2 = chain.add_accept("abc123", "3001")
    print(f"2. ACCEPT:  index={t2.index}, hash={t2.hash[:16]}..., prev={t2.prev_hash[:16]}...")

    t3 = chain.add_propose("1003", "3002", "support", "Hulp nodig")
    print(f"3. PROPOSE: index={t3.index}, hash={t3.hash[:16]}..., prev={t3.prev_hash[:16]}...")

    # Verify
    valid, errors = chain.verify()
    print(f"\nChain valid: {valid}")
    print(f"Chain length: {chain.length}")

    # Save
    chain.save("/tmp/demo_chain.json")
    print("\nSaved to /tmp/demo_chain.json")

    # Reload and verify
    loaded = TibetTokenChain.load("/tmp/demo_chain.json", "demo-secret")
    valid2, _ = loaded.verify()
    print(f"Reloaded chain valid: {valid2}")
