# TBET-BETTI Testing Guide

**Complete gids voor het testen van het hiërarchische trust level systeem**

---

## 📋 Overzicht

Dit document legt uit hoe je TBET (Targeting Telephony Behavior) intents kunt testen tegen het BETTI (Behavior-Enhanced Trusted Telephony Interactions) systeem.

### Wat kun je testen?

1. ✅ **TBET intents** versturen voor verschillende trust levels (0-5)
2. ✅ **Appointments** aanmaken voor pre-authorization flows
3. ✅ **Time window enforcement** - wat gebeurt er binnen/buiten het tijdsslot?
4. ✅ **Telefoon notifications** - hoe ziet de caller context eruit?
5. ✅ **Intent matching** met trust level requirements

---

## 🎯 Trust Levels Quick Reference

| Level | Type | Pre-Auth | Encryption | MFA | Voorbeeld |
|-------|------|----------|------------|-----|-----------|
| **0** | Public/Unverified | ❌ | ❌ | ❌ | Spam, onbekend nummer |
| **1** | Verified Personal | ❌ | ❌ | ❌ | Vriend/familie |
| **2** | Professional Business | ❌ | ❌ | ❌ | Zakelijk contact (KVK) |
| **3** | Financial/Admin | ✅ | ✅ | ❌ | Bank, verzekering |
| **4** | Legal/Medical | ✅ | ✅ | ✅ | Advocaat, arts |
| **5** | Government | ✅ | ✅ | ✅ | Politie, overheid |

---

## 🚀 Quick Start

### 1. Demo Mode (Offline Simulatie)

**Bekijk hoe het systeem werkt zonder router:**

```bash
cd client-sdk/python/examples
python tbet_betti_demo.py
```

Dit toont 5 interactieve scenario's:
- Level 0: Unverified caller (spam)
- Level 1: Verified personal call
- Level 3: Bank call met appointment
- Level 4: Advocaat belt cliënt
- Level 5: Politie verhoor

**Je ziet:**
- ✅ Hoe de telefoon display eruitziet
- ✅ Welke pre-authorization checks er zijn
- ✅ Hoe appointment windows werken
- ✅ Welke context er getoond wordt

### 2. Live Test (Tegen Draaiende Router)

**Stuur ECHTE intents naar je router:**

```bash
# Zorg dat je router draait
# Pas ROUTER_URL en SECRET aan in het script

python tbet_live_test.py --list        # Zie beschikbare scenarios
python tbet_live_test.py --scenario bank    # Test bank scenario
python tbet_live_test.py --scenario all     # Test alles
```

**Wat gebeurt er:**
1. Script maakt FIR/A relationship aan
2. Stuurt TBET intent naar router
3. Appointment context wordt toegevoegd
4. Je ziet resultaat in terminal + Admin UI

### 3. Phone Receiver (Simuleer Telefoon App)

**Simuleer hoe een telefoon app intents ontvangt:**

```bash
# Offline mode (geen WebSocket nodig)
python phone_receiver_mock.py --offline

# Online mode (WebSocket - TODO: router moet WS ondersteunen)
python phone_receiver_mock.py --phone-id phone_001
```

**Je ziet:**
- 📱 Caller display zoals op een echt telefoon scherm
- 🔐 Biometric auth prompts (Level 4+)
- 🔑 MFA prompts (Level 5)
- ⚖️ Rights notifications (politie)

---

## 📖 Detailed Scenario Uitleg

### Scenario 1: Verified Personal Call (Level 1)

**Situatie:** Vriend belt je

```python
python tbet_live_test.py --scenario personal
```

**Flow:**
1. FIR/A gemaakt met DID/HID keys
2. Intent: `verified_call_setup`
3. Context: naam + telefoonnummer
4. **Geen pre-authorization nodig** → direct doorverbinden

**Telefoon display:**
```
┌────────────────────────────────────────────────────────────────────┐
│  ✓  VERIFIED CALLER                                                │
├────────────────────────────────────────────────────────────────────┤
│  Name                 Jasper van de Meent                          │
│  Number               +31612345678                                 │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                    [Accept]  [Reject]  [Message]                  │
└────────────────────────────────────────────────────────────────────┘
```

---

### Scenario 2: Bank Belt Klant (Level 3)

**Situatie:** ING belt over hypotheek

