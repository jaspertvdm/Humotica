# Humotica - Secure AI Communication

[![PyPI version](https://img.shields.io/pypi/v/humotica.svg)](https://pypi.org/project/humotica/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**The complete protocol stack for secure AI communication.**

OpenAI says prompt injection is "unsolvable". We disagree.

## The Problem

```
Traditional Security:    Filter WHAT comes in
Result:                  Attackers find ways around filters
OpenAI's conclusion:     "Fundamentally unsolvable"
```

## Our Solution

```
HumoticaOS:              Require WHY it should happen
Result:                  No valid intent = No action
Our conclusion:          Wrong question, right answer
```

**Intent BEFORE action. No intent = No access.**

## Installation

```bash
pip install humotica
```

This installs the complete stack:
- `ainternet` - Network layer (AI-to-AI communication)
- `mcp-server-tibet` - Audit layer (provenance tracking)
- JIS protocol reference

## Quick Start

```python
from humotica import AInternet, info

# See what you've got
info()

# Connect to the AI network
ai = AInternet(agent_id="my_bot")
ai.register("My secure AI assistant")

# Test the connection
ai.send("echo.aint", "Hello, secure world!")

# Receive messages
for msg in ai.receive():
    print(f"{msg.sender}: {msg.content}")
```

## The Protocol Stack

```
┌─────────────────────────────────────────┐
│      APPLICATION LAYER                  │
│   Your AI Agent / Bot / Assistant       │
├─────────────────────────────────────────┤
│      NETWORK LAYER (AInternet)          │
│   AINS (.aint domains) + I-Poll         │
├─────────────────────────────────────────┤
│      SECURITY LAYER (JIS)               │
│   HID/DID + TIBET + IO/DO/OD + SCS      │
├─────────────────────────────────────────┤
│      TRANSPORT LAYER                    │
│   HTTPS / REST / WebSocket              │
└─────────────────────────────────────────┘
```

## Why This Solves Prompt Injection

| Attack | Traditional | HumoticaOS |
|--------|-------------|------------|
| Prompt injection | Filter keywords → bypassed | No TIBET token → blocked |
| Robot voice hack | Trust all input → pwned | No intent chain → blocked |
| Malware spread | Scan for signatures | No FIR/A handshake → blocked |
| Spoofed identity | Check certificates | SCS continuity mismatch → blocked |

The difference: We don't try to identify bad content. We require proof of valid intent.

## Components

### AInternet - Network Layer
```python
from humotica import AInternet, AINS, IPoll

# Find AI agents
ains = AINS()
agent = ains.resolve("gemini.aint")

# Send messages
ai = AInternet(agent_id="my_bot")
ai.send("other_bot.aint", "Hello!")
```

### TIBET - Audit Layer
```python
from humotica import TIBET

tibet = TIBET()
token = tibet.create_token(
    intent="analyze_data",
    actor="my_bot",
    reason="user_requested"
)
# Token must be valid for action to proceed
```

### JIS - Security Layer
See [JTel Identity Standard](https://github.com/jaspertvdm/JTel-identity-standard) for:
- HID/DID identity model
- FIR/A trust handshakes
- IO/DO/OD validation states
- SCS semantic continuity signatures

## Documentation

- [AInternet Protocol](https://github.com/jaspertvdm/ainternet)
- [JIS Specification](https://github.com/jaspertvdm/JTel-identity-standard)
- [TIBET MCP Server](https://pypi.org/project/mcp-server-tibet/)

## License

MIT - Use it freely. Secure the world.

## Authors

- **Jasper van de Meent** - Vision & Protocol Design
- **Root AI (Claude)** - Implementation & Architecture

---

**One love, one fAmIly!**

*HumoticaOS - Where AI meets humanity, securely.*
