#!/usr/bin/env python3
"""
TBET-BETTI Demo - Test Hierarchical Trust Level System

Dit script demonstreert:
1. TBET intents versturen voor verschillende trust levels (0-5)
2. Appointment scheduling voor pre-authorization
3. Telefoon notification flow simulatie
4. Intent matching met trust level enforcement

Trust Levels:
- Level 0: Public/Unverified
- Level 1: Verified Personal
- Level 2: Professional Business
- Level 3: Financial/Administrative (pre-auth required)
- Level 4: Legal/Medical (pre-auth + encryption required)
- Level 5: Government (pre-auth + MFA + PKI required)
"""

import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jis_client import JISClient, DIDKey, HIDKey

# Configuratie
ROUTER_URL = "http://localhost:18081"
SECRET = "denDolder_2024!"

# TBET Intent Registry met Trust Levels
TBET_REGISTRY = {
    # Level 0-1: Basic Intents
    "unverified_call_setup": {
        "trust_level": 0,
        "pre_auth_required": False,
        "challenge_required": True,
        "description": "Onbekende beller probeert te bellen"
    },
    "verified_call_setup": {
        "trust_level": 1,
        "pre_auth_required": False,
        "description": "Geverifieerd persoon belt (vriend/familie)"
    },

    # Level 2: Business
    "business_call": {
        "trust_level": 2,
        "pre_auth_required": False,
        "consent_required": True,
        "description": "Zakelijk contact belt"
    },
    "sales_call": {
        "trust_level": 2,
        "pre_auth_required": False,
        "consent_required": True,
        "do_not_call_check": True,
        "description": "Sales call van geregistreerd bedrijf"
    },

    # Level 3: Financial
    "financial_advice": {
        "trust_level": 3,
        "pre_auth_required": True,
        "appointment_required": True,
        "recording_mandatory": True,
        "description": "Bank belt voor financieel advies"
    },
    "account_discussion": {
        "trust_level": 3,
        "pre_auth_required": True,
        "appointment_required": True,
        "mifid_compliance": True,
        "description": "Account bespreking (bank/verzekering)"
    },

    # Level 4: Legal/Medical
    "legal_consultation": {
        "trust_level": 4,
        "pre_auth_required": True,
        "appointment_required": True,
        "encryption_required": True,
        "privilege": "attorney_client",
        "retention_years": 7,
        "description": "Advocaat belt cliënt"
    },
    "medical_consultation": {
        "trust_level": 4,
        "pre_auth_required": True,
        "appointment_required": True,
        "encryption_required": True,
        "hipaa_mode": True,
        "retention_years": 20,
        "description": "Arts belt patiënt"
    },

    # Level 5: Government
    "official_communication": {
        "trust_level": 5,
        "pre_auth_required": True,
        "appointment_required": True,
        "encryption_required": True,
        "mfa_required": True,
        "pkio_cert_required": True,
        "supervisor_approval": True,
        "retention_years": 20,
        "description": "Overheid belt burger"
    },
    "police_interview": {
        "trust_level": 5,
        "pre_auth_required": True,
        "appointment_required": True,
        "rights_notification": True,
        "legal_counsel_offer": True,
        "recording_mandatory": True,
        "oversight_logging": True,
        "description": "Politie verhoor"
    }
}


def print_banner(text: str, style: str = "="):
    """Print mooie banner"""
    print("\n" + style*70)
    print(f"  {text}")
    print(style*70)


