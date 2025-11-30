"""
Cryptographic utilities for JIS Client
Handles DID/HID key generation and management
"""
import hashlib
import json
from typing import Dict, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519


class DIDKey:
    """
    Device Identity Key (DID-KEY)

    - Can be shared with servers
    - Used for device authentication
    - Public key transmitted during FIR/A
    - Private key stays on device

    Example:
        did = DIDKey.generate()
        public_pem = did.export_public()

        # Later, load from storage
        did = DIDKey.from_private_pem(stored_pem)
    """

    def __init__(self, private_key: Optional[ed25519.Ed25519PrivateKey] = None):
        self.private_key = private_key
        self.public_key = private_key.public_key() if private_key else None

    @classmethod
    def generate(cls) -> "DIDKey":
        """Generate new DID key pair"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        return cls(private_key)

    def sign(self, data: bytes) -> bytes:
        """Sign data with DID private key"""
        if not self.private_key:
            raise ValueError("Private key not available")
        return self.private_key.sign(data)

    def export_public(self) -> str:
        """Export public key as PEM string"""
        if not self.public_key:
            raise ValueError("Public key not available")
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def export_private(self) -> str:
        """
        Export private key as PEM string
        WARNING: Store securely! This is your device identity.
        """
        if not self.private_key:
            raise ValueError("Private key not available")
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')

    @classmethod
    def from_private_pem(cls, pem: str) -> "DIDKey":
        """Load DID key from private PEM string"""
        private_key = serialization.load_pem_private_key(
            pem.encode('utf-8'),
            password=None
        )
        return cls(private_key)

    @classmethod
    def from_public_pem(cls, pem: str) -> "DIDKey":
        """
        Load DID key from public PEM (verification only)
        Note: Cannot sign with public-only key
        """
        public_key = serialization.load_pem_public_key(pem.encode('utf-8'))
        instance = cls()
        instance.public_key = public_key
        return instance


class HIDKey:
    """
    Human Identity Key (HID-KEY)

    ⚠️  CRITICAL: This key NEVER leaves the device!

    - Lives only in local secure storage
    - Bound to biometric data (optional integration)
    - Used to prove human presence
    - Creates attestations linking HID to DID
    - Public key never transmitted (only binding hashes)

    Example:
        hid = HIDKey.generate()

        # Create attestation proving human authorized this DID
        attestation = hid.attest_did(did.export_public(), context={...})

        # NEVER do this in production!
        # hid.export_private()  # ❌ Don't transmit HID!
    """

    def __init__(self, private_key: Optional[ed25519.Ed25519PrivateKey] = None):
        self.private_key = private_key
        # Public key exists but is NEVER transmitted
        self.public_key = private_key.public_key() if private_key else None

    @classmethod
    def generate(cls) -> "HIDKey":
        """Generate new HID key pair"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        return cls(private_key)

    def attest_did(self, did_public_pem: str, context: Dict) -> bytes:
        """
        Create attestation that links HID to DID
        This proves human authorized this device
        Returns signature, NOT the HID key itself
        """
        if not self.private_key:
            raise ValueError("Private key not available")

        payload = json.dumps({
            "did_public": did_public_pem,
            "context": context,
            "type": "hid_attestation"
        }, sort_keys=True).encode('utf-8')

        return self.private_key.sign(payload)

    def derive_did_binding(self, did_key: DIDKey) -> str:
        """
        Derive a binding hash between HID and DID
        This hash can be sent to the server for verification
        The server can verify the binding without knowing the HID
        """
        if not self.public_key or not did_key.public_key:
            raise ValueError("Keys not available")

        combined = (
            self.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            ) +
            did_key.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        )
        return hashlib.sha256(combined).hexdigest()

    def export_private(self) -> str:
        """
        ⚠️  WARNING: For backup/migration ONLY!
        Store in secure, encrypted storage (e.g., device keychain)
        NEVER transmit this over network!
        """
        if not self.private_key:
            raise ValueError("Private key not available")

        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')

    @classmethod
    def from_private_pem(cls, pem: str) -> "HIDKey":
        """
        Load HID key from secure storage
        Only for local restoration, never from network!
        """
        private_key = serialization.load_pem_private_key(
            pem.encode('utf-8'),
            password=None
        )
        return cls(private_key)


class KeyExchange:
    """
    Diffie-Hellman key exchange for secure channel setup
    Used during FIR/A initialization to establish shared secret
    """

    def __init__(self):
        self.private_key = x25519.X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def export_public(self) -> str:
        """Export public exchange key as hex string"""
        raw = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return raw.hex()

    def derive_shared_secret(self, peer_public_hex: str) -> bytes:
        """
        Derive shared secret from peer's public key
        Both parties will derive the same secret
        """
        peer_public_raw = bytes.fromhex(peer_public_hex)
        peer_public = x25519.X25519PublicKey.from_public_bytes(peer_public_raw)
        shared = self.private_key.exchange(peer_public)
        # Use HKDF for key derivation
        return hashlib.sha256(shared).digest()


def create_did_exchange_payload(did_key: DIDKey, exchange: KeyExchange) -> Dict:
    """
    Create complete DID exchange payload for FIR/A initialization

    Contains:
    - DID public key (for authentication)
    - Exchange public key (for encrypted channel)
    - Signature proving DID ownership

    Args:
        did_key: DID key to exchange
        exchange: Key exchange instance

    Returns:
        Dict ready to send to router
    """
    payload = {
        "did_public": did_key.export_public(),
        "exchange_public": exchange.export_public(),
    }

    # Sign the payload with DID to prove ownership
    to_sign = json.dumps(payload, sort_keys=True).encode('utf-8')
    signature = did_key.sign(to_sign)

    payload["signature"] = signature.hex()
    return payload
