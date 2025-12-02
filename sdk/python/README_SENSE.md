# Sense 2.0 Client SDK

**Privacy-First Client-Side Profiling voor JTel Apps**

---

## 🚀 Quick Install

```bash
# From Backend-server-JTel repo (spiegelserver):
git clone git@github.com:jaspertvdm/Backend-server-JTel.git
cd Backend-server-JTel/client-sdk/python
pip install -e .
```

---

## 📦 What You Get

**ClientSense class** - Privacy-first local profiling:
- ✅ Local behavior profiling (blijft op device!)
- ✅ Pattern detection ("Je belt mama vaak om 9u")
- ✅ Predictive suggestions (met confidence scores)
- ✅ Situation detection (tijd, activiteit, mode)
- ✅ GDPR compliant (export/delete)

---

## 🎯 Quick Start - 3 Lines!

```python
from tibet_betti_client.sense import ClientSense

# 1. Initialize
sense = ClientSense(user_id="jasper", privacy_mode=True)

# 2. Record actions
sense.record_action("call", {"target": "mama", "intent": "family_chat"})

# 3. Get suggestions
suggestions = sense.suggest_actions(limit=3)
print(suggestions)
# → [{"action": "call", "target": "mama", "confidence": 0.85}]
```

**DONE! 🎉**

---

## 📖 Complete Example

```python
from tibet_betti_client import TibetBettiClient
from tibet_betti_client.sense import ClientSense

class JTelApp:
    def __init__(self, user_id: str):
        # BETTI client
        self.client = TibetBettiClient(
            betti_url="http://localhost:18081",
            kit_url="http://localhost:8000",
            secret="your-secret"
        )

        # Sense (LOCAL profiling - privacy first!)
        self.sense = ClientSense(user_id=user_id, privacy_mode=True)

    async def make_call(self, contact: str):
        """Make call with Sense tracking"""
        # BEFORE: record intent
        self.sense.record_action("call", {
            "target": contact,
            "intent": "casual_call",
            "location": "home"
        })

        # Make actual call
        await self.client.send_tibet(
            intent="call",
            context={"to": contact}
        )

        # AFTER: record result
        self.sense.record_action("call", {
            "target": contact,
            "result": "success"
        })

    def show_suggestions(self):
        """Show smart suggestions on home screen"""
        suggestions = self.sense.suggest_actions(limit=3)

        for sug in suggestions:
            if sug['confidence'] > 0.7:
                print(f"💡 {sug['action'].title()} {sug['target']}?")
                print(f"   (Je doet dit vaak nu - {sug['confidence']*100:.0f}% zeker)")

# Usage
app = JTelApp(user_id="jasper")
await app.make_call("mama")
app.show_suggestions()
```

---

## 🔧 Install on Different Devices

### Flutter App (via Python bridge):
```dart
// Use flutter_python to call Sense SDK
import 'package:flutter_python/flutter_python.dart';

final sense = await FlutterPython.run('''
from tibet_betti_client.sense import ClientSense
sense = ClientSense(user_id="$userId")
sense.record_action("call", {"target": "$contact"})
''');
```

### React Native (via REST API):
```javascript
// Call backend Sense API
const response = await fetch('http://api/sense/context/record', {
  method: 'POST',
  body: JSON.stringify({
    user_id: userId,
    action: 'call',
    context: {target: contact}
  })
});
```

### Pure Python App:
```python
pip install -e git+ssh://git@github.com/jaspertvdm/Backend-server-JTel.git#egg=tibet-betti-client&subdirectory=client-sdk/python
```

---

## 🧪 Testing

```bash
# Test import
python3 -c "from tibet_betti_client.sense import ClientSense; print('✅ Import OK')"

# Test basic usage
python3 << 'EOF'
from tibet_betti_client.sense import ClientSense

sense = ClientSense("test_user")
sense.record_action("call", {"target": "mama"})
sense.record_action("call", {"target": "mama"})
sense.record_action("call", {"target": "mama"})

patterns = sense.get_all_patterns()
print(f"✅ Recorded {patterns['call']['count']} actions")

suggestions = sense.suggest_actions()
print(f"✅ Got {len(suggestions)} suggestions")
EOF
```