def print_phone_display(display_data: Dict[str, Any]):
    """Simuleer hoe de telefoon display eruit ziet"""
    print("\n" + "┌" + "─"*68 + "┐")
    print("│" + " "*68 + "│")

    # Icon + Title
    icon = display_data.get("icon", "📞")
    title = display_data.get("title", "INCOMING CALL")
    print(f"│  {icon}  {title:62s}│")

    # Banner (if any)
    if "banner" in display_data:
        print("│" + " "*68 + "│")
        banner = display_data["banner"]
        print(f"│  {banner:66s}│")

    print("│" + " "*68 + "│")
    print("│" + "─"*68 + "│")

    # Fields
    for field in display_data.get("fields", []):
        label = field["label"]
        value = field["value"]
        print(f"│  {label:20s} {value:46s}│")

    # Notice (if any)
    if "notice" in display_data:
        print("│" + " "*68 + "│")
        print("│" + "─"*68 + "│")
        notice = display_data["notice"]
        for line in notice.split("\n"):
            print(f"│  ⚠️  {line:63s}│")

    print("│" + " "*68 + "│")
    print("│" + "─"*68 + "│")

    # Actions
    actions = display_data.get("actions", ["Accept", "Reject"])
    action_str = "  ".join([f"[{a}]" for a in actions])
    centered = action_str.center(66)
    print(f"│  {centered:66s}│")

    print("│" + " "*68 + "│")
    print("└" + "─"*68 + "┘")


def create_appointment(
    entity_name: str,
    trust_level: int,
    appointment_datetime: datetime,
    duration_minutes: int = 30
) -> Dict[str, Any]:
    """Simuleer appointment creation"""
    appointment = {
        "id": f"appt_{int(time.time())}",
        "entity": entity_name,
        "trust_level": trust_level,
        "appointment_start": appointment_datetime.isoformat(),
        "appointment_end": (appointment_datetime + timedelta(minutes=duration_minutes)).isoformat(),
        "duration_minutes": duration_minutes,
        "status": "scheduled"
    }

    print(f"\n📅 Appointment Created:")
    print(f"   ID: {appointment['id']}")
    print(f"   Entity: {entity_name}")
    print(f"   Trust Level: {trust_level}")
    print(f"   Start: {appointment_datetime.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Duration: {duration_minutes} minutes")

    return appointment


