"""
JIS Client SDK - Python
Easy-to-use client library for JTel Identity Standard

Example usage:
    from jis_client import JISClient, DIDKey, HIDKey

    # Initialize client
    client = JISClient(router_url="http://localhost:18081", secret="your-secret")

    # Generate keys
    did = DIDKey.generate()
    hid = HIDKey.generate()  # This stays on device!

    # Create relationship
    fir_a = client.init_relationship(
        initiator="my-app",
        responder="server",
        roles=["client"],
        did_key=did,
        hid_key=hid
    )

    # Send intent
    client.send_intent(
        fir_a_id=fir_a.id,
        intent="unlock_door",
        context={"location": "home"}
    )
"""

from .client import JISClient
from .crypto import DIDKey, HIDKey
from .models import FIRARelationship, IntentResponse, NIRNotification

__version__ = "0.1.0"
__all__ = [
    "JISClient",
    "DIDKey",
    "HIDKey",
    "FIRARelationship",
    "IntentResponse",
    "NIRNotification",
]