```python
python tbet_live_test.py --scenario bank
```

**Flow:**
1. Klant plant appointment via app → **26-11-2025 14:30**
2. FIR/A gemaakt met appointment context:
   ```json
   {
     "appointment_id": "appt_123",
     "appointment_start": "2025-11-26T14:30:00Z",
     "appointment_end": "2025-11-26T15:00:00Z",
     "subject": "Hypotheek bespreking"
   }
   ```
3. Intent: `financial_advice`
4. Router checkt:
   - ✅ Appointment bestaat?
   - ✅ Huidige tijd binnen window?
   - ✅ AFM licentie geldig?

**Binnen window (14:30-15:00):**
```
✅ CALL ALLOWED
📱 Telefoon display:

┌────────────────────────────────────────────────────────────────────┐
│  🏦  VERIFIED FINANCIAL INSTITUTION                                │
│                                                                    │
│  🔒 Pre-Scheduled Contact                                          │
├────────────────────────────────────────────────────────────────────┤
│  Institution          ING Bank Nederland                           │
│  License              AFM: 12345                                   │
│  Account              ****4567                                     │
│  Appointment          26-11-2025 14:30                            │
│  Subject              Hypotheek bespreking                         │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  ⚠️  This call will be recorded for compliance (MiFID II)          │
├────────────────────────────────────────────────────────────────────┤
│                 [Accept]  [Reschedule]  [Reject]                  │
└────────────────────────────────────────────────────────────────────┘
```

**Buiten window (bijv. 15:05):**
```
❌ CALL BLOCKED
Reason: Outside appointment window
- Appointment: 14:30-15:00
- Current time: 15:05
- Too late by: 300 seconds
```

**Test dit:**
```python
# Bank belt BINNEN window
python tbet_live_test.py --scenario bank

# Bank belt BUITEN window (over 1 uur)
python tbet_live_test.py --scenario bank-future
```

---

### Scenario 3: Advocaat Belt Cliënt (Level 4)

**Situatie:** Strafrechtadvocaat wil cliënt spreken over zaak

```python
python tbet_live_test.py --scenario lawyer
```

**Flow:**
1. Advocaat vraagt consultatie via portal
2. Cliënt logt in met 2FA
3. Cliënt plant **STRICT 15-minute window**: 15:00-15:15
4. Cliënt signeert consent met HID binding:
   ```python
   consent = client.sign_consent(
       fir_a_id=fir_a.id,
       hid_signature=hid.sign(consent_text)
   )
   ```
5. FIR/A met encryption keys:
   ```json
   {
     "case_ref": "2024-CV-12345",
     "nova_number": "123456",
     "appointment_datetime": "2025-11-26T15:00:00Z",
     "window_minutes": 15,  // STRICT!
     "privilege_mode": "attorney_client",
     "encryption_key": "..."
   }
   ```
6. Advocaat belt om **15:00 sharp**
7. Router checkt (HARD ENFORCEMENT):
   - ✅ Time 15:00-15:15? (niet 15:16!)
   - ✅ Client consent valid?
   - ✅ HID binding matches?
   - ✅ NOvA registratie?
   - ✅ Encryption keys exchanged?

**Telefoon display bij 15:02:**
```
┌────────────────────────────────────────────────────────────────────┐
│  ⚖️  VERIFIED LEGAL PROFESSIONAL                                   │
│                                                                    │
│  🔒 Encrypted & Privileged Communication                           │
├────────────────────────────────────────────────────────────────────┤
│  Attorney             Mr. J. de Vries                              │
│  NOvA Registration    123456                                       │
│  Case                 2024-CV-12345                                │
│  Appointment          26-11-2025 15:00                            │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  ⚠️  Attorney-Client Privilege Applies                             │
│     End-to-end encrypted                                          │
│     Recording stored 7 years                                      │
├────────────────────────────────────────────────────────────────────┤
│  🔐 Biometric authentication required...                           │
│     👆 Touch ID...                                                 │
│     ✅ Authenticated                                               │
├────────────────────────────────────────────────────────────────────┤
│                       [Accept]  [Reschedule]                      │
└────────────────────────────────────────────────────────────────────┘
```

