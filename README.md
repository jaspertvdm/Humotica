# Humotica BETTI Framework

**Physics-Based Computing for Human-Robot Interaction**

```
Framework:  BETTI (Balanced Economic Transaction Trust Integration)
Protocol:   JIS (JTel Identity Standard)
Author:     Jasper van de Meent
License:    JOSL (Jasper Open Standard License)
```

---

## What is BETTI?

BETTI is the world's first computing framework that applies **14 natural physics laws** to:

- Resource allocation
- Trust verification
- Human-machine interaction
- Intent-based security

BETTI doesn't just validate data - it understands **meaning** and **intent**.

---

## Live System

The framework runs in production:

| Component | Location | Function |
|-----------|----------|----------|
| **JTel Core Server** | 192.168.4.76 | Brain API, validation engine |
| **JIS Router** | 192.168.4.125 | OpenWRT with JIS protocol layer |
| **RaspBETTI** | 192.168.4.75 | Raspberry Pi edge device |
| **Android App** | Mobile | JIS client with voice assistant |
| **Kali Laptop** | Development | SDK testing, monitoring |

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HUMOTICA BETTI NETWORK                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐    JIS     ┌──────────────┐    JIS    ┌──────────┐  │
│   │ Android  │───────────▶│  JIS Router  │──────────▶│ RaspBETTI│  │
│   │   App    │            │ 192.168.4.125│           │   .75    │  │
│   └──────────┘            └──────┬───────┘           └──────────┘  │
│                                  │                                  │
│   ┌──────────┐                   │                                  │
│   │  Kali    │                   │                                  │
│   │ Laptop   │───────────────────┤                                  │
│   └──────────┘                   │                                  │
│                                  ▼                                  │
│                          ┌──────────────┐                           │
│                          │  JTel Core   │                           │
│                          │ 192.168.4.76 │                           │
│                          │  Brain API   │                           │
│                          └──────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The 14 Natural Laws

BETTI applies physics principles to computing:

| # | Law | Computing Application |
|---|-----|----------------------|
| 1 | **Kepler's Law** | Orbital resource allocation |
| 2 | **Newton's Gravity** | Trust attraction between entities |
| 3 | **Einstein's E=mc²** | Energy-mass equivalence for computation |
| 4 | **Thermodynamics** | Entropy management in systems |
| 5 | **Conservation of Energy** | Resource preservation |
| 6 | **Archimedes' Principle** | Buoyancy-based priority |
| 7 | **Ohm's Law** | Resistance in data flow |
| 8 | **Hooke's Law** | Elastic load balancing |
| 9 | **Wave Equation** | Signal propagation |
| 10 | **Doppler Effect** | Velocity-based timing |
| 11 | **Planck's Constant** | Quantum discretization |
| 12 | **Heisenberg Uncertainty** | Trade-off optimization |
| 13 | **Maxwell's Equations** | Field-based coordination |
| 14 | **Entropy** | System complexity management |

---

## Key Protocols

### TIBET - Trust Token
```json
{
  "tibet_token": "TIBET-20251130-ABC123",
  "intent": "move_robot_arm",
  "hid": "@jasper:humotica.com",
  "did": "robot:uuid:manufacturer",
  "timestamp": "2025-11-30T22:00:00Z",
  "snaft_approved": true,
  "balans_score": 0.92
}
```

### SNAFT - Factory Firewall
Blocks dangerous operations at the system level:
- Harmful keywords detection
- Pattern matching
- Device-specific rules
- Rate limiting

### BALANS - Decision Engine
Pre-execution analysis:
- Urgency assessment
- Resource availability
- Timing optimization
- Risk calculation

### HICSS - Human Override
Emergency control system:
- **H**alt - Stop all operations
- **I**ntent - Clarify current action
- **C**hange - Modify parameters
- **S**witch - Change mode
- **S**top - Full shutdown

---

## Use Cases

### 1. Verified Phone Call
```
User receives call from "Bank"
  ↓
JIS Router validates TIBET token
  ↓
BETTI checks: 3 AM? 5th attempt? Unusual!
  ↓
NIR triggers: "Verify this call?"
  ↓
User confirms with fingerprint
  ↓
Call connects with full audit trail
```