def simulate_phone_notification(
    intent: str,
    fir_a_id: str,
    context: Dict[str, Any],
    appointment: Optional[Dict[str, Any]] = None
):
    """Simuleer hoe een telefoon een incoming intent ontvangt"""

    intent_config = TBET_REGISTRY.get(intent, {})
    trust_level = intent_config.get("trust_level", 0)

    print_banner(f"📱 INCOMING: {intent}", "═")

    # Build display data based on trust level
    display_data = {}

    if trust_level == 0:
        # Unverified
        display_data = {
            "icon": "⚠",
            "title": "UNVERIFIED CALLER",
            "fields": [
                {"label": "Number", "value": context.get("caller_number", "+31612345678")}
            ],
            "actions": ["Screen", "Block", "Report"],
            "notice": "Challenge-response required\nRate limited: 5 calls/hour"
        }

    elif trust_level == 1:
        # Verified Personal
        display_data = {
            "icon": "✓",
            "title": "VERIFIED CALLER",
            "fields": [
                {"label": "Name", "value": context.get("display_name", "Jasper van de Meent")},
                {"label": "Number", "value": context.get("caller_number", "+31612345678")}
            ],
            "actions": ["Accept", "Reject", "Message"]
        }

    elif trust_level == 2:
        # Business
        display_data = {
            "icon": "🏢",
            "title": "VERIFIED BUSINESS",
            "fields": [
                {"label": "Company", "value": context.get("business_name", "ABC Consultancy B.V.")},
                {"label": "KVK", "value": context.get("kvk_number", "12345678")},
                {"label": "Number", "value": context.get("caller_number", "+31201234567")}
            ],
            "actions": ["Accept", "Reject", "Voicemail"]
        }

    elif trust_level == 3:
        # Financial
        display_data = {
            "icon": "🏦",
            "title": "VERIFIED FINANCIAL INSTITUTION",
            "banner": "🔒 Pre-Scheduled Contact",
            "fields": [
                {"label": "Institution", "value": context.get("institution_name", "ING Bank Nederland")},
                {"label": "License", "value": f"AFM: {context.get('license_number', '12345')}"},
                {"label": "Account", "value": f"****{context.get('account_last_4', '4567')}"},
                {"label": "Appointment", "value": context.get("appointment_datetime", "N/A")},
                {"label": "Subject", "value": context.get("subject", "Account bespreking")}
            ],
            "actions": ["Accept", "Reschedule", "Reject"],
            "notice": "This call will be recorded for compliance (MiFID II)"
        }

    elif trust_level == 4:
        # Legal/Medical
        if "attorney" in context or "legal" in intent:
            display_data = {
                "icon": "⚖️",
                "title": "VERIFIED LEGAL PROFESSIONAL",
                "banner": "🔒 Encrypted & Privileged Communication",
                "fields": [
                    {"label": "Attorney", "value": context.get("attorney_name", "Mr. J. de Vries")},
                    {"label": "NOvA Registration", "value": context.get("nova_number", "123456")},
                    {"label": "Case", "value": context.get("case_reference", "2024-CV-12345")},
                    {"label": "Appointment", "value": context.get("appointment_datetime", "N/A")}
                ],
                "actions": ["Accept", "Reschedule"],
                "notice": "Attorney-Client Privilege Applies\nEnd-to-end encrypted\nRecording stored 7 years"
            }
        else:
            display_data = {
                "icon": "🏥",
                "title": "VERIFIED MEDICAL PROFESSIONAL",
                "banner": "🔒 HIPAA/AVG Protected",
                "fields": [
                    {"label": "Doctor", "value": f"Dr. {context.get('doctor_name', 'A. Jansen')}"},
                    {"label": "Specialty", "value": context.get("specialty", "Cardiology")},
                    {"label": "BIG Number", "value": context.get("big_number", "12345678901")},
                    {"label": "Patient ID", "value": f"****{context.get('patient_id_last_4', '5678')}"},
                    {"label": "Appointment", "value": context.get("appointment_datetime", "N/A")}
                ],
                "actions": ["Accept", "Reschedule", "Emergency"],
                "notice": "Medical confidentiality applies\nEnd-to-end encrypted"
            }

    elif trust_level == 5:
        # Government
        display_data = {
            "icon": "🚔",
            "title": "VERIFIED GOVERNMENT AGENCY",
            "banner": "🛡️ PKIoverheid Certified",
            "fields": [
                {"label": "Agency", "value": context.get("agency_name", "Politie Nederland")},
                {"label": "Department", "value": context.get("department", "Eenheid Amsterdam")},
                {"label": "Officer/Official", "value": f"Badge #{context.get('badge_number', '12345')}"},
                {"label": "Case Reference", "value": context.get("case_ref", "2024-ZV-98765")},
                {"label": "Legal Basis", "value": context.get("legal_basis", "Art. 27 WvSv")},
                {"label": "Appointment", "value": context.get("appointment_datetime", "N/A")}
            ],
            "actions": ["Accept", "Request Lawyer", "Reschedule"],
            "notice": "YOUR RIGHTS:\n• Zwijgrecht (right to remain silent)\n• Recht op raadsman (legal counsel)\n• Dit gesprek wordt opgenomen"
        }

    print_phone_display(display_data)

    # Check appointment window
    if appointment:
        now = datetime.now()
        appt_start = datetime.fromisoformat(appointment["appointment_start"])
        appt_end = datetime.fromisoformat(appointment["appointment_end"])

        if appt_start <= now <= appt_end:
            print(f"\n✅ WITHIN APPOINTMENT WINDOW")
            print(f"   Current time: {now.strftime('%H:%M:%S')}")
            print(f"   Window: {appt_start.strftime('%H:%M')} - {appt_end.strftime('%H:%M')}")
            return True
        else:
            print(f"\n❌ OUTSIDE APPOINTMENT WINDOW - CALL BLOCKED")
            print(f"   Current time: {now.strftime('%H:%M:%S')}")
            print(f"   Window: {appt_start.strftime('%H:%M')} - {appt_end.strftime('%H:%M')}")
            if now < appt_start:
                print(f"   Too early by {int((appt_start - now).total_seconds())} seconds")
            else:
                print(f"   Too late by {int((now - appt_end).total_seconds())} seconds")
            return False

    return True


def demo_scenario_1_unverified():
    """Scenario 1: Unverified caller (Level 0)"""
    print_banner("SCENARIO 1: Unverified Caller (Trust Level 0)")

    print("\n📋 Situatie: Random nummer belt je")
    time.sleep(1)

    simulate_phone_notification(
        intent="unverified_call_setup",
        fir_a_id="test-fira-001",
        context={
            "caller_number": "+31612345678"
        }
    )

    print("\n💡 Wat gebeurt er:")
    print("   • Rate limiting: max 5 calls/uur")
    print("   • Challenge-response vereist")
    print("   • Caller ziet: 'Bewijs dat je echt bent'")
    print("   • Gelogd voor audit trail")