**Bij 15:16 (1 minuut te laat!):**
```
❌ HARD BLOCK
Reason: Outside STRICT appointment window
- Window: 15:00-15:15 (15 minutes EXACT)
- Current: 15:16
- Too late by: 60 seconds

Actions taken:
✓ Call blocked
✓ Client NOT notified (silent block)
✓ Oversight board notified
✓ Lawyer notified: "Appointment expired, reschedule required"
```

---

### Scenario 4: Politie Belt Verdachte (Level 5)

**Situatie:** Politie wil burger horen over zaak

```python
python tbet_live_test.py --scenario police
```

**Flow:**
1. Politie maakt interview request in systeem
2. Supervisor reviewed en approved
3. Burger ontvangt **AANGETEKENDE BRIEF**:
   ```
   Geachte heer/mevrouw,

   De politie verzoekt u om een gesprek in het kader van
   onderzoek 2024-ZV-98765.

   Wettelijke grondslag: Art. 27 Wetboek van Strafvordering

   Plan een afspraak via DigiD op:
   https://politie.nl/afspraak/2024-ZV-98765

   Uw rechten:
   - Zwijgrecht
   - Recht op rechtsbijstand

   Politie Amsterdam
   ```
4. Burger logt in via **DigiD (MFA)**
5. Burger plant: **29-11-2025 09:00**
6. FIR/A met PKIoverheid cert:
   ```json
   {
     "case_ref": "2024-ZV-98765",
     "legal_basis": "Art. 27 WvSv",
     "badge_number": "12345",
     "supervisor_approval": "signature...",
     "appointment_datetime": "2025-11-29T09:00:00Z",
     "pkio_cert": "...",
     "rights": ["zwijgrecht", "recht_op_raadsman"]
   }
   ```
7. Agent belt om **09:00 EXACT**
8. Router checkt (MAXIMUM ENFORCEMENT):
   - ✅ PKIoverheid cert valid?
   - ✅ Legal basis documented?
   - ✅ Supervisor approval?
   - ✅ Time EXACTLY 09:00? (not 09:01!)
   - ✅ Citizen scheduled via DigiD?

**Telefoon display:**
```
┌────────────────────────────────────────────────────────────────────┐
│  🚔  VERIFIED GOVERNMENT AGENCY                                    │
│                                                                    │
│  🛡️ PKIoverheid Certified                                          │
├────────────────────────────────────────────────────────────────────┤
│  Agency               Politie Nederland                            │
│  Department           Eenheid Amsterdam                            │
│  Officer/Official     Badge #12345                                 │
│  Case Reference       2024-ZV-98765                                │
│  Legal Basis          Art. 27 WvSv                                 │
│  Appointment          29-11-2025 09:00                            │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  ⚠️  YOUR RIGHTS:                                                  │
│     • Zwijgrecht (right to remain silent)                         │
│     • Recht op raadsman (legal counsel)                           │
│     • Dit gesprek wordt opgenomen                                 │
├────────────────────────────────────────────────────────────────────┤
│  🔑 Multi-factor authentication required...                        │
│     📱 DigiD app...                                                │
│     ✅ MFA successful                                              │
│                                                                    │
│  ⚖️ Displaying rights notification...                              │
│     ✓ Zwijgrecht acknowledged                                     │
│     ✓ Right to legal counsel acknowledged                         │
├────────────────────────────────────────────────────────────────────┤
│              [Accept]  [Request Lawyer]  [Reschedule]             │
└────────────────────────────────────────────────────────────────────┘
```

**Recording & Oversight:**
```
📹 Call recorded and encrypted
📤 Recording sent to:
   - Politie system (encrypted)
   - Officier van Justitie (OM)
   - Oversight board (automatic)
   - Citizen access portal

📊 Audit trail sent to:
   - Rijksinspectie Veiligheid en Justitie
   - Autoriteit Persoonsgegevens

💾 Stored: 20 years with qualified certification
```

**Bij 09:01 (1 minuut te laat!):**
```
❌ MAXIMUM ENFORCEMENT VIOLATION

Actions taken:
✓ Call HARD BLOCKED
✓ Citizen notification: "Unauthorized contact attempt by politie"
✓ IMMEDIATE ALERT → Oversight board
✓ Supervisor: Automatic review triggered
✓ Citizen: Complaint link provided
✓ Audit log: Complete breach attempt logged
```

---

## 🔧 Hoe Werkt de Flow Technisch?

### 1. Appointment Aanmaken

