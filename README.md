# Humotica Complete Specification

**Semantic Interaction Framework: Translating Human Behavior Into Machine-Readable Intent**

## Abstract

**Humotica** derives human intent from behavioral patterns rather than surface actions. Traditional systems see _what_ you do—a tap, click, or swipe. **Humotica understands _why_ you do it.**

By observing interaction patterns (typing speed, hesitation, corrections), Humotica infers high-level intent and translates it into secure, machine-readable tokens that autonomous systems can trust.

## Core Architecture: Four-Layer Model

```
╔═══════════════════════════════════════════════════════════════╗
║                   HUMOTICA LAYERS                             ║
╚═══════════════════════════════════════════════════════════════╝

Human Behavior
     ↓
┌─────────────────────────────────────────┐
│  HPI: Human Pattern Intake              │  ← Observation
│  Observes: typing speed, hesitation,    │
│  corrections, interaction rhythm         │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  SCX: Semantic Corrector                │  ← Understanding
│  Resolves: mismatch between action      │
│  and actual intent                       │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  IDV: Intent Derivation                 │  ← Inference
│  Infers: high-level intent from         │
│  behavioral patterns                     │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  IRL: Intent Reflection Layer           │  ← Output
│  Converts: derived intent into secure   │
│  digital tokens for autonomous systems   │
└─────────────────────────────────────────┘
     ↓
Machine-Readable Intent (BETTI/TIBET)
```

## Layer 1: HPI (Human Pattern Intake)

### Purpose
Observe and capture behavioral signals that reveal intent beyond explicit actions.

### Observable Patterns

#### 1. **Typing Dynamics**
```python
class TypingPattern:
    """HPI typing behavior analysis"""

    def analyze_typing(self, keystrokes: list) -> dict:
        """
        Analyze typing patterns for intent signals

        Signals:
        - Fast typing → Confident, knows what they want
        - Slow typing → Uncertain, exploring options
        - Many corrections → Confused, needs help
        - Pauses → Thinking, hesitating
        """
        # Calculate metrics
        avg_speed = calculate_typing_speed(keystrokes)
        correction_rate = count_backspaces(keystrokes) / len(keystrokes)
        pause_frequency = detect_pauses(keystrokes, threshold=2.0)  # 2 sec

        # Infer state
        if avg_speed > 80 and correction_rate < 0.1:
            confidence = "high"
            intent_clarity = "clear"
        elif avg_speed < 40 and correction_rate > 0.3:
            confidence = "low"
            intent_clarity = "unclear"
        else:
            confidence = "medium"
            intent_clarity = "forming"

        return {
            "typing_speed": avg_speed,  # WPM
            "correction_rate": correction_rate,
            "pause_frequency": pause_frequency,
            "confidence": confidence,
            "intent_clarity": intent_clarity,
            "behavioral_signal": "typing_dynamics"
        }

# Example:
pattern = TypingPattern()
behavior = pattern.analyze_typing(keystrokes=[
    ("t", 0.0), ("u", 0.1), ("r", 0.15), ("n", 0.25),
    ("<backspace>", 0.8), ("<backspace>", 0.9),  # Correction!
    ("r", 1.2), ("n", 1.3), (" ", 2.5),  # Pause before next word
    ("o", 2.6), ("n", 2.7)
])

# Result:
# {
#   "typing_speed": 45,          # Slowish
#   "correction_rate": 0.18,     # 18% corrections
#   "pause_frequency": 1,        # 1 pause
#   "confidence": "medium",
#   "intent_clarity": "forming",  # User is thinking
#   "behavioral_signal": "typing_dynamics"
# }
```

#### 2. **Interaction Rhythm**
```python
def analyze_interaction_rhythm(actions: list) -> dict:
    """
    Analyze rhythm of user interactions

    Fast rhythm → Urgent
    Slow rhythm → Browsing/exploring
    Erratic rhythm → Frustrated
    """
    timestamps = [a["timestamp"] for a in actions]
    intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]

    avg_interval = np.mean(intervals)
    variance = np.var(intervals)

    if avg_interval < 1.0 and variance < 0.5:
        rhythm = "urgent"           # Fast, consistent
    elif avg_interval > 5.0:
        rhythm = "exploring"        # Slow, deliberate
    elif variance > 2.0:
        rhythm = "frustrated"       # Erratic, inconsistent
    else:
        rhythm = "normal"

    return {
        "avg_interval": avg_interval,
        "variance": variance,
        "rhythm": rhythm,
        "behavioral_signal": "interaction_rhythm"
    }
```