---

## 📊 API Reference

### ClientSense(user_id, storage_dir=None, privacy_mode=True)

**Constructor:**
- `user_id`: Unique user identifier
- `storage_dir`: Where to store data (default: ~/.humotica/sense/)
- `privacy_mode`: True = no sync to backend (default)

**Methods:**

#### `record_action(action: str, context: dict)`
Record user action with context.

```python
sense.record_action("call", {
    "target": "mama",
    "intent": "family_chat",
    "location": "home",
    "result": "success"
})
```

#### `get_pattern(action: str) -> dict`
Get behavior pattern for action.

```python
pattern = sense.get_pattern("call")
# → {"count": 45, "common_hours": [(9, 23), (14, 12)], ...}
```

#### `suggest_actions(limit: int = 3) -> list`
Get smart suggestions based on current time.

```python
suggestions = sense.suggest_actions(limit=3)
# → [{"action": "call", "target": "mama", "confidence": 0.85}, ...]
```

#### `detect_situation() -> dict`
Detect current user situation.

```python
situation = sense.detect_situation()
# → {"time_of_day": "morning", "typical_activity": "call", ...}
```

#### `export_data() -> dict`
GDPR: Export all user data.

```python
data = sense.export_data()
# Save to JSON file for user
```

#### `delete_data()`
GDPR: Delete all user data (right to be forgotten).

```python
sense.delete_data()
```

---

## 🔒 Privacy & GDPR

**Default: Privacy Mode ON** - Alles blijft lokaal!

**MUST HAVE in app settings:**
1. ✅ "Export my data" button → `sense.export_data()`
2. ✅ "Delete my data" button → `sense.delete_data()`
3. ✅ "Sync to cloud" toggle (opt-in!)
4. ✅ "Show what you know" → `sense.get_all_patterns()`

**Storage Location:** `~/.humotica/sense/{user_id}_stats.json`

**What's Stored:**
- Action history (last 1000 per type)
- Patterns (hours, days, targets)
- Statistics (counts, confidence scores)

**What's NOT Stored:**
- Exact GPS coordinates (only categories: home/work/travel)
- Message content (only that you sent a message)
- Call recordings (only that you called someone)

---

## 🐛 Troubleshooting

### "No patterns detected"
```python
# Need at least 5 actions:
stats = sense.get_stats_summary()
print(f"Total actions: {stats['total_actions']}")  # Should be >5
```

### "Patterns not saving"
```bash
# Check storage permissions:
ls -la ~/.humotica/sense/
# Should have {user_id}_stats.json
```

### "ImportError: No module named tibet_betti_client"
```bash
# Reinstall SDK:
cd Backend-server-JTel/client-sdk/python
pip install -e .
```

---

## 📚 Complete Documentation

- `SENSE_INTEGRATION_GUIDE.md` - Full guide (in brain_api/)
- `SENSE_APP_INTEGRATION.md` - App developer guide (in brain_api/)
- `examples/sense_app_example.py` - Complete working example (in brain_api/)

---

## ✅ Checklist for App Integration

- [ ] SDK installed (`pip install -e .`)
- [ ] ClientSense initialized (`sense = ClientSense(user_id)`)
- [ ] All actions recorded (`record_action()` everywhere!)
- [ ] Suggestions shown on home screen
- [ ] Privacy controls in settings (export/delete/show)
- [ ] Context sent to Kit for smart responses
- [ ] Tested with real usage (5+ actions)

---

## 🎯 What Does Sense 2.0 Do?

**ZONDER Sense:**
```
User: "Bel"
App: "Wie wil je bellen?"
User: "Mama"
```

**MET Sense:**
```
User: "Bel"
App: "Bel mama? (Je belt haar vaak om deze tijd - 85% zeker)"
User: *tikt eens* → gebeld!
```

**3x sneller, 10x slimmer! 🚀**

---

**Need Help?** Check complete docs in `brain_api/SENSE_INTEGRATION_GUIDE.md`!