### 2. Robot Command
```
User: "Hey BETTI, move the arm"
  ↓
Voice → Intent: "move_arm"
  ↓
TIBET token generated
  ↓
SNAFT check: Safe operation? ✓
  ↓
BALANS: Resources available? ✓
  ↓
Execute with real-time monitoring
```

### 3. IoT Device Control
```
App sends: turn_on_light
  ↓
JIS Router validates HID/DID
  ↓
TIBET token with context
  ↓
Device executes if IO/DO/OD = OK
  ↓
Continuity chain updated
```

### 4. Deepfake Detection
```
Incoming video message
  ↓
Check: Has valid SCS signature?
  ↓
Check: Does IO/DO/OD chain match?
  ↓
Check: Human behavioral continuity?
  ↓
No valid chain → FLAGGED → BLOCKED
```

---

## Framework Structure

```
Humotica/
├── betti-core/           # Core BETTI algorithms
│   ├── natural_laws.py   # 14 physics laws engine
│   ├── snaft.py          # Safety firewall
│   ├── balans.py         # Decision engine
│   ├── hicss.py          # Human override
│   └── complexity.py     # Betti number analysis
│
├── jis-protocol/         # JIS documentation
│   └── README.md         # Protocol reference
│
├── integrations/
│   └── voice/            # Voice assistant
│       ├── tts.py        # Text-to-Speech (Piper, Coqui)
│       ├── stt.py        # Speech-to-Text (Whisper, Vosk)
│       ├── wake_word.py  # Wake word detection
│       └── assistant.py  # Complete assistant
│
├── sdk/
│   ├── python/           # Python SDK
│   └── typescript/       # TypeScript SDK
│
├── examples/             # Working examples
└── docs/                 # Documentation
```

---

## Quick Start

```bash
# Clone the framework
git clone https://github.com/jaspertvdm/Humotica.git
cd Humotica

# Install Python SDK
cd sdk/python
pip install -e .

# Run example
python examples/basic_usage.py
```

### Voice Assistant

```python
from humotica.integrations.voice import VoiceAssistant

assistant = VoiceAssistant(
    betti_url="http://192.168.4.76:8010",
    tts_engine="piper",
    stt_engine="whisper",
    wake_word="hey betti"
)

@assistant.on_intent
async def handle(intent, context, tibet_token):
    print(f"Executing: {intent}")
    return "Done!"

assistant.run()
```

---

## Websites

| Site | URL | Description |
|------|-----|-------------|
| **Humotica** | [humotica.com](https://humotica.com) | Main website |
| **BETTI** | [betti.humotica.com](https://betti.humotica.com) | BETTI framework & monitor |
| **JIS** | [jis.humotica.com](https://jis.humotica.com) | JIS Protocol docs |
| **JOSL** | [josl.humotica.com](https://josl.humotica.com) | License info |

---

## Build Your Own

For full implementation with server, database, and all services:

1. **Protocol Spec**: [JTel-identity-standard](https://github.com/jaspertvdm/JTel-identity-standard)
2. **License**: [JOSL](https://github.com/jaspertvdm/JOSL)
3. **This Framework**: Use as foundation

The framework provides all algorithms and protocols. Build your server implementation on top.

---

## Related Repositories

| Repository | Description |
|------------|-------------|
| [JTel-identity-standard](https://github.com/jaspertvdm/JTel-identity-standard) | JIS Protocol specification |
| [JOSL](https://github.com/jaspertvdm/JOSL) | Jasper Open Standard License |

---

## Author

**Jasper van de Meent**
Humotica - Making AI Human

- Web: [humotica.com](https://humotica.com)
- Email: jtmeent@gmail.com
- GitHub: [@jaspertvdm](https://github.com/jaspertvdm)

---

## License

**JOSL** (Jasper Open Standard License)

Free to use, implement, and integrate. Attribution required.

```
"Powered by JIS (JTel Identity Standard), authored by Jasper van de Meent."
```
