#!/usr/bin/env python3
"""
Basic usage example for JIS Client SDK

This example shows:
1. Generating DID/HID keys
2. Initializing a FIR/A relationship
3. Sending intents
4. Handling NIR notifications
"""

import logging

from jis_client import DIDKey, HIDKey, JISClient

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # 1. Initialize client
    client = JISClient(
        router_url="http://localhost:18081",
        secret="denDolder_2024!"  # Change to your router secret
    )

    # 2. Check router health
    health = client.health_check()
    logger.info(f"Router status: {health['status']}")

    # 3. Generate keys
    logger.info("Generating DID and HID keys...")
    did = DIDKey.generate()
    hid = HIDKey.generate()  # This key NEVER leaves this device!

    logger.info(f"DID public key: {did.export_public()[:50]}...")
    logger.info(f"HID-DID binding: {hid.derive_did_binding(did)[:16]}...")

    # 4. Initialize FIR/A relationship
    logger.info("\nInitializing FIR/A relationship...")
    fir_a = client.init_relationship(
        initiator="python-demo-client",
        responder="jis-router",
        roles=["client", "demo"],
        context={
            "device": "laptop",
            "location": "office",
            "app_version": "1.0.0"
        },
        humotica="Demo session with Python SDK",
        did_key=did,
        hid_key=hid  # Used to create binding, but NOT sent to router
    )

    logger.info(f"✓ FIR/A created: {fir_a.id}")
    logger.info(f"  Continuity hash: {fir_a.continuity_hash[:16]}...")
    logger.info(f"  Events: {fir_a.events}")

    # 5. Send some intents
    logger.info("\nSending intents...")

    intent1 = client.send_intent(
        fir_a_id=fir_a.id,
        intent="verify_identity",
        context={"method": "demo"}
    )
    logger.info(f"✓ Intent sent. New hash: {intent1.continuity_hash[:16]}...")

    intent2 = client.send_intent(
        fir_a_id=fir_a.id,
        intent="request_data",
        context={"data_type": "user_profile"}
    )
    logger.info(f"✓ Intent sent. New hash: {intent2.continuity_hash[:16]}...")

    # 6. Simulate NIR notification
    logger.info("\nSimulating NIR (flag)...")
    nir = client.notify_nir(
        fir_a_id=fir_a.id,
        reason="unusual_activity_demo",
        suggested_method="biometric_confirm"
    )
    logger.info(f"⚠ NIR notification sent: {nir.reason}")

    # 7. Confirm NIR
    logger.info("\nResolving NIR...")
    confirmed = client.confirm_nir(
        fir_a_id=fir_a.id,
        method="biometric",
        result="confirmed"
    )
    logger.info(f"✓ NIR resolved. New hash: {confirmed.continuity_hash[:16]}...")

    # 8. Get relationship info
    logger.info("\nFetching relationship info...")
    info = client.get_relationship(fir_a.id)
    logger.info(f"Total events: {info.events}")
    logger.info(f"Current hash: {info.continuity_hash[:16]}...")

    # 9. Get event history
    logger.info("\nFetching event history...")
    events = client.get_events(fir_a.id, limit=10)
    for event in events:
        logger.info(f"  Event {event.seq}: {event.payload.get('type')} @ {event.timestamp}")

    # 10. Get DID keys
    logger.info("\nFetching DID keys...")
    keys = client.get_did_keys(fir_a.id)
    for entity, key_info in keys.items():
        logger.info(f"  {entity}:")
        logger.info(f"    DID: {key_info.did_public_key[:50]}...")
        if key_info.hid_did_binding:
            logger.info(f"    HID-DID binding: {key_info.hid_did_binding[:16]}...")

    # 11. Get metrics
    logger.info("\nRouter metrics:")
    metrics = client.get_metrics()
    logger.info(f"  Total relationships: {metrics.get('total_relationships', 'N/A')}")
    logger.info(f"  Total events: {metrics.get('total_events', 'N/A')}")

    logger.info("\n✓ Demo completed successfully!")


if __name__ == "__main__":
    main()
