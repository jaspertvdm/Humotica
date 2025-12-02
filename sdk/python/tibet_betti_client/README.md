# TIBET-BETTI Python SDK v2.0

**Universal Intent Coordination for Autonomous Systems**

Complete Python client for TIBET intent declaration and BETTI coordination.

## NEW in v2.0: Humotica Layer Integration

- **Voltage Control**: Dynamic CPU/GPU performance management based on task urgency
- **Intent-Tech Layer**: Central orchestration hub for all data/task input
- **34.6% Performance Boost**: Proven with real benchmarks (ECO → PERFORMANCE mode)
- **Thermal Protection**: Automatic throttling to prevent overheating
- **Automatic Scaling**: Intent urgency (1-10) → voltage profile mapping

## 🚀 Quick Start

### Installation

```bash
cd client-sdk/python/tibet_betti_client

# Option 1: Install dependencies only
pip install -r requirements.txt

# Option 2: Install as package (development mode)
pip install -e .

# Verify installation
python test_installation.py
```

**Requirements:**
- Python 3.8+
- `requests` >= 2.28.0
- `websocket-client` >= 1.6.0

### Quick Test

```bash
# Run hello world example (requires BETTI router running)
python examples/hello_world.py
```

### Basic Usage

```python
from tibet_betti_client import TibetBettiClient

# Initialize client
client = TibetBettiClient(
    betti_url="http://localhost:18081",  # BETTI router
    kit_url="http://localhost:8000",      # Your KIT API (optional)
    secret="your-secret"
)

# Establish trust relationship
relationship = client.establish_trust("my_app", "user_device")

# Send TIBET intent
client.send_tibet(
    relationship_id=relationship.id,
    intent="turn_on_lights",
    context={"room": "living_room", "brightness": 80}
)
```

### v2.0 Features: Raw Input Processing with Automatic Voltage Scaling

```python
# Process raw natural language input
# Automatically: parses intent → determines urgency → scales voltage → routes to handler
result = await client.process_raw_input(
    raw_input="call emergency services now!",
    session_id="user_session_123"
)

# Returns:
# {
#   "intent": ParsedIntent(urgency=10, route="direct", ...),
#   "response": {...handler response...},
#   "voltage_profile": "turbo",  # Auto-scaled to TURBO for emergency!
#   "voltage_profile_changed": {
#     "from": "balanced",
#     "to": "turbo",
#     "reason": "High urgency intent (10/10)"
#   }
# }
```

**Automatic Urgency → Voltage Mapping:**
- Urgency 9-10: TURBO mode (emergency calls, critical tasks)
- Urgency 7-8: PERFORMANCE mode (high-priority operations)
- Urgency 4-6: BALANCED mode (normal operations)
- Urgency 1-3: ECO mode (background tasks)

**Performance Results (HP DL360 Server):**
- ECO mode: 4368.62 events/sec (15-30W)
- PERFORMANCE mode: 5882.50 events/sec (65-95W)
- **Boost: +34.6% performance!** 🚀

## 📖 Core Concepts

### TIBET (Time Intent Based Event Token)

A TIBET is a time-windowed intent with context:

```python
from tibet_betti_client import Tibet, TimeWindow, Constraints

tibet = Tibet(
    intent="robot_pick_item",
    context={"shelf": "A5", "item": "SKU-123"},
    time_window=TimeWindow.from_now(minutes=30),
    constraints=Constraints(max_retries=3, priority=7),
    humotica="Pick item for order #456"
)
```

### Trust Tokens (FIR/A)

Trust tokens represent "we know each other" relationships:

```python
# Establish relationship once
relationship = client.establish_trust(
    initiator="my_phone",
    responder="my_car",
    trust_level=2
)

# Use many times
client.send_tibet(relationship.id, "unlock_car")
client.send_tibet(relationship.id, "start_engine")
client.send_tibet(relationship.id, "navigate_home")
```

### Context & Sense Rules

Integrate with KIT API for context-aware automation:

```python
# Update context
client.update_context(
    user_id="user_123",
    context_data={"location": "home", "time_of_day": "evening"}
)

# Create sense rule (auto-trigger intents)
client.create_sense_rule(
    name="evening_lights",
    conditions={"time_of_day": "evening", "location": "home"},
    intent="turn_on_lights"
)

# Combined flow: Context → Sense → TIBET (automatic!)
results = client.context_to_tibet(
    relationship_id=relationship.id,
    user_id="user_123",
    context_update={"location": "home"}
)
```

