# Humotica BETTI Architecture

**Live Production System - November 2025**

---

## Network Overview

```
                            INTERNET
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                        HUMOTICA NETWORK                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                     JIS ROUTER LAYER                       │  │
│  │                     192.168.4.125                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │  │
│  │  │ Port 80/443 │  │  Port 8080  │  │ Port 18081  │        │  │
│  │  │   Web UI    │  │  JIS API    │  │ BETTI/JIS   │        │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                               │                                  │
│              ┌────────────────┼────────────────┐                 │
│              ▼                ▼                ▼                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   JTel Core     │  │   RaspBETTI     │  │   Android App   │  │
│  │  192.168.4.76   │  │  192.168.4.75   │  │    (Mobile)     │  │
│  │                 │  │                 │  │                 │  │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │
│  │  │ Brain API │  │  │  │ Edge Node │  │  │  │ JIS Client│  │  │
│  │  │ Port 8010 │  │  │  │  + GPIO   │  │  │  │   + TTS   │  │  │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │  │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │
│  │  │ Postgres  │  │  │  │  Sensors  │  │  │  │   Voice   │  │  │
│  │  │ Database  │  │  │  │ Actuators │  │  │  │ Assistant │  │  │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────┐                                            │
│  │  Kali Laptop    │  Development & Monitoring                  │
│  │   (Mobile)      │  - SDK Testing                             │
│  │                 │  - JIS Monitor                             │
│  │                 │  - Protocol Debug                          │
│  └─────────────────┘                                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Components

### JTel Core Server (192.168.4.76)

The brain of the system:

| Service | Port | Function |
|---------|------|----------|
| **Brain API** | 8010 | FastAPI with BETTI validation |
| **PostgreSQL** | 5432 | Device registry, intent logs |
| **Nginx** | 80/443 | Reverse proxy, SSL termination |

**Endpoints:**
- `/betti/validate` - Validate intent + generate TIBET
- `/betti/intent-log` - Query intent history
- `/home/{user_id}` - App home screen data
- `/ws/{user_id}` - WebSocket for real-time

### JIS Router (192.168.4.125)

OpenWRT router with JIS protocol layer:

| Port | Service |
|------|---------|
| 80 | LuCI Web Interface |
| 443 | HTTPS |
| 8080 | JIS Validation API |
| 18081 | BETTI/JIS Service |

**Functions:**
- Packet inspection at network level
- TIBET token validation
- SNAFT rule enforcement
- Traffic routing based on trust

### RaspBETTI (192.168.4.75)

Raspberry Pi edge device:

- GPIO control for physical devices
- Local BETTI validation
- Sensor data collection
- Real-time actuator control
- Offline capability with sync

### Android App

Mobile JIS client:

- JIS SDK integration
- Voice assistant (Piper TTS, Whisper STT)
- Push notifications via WebSocket
- Biometric authentication
- TIBET token management

### Kali Laptop

Development workstation:

- SDK testing environment
- JIS Monitor dashboard
- Protocol debugging
- Network analysis
- Framework development

---

## Data Flow Examples

### Example 1: Voice Command to Robot

```
┌─────────┐   Voice    ┌─────────┐   HTTP    ┌─────────┐   JIS    ┌─────────┐
│ Android │  ───────▶  │ Whisper │  ───────▶ │  Brain  │ ───────▶│RaspBETTI│
│   App   │  "move"    │   STT   │  intent   │   API   │  TIBET  │  Robot  │
└─────────┘            └─────────┘           └─────────┘         └─────────┘
                                                  │
                                             ┌────┴────┐
                                             │  SNAFT  │
                                             │ BALANS  │
                                             │  Check  │
                                             └─────────┘
```

### Example 2: IoT Device Control

```
┌─────────┐   JIS     ┌─────────┐  Validate  ┌─────────┐  Execute ┌─────────┐
│  Kali   │ ───────▶  │   JIS   │  ───────▶  │  Brain  │ ───────▶│  IoT    │
│ Laptop  │  Packet   │ Router  │   TIBET    │   API   │  Action │ Device  │
└─────────┘           └─────────┘            └─────────┘         └─────────┘
                           │
                      ┌────┴────┐
                      │Firewall │
                      │ Rules   │
                      └─────────┘
```

### Example 3: Verified Phone Call

```
┌─────────┐  Incoming  ┌─────────┐  Validate  ┌─────────┐   NIR   ┌─────────┐
│External │  ───────▶  │   JIS   │  ───────▶  │  BETTI  │ ───────▶│ Android │
│ Caller  │   Call     │ Router  │   Check    │  Engine │ Verify? │   App   │
└─────────┘            └─────────┘            └─────────┘         └─────────┘
                                                  │
                                             ┌────┴────┐
                                             │Context: │
                                             │ 3 AM?   │
                                             │Unusual? │
                                             └─────────┘
```

---

## Protocol Stack

```
┌──────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                        │
│   Android App  │  Voice Assistant  │  Web Dashboard           │
├──────────────────────────────────────────────────────────────┤
│                       BETTI LAYER                             │
│   SNAFT  │  BALANS  │  HICSS  │  14 Natural Laws             │
├──────────────────────────────────────────────────────────────┤
│                        JIS LAYER                              │
│   HID/DID  │  TIBET  │  FIR/A  │  NIR  │  Continuity Chain   │
├──────────────────────────────────────────────────────────────┤
│                      TRANSPORT LAYER                          │
│   HTTP/REST  │  WebSocket  │  MQTT  │  SIP                   │
├──────────────────────────────────────────────────────────────┤
│                       NETWORK LAYER                           │
│   JIS Router  │  Firewall  │  Encryption                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Monitoring

### JIS Monitor

Access: `https://betti.humotica.com/static/jis-monitor.html`

Shows:
- Real-time packet stream
- Validation statistics
- Network topology
- TIBET token inspection
- Trust level overview

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/betti/intent-log` | GET | Last 50 intents |
| `/betti/intent-log/stats` | GET | Validation statistics |
| `/ws/status` | GET | WebSocket connections |

---

## Websites

| Domain | Service |
|--------|---------|
| [humotica.com](https://humotica.com) | Main website |
| [betti.humotica.com](https://betti.humotica.com) | BETTI API + Monitor |
| [jis.humotica.com](https://jis.humotica.com) | JIS Protocol docs |
| [josl.humotica.com](https://josl.humotica.com) | License |

---

## Contact

**Jasper van de Meent**
Humotica - Making AI Human

jtmeent@gmail.com