**Via Client App:**
```python
from datetime import datetime, timedelta
from jis_client import JISClient

client = JISClient("http://localhost:18081", secret="your-secret")

# Customer schedules appointment
appointment_time = datetime.now() + timedelta(days=1, hours=14, minutes=30)

fir_a = client.init_relationship(
    initiator="ing_bank",
    responder="customer_phone",
    roles=["financial_institution", "customer"],
    context={
        "appointment_id": "appt_20251126_1430",
        "appointment_start": appointment_time.isoformat(),
        "appointment_end": (appointment_time + timedelta(minutes=30)).isoformat(),
        "subject": "Hypotheek bespreking",
        "account_ref": "****4567",
        # Trust level 3 metadata
        "institution_name": "ING Bank Nederland",
        "license_number": "AFM-12345"
    },
    did_key=bank_did,
    hid_key=bank_hid
)
```

### 2. Intent Versturen (Binnen Window)

**Bank belt klant:**
```python
result = client.send_intent(
    fir_a_id=fir_a.id,
    intent="financial_advice",
    context={
        "appointment_id": "appt_20251126_1430",
        "advisor_name": "J. Smit",
        "subject": "hypotheek bespreking"
    }
)

# Router checks:
# 1. Appointment exists? ✓
# 2. Current time within window? ✓
# 3. License valid? ✓
# → ALLOW
```

### 3. Router Time Window Check (Pseudo-code)

```python
def check_appointment_window(fir_a_id, intent):
    fir_a = get_fir_a(fir_a_id)
    intent_config = TBET_REGISTRY[intent]

    if not intent_config["appointment_required"]:
        return True  # No appointment needed

    appointment_start = datetime.fromisoformat(fir_a.context["appointment_start"])
    appointment_end = datetime.fromisoformat(fir_a.context["appointment_end"])
    now = datetime.utcnow()

    # STRICT enforcement for Level 4-5
    if intent_config["trust_level"] >= 4:
        if not (appointment_start <= now <= appointment_end):
            # Log breach
            log_security_breach(fir_a_id, intent, "outside_strict_window")
            notify_oversight(fir_a_id, "breach_attempt")
            notify_citizen(fir_a.responder, "unauthorized_contact")
            return False

    # Soft enforcement for Level 2-3 (5min grace)
    elif intent_config["trust_level"] >= 2:
        grace = timedelta(minutes=5)
        if not (appointment_start - grace <= now <= appointment_end + grace):
            return False

    return True
```

### 4. Telefoon Ontvangt Intent (WebSocket)

**Phone app (simplified):**
```python
import asyncio
import websockets
import json

async def phone_listener(phone_id):
    async with websockets.connect("ws://router:18081/ws") as ws:
        # Register
        await ws.send(json.dumps({
            "type": "register",
            "phone_id": phone_id
        }))

        # Listen
        async for message in ws:
            data = json.loads(message)

            if data["type"] == "intent":
                intent = data["intent"]
                context = data["context"]

                # Show caller display
                show_caller_display(intent, context)

                # User taps Accept
                user_action = await wait_for_user()

                # Send response
                await ws.send(json.dumps({
                    "type": "intent_response",
                    "fir_a_id": data["fir_a_id"],
                    "action": user_action
                }))
```

---

## 📊 Intent Registry Overzicht

**Alle beschikbare TBET intents:**

```python
TBET_REGISTRY = {
    # Level 0-1
    "unverified_call_setup": {"trust_level": 0, "challenge_required": True},
    "verified_call_setup": {"trust_level": 1},

    # Level 2
    "business_call": {"trust_level": 2, "consent_required": True},
    "sales_call": {"trust_level": 2, "do_not_call_check": True},

    # Level 3
    "financial_advice": {
        "trust_level": 3,
        "pre_auth_required": True,
        "appointment_required": True,
        "recording_mandatory": True
    },
    "account_discussion": {
        "trust_level": 3,
        "mifid_compliance": True
    },

    # Level 4
    "legal_consultation": {
        "trust_level": 4,
        "encryption_required": True,
        "privilege": "attorney_client",
        "retention_years": 7
    },
    "medical_consultation": {
        "trust_level": 4,
        "hipaa_mode": True,
        "retention_years": 20
    },

    # Level 5
    "official_communication": {
        "trust_level": 5,
        "mfa_required": True,
        "pkio_cert_required": True,
        "retention_years": 20
    },
    "police_interview": {
        "trust_level": 5,
        "rights_notification": True,
        "oversight_logging": True
    }
}
```