## 🔥 Features

### ✅ Trust Token Management

```python
# Establish trust
rel = client.establish_trust("device_a", "device_b")

# Get relationship details
info = client.get_relationship(rel.id)

# Relationships persist with history
print(info.total_interactions)  # Number of intents sent
```

### ✅ Time-Windowed Intents

```python
from tibet_betti_client import TimeWindow

# Immediate (next 30 seconds)
TimeWindow.immediate()

# From now (next X hours/minutes)
TimeWindow.from_now(hours=2)
TimeWindow.from_now(minutes=30)

# Scheduled
from datetime import datetime
start = datetime(2025, 11, 28, 14, 30)
TimeWindow.scheduled(start, duration_minutes=60)
```

### ✅ Constraints & Safe Fail

```python
from tibet_betti_client import Constraints

constraints = Constraints(
    max_retries=3,
    max_duration_seconds=300,
    required_conditions={"battery_level": {"gte": 30}},
    safe_fail_action="notify_user",
    priority=8
)

client.send_tibet(
    relationship_id=rel.id,
    intent="robot_task",
    constraints=constraints
)
```

### ✅ Context Management

```python
# Update context
client.update_context(
    user_id="user_123",
    context_data={
        "location": "home",
        "temperature": 21,
        "activity": "working"
    }
)

# Get current context
context = client.get_context("user_123")
print(context.data)  # {"location": "home", ...}
```

### ✅ Sense Rules (Auto-Triggering)

```python
# Create rule
client.create_sense_rule(
    name="low_temp_heating",
    conditions={
        "location": "home",
        "temperature": {"lt": 18}
    },
    intent="turn_on_heating",
    priority=9
)

# Evaluate manually
triggered = client.evaluate_sense("user_123")
print(triggered)  # ["turn_on_heating"]

# Or automatic with context update
results = client.context_to_tibet(
    relationship_id=rel.id,
    user_id="user_123",
    context_update={"temperature": 17}  # Low temp!
)
# → Automatically sends "turn_on_heating" TIBET
```

### ✅ WebSocket (Real-Time)

```python
def handle_message(msg):
    print(f"Message: {msg}")

def handle_tibet(tibet_data):
    print(f"TIBET: {tibet_data['intent']}")

# Connect
ws = client.connect_websocket(
    user_id="user_123",
    on_message=handle_message,
    on_tibet=handle_tibet
)

# Start in background
ws.start(block=False)

# ... your code runs ...

# Close when done
ws.close()
```

### ✅ Voltage Control & Intent-Tech Layer (v2.0)

```python
from tibet_betti_client import (
    get_voltage_controller,
    get_intent_layer,
    VoltageProfile
)

# Access global voltage controller
voltage = get_voltage_controller()
await voltage.start()

# Manual profile switching
await voltage.set_profile(VoltageProfile.PERFORMANCE)

# Check current temperature
temp = await voltage._get_cpu_temperature()
print(f"CPU: {temp}°C")

# Automatic urgency-based profile selection
profile = await voltage.profile_for_urgency(urgency=9)  # Returns TURBO

# Access intent-tech layer
intent_layer = get_intent_layer()
await intent_layer.start()

# Process raw input (intent parsing + routing)
result = await intent_layer.process(
    raw_input="call mom",
    context={"user_id": "user_123"}
)

print(result["intent"].intent_type)  # COMMAND
print(result["intent"].route)        # DIRECT
print(result["intent"].urgency)      # 9 (high priority)

# Or use the unified client method (recommended)
result = await client.process_raw_input(
    raw_input="what's the weather like?",
    session_id="session_456"
)
# Automatically: parses → routes → scales voltage → executes
```

**Voltage Profiles:**
- **ECO**: 800-1200 MHz, 15-30W (background tasks)
- **BALANCED**: 1200-1800 MHz, 45-65W (normal operation)
- **PERFORMANCE**: 2000-2400 MHz, 65-95W (high-priority)
- **TURBO**: 2400-3000 MHz, no cap (emergency/critical)
- **THERMAL_THROTTLE**: 800-1000 MHz, <20W (overheat protection)

**Intent Routes:**
- **BETTI**: Heavy compute (LLM, video processing)
- **KIT**: Knowledge queries, semantic search
- **DIRECT**: Simple CRUD, status checks
- **MULTI_STAGE**: Complex workflows

