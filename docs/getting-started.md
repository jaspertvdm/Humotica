# Getting Started with BETTI

**Build your first JIS-enabled application in 10 minutes**

---

## Prerequisites

- Python 3.9+
- pip

---

## 1. Install the SDK

```bash
git clone https://github.com/jaspertvdm/Humotica.git
cd Humotica/sdk/python
pip install -e .
```

---

## 2. Basic Usage

```python
from jis_client import JISClient

# Connect to BETTI server
client = JISClient("http://localhost:8010")

# Register your device
client.register_device(
    device_type="app",
    name="MyFirstApp"
)

# Validate an intent before executing
result = client.validate_intent(
    intent="send_message",
    context={"to": "@user:domain.com", "message": "Hello!"}
)

if result.approved:
    print(f"TIBET Token: {result.tibet_token}")
    print(f"SNAFT Approved: {result.snaft_approved}")
    print(f"BALANS Score: {result.balans_score}")
    # Execute your action here
else:
    print("Action not approved")
```

---

## 3. Understanding the Response

When you validate an intent, BETTI returns:

| Field | Description |
|-------|-------------|
| `approved` | Whether the action is allowed |
| `tibet_token` | Unique token for this transaction |
| `snaft_approved` | Safety firewall check passed |
| `balans_score` | Decision confidence (0.0 - 1.0) |
| `humotica` | Human-readable explanation |

---

## 4. Voice Assistant (Optional)

```python
from humotica.integrations.voice import VoiceAssistant

assistant = VoiceAssistant(
    betti_url="http://localhost:8010",
    tts_engine="piper",      # or "coqui", "system"
    stt_engine="whisper",    # or "vosk"
    wake_word="hey betti"
)

@assistant.on_intent
async def handle(intent, context, tibet_token):
    print(f"Received: {intent}")
    return f"Executing {intent}"

# Start listening
assistant.run()
```

---

## 5. Key Concepts

### TIBET Token
Every validated action gets a time-bound token. Use it to prove authorization.

### SNAFT
Factory-level safety firewall. Blocks dangerous operations automatically.

### BALANS
Pre-execution decision engine. Weighs urgency, resources, and context.

### HID/DID
- **HID**: Human Identity (never transmitted)
- **DID**: Device Identity (used in communications)

---

## 6. Example: IoT Light Control

```python
from jis_client import JISClient

client = JISClient("http://192.168.4.76:8010")
client.register_device(device_type="iot_controller", name="LightController")

def turn_on_light(room):
    result = client.validate_intent(
        intent="device_on",
        context={
            "device": "light",
            "room": room,
            "source": "voice_command"
        }
    )

    if result.approved:
        # Send command to actual light
        print(f"Light in {room} turned on")
        print(f"Token: {result.tibet_token}")
    else:
        print("Not authorized")

turn_on_light("living_room")
```

---

## 7. Example: Verified Call

```python
result = client.validate_intent(
    intent="initiate_call",
    context={
        "caller": "@jasper:humotica.com",
        "callee": "+31612345678",
        "reason": "appointment_reminder"
    }
)

if result.approved:
    # Proceed with SIP call
    # Include tibet_token in SIP headers
    pass
```

---

## Next Steps

- [Architecture Overview](ARCHITECTURE.md)
- [JIS Protocol Spec](https://github.com/jaspertvdm/JTel-identity-standard)
- [API Reference](https://betti.humotica.com)

---

## Support

**Jasper van de Meent**
- Web: [humotica.com](https://humotica.com)
- Email: jtmeent@gmail.com
