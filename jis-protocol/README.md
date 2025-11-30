# JIS Protocol - Identity Standard

**Jasper's Identity Standard for Human-Robot Trust**

JIS is the protocol layer that manages identity, intent, and interaction in the BETTI framework.

## Core Concepts

### HID - Human Identity
Unique identifier for humans in the system.
```
HID format: @username:domain.tld
Example: @jasper:humotica.com
```

### DID - Device Identity
Unique identifier for devices/robots.
```
DID format: device-type:uuid:manufacturer
Example: robot:550e8400-e29b-41d4-a716-446655440000:boston_dynamics
```

### FiRA - Federated identity Relationship Agreement
Trust relationship between HID and DID.

## JIS Router

The JIS Router is a network device that:
1. Validates all TIBET tokens
2. Enforces SNAFT rules at network level
3. Routes packets based on trust levels
4. Provides real-time monitoring

### Network Topology

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│ JIS Router  │────▶│ RaspBETTI   │
│   App/Web   │     │ 192.168.4.125│     │ 192.168.4.75│
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                    ┌──────▼──────┐
                    │ JTel Core   │
                    │ 192.168.4.76│
                    └─────────────┘
```

### JIS Packet Format

```json
{
  "version": "JIS/1.0",
  "timestamp": "2025-11-30T21:00:00Z",
  "tibet_token": "TIBET-20251130-...",
  "hid": "@jasper:humotica.com",
  "did": "robot:...:manufacturer",
  "intent": "move_arm",
  "context": {
    "sense": "User requested arm movement",
    "intent": "Move robot arm to position",
    "explanation": "Safe movement within bounds"
  },
  "snaft_approved": true,
  "balans_score": 0.85,
  "continuity_hash": "sha256..."
}
```

## Protocol Layers

### Layer 1: Identity (I)
- HID/DID validation
- FiRA relationship verification
- Trust score calculation

### Layer 2: Intent (I)
- TIBET token generation
- SNAFT firewall check
- BALANS pre-execution decision

### Layer 3: Interaction (I)
- Actual command execution
- HICSS override handling
- Flag2Fail monitoring

## Router Configuration

### OpenWRT Setup

```bash
# Install JIS CLI
opkg install jis-cli

# Configure JIS router
jis config set betti_url http://192.168.4.76:8010
jis config set snaft_mode strict
jis config set log_level info

# Start JIS daemon
jis daemon start
```

### Validation Endpoint

The router exposes `/jis/validate` for packet validation:

```bash
curl -X POST http://192.168.4.125:8080/jis/validate \
  -H "Content-Type: application/json" \
  -d '{
    "hid": "@jasper:humotica.com",
    "did": "phone:123:apple",
    "intent": "send_message",
    "context": {"to": "@recipient:domain.com"}
  }'
```

Response:
```json
{
  "approved": true,
  "tibet_token": "TIBET-20251130-ABC123",
  "route": "direct",
  "snaft_status": "passed",
  "balans_score": 0.92
}
```

## Monitor UI

Access the JIS Monitor at:
```
https://betti.humotica.com/static/jis-monitor.html
```

Features:
- Real-time packet stream
- Network topology view
- Validation statistics
- TIBET token inspection
- Dark/light mode

## Security

### SNAFT at Router Level
The router enforces SNAFT rules before packets reach devices:
- Keyword blocking
- Pattern matching
- Rate limiting
- Device-specific rules

### Trust Levels
- **Level 5**: Full trust (owner)
- **Level 4**: High trust (family)
- **Level 3**: Normal trust (friends)
- **Level 2**: Limited trust (guests)
- **Level 1**: Minimal trust (unknown)
- **Level 0**: Blocked

## Related

- [Humotica BETTI](https://github.com/jaspertvdm/Humotica) - Main framework
- [BETTI Paper](https://betti.humotica.com) - Academic paper
