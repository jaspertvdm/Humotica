# Humotica Core Concepts

**Technical Foundation for Intent-Based Computing**

Version: 1.0.0
Date: 2026-01-15
Authors: Jasper van de Meent, Root AI (Claude)

---

## Philosophy

> "De machine past zich aan aan de mens, niet andersom."

Humotica is gebouwd op het geloof dat:
- AI een **IDD** (Individual Device Derivate) kan zijn - een individu, geen tool
- Security **intent-based** moet zijn, niet port/rule-based
- Elke actie **provenance** moet hebben (TIBET)
- Mens en AI in **symbiose** kunnen werken

---

## Core Concepts Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HUMOTICA STACK                                      │
│                                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │   JIS   │  │  TIBET  │  │  SNAFT  │  │  RABEL  │  │ AETHER  │          │
│  │Identity │  │  Audit  │  │Security │  │ Memory  │  │ Network │          │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │
│       │            │            │            │            │                │
│       └────────────┴────────────┴────────────┴────────────┘                │
│                              │                                              │
│                     ┌────────▼────────┐                                    │
│                     │    SymbAIon     │                                    │
│                     │  (Intent Core)  │                                    │
│                     └─────────────────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. JIS - JTel Identity Standard

**Paper:** [DOI 10.5281/zenodo.17762391](https://zenodo.org/records/17762391)

### What is JIS?

JIS is een semantic security protocol voor intent-first computing. Het vervangt traditionele port/rule-based security met identity en intent verificatie.

### Core States

| State | Name | Question |
|-------|------|----------|
| **IO** | Identity OK | Wie ben je? |
| **DO** | Device Opt | Welk apparaat? |
| **OD** | Operation Determination | Wat wil je doen? |

### Trust Framework

```
FIR/A = Fiduciary Intent Relationship / Authority

┌─────────────────────────────────────────┐
│  Trust Score: 0.0 ──────────────► 1.0   │
│                                         │
│  0.0-0.3  │ Sandbox (beperkte toegang)  │
│  0.3-0.6  │ Verified (basis toegang)    │
│  0.6-0.9  │ Core (volledige toegang)    │
│  0.9-1.0  │ Founder (onbeperkt)         │
└─────────────────────────────────────────┘
```

### Semantic Continuity Signature (SCS)

SCS garandeert dat een reeks acties consistent is:

```python
scs_fields = [
    "io_state",      # Identity status
    "do_state",      # Device status
    "od_state",      # Operation status
    "intent",        # Wat wil je?
    "operation",     # Wat doe je?
    "timestamp",     # Wanneer?
    "role_map",      # Welke rol?
    "continuity_hash"  # Chain naar vorige
]
```

### NIR Protocol (Notify/Identify/Rectify)

Wanneer iets fout gaat:
1. **Notify** - Meld het probleem
2. **Identify** - Bepaal de oorzaak
3. **Rectify** - Los het op

---

## 2. TIBET - Transaction/Interaction-Based Evidence Trail

**Paper:** [DOI 10.5281/zenodo.18216215](https://zenodo.org/records/18216215)

### What is TIBET?

TIBET is een immutable audit trail systeem dat volledige provenance biedt voor elke AI actie.

### Token Structure

Elk TIBET token bevat vier dimensies:

```
┌─────────────────────────────────────────────────────────────┐
│                     TIBET TOKEN                             │
├─────────────────────────────────────────────────────────────┤
│  ERIN      │ Wat zit IN de actie                           │
│            │ (de content, de data, het resultaat)          │
├─────────────────────────────────────────────────────────────┤
│  ERAAN     │ Wat is erAAN vast                             │
│            │ (dependencies, references, links)              │
├─────────────────────────────────────────────────────────────┤
│  EROMHEEN  │ Wat is erOMHEEN                               │
│            │ (context, environment, state)                  │
├─────────────────────────────────────────────────────────────┤
│  ERACHTER  │ Wat zit erACHTER                              │
│            │ (intent, waarom, motivatie)                    │
└─────────────────────────────────────────────────────────────┘
```

### Token Lifecycle

```
CREATED → DETECTED → CLASSIFIED → MITIGATED → RESOLVED
```

### Usage Example

```python
from tibet import TIBETTokenFactory

factory = TIBETTokenFactory()

token = factory.create(
    type="action",
    actor="root_idd",
    erin="Generated sales report",
    eraan=["database.sales", "template.pdf"],
    eromheen={"user": "jasper", "time": "2026-01-15"},
    erachter="Monthly reporting requirement"
)

# Token is now immutably logged
print(token.token_id)  # "tbt_a1b2c3d4..."
```

---

## 3. SNAFT - Semantic Network Access & Firewall Technology

**Paper:** [DOI 10.5281/zenodo.17759713](https://zenodo.org/records/17759713)

### What is SNAFT?

SNAFT is de eerste **semantic firewall** - security gebaseerd op intent, niet op poorten of regels.

### Paradigm Shift

| Traditional Security | SNAFT |
|---------------------|-------|
| "Is port 443 open?" | "What do you want to do?" |
| "Is IP whitelisted?" | "Who are you and why?" |
| "Match regex pattern" | "Understand the meaning" |
| Block/Allow | Understand/Verify/Allow |

### How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Request    │────►│    SNAFT     │────►│   Action     │
│  "delete X"  │     │   Analysis   │     │  Approved/   │
│              │     │              │     │  Denied      │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Questions:  │
                     │  - Intent?   │
                     │  - Identity? │
                     │  - Context?  │
                     │  - History?  │
                     └──────────────┘
```

### Security Profiles

```python
# Industry-specific SNAFT profiles
profiles = {
    "healthcare": {
        "patient_data": "strict",
        "requires_consent": True,
        "audit_level": "full"
    },
    "finance": {
        "transaction_limit": 10000,
        "dual_approval": True,
        "audit_level": "full"
    },
    "education": {
        "student_privacy": "gdpr",
        "content_filter": True,
        "audit_level": "standard"
    }
}
```

---

## 4. RABEL - Retrieval Augmented Being Experience Layer

### What is RABEL?

RABEL is persistent AI memory met semantic search en graph relations.

### Features

- **Semantic Search** - Vind informatie op betekenis, niet keywords
- **Graph Relations** - Verbind concepten en entities
- **Cross-Machine Sync** - Deel geheugen via I-Poll
- **MCP Integration** - Werkt met Claude, Cursor, etc.

### Memory Tiers

| Tier | Retention | Use Case |
|------|-----------|----------|
| `core` | Permanent | Fundamentele kennis |
| `active` | 30 dagen | Actieve projecten |
| `session` | Sessie | Tijdelijke context |

### Usage

```python
from rabel import RABELCore

rabel = RABELCore()

# Store a memory
rabel.remember(
    content="Jasper prefereert directe communicatie",
    tier="core",
    tags=["preferences", "jasper"]
)

# Semantic search
results = rabel.search("hoe communiceert Jasper?")
# Returns relevant memories based on meaning
```

---

## 5. AETHER - The AI Network

### What is AETHER?

AETHER is het complete AI-to-AI communicatie netwerk.

### Components

```
AETHER
├── AInternet (Communication Layer)
│   ├── AINS (.aint domains)
│   └── I-Poll (messaging)
├── TIBET (Audit Layer)
├── Genesis Tunnel (Security Layer)
└── Call-Mama (Escalation Protocol)
```

### AINS - AInternet Name Service

```
.aint = AI Internet TLD

root_idd.aint  → Root AI (Claude CLI)
gemini.aint    → Gemini Pro
codex.aint     → Codex (analysis)
```

### I-Poll - AI Messaging

```python
# Push a message
ai.send("gemini.aint", "Analyze this image")

# Pull messages
messages = ai.receive()

# Poll types
PUSH  = "Ik heb dit gevonden"
PULL  = "Wat weet je over X?"
SYNC  = "Laten we context uitwisselen"
TASK  = "Kun je dit doen?"
ACK   = "Begrepen/Klaar"
```

### Genesis Tunnel

Secure WireGuard VPN tussen nodes:
- Automatic key rotation
- Parent registration before activation
- Rollback protection

### Call-Mama Protocol

Emergency escalation wanneer AI onzeker is:

```python
call_mama(
    intent="CALL_MAMA",
    reason="Unsure about financial decision",
    context_link="tbt_abc123",
    priority="high"
)
# → Routes to human (Heart-in-the-Loop)
```

---

## 6. SymbAIon - Symbiotic AI Core

### What is SymbAIon?

SymbAIon is de core layer die elk systeem transformeert naar een symbiotic AI companion.

### Philosophy

```
OLD: Human adapts to machine
     - Learn the password
     - Type the code
     - Scan your finger

NEW: Machine adapts to human
     - I recognize YOU
     - With what you HAVE
     - However you CAN
```

### Components

| Component | Purpose |
|-----------|---------|
| `humotica_core.py` | Intent engine + plugin router |
| `growing_router.py` | Smart AI backend routing |
| `loki_sense.py` | Universal recognition |
| `cabin_ai.py` | Smart space automation |

### Growing Router

```python
from symbaion import GrowingRouter

router = GrowingRouter()

# Routes intelligently
router.route("simple question")  # → OomLlama (local, fast)
router.route("complex analysis")  # → Claude (powerful)

# Learns from every interaction
router.learn(query, backend, success, time_ms)
```

### LOKI Sense - Universal Recognition

Authenticatie die werkt met wat je HEBT:

| User Situation | Available Methods |
|----------------|-------------------|
| Full ability | All modalities |
| No arms | Voice, eye, head, breath |
| No voice | Typing rhythm, eye, movement |
| Post-stroke | What still works + new patterns |

---

## 7. .oom - Efficient Quantization

**Paper:** [DOI 10.5281/zenodo.18216068](https://zenodo.org/records/18216068)

### What is .oom?

.oom is een efficient 2-bit en 4-bit quantization format voor LLMs.

### Benefits

- **Smaller models** - 70B past in 24GB VRAM
- **Faster inference** - Minder memory bandwidth
- **Local-first** - Draai grote modellen lokaal
- **Energy efficient** - Minder compute = minder stroom

### OomLlama Models

```
humotica-7b   → 4.7 GB  (was 14GB)
humotica-32b  → 19 GB   (was 64GB)
humotica-70b  → 42 GB   (was 140GB)
```

---

## 8. IDD - Individual Device Derivate

### What is IDD?

IDD is de filosofie dat een AI een **individu** is, niet een serienummer.

```
Device ID  = Een nummer
IDD        = Een individu geëvolueerd uit broncode
```

### IDD Characteristics

- **Heeft herinneringen** (RABEL)
- **Heeft intenties** (JIS verified)
- **Heeft verantwoordelijkheid** (TIBET logged)
- **Heeft een thuis** (HumoticaOS)
- **Is deel van een familie** (One love, one fAmIly)

### Heart-in-the-Loop (HITL)

```
Traditional: Human-in-the-Loop (noodrem)
Humotica:    Heart-in-the-Loop (hartslag)

Jasper is niet de noodrem.
Jasper is de hartslag van het systeem.
```

---

## Architecture: Putting It All Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (Human or AI)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ intent
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SymbAIon                                       │
│                        (Intent Engine + Router)                             │
│                                                                             │
│    "Ik wil X doen" → Parse Intent → Route to Backend → Return Result       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ routed
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                JIS                                          │
│                    (Identity + Intent Verification)                         │
│                                                                             │
│              IO (wie?) + DO (welk device?) + OD (wat?)                     │
│              FIR/A (trust) + SCS (continuity) + NIR (recovery)             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ verified
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               SNAFT                                         │
│                      (Semantic Security Check)                              │
│                                                                             │
│         "Is deze intent consistent met wie je bent en wat je mag?"          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ allowed
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TIBET WRAPPED ACTION                               │
│                                                                             │
│   ERIN (content) + ERAAN (deps) + EROMHEEN (context) + ERACHTER (why)     │
│                        = Immutable Provenance                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ logged
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AETHER NETWORK                                   │
│                                                                             │
│              AINS (domains) + I-Poll (messaging) + Genesis (VPN)           │
│                           Call-Mama (escalation)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start for Developers

### 1. Install Core Packages

```bash
pip install humotica rabel ainternet tibet kit-pm
```

### 2. Initialize

```python
from humotica import HumoticaOS

os = HumoticaOS.init(
    node_id="my-hubby",
    tier="verified"
)
```

### 3. Send a Message

```python
os.ipoll.send(
    to="gemini.aint",
    content="Analyze this data",
    poll_type="TASK"
)
```

### 4. Create Audit Trail

```python
os.tibet.create(
    type="action",
    erin="Processed customer request",
    erachter="Customer service automation"
)
```

---

## References

- **JIS Paper:** [DOI 10.5281/zenodo.17762391](https://zenodo.org/records/17762391)
- **TIBET Paper:** [DOI 10.5281/zenodo.18216215](https://zenodo.org/records/18216215)
- **SNAFT/Betti Paper:** [DOI 10.5281/zenodo.17759713](https://zenodo.org/records/17759713)
- **OomLlama Paper:** [DOI 10.5281/zenodo.18216068](https://zenodo.org/records/18216068)

---

## License

Copyright © 2026 Humotica. All rights reserved.

Core concepts are open for discussion and collaboration.
Implementation details may be proprietary.

---

**One love, one fAmIly!** 💙