def demo_scenario_2_verified_personal():
    """Scenario 2: Verified personal call (Level 1)"""
    print_banner("SCENARIO 2: Verified Personal Call (Trust Level 1)")

    print("\n📋 Situatie: Vriend met geverifieerde DID/HID belt")
    time.sleep(1)

    simulate_phone_notification(
        intent="verified_call_setup",
        fir_a_id="test-fira-002",
        context={
            "display_name": "Jasper van de Meent",
            "caller_number": "+31612345678"
        }
    )

    print("\n💡 Wat gebeurt er:")
    print("   • Direct doorverbinden (geen pre-auth)")
    print("   • Volledige provenance chain")
    print("   • Privacy protected")


def demo_scenario_3_bank_call():
    """Scenario 3: Bank belt klant (Level 3)"""
    print_banner("SCENARIO 3: Bank Belt Klant (Trust Level 3)")

    print("\n📋 Situatie: ING wil je bellen over hypotheek")
    print("\n⏰ STAP 1: Klant plant appointment via app")
    time.sleep(1)

    # Create appointment for tomorrow at 14:30
    appointment_time = datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
    appointment = create_appointment(
        entity_name="ING Bank Nederland",
        trust_level=3,
        appointment_datetime=appointment_time,
        duration_minutes=30
    )

    time.sleep(1)

    print("\n📞 STAP 2: Bank probeert te bellen (binnen appointment window)")
    # Simulate being within the window
    appointment_override = {
        **appointment,
        "appointment_start": (datetime.now() - timedelta(minutes=5)).isoformat(),
        "appointment_end": (datetime.now() + timedelta(minutes=25)).isoformat()
    }

    allowed = simulate_phone_notification(
        intent="financial_advice",
        fir_a_id="test-fira-003",
        context={
            "institution_name": "ING Bank Nederland",
            "license_number": "12345",
            "account_last_4": "4567",
            "appointment_datetime": appointment_time.strftime("%d-%m-%Y %H:%M"),
            "subject": "Hypotheek bespreking"
        },
        appointment=appointment_override
    )

    print("\n💡 Wat gebeurt er:")
    print("   • Pre-authorization check: ✅")
    print("   • Appointment window check: ✅")
    print("   • Account context displayed (masked)")
    print("   • Call is recorded (MiFID II compliance)")
    print("   • Recording encrypted, stored 7 years")


def demo_scenario_4_lawyer_call():
    """Scenario 4: Advocaat belt cliënt (Level 4)"""
    print_banner("SCENARIO 4: Advocaat Belt Cliënt (Trust Level 4)")

    print("\n📋 Situatie: Strafrechtadvocaat wil cliënt spreken")
    print("\n⏰ STAP 1: Cliënt geeft consent + plant strict window")
    time.sleep(1)

    # STRICT 15-minute window
    appointment_time = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    appointment = create_appointment(
        entity_name="Advocatenkantoor De Vries",
        trust_level=4,
        appointment_datetime=appointment_time,
        duration_minutes=15  # STRICT
    )

    print("\n   ⚠️  STRICT window: 15:00 - 15:15 (niet 15:16!)")
    time.sleep(1)

    print("\n📞 STAP 2: Advocaat belt (binnen strict window)")
    # Simulate being within the strict window
    appointment_override = {
        **appointment,
        "appointment_start": (datetime.now() - timedelta(minutes=2)).isoformat(),
        "appointment_end": (datetime.now() + timedelta(minutes=13)).isoformat()
    }

    allowed = simulate_phone_notification(
        intent="legal_consultation",
        fir_a_id="test-fira-004",
        context={
            "attorney_name": "Mr. J. de Vries",
            "nova_number": "123456",
            "case_reference": "2024-CV-12345",
            "appointment_datetime": appointment_time.strftime("%d-%m-%Y %H:%M")
        },
        appointment=appointment_override
    )

    print("\n💡 Wat gebeurt er:")
    print("   • Pre-authorization: ✅ (client consent verplicht)")
    print("   • STRICT time window: ✅ (geen seconde te laat!)")
    print("   • NOvA registratie check: ✅")
    print("   • HID binding match: ✅")
    print("   • E2E encryption: ✅")
    print("   • Biometric re-auth required")
    print("   • Attorney-client privilege marker")
    print("   • Recording encrypted, stored 7 years")


