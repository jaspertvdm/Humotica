#!/usr/bin/env python3
"""
Phone Receiver Mock - Simuleer hoe een telefoon app intents ontvangt

Dit script simuleert een telefoon app die:
1. WebSocket verbinding maakt met JIS Router
2. Incoming TBET intents ontvangt
3. Caller context toont (zoals op een echt scherm)
4. Appointments kan accepteren/weigeren
5. Biometric authentication simuleert

Gebruik:
  python phone_receiver_mock.py                 # Start receiver
  python phone_receiver_mock.py --phone-id 001  # Specific phone ID
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    print("❌ websockets module not found!")
    print("Install: pip install websockets")
    sys.exit(1)


ROUTER_WS_URL = "ws://localhost:18081/ws"


def print_banner(text: str, char: str = "="):
    """Print banner"""
    print("\n" + char*70)
    print(f"  {text}")
    print(char*70)


def print_phone_display(intent: str, context: Dict[str, Any], trust_level: int):
    """Display incoming call/intent op telefoon scherm"""

    print("\n" + "┌" + "─"*68 + "┐")
    print("│" + " "*68 + "│")

    # Determine display based on trust level
    if trust_level == 0:
        icon = "⚠"
        title = "UNVERIFIED CALLER"
        fields = [
            ("Number", context.get("caller_number", "Unknown"))
        ]
        actions = ["Screen", "Block", "Report"]
        notice = "⚠️  Challenge-response required"

    elif trust_level == 1:
        icon = "✓"
        title = "VERIFIED CALLER"
        fields = [
            ("Name", context.get("display_name", "Unknown")),
            ("Number", context.get("caller_number", "Unknown"))
        ]
        actions = ["Accept", "Reject", "Message"]
        notice = None

    elif trust_level == 2:
        icon = "🏢"
        title = "VERIFIED BUSINESS"
        fields = [
            ("Company", context.get("business_name", "Unknown")),
            ("KVK", context.get("kvk_number", "N/A")),
            ("Number", context.get("caller_number", "Unknown"))
        ]
        actions = ["Accept", "Reject", "Voicemail"]
        notice = None

    elif trust_level == 3:
        icon = "🏦"
        title = "VERIFIED FINANCIAL INSTITUTION"
        fields = [
            ("Institution", context.get("institution_name", "Unknown")),
            ("License", f"AFM: {context.get('license_number', 'N/A')}"),
            ("Account", f"****{context.get('account_last_4', 'XXXX')}"),
            ("Appointment", context.get("appointment_datetime", "N/A")),
            ("Subject", context.get("subject", "N/A"))
        ]
        actions = ["Accept", "Reschedule", "Reject"]
        notice = "🔒 Pre-Scheduled • Call will be recorded (MiFID II)"

    elif trust_level == 4:
        if "attorney" in context or "legal" in intent:
            icon = "⚖️"
            title = "VERIFIED LEGAL PROFESSIONAL"
            fields = [
                ("Attorney", context.get("attorney_name", "Unknown")),
                ("NOvA", context.get("nova_number", "N/A")),
                ("Case", context.get("case_reference", "N/A")),
                ("Appointment", context.get("appointment_datetime", "N/A"))
            ]
            notice = "🔒 Attorney-Client Privilege • E2E Encrypted"
        else:
            icon = "🏥"
            title = "VERIFIED MEDICAL PROFESSIONAL"
            fields = [
                ("Doctor", f"Dr. {context.get('doctor_name', 'Unknown')}"),
                ("Specialty", context.get("specialty", "N/A")),
                ("BIG", context.get("big_number", "N/A")),
                ("Patient ID", f"****{context.get('patient_id_last_4', 'XXXX')}"),
                ("Appointment", context.get("appointment_datetime", "N/A"))
            ]
            notice = "🔒 HIPAA/AVG Protected • E2E Encrypted"
        actions = ["Accept", "Reschedule"]

    elif trust_level == 5:
        icon = "🚔"
        title = "VERIFIED GOVERNMENT AGENCY"
        fields = [
            ("Agency", context.get("agency_name", "Unknown")),
            ("Department", context.get("department", "N/A")),
            ("Officer", f"Badge #{context.get('badge_number', 'N/A')}"),
            ("Case", context.get("case_ref", "N/A")),
            ("Legal Basis", context.get("legal_basis", "N/A")),
            ("Appointment", context.get("appointment_datetime", "N/A"))
        ]
        actions = ["Accept", "Request Lawyer", "Reschedule"]
        notice = "🛡️ PKIoverheid • YOUR RIGHTS:\n• Zwijgrecht • Recht op raadsman"

    else:
        icon = "📞"
        title = "INCOMING"
        fields = [("Intent", intent)]
        actions = ["Accept", "Reject"]
        notice = None

    # Display
    print(f"│  {icon}  {title:62s}│")
    print("│" + " "*68 + "│")
    print("│" + "─"*68 + "│")

    for label, value in fields:
        print(f"│  {label:20s} {value:46s}│")

    if notice:
        print("│" + " "*68 + "│")
        print("│" + "─"*68 + "│")
        for line in notice.split("\n"):
            print(f"│  {line:66s}│")

    print("│" + " "*68 + "│")
    print("│" + "─"*68 + "│")

    action_str = "  ".join([f"[{a}]" for a in actions])
    centered = action_str.center(66)
    print(f"│  {centered:66s}│")
    print("│" + " "*68 + "│")
    print("└" + "─"*68 + "┘")


def check_appointment_window(context: Dict[str, Any]) -> bool:
    """Check if current time is within appointment window"""
    if "appointment_id" not in context:
        return True  # No appointment = always allowed

    # In real implementation, this would check against stored appointments
    # For now, we simulate based on context
    return True  # Simplified for demo


async def handle_incoming_intent(
    intent_data: Dict[str, Any],
    phone_id: str
) -> Dict[str, str]:
    """
    Handle incoming intent

    Returns:
        Response dict with action taken
    """
    intent = intent_data.get("intent", "unknown")
    context = intent_data.get("context", {})
    fir_a_id = intent_data.get("fir_a_id", "unknown")

    # Determine trust level from context
    trust_level = context.get("trust_level", 1)

    print_banner(f"📱 INCOMING INTENT: {intent}", "═")
    print(f"\nFIR/A ID: {fir_a_id}")
    print(f"Trust Level: {trust_level}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Show phone display
    print_phone_display(intent, context, trust_level)

    # Check appointment if required
    if trust_level >= 3:
        in_window = check_appointment_window(context)
        if not in_window:
            print("\n❌ CALL BLOCKED: Outside appointment window")
            return {"action": "blocked", "reason": "outside_appointment_window"}

    # Simulate biometric auth for Level 4+
    if trust_level >= 4:
        print("\n🔐 Biometric authentication required...")
        await asyncio.sleep(1)
        print("   👆 Touch ID...")
        await asyncio.sleep(0.5)
        print("   ✅ Authenticated")

    # Simulate MFA for Level 5
    if trust_level >= 5:
        print("\n🔑 Multi-factor authentication required...")
        await asyncio.sleep(1)
        print("   📱 DigiD app...")
        await asyncio.sleep(0.5)
        print("   ✅ MFA successful")

        print("\n⚖️ Displaying rights notification...")
        await asyncio.sleep(0.5)
        print("   • Zwijgrecht (right to remain silent)")
        print("   • Recht op raadsman (legal counsel)")
        print("   • Dit gesprek wordt opgenomen")

    # Auto-accept for demo (in real app, user would tap)
    print("\n⏳ Waiting for user action...")
    await asyncio.sleep(2)
    print("✅ User accepted call")

    # Log acceptance
    print(f"\n📞 Call connected!")
    print(f"   Intent: {intent}")
    print(f"   Trust Level: {trust_level}")
    if "appointment_datetime" in context:
        print(f"   Appointment: {context['appointment_datetime']}")

    return {
        "action": "accepted",
        "timestamp": datetime.now().isoformat()
    }


async def phone_receiver(phone_id: str, router_ws_url: str):
    """
    Main phone receiver loop

    Connects to router via WebSocket and listens for incoming intents
    """
    print_banner(f"📱 Phone Receiver Mock - ID: {phone_id}")

    print(f"\nConnecting to router: {router_ws_url}")

    try:
        async with websockets.connect(router_ws_url) as websocket:
            print(f"✅ Connected to router")

            # Register phone
            await websocket.send(json.dumps({
                "type": "register",
                "phone_id": phone_id,
                "timestamp": datetime.now().isoformat()
            }))

            print(f"📱 Phone registered: {phone_id}")
            print(f"\n🎧 Listening for incoming intents...")
            print(f"   (Press Ctrl+C to stop)\n")

            # Listen for incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "intent":
                        # Incoming intent
                        response = await handle_incoming_intent(data, phone_id)

                        # Send response back
                        await websocket.send(json.dumps({
                            "type": "intent_response",
                            "fir_a_id": data.get("fir_a_id"),
                            "response": response
                        }))

                        print("\n" + "-"*70)
                        print("🎧 Listening for next intent...\n")

                    elif msg_type == "ping":
                        # Keep-alive
                        await websocket.send(json.dumps({"type": "pong"}))

                    else:
                        print(f"⚠️  Unknown message type: {msg_type}")

                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON: {message}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")

    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        print(f"\nMake sure:")
        print(f"  1. JIS Router is running")
        print(f"  2. WebSocket endpoint is enabled: {router_ws_url}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def simulate_offline_mode(phone_id: str):
    """
    Offline mode - manually trigger test intents

    Voor als WebSocket nog niet beschikbaar is
    """
    print_banner(f"📱 Phone Receiver Mock (Offline) - ID: {phone_id}")

    print("\n⚠️  WebSocket not available - running in OFFLINE mode")
    print("   This will simulate incoming intents manually\n")

    test_intents = [
        {
            "intent": "verified_call_setup",
            "fir_a_id": "test-001",
            "context": {
                "trust_level": 1,
                "display_name": "Jasper van de Meent",
                "caller_number": "+31612345678"
            }
        },
        {
            "intent": "financial_advice",
            "fir_a_id": "test-002",
            "context": {
                "trust_level": 3,
                "institution_name": "ING Bank Nederland",
                "license_number": "12345",
                "account_last_4": "4567",
                "appointment_datetime": "26-11-2025 14:30",
                "subject": "Hypotheek bespreking"
            }
        },
        {
            "intent": "legal_consultation",
            "fir_a_id": "test-003",
            "context": {
                "trust_level": 4,
                "attorney_name": "Mr. J. de Vries",
                "nova_number": "123456",
                "case_reference": "2024-CV-12345",
                "appointment_datetime": "26-11-2025 15:00"
            }
        },
        {
            "intent": "police_interview",
            "fir_a_id": "test-004",
            "context": {
                "trust_level": 5,
                "agency_name": "Politie Nederland",
                "department": "Eenheid Amsterdam",
                "badge_number": "12345",
                "case_ref": "2024-ZV-98765",
                "legal_basis": "Art. 27 WvSv",
                "appointment_datetime": "26-11-2025 09:00"
            }
        }
    ]

    async def run_tests():
        for i, intent_data in enumerate(test_intents, 1):
            print(f"\n{'='*70}")
            print(f"  Test {i}/{len(test_intents)}")
            print(f"{'='*70}")

            await handle_incoming_intent(intent_data, phone_id)

            if i < len(test_intents):
                input("\n\nPress ENTER for next test...")

    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n\nInterrupted. Bye! 👋")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Phone Receiver Mock - Simulate phone receiving TBET intents"
    )
    parser.add_argument(
        "--phone-id",
        default="phone_001",
        help="Phone identifier (default: phone_001)"
    )
    parser.add_argument(
        "--router-ws",
        default=ROUTER_WS_URL,
        help=f"Router WebSocket URL (default: {ROUTER_WS_URL})"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run in offline mode (simulate without WebSocket)"
    )

    args = parser.parse_args()

    if args.offline:
        simulate_offline_mode(args.phone_id)
    else:
        try:
            asyncio.run(phone_receiver(args.phone_id, args.router_ws))
        except KeyboardInterrupt:
            print("\n\n📱 Phone receiver stopped. Bye! 👋")


if __name__ == "__main__":
    main()