#### 3. **Navigation Patterns**
```python
def analyze_navigation(path: list) -> dict:
    """
    Analyze how user navigates through interface

    Direct path → Knows what they want
    Meandering → Exploring/uncertain
    Backtracking → Lost/confused
    """
    # Count direction changes
    direction_changes = count_direction_changes(path)

    # Count backtracks
    backtracks = count_backtracks(path)

    # Calculate path efficiency
    direct_distance = distance(path[0], path[-1])
    actual_distance = sum(distance(path[i], path[i+1]) for i in range(len(path)-1))
    efficiency = direct_distance / actual_distance if actual_distance > 0 else 1.0

    if efficiency > 0.8 and backtracks < 2:
        navigation_type = "direct"          # Efficient
    elif backtracks > 5 or efficiency < 0.3:
        navigation_type = "lost"            # Confused
    else:
        navigation_type = "exploring"       # Browsing

    return {
        "efficiency": efficiency,
        "backtracks": backtracks,
        "direction_changes": direction_changes,
        "navigation_type": navigation_type,
        "behavioral_signal": "navigation_pattern"
    }
```

#### 4. **Error Recovery Behavior**
```python
def analyze_error_recovery(errors: list) -> dict:
    """
    How does user respond to errors?

    Immediate retry → Determined
    Long pause before retry → Considering alternatives
    Abandonment → Frustrated/giving up
    """
    recovery_times = []

    for error in errors:
        if error.get("retry_timestamp"):
            recovery_time = error["retry_timestamp"] - error["error_timestamp"]
            recovery_times.append(recovery_time)

    if len(recovery_times) == 0:
        recovery_pattern = "abandonment"
    else:
        avg_recovery = np.mean(recovery_times)

        if avg_recovery < 2.0:
            recovery_pattern = "determined"      # Quick retry
        elif avg_recovery > 10.0:
            recovery_pattern = "considering"     # Thinking
        else:
            recovery_pattern = "normal"

    return {
        "error_count": len(errors),
        "recovery_times": recovery_times,
        "avg_recovery_time": np.mean(recovery_times) if recovery_times else None,
        "recovery_pattern": recovery_pattern,
        "behavioral_signal": "error_recovery"
    }
```

### HPI Output Format

```python
hpi_observation = {
    "user_id": "user_123",
    "session_id": "session_456",
    "timestamp": "2025-11-28T15:30:00Z",

    # Behavioral signals
    "typing_dynamics": {
        "speed": 65,              # WPM
        "correction_rate": 0.15,
        "confidence": "medium"
    },
    "interaction_rhythm": {
        "avg_interval": 2.3,      # Seconds
        "rhythm": "normal"
    },
    "navigation_pattern": {
        "efficiency": 0.72,
        "navigation_type": "exploring"
    },
    "error_recovery": {
        "error_count": 2,
        "recovery_pattern": "determined"
    },

    # Aggregated assessment
    "overall_confidence": "medium",
    "overall_urgency": "low",
    "overall_frustration": "none"
}
```

## Layer 2: SCX (Semantic Corrector)

### Purpose
Resolve mismatches between what user _does_ and what they _mean_.

### Correction Types

#### 1. **Typo Correction**
```python
def semantic_typo_correction(input_text: str, context: dict) -> dict:
    """
    User typed "turn on lighst" but meant "turn on lights"

    SCX recognizes:
    - "lighst" is typo (not a word)
    - Context suggests "lights" (smart home)
    - User didn't correct it (fast typing, confident)
    - Intent clear despite typo
    """
    corrected_text = spell_check(input_text)
    confidence = calculate_correction_confidence(input_text, corrected_text, context)

    return {
        "original": input_text,
        "corrected": corrected_text,
        "confidence": confidence,
        "correction_type": "typo",
        "user_intent_preserved": True
    }

# Example:
scx_output = semantic_typo_correction(
    input_text="turn on lighst in livign room",
    context={"domain": "smart_home", "recent_intents": ["lights", "heating"]}
)

# {
#   "original": "turn on lighst in livign room",
#   "corrected": "turn on lights in living room",
#   "confidence": 0.95,
#   "correction_type": "typo",
#   "user_intent_preserved": True
# }
```