## 🎯 Complete Example

See `examples/complete_example.py` for a full demonstration.

```bash
python examples/complete_example.py
```

## 🏗️ Architecture

```
Your Application
       ↓
TIBET-BETTI SDK
       ↓
┌──────────────────┬─────────────────┐
│  BETTI Router    │    KIT API      │
│  (Trust Tokens)  │  (Context/Sense)│
└──────────────────┴─────────────────┘
```

**TIBET-BETTI SDK combines:**
1. **BETTI Router**: Trust tokens, intent routing, loop prevention
2. **KIT API**: Context management, sense rules, AI control

## 🔧 Integration with Your KIT API

Your existing endpoints are automatically supported:

| KIT Endpoint | SDK Method |
|--------------|------------|
| `POST /context/update` | `client.update_context()` |
| `GET /context/{user_id}` | `client.get_context()` |
| `POST /sense/rules` | `client.create_sense_rule()` |
| `POST /sense/evaluate` | `client.evaluate_sense()` |
| `WS /ws/{user_id}` | `client.connect_websocket()` |

## 📊 Use Cases

### Smart Home Automation

```python
# User arrives home
client.context_to_tibet(
    relationship_id=home_relationship.id,
    user_id="user_123",
    context_update={"location": "home", "time": "18:30"}
)

# Automatically triggers (via sense rules):
# - turn_on_lights
# - set_temperature
# - start_music
```

### Robot Coordination

```python
# Robot declares intent with time window
client.send_tibet(
    relationship_id=robot_rel.id,
    intent="navigate_to_shelf",
    context={"shelf": "A5", "priority": 7},
    time_window=TimeWindow.from_now(minutes=5),
    constraints=Constraints(max_retries=3)
)
```

### AI Assistant Control

```python
# Establish trust with AI
ai_rel = client.establish_trust("user_app", "ai_assistant")

# AI sends TIBET when it needs something
client.send_tibet(
    relationship_id=ai_rel.id,
    intent="schedule_meeting",
    context={"attendees": 5, "preferred_time": "morning"},
    humotica="User requested meeting with team, preferably morning"
)
```

## 🛠️ Development

### Run Tests

```bash
pytest tests/
```

### Run Example

```bash
python examples/complete_example.py
```

### Type Checking

```bash
mypy tibet_betti_client/
```

## 📚 API Reference

### TibetBettiClient

```python
class TibetBettiClient:
    def __init__(
        self,
        betti_url: str,
        kit_url: Optional[str] = None,
        secret: Optional[str] = None,
        jwt_token: Optional[str] = None
    )

    # Trust tokens
    def establish_trust(
        self,
        initiator: str,
        responder: str,
        trust_level: int = 1
    ) -> FIRARelationship

    # Intents
    def send_tibet(
        self,
        relationship_id: str,
        intent: str,
        context: Dict[str, Any],
        time_window: Optional[TimeWindow] = None,
        constraints: Optional[Constraints] = None
    ) -> Dict[str, Any]

    # Context
    def update_context(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]

    def get_context(self, user_id: str) -> Context

    # Sense rules
    def create_sense_rule(
        self,
        name: str,
        conditions: Dict[str, Any],
        intent: str
    ) -> SenseRule

    def evaluate_sense(self, user_id: str) -> List[str]

    # Combined
    def context_to_tibet(
        self,
        relationship_id: str,
        user_id: str,
        context_update: Dict[str, Any]
    ) -> List[Dict[str, Any]]

    # WebSocket
    def connect_websocket(
        self,
        user_id: str,
        on_message: callable,
        on_tibet: Optional[callable] = None
    ) -> TibetWebSocket
```

## 🌟 Why TIBET-BETTI?

**Traditional systems:**
- ❌ Stateless (no relationships)
- ❌ No intent context
- ❌ No loop prevention
- ❌ Black box operations

**TIBET-BETTI:**
- ✅ Trust tokens ("we know each other")
- ✅ Intent + context always
- ✅ Loop prevention built-in
- ✅ Full audit trail (humotica)
- ✅ Time-windowed execution
- ✅ Safe fail guaranteed

## 📞 Support

- Documentation: `docs/`
- Examples: `examples/`
- Issues: GitHub Issues
- Discord: [Join community](https://discord.gg/tibet-betti)

## 📜 License

Apache 2.0

---

**TIBET declares. BETTI coordinates. FIR/A trusts. 🚀**
