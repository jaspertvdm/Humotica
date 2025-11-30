#!/usr/bin/env python3
"""
TBET Live Test - Stuur ECHTE TBET intents naar JIS Router

Dit script:
1. Stuurt TBET intents naar een draaiende JIS Router
2. Maakt appointments aan voor pre-authorization
3. Test time window enforcement
4. Toont resultaten in Admin UI

Gebruik:
  python tbet_live_test.py                    # Interactive mode
  python tbet_live_test.py --scenario bank    # Specific scenario
  python tbet_live_test.py --list             # List available scenarios
"""

import argparse
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
from jis_client import JISClient, DIDKey, HIDKey

# Configuratie
ROUTER_URL = "http://localhost:18081"
SECRET = "denDolder_2024!"


def print_banner(text: str):
    """Print banner"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


class TBETTester:
    """TBET Intent Tester"""

    def __init__(self, router_url: str, secret: str):
        self.client = JISClient(router_url, secret=secret)
        self.router_url = router_url

        # Check connection
        try:
            health = self.client.health_check()
            print(f"✓ Connected to router: {health['status']}")
        except Exception as e:
            print(f"✗ Cannot connect to router: {e}")
            sys.exit(1)

    def create_fira_with_intent(
        self,
        scenario_name: str,
        initiator: str,
        responder: str,
        roles: list,
        intent: str,
        intent_context: Dict[str, Any],
        appointment_offset_minutes: int = 0,
        appointment_duration_minutes: int = 30,
        trust_level: int = 1
    ):
        """
        Create FIR/A and send TBET intent

        Args:
            scenario_name: Name of test scenario
            initiator: Initiating entity
            responder: Responding entity
            roles: Declared roles
            intent: TBET intent identifier
            intent_context: Context for intent
            appointment_offset_minutes: Minutes from now for appointment (0 = now)
            appointment_duration_minutes: Duration of appointment window
            trust_level: Trust level (0-5)
        """
        print_banner(f"Test: {scenario_name}")

        # Generate keys
        print("\n🔑 Generating keys...")
        did = DIDKey.generate()
        hid = HIDKey.generate()

        # Create appointment context if needed
        fir_context = {
            "test_scenario": scenario_name,
            "trust_level": trust_level,
            "timestamp": datetime.now().isoformat()
        }

        if appointment_offset_minutes is not None:
            appointment_start = datetime.now() + timedelta(minutes=appointment_offset_minutes)
            appointment_end = appointment_start + timedelta(minutes=appointment_duration_minutes)

            fir_context["appointment_id"] = f"appt_{int(time.time())}_{scenario_name}"
            fir_context["appointment_start"] = appointment_start.isoformat()
            fir_context["appointment_end"] = appointment_end.isoformat()
            fir_context["appointment_subject"] = intent_context.get("subject", scenario_name)

            print(f"\n📅 Appointment Window:")
            print(f"   Start: {appointment_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   End:   {appointment_end.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duration: {appointment_duration_minutes} minutes")

        # Create FIR/A
        print(f"\n🤝 Creating FIR/A: {initiator} <-> {responder}")
        fir_a = self.client.init_relationship(
            initiator=initiator,
            responder=responder,
            roles=roles,
            context=fir_context,
            humotica=f"TBET test: {scenario_name}",
            did_key=did,
            hid_key=hid
        )

        print(f"✓ FIR/A ID: {fir_a.id}")
        print(f"✓ Continuity: {fir_a.continuity_hash[:16]}...")

        # Send intent
        print(f"\n🎯 Sending TBET intent: {intent}")

        # Add appointment context to intent if exists
        if "appointment_id" in fir_context:
            intent_context["appointment_id"] = fir_context["appointment_id"]
            intent_context["appointment_datetime"] = appointment_start.strftime("%d-%m-%Y %H:%M")

        result = self.client.send_intent(
            fir_a_id=fir_a.id,
            intent=intent,
            context=intent_context
        )

        print(f"✓ Intent sent successfully")
        print(f"✓ New continuity: {result.continuity_hash[:16]}...")
        print(f"✓ Total events: {result.events}")

        # Check appointment window
        if "appointment_id" in fir_context:
            now = datetime.now()
            if appointment_start <= now <= appointment_end:
                print(f"\n✅ Current time IS within appointment window")
            else:
                print(f"\n⚠️  Current time is OUTSIDE appointment window")
                if now < appointment_start:
                    print(f"   (Starts in {int((appointment_start - now).total_seconds())} seconds)")
                else:
                    print(f"   (Ended {int((now - appointment_end).total_seconds())} seconds ago)")

        # Show in Admin UI
        print(f"\n👀 View in Admin UI:")
        print(f"   {self.router_url}/")
        print(f"   → Relationships → {fir_a.id}")

        return fir_a, result

    def scenario_verified_personal(self):
        """Level 1: Verified Personal Call"""
        return self.create_fira_with_intent(
            scenario_name="Verified Personal Call",
            initiator="jasper_mobile",
            responder="friend_phone",
            roles=["caller", "verified_personal"],
            intent="verified_call_setup",
            intent_context={
                "display_name": "Jasper van de Meent",
                "caller_number": "+31612345678"
            },
            appointment_offset_minutes=None,  # No appointment needed
            trust_level=1
        )

    def scenario_business_call(self):
        """Level 2: Business Call"""
        return self.create_fira_with_intent(
            scenario_name="Business Call",
            initiator="abc_consultancy",
            responder="customer_phone",
            roles=["business", "verified_company"],
            intent="business_call",
            intent_context={
                "business_name": "ABC Consultancy B.V.",
                "kvk_number": "12345678",
                "caller_number": "+31201234567",
                "subject": "Project follow-up"
            },
            appointment_offset_minutes=None,  # No appointment required
            trust_level=2
        )

    def scenario_bank_call(self):
        """Level 3: Bank calls customer"""
        print("\n💡 Scenario: Bank belt klant over hypotheek")
        print("   → Pre-authorization: REQUIRED")
        print("   → Appointment: REQUIRED")
        print("   → Recording: MANDATORY")

        return self.create_fira_with_intent(
            scenario_name="Bank Financial Advice",
            initiator="ing_bank",
            responder="customer_phone",
            roles=["financial_institution", "customer"],
            intent="financial_advice",
            intent_context={
                "institution_name": "ING Bank Nederland",
                "license_number": "AFM-12345",
                "account_last_4": "4567",
                "subject": "Hypotheek bespreking",
                "advisor_name": "J. Smit"
            },
            appointment_offset_minutes=-5,  # Started 5 min ago
            appointment_duration_minutes=30,
            trust_level=3
        )

    def scenario_bank_call_future(self):
        """Level 3: Bank appointment in future"""
        print("\n💡 Scenario: Bank appointment over 1 uur")
        print("   → Intent NU versturen = BLOCKED (outside window)")

        return self.create_fira_with_intent(
            scenario_name="Bank Future Appointment",
            initiator="ing_bank",
            responder="customer_phone",
            roles=["financial_institution", "customer"],
            intent="financial_advice",
            intent_context={
                "institution_name": "ING Bank Nederland",
                "license_number": "AFM-12345",
                "account_last_4": "4567",
                "subject": "Investment portfolio review"
            },
            appointment_offset_minutes=60,  # 1 hour from now
            appointment_duration_minutes=30,
            trust_level=3
        )

    def scenario_lawyer_call(self):
        """Level 4: Lawyer calls client"""
        print("\n💡 Scenario: Advocaat belt cliënt over strafzaak")
        print("   → Pre-authorization: MANDATORY")
        print("   → Client consent: REQUIRED (HID binding)")
        print("   → Time window: STRICT (15 minutes)")
        print("   → Encryption: E2E required")
        print("   → Privilege: Attorney-client")

        return self.create_fira_with_intent(
            scenario_name="Legal Consultation",
            initiator="lawyer_de_vries",
            responder="client_phone",
            roles=["attorney", "client"],
            intent="legal_consultation",
            intent_context={
                "attorney_name": "Mr. J. de Vries",
                "nova_number": "123456",
                "case_reference": "2024-CV-12345",
                "consultation_type": "defense_strategy",
                "privileged": True
            },
            appointment_offset_minutes=-2,  # Started 2 min ago
            appointment_duration_minutes=15,  # STRICT window
            trust_level=4
        )

    def scenario_doctor_call(self):
        """Level 4: Doctor calls patient"""
        print("\n💡 Scenario: Arts belt patiënt over testresultaten")
        print("   → Pre-authorization: MANDATORY")
        print("   → Patient consent: REQUIRED")
        print("   → Encryption: HIPAA/AVG compliant")
        print("   → Medical confidentiality applies")

        return self.create_fira_with_intent(
            scenario_name="Medical Consultation",
            initiator="dr_jansen_cardiology",
            responder="patient_phone",
            roles=["medical_professional", "patient"],
            intent="medical_consultation",
            intent_context={
                "doctor_name": "Dr. A. Jansen",
                "specialty": "Cardiology",
                "big_number": "12345678901",
                "patient_id_last_4": "5678",
                "subject": "Test results discussion"
            },
            appointment_offset_minutes=-3,
            appointment_duration_minutes=20,
            trust_level=4
        )

    def scenario_police_call(self):
        """Level 5: Police calls citizen"""
        print("\n💡 Scenario: Politie belt burger voor verhoor")
        print("   → Pre-authorization: MANDATORY")
        print("   → DigiD authentication: REQUIRED")
        print("   → PKIoverheid cert: REQUIRED")
        print("   → Supervisor approval: REQUIRED")
        print("   → Rights notification: MANDATORY")
        print("   → Recording → Politie + OM + Oversight")

        return self.create_fira_with_intent(
            scenario_name="Police Interview",
            initiator="politie_amsterdam",
            responder="citizen_phone",
            roles=["law_enforcement", "citizen"],
            intent="police_interview",
            intent_context={
                "agency_name": "Politie Nederland",
                "department": "Eenheid Amsterdam",
                "badge_number": "12345",
                "case_ref": "2024-ZV-98765",
                "legal_basis": "Art. 27 Wetboek van Strafvordering",
                "supervisor": "Badge #67890",
                "interview_type": "witness_statement"
            },
            appointment_offset_minutes=-1,
            appointment_duration_minutes=60,
            trust_level=5
        )


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="TBET Live Test - Test against running JIS Router")
    parser.add_argument("--scenario", choices=[
        "personal", "business", "bank", "bank-future",
        "lawyer", "doctor", "police", "all"
    ], help="Run specific scenario")
    parser.add_argument("--list", action="store_true", help="List available scenarios")
    parser.add_argument("--router", default=ROUTER_URL, help=f"Router URL (default: {ROUTER_URL})")
    parser.add_argument("--secret", default=SECRET, help="Router secret")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable scenarios:")
        print("  personal     - Level 1: Verified personal call")
        print("  business     - Level 2: Business call")
        print("  bank         - Level 3: Bank financial advice (active window)")
        print("  bank-future  - Level 3: Bank appointment (future window)")
        print("  lawyer       - Level 4: Legal consultation")
        print("  doctor       - Level 4: Medical consultation")
        print("  police       - Level 5: Police interview")
        print("  all          - Run all scenarios")
        return

    print_banner("🚀 TBET Live Test - Real Router Testing")
    print(f"\nRouter: {args.router}")

    tester = TBETTester(args.router, args.secret)

    scenarios = {
        "personal": tester.scenario_verified_personal,
        "business": tester.scenario_business_call,
        "bank": tester.scenario_bank_call,
        "bank-future": tester.scenario_bank_call_future,
        "lawyer": tester.scenario_lawyer_call,
        "doctor": tester.scenario_doctor_call,
        "police": tester.scenario_police_call
    }

    if args.scenario:
        if args.scenario == "all":
            # Run all scenarios
            for name, func in scenarios.items():
                func()
                print("\n" + "-"*70)
                time.sleep(2)
        else:
            # Run specific scenario
            scenarios[args.scenario]()
    else:
        # Interactive mode
        print("\nAvailable scenarios:")
        for i, name in enumerate(scenarios.keys(), 1):
            print(f"  {i}. {name}")
        print(f"  {len(scenarios)+1}. all")

        choice = input("\nSelect scenario (1-{}): ".format(len(scenarios)+1))
        try:
            choice_idx = int(choice) - 1
            if choice_idx == len(scenarios):
                # All
                for func in scenarios.values():
                    func()
                    print("\n" + "-"*70)
                    time.sleep(2)
            else:
                scenario_name = list(scenarios.keys())[choice_idx]
                scenarios[scenario_name]()
        except (ValueError, IndexError):
            print("Invalid choice")
            sys.exit(1)

    print_banner("✅ Test Complete")
    print(f"\n👀 Check Admin UI: {args.router}/")
    print("\n💡 Tip: Run with --scenario to test specific cases")
    print("   Example: python tbet_live_test.py --scenario bank")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted. Bye! 👋")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