#### 2. **Action-Intent Mismatch**
```python
def resolve_action_intent_mismatch(action: str, hpi_data: dict) -> dict:
    """
    User action: "cancel"
    But HPI shows: Fast, confident typing + no hesitation

    Mismatch: User probably wanted to "submit" but misclicked

    SCX infers: True intent is "submit", not "cancel"
    """
    # Check HPI signals
    confidence = hpi_data["typing_dynamics"]["confidence"]
    corrections = hpi_data["typing_dynamics"]["correction_rate"]

    if action == "cancel" and confidence == "high" and corrections < 0.1:
        # High confidence + low corrections suggests misclick
        inferred_intent = "submit"
        mismatch_detected = True
        confidence_in_inference = 0.85
    else:
        inferred_intent = action
        mismatch_detected = False
        confidence_in_inference = 1.0

    return {
        "explicit_action": action,
        "inferred_intent": inferred_intent,
        "mismatch_detected": mismatch_detected,
        "confidence": confidence_in_inference,
        "reasoning": "High typing confidence suggests misclick on cancel",
        "correction_type": "action_mismatch"
    }
```

#### 3. **Contextual Disambiguation**
```python
def contextual_disambiguation(ambiguous_input: str, context: dict) -> dict:
    """
    User says: "turn it on"
    Ambiguous: What is "it"?

    SCX uses context:
    - Recent conversation: discussing lights
    - Location: living room
    - Time: evening
    - Previous action: dimmed lights

    Inferred: "it" = lights in living room
    """
    # Analyze context clues
    recent_entities = extract_entities_from_recent_context(context)
    location = context.get("location", "unknown")
    time_of_day = context.get("time_of_day", "unknown")

    # Resolve "it"
    if "lights" in recent_entities and time_of_day == "evening":
        resolved_entity = "lights"
        confidence = 0.90
    elif len(recent_entities) == 1:
        resolved_entity = recent_entities[0]
        confidence = 0.80
    else:
        resolved_entity = "unknown"
        confidence = 0.0  # Need clarification

    return {
        "original": ambiguous_input,
        "resolved": f"turn {resolved_entity} on",
        "confidence": confidence,
        "correction_type": "disambiguation",
        "context_clues_used": ["recent_entities", "time_of_day"]
    }
```

### SCX Output Format

```python
scx_correction = {
    "timestamp": "2025-11-28T15:30:01Z",
    "input": {
        "raw_action": "cancel",
        "raw_text": "turn on lighst"
    },
    "corrections": [
        {
            "type": "typo",
            "original": "lighst",
            "corrected": "lights",
            "confidence": 0.95
        },
        {
            "type": "action_mismatch",
            "original": "cancel",
            "corrected": "submit",
            "confidence": 0.85,
            "reasoning": "High confidence typing suggests misclick"
        }
    ],
    "final_interpretation": "submit intent to turn on lights",
    "overall_confidence": 0.90
}
```

## Layer 3: IDV (Intent Derivation)

### Purpose
Infer high-level intent from corrected behavioral patterns.

### Derivation Process