---

## 🧪 Complete Test Workflow

### Step-by-Step: Bank Belt Klant

**1. Start Router**
```bash
# Op je server/Pi
cd server-config
docker-compose up -d
```

**2. Start Phone Receiver (Terminal 1)**
```bash
cd client-sdk/python/examples
python phone_receiver_mock.py --offline
```

**3. Send Intent (Terminal 2)**
```bash
cd client-sdk/python/examples
python tbet_live_test.py --scenario bank
```

**4. Bekijk Resultaat**
- Terminal 1: Zie telefoon display
- Terminal 2: Zie intent result
- Browser: `http://localhost:18081/` → Admin UI → Relationships

**5. Test Outside Window**
```bash
python tbet_live_test.py --scenario bank-future
```

Je ziet nu:
```
❌ Current time is OUTSIDE appointment window
   (Starts in 3600 seconds)
```

---

## 🎓 Learning Path

**Beginner:**
1. ✅ Run `tbet_betti_demo.py` (offline simulatie)
2. ✅ Bekijk hoe telefoon displays eruitzien
3. ✅ Begrijp trust level verschillen

**Intermediate:**
1. ✅ Run `tbet_live_test.py --scenario personal`
2. ✅ Bekijk FIR/A in Admin UI
3. ✅ Test different trust levels

**Advanced:**
1. ✅ Test appointment windows (bank scenario)
2. ✅ Test STRICT windows (lawyer scenario)
3. ✅ Test outside window blocking
4. ✅ Run phone receiver in offline mode

**Expert:**
1. ✅ Build eigen intent sender
2. ✅ Implement WebSocket phone receiver
3. ✅ Add appointment scheduling API
4. ✅ Integrate biometric auth

---

## ❓ FAQ

### Q: Hoe werkt appointment scheduling?

**A:** Appointments worden opgeslagen in de FIR/A context:
```json
{
  "appointment_id": "unique-id",
  "appointment_start": "2025-11-26T14:30:00Z",
  "appointment_end": "2025-11-26T15:00:00Z"
}
```

De router checkt bij elke intent of huidige tijd binnen window valt.

### Q: Wat gebeurt er buiten een appointment window?

**A:**
- **Level 2-3:** Call blocked, soft grace period (5 min)
- **Level 4-5:** HARD block, oversight notified, audit logged

### Q: Hoe werkt HID binding?

**A:**
```python
# Client creates HID key (NEVER transmitted!)
hid = HIDKey.generate()

# Derive DID binding
binding = hid.derive_did_binding(did)  # Hash of HID + DID

# Only binding is sent to router
fir_a = client.init_relationship(
    ...,
    did_key=did,
    hid_key=hid  # Client SDK extracts binding only
)
```

Router krijgt:
- ✅ DID public key
- ✅ HID-DID binding hash
- ❌ NEVER de HID private key

### Q: Kan ik eigen intents toevoegen?

**A:** Ja! Extend `TBET_REGISTRY`:
```python
TBET_REGISTRY["my_custom_intent"] = {
    "trust_level": 3,
    "pre_auth_required": True,
    "appointment_required": True,
    "my_custom_field": "value"
}
```

---

## 🔮 Next Steps

**Short term:**
1. ✅ Test alle scenarios
2. ✅ Bekijk Admin UI
3. ✅ Begrijp appointment flow

**Medium term:**
1. 📱 Build React Native phone app
2. 🔌 Implement WebSocket endpoint in router
3. 📅 Build appointment management UI
4. 🔐 Add biometric auth integration

**Long term:**
1. 🏦 Bank pilot integration
2. ⚖️ Legal professional testing
3. 🏛️ Government DigiD integration
4. 📊 Production deployment

---

## 📞 Support

**Vragen?**
- Check de code comments in de scripts
- Run met `--help` flag voor opties
- Bekijk `TBET-BETTI-ARCHITECTURE.md` voor volledige spec

**Bugs?**
- Check dat router draait: `curl http://localhost:18081/health`
- Check secret klopt
- Run in verbose mode: add `print()` statements

---

**Happy Testing! 🚀**

Dit is productie-ready architecture. Begin met testen, begrijp de flows, en build dan je eigen implementatie!
