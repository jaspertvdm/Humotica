#!/usr/bin/env python3
"""
Simplest possible TIBET-BETTI example

This shows the absolute minimum needed to:
1. Connect to BETTI router
2. Establish trust
3. Send a TIBET intent
"""

import sys
import os

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from tibet_betti_client import TibetBettiClient


def main():
    print("TIBET-BETTI Hello World\n")

    # 1. Initialize client
    print("1. Connecting to BETTI router...")
    client = TibetBettiClient(
        betti_url="http://localhost:18081",  # BETTI router
        secret="denDolder_2024!"
    )

    try:
        health = client.health_check()
        print(f"   ✓ Connected! Status: {health['status']}\n")
    except Exception as e:
        print(f"   ✗ BETTI router not running: {e}")
        print("\n   Please start the BETTI router first:")
        print("   cd tbet-router && node src/index.js\n")
        return

    # 2. Establish trust
    print("2. Establishing trust relationship...")
    relationship = client.establish_trust(
        initiator="hello_world_app",
        responder="test_user"
    )
    print(f"   ✓ Trust established!")
    print(f"   FIR/A ID: {relationship.id}\n")

    # 3. Send TIBET intent
    print("3. Sending TIBET intent...")
    result = client.send_tibet(
        relationship_id=relationship.id,
        intent="hello_world",
        context={
            "message": "Hello from TIBET-BETTI!",
            "timestamp": "2025-11-27"
        }
    )
    print(f"   ✓ TIBET sent!")
    print(f"   Status: {result['status']}\n")

    print("=" * 50)
    print("Success! Your TIBET-BETTI SDK is working! 🎉")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Bye!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