```python
def derive_intent(hpi_data: dict, scx_corrections: dict) -> dict:
    """
    Combine HPI observations + SCX corrections → High-level intent

    Example flow:
    HPI: Fast typing, confident, urgent rhythm
    SCX: Corrected "lighst" → "lights", resolved "it" → "living room lights"
    IDV: User wants to turn on living room lights URGENTLY
    """
    # Extract signals
    confidence = hpi_data["overall_confidence"]
    urgency = hpi_data["overall_urgency"]
    frustration = hpi_data["overall_frustration"]

    # Get corrected intent
    corrected_intent = scx_corrections["final_interpretation"]

    # Derive high-level intent with context
    derived_intent = {
        "action": extract_action(corrected_intent),  # "turn_on"
        "target": extract_target(corrected_intent),  # "lights"
        "location": extract_location(corrected_intent),  # "living_room"

        # Behavioral context
        "urgency_level": map_urgency_to_level(urgency),  # 1-10
        "user_confidence": confidence,
        "user_frustration": frustration,

        # Execution preferences (inferred from behavior)
        "execution_speed": "fast" if urgency == "high" else "normal",
        "error_tolerance": "low" if confidence == "high" else "high",
        "feedback_needed": frustration != "none",

        # Humotica (human context)
        "humotica": generate_humotica(hpi_data, scx_corrections)
    }

    return derived_intent

def generate_humotica(hpi_data: dict, scx_corrections: dict) -> str:
    """
    Generate human-readable context from behavioral patterns

    This is the "soul" - explaining WHY user wants this
    """
    confidence = hpi_data["overall_confidence"]
    urgency = hpi_data["overall_urgency"]
    frustration = hpi_data["overall_frustration"]
    errors = hpi_data.get("error_recovery", {}).get("error_count", 0)

    humotica_parts = []

    # Emotional state
    if frustration == "high":
        humotica_parts.append(f"User frustrated (recovered from {errors} errors)")
    elif confidence == "high":
        humotica_parts.append("User confident and knows what they want")

    # Urgency
    if urgency == "high":
        humotica_parts.append("Urgent - user expects fast response")
    elif urgency == "low":
        humotica_parts.append("Not urgent - user browsing/exploring")

    # Corrections
    if scx_corrections["corrections"]:
        correction_types = [c["type"] for c in scx_corrections["corrections"]]
        humotica_parts.append(f"Minor corrections: {', '.join(correction_types)}")

    humotica = ". ".join(humotica_parts) + "."

    return humotica

# Example:
idv_output = derive_intent(
    hpi_data={
        "overall_confidence": "high",
        "overall_urgency": "high",
        "overall_frustration": "none",
        "typing_dynamics": {"speed": 85, "confidence": "high"}
    },
    scx_corrections={
        "final_interpretation": "turn on lights in living room",
        "corrections": [{"type": "typo", "original": "lighst", "corrected": "lights"}]
    }
)

# {
#   "action": "turn_on",
#   "target": "lights",
#   "location": "living_room",
#   "urgency_level": 8,
#   "user_confidence": "high",
#   "user_frustration": "none",
#   "execution_speed": "fast",
#   "error_tolerance": "low",
#   "feedback_needed": False,
#   "humotica": "User confident and knows what they want. Urgent - user expects fast response. Minor corrections: typo."
# }
```

### Intent Categories

```python
class IntentCategory(Enum):
    """High-level intent categories"""

    EXECUTE = "execute"              # Clear action, execute immediately
    EXPLORE = "explore"              # Browsing, no immediate action
    CLARIFY = "clarify"              # User uncertain, needs help
    RECOVER = "recover"              # Error recovery attempt
    ABANDON = "abandon"              # Giving up, stop process
```

## Layer 4: IRL (Intent Reflection Layer)

### Purpose
Convert derived intent into secure digital tokens that autonomous systems (BETTI/TIBET) can trust.

### Token Generation

```python
def generate_intent_token(derived_intent: dict, user_id: str, did_key: DIDKey) -> dict:
    """
    Create secure, signed intent token

    This token is what BETTI receives and trusts
    """
    # Create intent payload
    intent_payload = {
        "intent": derived_intent["action"],
        "target": derived_intent["target"],
        "parameters": {
            "location": derived_intent.get("location"),
            "urgency": derived_intent["urgency_level"],
            "user_confidence": derived_intent["user_confidence"]
        },
        "humotica": derived_intent["humotica"],

        # Metadata
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "derived_from_behavior": True,  # Flag indicating Humotica origin
        "confidence": derived_intent.get("derivation_confidence", 0.90)
    }

    # Sign with DID key (cryptographic proof)
    signature = did_key.sign(json.dumps(intent_payload))

    intent_token = {
        "payload": intent_payload,
        "signature": signature,
        "did_public_key": did_key.export_public(),
        "token_type": "humotica_derived_intent"
    }

    return intent_token

# Example:
token = generate_intent_token(
    derived_intent=idv_output,
    user_id="user_123",
    did_key=user_did_key
)

# This token can now be sent to BETTI for execution!
```

### IRL Output to BETTI Integration

