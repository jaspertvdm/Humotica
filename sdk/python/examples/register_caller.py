#!/usr/bin/env python3
"""
Caller Registration Tool
========================

Register your phone number with DID/HID keys for verified calling.

This creates a "caller identity" that can be verified during calls:
- DID Key: Device identity (your phone)
- HID Key: Human identity (your biometric/PIN)
- Phone Number: Your verified number
- Display Name: How you appear to receivers

Usage:
    # Interactive mode
    python register_caller.py

    # Command line
    python register_caller.py --phone +31612345678 --name "Jasper van de Meent"

    # Use existing keys
    python register_caller.py --phone +31612345678 --name "Jasper" --did-file ~/.jis/did.pem --hid-file ~/.jis/hid.pem
"""

import argparse
import json
import os
import sys
from pathlib import Path

from jis_client import DIDKey, HIDKey, JISClient


def save_keys(did: DIDKey, hid: HIDKey, phone: str):
    """Save keys to secure storage"""
    config_dir = Path.home() / ".jis"
    config_dir.mkdir(exist_ok=True, mode=0o700)

    # Save DID (can be backed up)
    did_file = config_dir / f"did_{phone.replace('+', '')}.pem"
    did_file.write_text(did.export_private())
    did_file.chmod(0o600)

    # Save HID (NEVER transmit, NEVER backup to cloud!)
    hid_file = config_dir / f"hid_{phone.replace('+', '')}.pem"
    hid_file.write_text(hid.export_private())
    hid_file.chmod(0o600)

    print(f"\n✓ Keys saved to:")
    print(f"  DID: {did_file}")
    print(f"  HID: {hid_file}")
    print(f"\n⚠️  IMPORTANT:")
    print(f"  - Keep HID file secure (never transmit!)")
    print(f"  - DID can be backed up")
    print(f"  - Both files are chmod 600 (owner only)")


def load_keys(did_file: str, hid_file: str):
    """Load keys from files"""
    did = DIDKey.from_private_pem(Path(did_file).read_text())
    hid = HIDKey.from_private_pem(Path(hid_file).read_text())
    return did, hid


def register_caller(
    client: JISClient,
    phone: str,
    name: str,
    did: DIDKey,
    hid: HIDKey
):
    """Register caller identity with JIS Router"""

    print(f"\n📞 Registering Caller Identity")
    print(f"  Phone: {phone}")
    print(f"  Name: {name}")

    # Create FIR/A for this phone number registration
    fir_a = client.init_relationship(
        initiator=f"phone_{phone}",
        responder="verified_calling_registry",
        roles=["caller", "phone_owner"],
        context={
            "phone_number": phone,
            "display_name": name,
            "registration_type": "verified_caller"
        },
        humotica=f"Caller registration for {name} ({phone})",
        did_key=did,
        hid_key=hid
    )

    print(f"\n✓ Registration successful!")
    print(f"  FIR/A ID: {fir_a.id}")
    print(f"  Phone: {phone}")
    print(f"  Name: {name}")
    print(f"  DID: {did.export_public()[:50]}...")
    print(f"  HID Binding: {hid.derive_did_binding(did)[:32]}...")

    # Send registration intent
    result = client.send_intent(
        fir_a.id,
        "register_verified_caller",
        context={
            "phone_number": phone,
            "display_name": name,
            "capabilities": ["voice", "verified"]
        }
    )

    print(f"\n✓ Registration confirmed in chain")
    print(f"  Events: {result.events}")
    print(f"  Hash: {result.continuity_hash[:16]}...")

    return fir_a


def interactive_mode(client: JISClient):
    """Interactive registration"""
    print("=" * 60)
    print("  JIS Verified Caller Registration")
    print("=" * 60)

    # Get phone number
    phone = input("\nPhone number (e.g. +31612345678): ").strip()
    if not phone:
        print("❌ Phone number required")
        return

    # Get display name
    name = input("Display name (e.g. Jasper van de Meent): ").strip()
    if not name:
        print("❌ Display name required")
        return

    # Check for existing keys
    config_dir = Path.home() / ".jis"
    did_file = config_dir / f"did_{phone.replace('+', '')}.pem"
    hid_file = config_dir / f"hid_{phone.replace('+', '')}.pem"

    if did_file.exists() and hid_file.exists():
        use_existing = input(f"\nFound existing keys for {phone}. Use them? [Y/n]: ").strip().lower()
        if use_existing != 'n':
            print("\n🔑 Loading existing keys...")
            did, hid = load_keys(str(did_file), str(hid_file))
            print("✓ Keys loaded")
        else:
            print("\n🔑 Generating NEW keys...")
            did = DIDKey.generate()
            hid = HIDKey.generate()
            save_keys(did, hid, phone)
    else:
        print("\n🔑 Generating NEW DID/HID keys...")
        print("  (This may take a few seconds...)")
        did = DIDKey.generate()
        hid = HIDKey.generate()
        print("✓ Keys generated")
        save_keys(did, hid, phone)

    # Register
    fir_a = register_caller(client, phone, name, did, hid)

    print("\n" + "=" * 60)
    print("  ✓ Registration Complete!")
    print("=" * 60)
    print(f"\nYour phone number {phone} is now VERIFIED.")
    print(f"When you call someone, they will see:")
    print(f"  ✓ VERIFIED: {name}")
    print(f"\nYour keys are stored in: {config_dir}")
    print(f"Keep these files secure!")


def main():
    parser = argparse.ArgumentParser(description="Register verified caller identity")
    parser.add_argument("--router", default="http://localhost:18081", help="JIS Router URL")
    parser.add_argument("--secret", default=os.getenv("JIS_SECRET", "denDolder_2024!"), help="JIS shared secret")
    parser.add_argument("--phone", help="Phone number (e.g. +31612345678)")
    parser.add_argument("--name", help="Display name")
    parser.add_argument("--did-file", help="Path to existing DID private key file")
    parser.add_argument("--hid-file", help="Path to existing HID private key file")

    args = parser.parse_args()

    # Initialize client
    client = JISClient(args.router, secret=args.secret)

    # Check connection
    try:
        health = client.health_check()
        print(f"✓ Connected to JIS Router: {args.router}")
    except Exception as e:
        print(f"❌ Cannot connect to router: {e}")
        print(f"Make sure router is running on {args.router}")
        sys.exit(1)

    # Command line mode or interactive
    if args.phone and args.name:
        # Load or generate keys
        if args.did_file and args.hid_file:
            print("🔑 Loading keys from files...")
            did, hid = load_keys(args.did_file, args.hid_file)
        else:
            print("🔑 Generating new keys...")
            did = DIDKey.generate()
            hid = HIDKey.generate()
            save_keys(did, hid, args.phone)

        # Register
        register_caller(client, args.phone, args.name, did, hid)
    else:
        # Interactive mode
        interactive_mode(client)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nRegistration cancelled. Bye! 👋")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