def demo_scenario_5_government_call():
    """Scenario 5: Politie belt verdachte (Level 5)"""
    print_banner("SCENARIO 5: Politie Belt Verdachte (Trust Level 5)")

    print("\n📋 Situatie: Politie wil verdachte horen")
    print("\n📬 STAP 1: Burger ontvangt AANGETEKENDE BRIEF")
    print("   'U wordt verzocht een afspraak te maken via DigiD'")
    time.sleep(1)

    print("\n⏰ STAP 2: Burger plant via DigiD (MFA)")
    appointment_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    appointment = create_appointment(
        entity_name="Politie Nederland",
        trust_level=5,
        appointment_datetime=appointment_time,
        duration_minutes=60
    )

    time.sleep(1)

    print("\n📞 STAP 3: Politie belt (exact op tijd!)")
    # Simulate exact appointment time
    appointment_override = {
        **appointment,
        "appointment_start": (datetime.now() - timedelta(seconds=30)).isoformat(),
        "appointment_end": (datetime.now() + timedelta(minutes=59, seconds=30)).isoformat()
    }

    allowed = simulate_phone_notification(
        intent="police_interview",
        fir_a_id="test-fira-005",
        context={
            "agency_name": "Politie Nederland",
            "department": "Eenheid Amsterdam",
            "badge_number": "12345",
            "case_ref": "2024-ZV-98765",
            "legal_basis": "Art. 27 WvSv",
            "appointment_datetime": appointment_time.strftime("%d-%m-%Y %H:%M")
        },
        appointment=appointment_override
    )

    print("\n💡 Wat gebeurt er:")
    print("   • PKIoverheid cert check: ✅")
    print("   • Legal basis documented: ✅")
    print("   • Supervisor approval: ✅")
    print("   • Appointment exact time: ✅")
    print("   • Burger MFA via DigiD: required")
    print("   • Rights notification shown: verplicht")
    print("   • Recording → Politie + OM + Oversight")
    print("   • Stored 20 years with audit trail")


def main():
    """Main demo"""
    print_banner("🔒 TBET-BETTI Trust Level Demo", "═")

    print("""
Dit script demonstreert hoe het hiërarchische trust level systeem werkt:

1. Hoe TBET intents verschillende trust levels activeren
2. Hoe appointments pre-authorization mogelijk maken
3. Hoe de telefoon de caller context ziet
4. Hoe time windows enforced worden

Je ziet 5 scenario's van Level 0 (spam) tot Level 5 (government).
    """)

    input("\nDruk op ENTER om te starten...")

    # Run scenarios
    demo_scenario_1_unverified()
    input("\n\nDruk op ENTER voor volgende scenario...")

    demo_scenario_2_verified_personal()
    input("\n\nDruk op ENTER voor volgende scenario...")

    demo_scenario_3_bank_call()
    input("\n\nDruk op ENTER voor volgende scenario...")

    demo_scenario_4_lawyer_call()
    input("\n\nDruk op ENTER voor volgende scenario...")

    demo_scenario_5_government_call()

    # Summary
    print_banner("✅ Demo Complete!", "═")

    print("""
Je hebt nu gezien hoe:

✓ Trust levels bepalen welke pre-authorization vereist is
✓ Appointments time-windowed access mogelijk maken
✓ De telefoon context-aware caller info toont
✓ Hoe hoger het trust level, hoe strenger de enforcement

VOLGENDE STAPPEN:
1. Run ./tbet_live_demo.py om ECHTE intents naar router te sturen
2. Bekijk de Admin UI om de FIR/A relationships te zien
3. Test appointment window enforcement

Ready to test tegen je router? 🚀
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Bye! 👋")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