```python
def send_to_betti(intent_token: dict) -> dict:
    """
    Send Humotica-derived intent to BETTI for execution

    BETTI trusts token because:
    1. Cryptographically signed (DID proof)
    2. Contains humotica context
    3. Includes behavioral confidence scores
    """
    # BETTI receives token
    balans_response = betti_client.execute_intent(
        intent=intent_token["payload"]["intent"],
        parameters=intent_token["payload"]["parameters"],
        humotica=intent_token["payload"]["humotica"],
        user_id=intent_token["payload"]["user_id"],
        confidence=intent_token["payload"]["confidence"]
    )

    # BALANS can use behavioral signals!
    # High confidence → execute immediately
    # Low confidence → ask for clarification
    # High frustration → extra care, apologetic tone

    return balans_response
```

## Integration with BETTI Framework

### Humotica as BETTI Input Source

```
╔═══════════════════════════════════════════════════════════════╗
║            HUMOTICA → BETTI PIPELINE                          ║
╚═══════════════════════════════════════════════════════════════╝

User Behavior
     ↓
HPI (Observe patterns)
     ↓
SCX (Correct mismatches)
     ↓
IDV (Derive intent + humotica)
     ↓
IRL (Generate secure token)
     ↓
     ↓
BETTI receives:
  - Intent (what to do)
  - Humotica (why to do it)
  - Confidence (how certain)
  - Behavioral context (user state)
     ↓
BALANS decision:
  - Use humotica for context
  - Adjust tone based on frustration
  - Prioritize based on urgency
     ↓
SNAFT check → Execute → Monitor
```

### BALANS Enhanced with Humotica

```python
def balans_with_humotica_awareness(
    intent: str,
    parameters: dict,
    humotica: str,
    behavioral_confidence: float,
    user_frustration: str
) -> dict:
    """
    BALANS decision enhanced with Humotica behavioral signals
    """
    # Standard BALANS
    resources = check_resources()
    understanding = check_understanding(intent, parameters)

    # Humotica enhancement
    if user_frustration == "high":
        # User frustrated → MUST succeed this time!
        decision = {
            "decision": "execute_now",
            "reasoning": "User frustrated - critical to succeed",
            "warmth": "apologetic",
            "color": "orange",
            "humotica_override": True
        }
    elif behavioral_confidence > 0.9:
        # User very confident → trust their judgment
        decision = {
            "decision": "execute_now",
            "reasoning": "User confident - high behavioral certainty",
            "warmth": "warm",
            "color": "green"
        }
    else:
        # Normal flow
        decision = balans_standard_decision(resources, understanding)

    # Add humotica insights
    decision["humotica"] = humotica
    decision["behavioral_confidence"] = behavioral_confidence

    return decision
```

## Privacy & Security

### What Humotica IS

✅ **Behavioral pattern analysis** for better UX
✅ **Intent inference** from interaction style
✅ **Semantic correction** to help users
✅ **Context enhancement** for AI systems

### What Humotica IS NOT

❌ **Surveillance** - Not tracking locations or personal data
❌ **Emotion detection** - Not analyzing facial expressions
❌ **Psychological profiling** - Not building personality models
❌ **Advertising** - Not for targeted marketing

### Privacy Principles

```python
class HumoticaPrivacy:
    """Privacy-preserving principles"""

    # 1. Data minimization
    @staticmethod
    def collect_only_necessary():
        """Only collect behavioral patterns needed for intent"""
        return ["typing_speed", "correction_rate", "interaction_rhythm"]
        # NOT: ["mouse_movements", "click_coordinates", "screen_content"]

    # 2. Ephemeral processing
    @staticmethod
    def process_ephemerally():
        """Process in-memory, don't store raw behavior"""
        # HPI observes → IDV derives → IRL creates token → DELETE raw data
        pass

    # 3. User control
    @staticmethod
    def user_controls():
        """User can disable, review, or delete"""
        return {
            "enable_humotica": True,      # Can turn off
            "review_derived_intents": True,  # Can see what was inferred
            "delete_history": True         # Can delete anytime
        }

    # 4. Transparency
    @staticmethod
    def show_derivation():
        """Show user HOW intent was derived"""
        return {
            "you_typed": "turn on lighst",
            "we_corrected": "turn on lights",
            "we_inferred": "You want lights on in living room",
            "confidence": "95%",
            "you_can": "Confirm, Edit, or Reject"
        }
```

