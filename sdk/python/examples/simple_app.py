#!/usr/bin/env python3
"""
Simple app example - minimal code to get started

This is the SIMPLEST way to use JIS Client SDK.
Perfect for quick prototyping or simple applications.
"""

from jis_client import DIDKey, HIDKey, JISClient

# 1. Setup
client = JISClient("http://localhost:18081", secret="denDolder_2024!")
did = DIDKey.generate()
hid = HIDKey.generate()

# 2. Create relationship
fir_a = client.init_relationship(
    initiator="my-app",
    responder="server",
    roles=["client"],
    did_key=did,
    hid_key=hid
)

print(f"✓ Relationship created: {fir_a.id}")

# 3. Send intent
result = client.send_intent(
    fir_a_id=fir_a.id,
    intent="unlock_door",
    context={"location": "home"}
)

print(f"✓ Intent sent. Events: {result.events}")

# That's it! You now have:
# - Cryptographically secure device identity (DID)
# - Human binding (HID)
# - Immutable continuity chain
# - Intent-based operations