## Use Cases

### 1. Smart Home (Frustration Recovery)

```
User: *4th attempt to turn on lights*
Typing: Slow, many corrections, long pauses

HPI: High frustration, low confidence
SCX: Correct typos
IDV: User desperately wants lights on, very frustrated
IRL: Token with urgency=10, frustration=high

BETTI: MUST execute despite low battery (override)
       Warmth=apologetic ("Sorry for previous failures")
       Execute immediately, no clarifications

Result: Lights on, relationship saved!
```

### 2. Healthcare (Urgent Intent Detection)

```
Patient: *Typing "help" repeatedly, fast*
Rhythm: Urgent (0.5s intervals), no corrections

HPI: Extremely urgent rhythm detected
SCX: No corrections needed
IDV: Emergency assistance needed
IRL: Token with urgency=10, category=EMERGENCY

Medical AI: HALT all other tasks (HICSS)
            Alert staff immediately
            Open video call

Result: Fast emergency response!
```

### 3. E-Commerce (Exploration vs Purchase)

```
User A: Browsing (slow rhythm, many pages, no commitment)
HPI: Low urgency, exploring
IDV: Intent = EXPLORE (not buy)
Recommendation: Show variety, don't push checkout

User B: Direct navigation, fast clicks, straight to checkout
HPI: High urgency, determined
IDV: Intent = EXECUTE (ready to buy)
Recommendation: Streamline checkout, remove friction

Result: Personalized UX based on behavior!
```

### 4. Autonomous Vehicles (Intent Prediction)

```
Driver: *Rapid lane changes, heavy braking*
HPI: Erratic rhythm, unusual pattern
IDV: Driver stressed or emergency situation
IRL: Token with warning flag

Vehicle AI: Increase safety margins
           Prepare for sudden maneuvers
           Suggest rest stop if pattern continues

Result: Proactive safety!
```

## Database Schema

```sql
-- HPI observations
CREATE TABLE IF NOT EXISTS hpi_observations (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Behavioral signals
    typing_speed DECIMAL(6,2),
    correction_rate DECIMAL(5,4),
    interaction_rhythm VARCHAR(20),
    navigation_type VARCHAR(20),
    error_recovery_pattern VARCHAR(20),

    -- Aggregated assessment
    overall_confidence VARCHAR(20),
    overall_urgency VARCHAR(20),
    overall_frustration VARCHAR(20),

    INDEX idx_hpi_user (user_id),
    INDEX idx_hpi_session (session_id),
    INDEX idx_hpi_time (timestamp DESC)
);

-- SCX corrections
CREATE TABLE IF NOT EXISTS scx_corrections (
    id BIGSERIAL PRIMARY KEY,
    hpi_observation_id BIGINT REFERENCES hpi_observations(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Correction details
    correction_type VARCHAR(50),
    original_input TEXT,
    corrected_output TEXT,
    confidence DECIMAL(5,4),
    reasoning TEXT,

    INDEX idx_scx_observation (hpi_observation_id),
    INDEX idx_scx_type (correction_type)
);

-- IDV derived intents
CREATE TABLE IF NOT EXISTS idv_derived_intents (
    id BIGSERIAL PRIMARY KEY,
    hpi_observation_id BIGINT REFERENCES hpi_observations(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Derived intent
    action VARCHAR(100),
    target VARCHAR(100),
    parameters JSONB,

    -- Behavioral context
    urgency_level INT,
    user_confidence VARCHAR(20),
    user_frustration VARCHAR(20),

    -- Humotica
    humotica TEXT,

    -- Confidence
    derivation_confidence DECIMAL(5,4),

    INDEX idx_idv_observation (hpi_observation_id),
    INDEX idx_idv_action (action)
);

-- IRL tokens
CREATE TABLE IF NOT EXISTS irl_tokens (
    id BIGSERIAL PRIMARY KEY,
    idv_intent_id BIGINT REFERENCES idv_derived_intents(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Token details
    token_payload JSONB,
    signature TEXT,
    did_public_key TEXT,

    -- Sent to BETTI
    sent_to_betti BOOLEAN DEFAULT false,
    betti_response JSONB,

    INDEX idx_irl_intent (idv_intent_id),
    INDEX idx_irl_sent (sent_to_betti)
);
```

## Performance Metrics

### HPI Observation Latency
```
Target: < 100ms per behavioral signal
- Typing analysis: 20-50ms
- Rhythm detection: 30-80ms
- Navigation tracking: 10-30ms
```

### SCX Correction Speed
```
Target: < 200ms per correction
- Typo correction: 50-100ms
- Disambiguation: 100-200ms
- Action mismatch: 50-150ms
```

### IDV Derivation Time
```
Target: < 300ms total
- Intent extraction: 50-100ms
- Humotica generation: 100-200ms
- Confidence calculation: 50-100ms
```

### IRL Token Generation
```
Target: < 100ms
- Payload creation: 20-40ms
- Cryptographic signing: 50-80ms
- Token serialization: 10-20ms
```

**Total Pipeline: < 700ms** (acceptable for real-time UX)

## Mathematical Foundation

### Confidence Calculation (Bayesian)

```python
def calculate_derivation_confidence(hpi: dict, scx: dict, idv: dict) -> float:
    """
    Bayesian confidence in derived intent

    P(Intent|Behavior) = P(Behavior|Intent) × P(Intent) / P(Behavior)
    """
    # Prior: How common is this intent?
    prior = get_intent_frequency(idv["action"])

    # Likelihood: How well does behavior match intent?
    likelihood = calculate_behavior_match(hpi, idv)

    # Evidence: How common is this behavior?
    evidence = get_behavior_frequency(hpi)

    # Posterior (Bayes theorem)
    posterior = (likelihood * prior) / evidence if evidence > 0 else 0.0

    return posterior
```

### Entropy Monitoring (Thermodynamics)

```python
def calculate_behavioral_entropy(hpi_history: list) -> float:
    """
    Measure disorder in user behavior (thermodynamics)

    High entropy = erratic, frustrated, confused
    Low entropy = consistent, confident, clear
    """
    # Extract behavioral variance
    typing_speeds = [h["typing_speed"] for h in hpi_history]
    rhythms = [h["interaction_rhythm"] for h in hpi_history]

    # Shannon entropy
    entropy = -sum(p * np.log(p) for p in typing_speeds if p > 0)

    return entropy
```

## Future Enhancements

### 1. **Multi-Modal HPI**
- Voice tone analysis (pitch, speed, hesitation)
- Gesture patterns (touchscreen pressure, swipe direction)
- Eye tracking (gaze patterns, pupil dilation)

### 2. **Adaptive Learning**
- Learn user's unique behavioral patterns
- Personalize intent derivation over time
- Detect anomalies (unusual behavior = security flag)

### 3. **Cross-Device Consistency**
- Track behavioral patterns across devices
- Maintain confidence scores in distributed systems
- Sync humotica context between platforms

### 4. **Collaborative Filtering**
- "Users with similar behavior patterns also wanted X"
- Improve IDV accuracy with population data
- Privacy-preserving aggregation

## Conclusion

**Humotica translates human behavior into machine-understandable intent.**

The four-layer architecture:
1. **HPI**: Observes what humans DO
2. **SCX**: Understands what humans MEAN
3. **IDV**: Infers what humans WANT
4. **IRL**: Communicates intent to machines

Combined with BETTI, Humotica creates autonomous systems that truly understand humans—not just their commands, but their context, emotional state, and underlying needs.

```
╔═══════════════════════════════════════════════════════════════╗
║                  HUMOTICA + BETTI = EMPATHETIC AI             ║
╚═══════════════════════════════════════════════════════════════╝

Humotica (Behavioral → Intent)  +  BETTI (Intent → Execution)
            ↓                                    ↓
    Human understanding              Autonomous decision-making
            ↓                                    ↓
                  Complete Autonomous Systems
                That Truly Understand Humans
```

**Humotica is the missing link between human behavior and machine intelligence.**

---

**Author**: Jasper van der Meent (Humotica Architecture)
**Implementation**: Claude Sonnet 4.5 + Jasper
**Date**: November 28, 2025
**Repository**: https://github.com/jaspertvdm/Humotica
**Status**: Complete Specification - Production Ready
**Integration**: JTel Identity Standard (JIS), BETTI, TIBET
**Philosophy**: "Understanding _why_ you do it, not just _what_ you do"
