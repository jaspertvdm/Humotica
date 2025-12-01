# DABS Wetstructuur - 14 Natuurwetten

**DABS = Device → Agent → Brain → Security Layer**

```
Device    = Hardware (router, phone, IoT, laptop)
Agent     = Software interface (app, script, service, daemon, API client)
Brain     = Centrale intelligentie (Brain API, Resource Planner)
Security  = BETTI Security Layer (SNAFT, BALANS, 14 Wetten)
```

## Overzicht

Elke intent doorloopt het DABS systeem en krijgt resource allocatie
gebaseerd op 14 natuurkundige wetten. Dit is geen simulatie - dit zijn
ECHTE beslissingen die het systeem beïnvloeden.

## De 14 Wetten

### Categorie 1: BLOCKING (Kunnen request afwijzen)

| # | Wet | Formule | Threshold | Actie |
|---|-----|---------|-----------|-------|
| 2 | Newton | F = Gm₁m₂/r² | trust < 0.3 | **BLOCK** |
| 4 | Thermodynamics | S = k ln(Ω) | health = CRITICAL | **BLOCK** |
| 12 | Heisenberg | ΔxΔp ≥ ℏ/2 | latency×throughput > 0.7 | **BLOCK** |

### Categorie 2: DELAY (Voegen wachttijd toe)

| # | Wet | Formule | Wanneer | Effect |
|---|-----|---------|---------|--------|
| 1 | Kepler | T² = a³/10 | interval > 1000ms | await sleep(ms/100) |
| 9 | Wave | v = fλ | devices > 1 | await sleep(propagation_ms) |

### Categorie 3: SIGNAL (Doorgeven aan downstream)

| # | Wet | Formule | Output | Context key |
|---|-----|---------|--------|-------------|
| 6 | Archimedes | Fb = ρVg | queue_priority 1-10 | `_archimedes_queue` |
| 7 | Ohm | I = V/R | flow_rate_kbps | `_ohm_rate_limit` |
| 8 | Hooke | F = -kx | SCALE_UP/DOWN/STABLE | `_hooke_scale_signal` |
| 10 | Doppler | f' = f(v+vr)/(v+vs) | timeout_ms | `_doppler_timeout_ms` |
| 13 | Maxwell | \|F\| = √(E²+B²) | field_strength | `_maxwell_field` |

### Categorie 4: ACTIEF (Direct toegepast)

| # | Wet | Formule | Effect |
|---|-----|---------|--------|
| 3 | Einstein | E = mc² | cpu_percent boost |
| 5 | Conservation | E_in = E_out | chain_hash tracking |
| 11 | Planck | E = nhf | memory in 32MB quanta |
| 14 | Betti | χ = αB₀+βB₁+γB₂+δB₃ | split_required decision |

---

## Berekeningen per Wet

### WET 1: KEPLER - Orbital Scheduling

```
Concept: Taken draaien in "orbits" rond de processor
         Hoge prioriteit = kleine orbit = sneller aan de beurt

Formule: T² = a³/10
         a = 10 - urgency
         interval_ms = √T² × 1000

Voorbeeld (urgency=8):
  a = 10 - 8 = 2
  T² = 2³/10 = 0.8
  interval = √0.8 × 1000 = 894ms

Effect: Lage urgency taken moeten langer wachten
```

### WET 2: NEWTON - Gravitational Trust

```
Concept: Trust tussen entities trekt aan zoals massa's
         Lage trust = zwakke binding = geen toegang

Formule: F = G × m₁ × m₂ / r²
         G = 0.1 (trust gravity constant)
         m = trust_score per participant

Threshold: average_trust < 0.3 → BLOCKED

Voorbeeld:
  participants: [alice: 0.8, bob: 0.9]
  F = 0.1 × 0.8 × 0.9 / 1 = 0.072
  avg = 0.85 ✓ OK
```

### WET 3: EINSTEIN - Energy-Mass Equivalence

```
Concept: Data heeft "massa", verwerking kost "energie"
         Meer data = meer CPU nodig

Formule: E = m × c² × 0.001
         m = data_kb × operations
         c = 1000 (computing speed of light)
         cpu_boost = E / 100000

Voorbeeld (100KB, 2 ops):
  m = 100 × 2 = 200
  E = 200 × 1000² × 0.001 = 200,000
  cpu_boost = 200000 / 100000 = 2%
```

### WET 4: THERMODYNAMICS - System Entropy

```
Concept: Complexiteit verhoogt "wanorde" (entropy)
         Te veel entropy = systeem crasht

Formule: S = k × ln(Ω) × 1000
         k = 0.01 (Boltzmann constant)
         Ω = operations × devices + 1
         health = 100 - S

Thresholds:
  health < 30 → CRITICAL (BLOCK)
  health < 60 → WARNING (log)
  health ≥ 60 → OK
```

### WET 5: CONSERVATION - Energy Conservation

```
Concept: Resources moeten getracked worden
         Wat erin gaat moet eruit komen

Formule: E_in = E_out
         Chain: GENESIS → hash1 → hash2 → ...

Effect: Detecteert resource leaks
        Verificatie via HMAC chain
```

### WET 6: ARCHIMEDES - Buoyancy Priority

```
Concept: Lichte+urgente taken "drijven" omhoog
         Zware+niet-urgente taken zinken

Formule: density = mass / urgency
         buoyancy = 10 / density
         queue_position = 11 - buoyancy (1-10)
         estimated_wait = position × 50ms

Voorbeeld (mass=200, urgency=8):
  density = 200 / 8 = 25
  buoyancy = 10 / 25 = 0.4
  position = 11 - 0.4 = 10 (laag!)
```

### WET 7: OHM - Flow Control

```
Concept: Netwerk heeft "weerstand"
         Hoge weerstand = lagere doorvoer

Formule: I = V / R
         V = urgency × 10 (voltage)
         R = network_resistance (0.1-10)
         flow_rate = I × 1000 (kbps)

Voorbeeld (urgency=8, resistance=1.5):
  V = 8 × 10 = 80
  I = 80 / 1.5 = 53.3
  flow = 53,333 kbps
```

### WET 8: HOOKE - Elastic Scaling

```
Concept: Systeem is een "veer"
         Te veel spanning = moet opschalen

Formule: F = -k × (load - baseline)
         k = 0.5
         baseline = 50%

Actions:
  F < -15 (load > 80%) → SCALE_UP
  F > 15  (load < 20%) → SCALE_DOWN
  else → STABLE
```

### WET 9: WAVE - Signal Propagation

```
Concept: Signalen hebben tijd nodig om te reizen
         Meer devices = meer sync tijd

Formule: speed = frequency × wavelength
         λ = trust × 10
         delay = (devices / speed) × 100 ms

Voorbeeld (4 devices, trust=0.8):
  λ = 0.8 × 10 = 8
  speed = 10 × 8 = 80
  delay = (4 / 80) × 100 = 5ms
```

### WET 10: DOPPLER - Adaptive Timeout

```
Concept: Urgente taken "naderen snel"
         Timeout past zich aan

Formule: doppler = (1 + v_receiver) / (1 + v_source)
         v_source = (10 - urgency) / 10
         v_receiver = urgency / 10
         timeout = base_timeout / doppler

Voorbeeld (urgency=8, base=30s):
  vs = (10-8)/10 = 0.2
  vr = 8/10 = 0.8
  doppler = 1.8/1.2 = 1.5
  timeout = 30000/1.5 = 20000ms
```

### WET 11: PLANCK - Quantum Memory

```
Concept: Memory komt in vaste "quanta"
         Voorkomt fragmentatie

Formule: quanta = ceil(requested / 32)
         allocated = quanta × 32 MB

Voorbeeld (150MB requested):
  quanta = ceil(150/32) = 5
  allocated = 5 × 32 = 160MB
  overhead = 10MB
```

### WET 12: HEISENBERG - Uncertainty Trade-off

```
Concept: Kan niet alles tegelijk optimaliseren
         Latency vs Throughput

Formule: latency × throughput ≤ 0.7

Check: product > 0.7 → BLOCKED
       "Reduce requirements or split task"
```

### WET 13: MAXWELL - Field Coordination

```
Concept: Trust en flow creëren "veld"
         Sterker veld = betere coördinatie

Formule: strength = √(E² + B²)
         E = trust_force
         B = flow_rate × 10

Effect: coordination_priority = int(strength × 10)
```

### WET 14: BETTI - Topological Complexity

```
Concept: Complexiteit gemeten via Betti numbers
         Te complex = moet splitsen

Formule: χ = 3×B₀ + 2×B₁ + 1.5×B₂ + 1×B₃
         B₀ = humans (participants)
         B₁ = devices
         B₂ = operations
         B₃ = steps

Threshold: χ > 50 → split_required = true
           sub_tasks = min(5, ceil(χ/50))
```

---

## DABS Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              DEVICE                                      │
│  (Router, Phone, IoT, Laptop, Server)                                   │
│                                                                          │
│  Intent: "video_call alice urgency=8 devices=[phone,laptop]"            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                               AGENT                                      │
│  (App, Script, Service, Daemon, API Client)                             │
│                                                                          │
│  POST /betti/intent/execute                                             │
│  {                                                                       │
│    "user_id": "alice_hid",                                              │
│    "intent": "video_call",                                              │
│    "context": {"urgency": 8, "devices": ["phone", "laptop"]}            │
│  }                                                                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                               BRAIN                                      │
│  (Brain API + Resource Planner)                                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ STEP 1: SNAFT Check                                              │   │
│  │ STEP 2: Complexity Analysis (B0-B5)                              │   │
│  │ STEP 3: BALANS Decision                                          │   │
│  │ STEP 3b: RESOURCE PLANNER (14 WETTEN) ←──────────────────────────│───│
│  │ STEP 3c: ENFORCE                                                 │   │
│  │ STEP 4: Execute or Return                                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYER                                  │
│  (BETTI Framework)                                                       │
│                                                                          │
│  ✓ Newton trust verified                                                │
│  ✓ Thermodynamics health OK                                             │
│  ✓ Heisenberg tradeoff valid                                            │
│  ✓ All 14 laws enforced                                                 │
│                                                                          │
│  Response:                                                               │
│  {                                                                       │
│    "status": "executed",                                                │
│    "resource_allocation": {...},                                        │
│    "enforcements": {...}                                                │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Gebruik

### Python (Direct)

```python
from resource_planner import plan_resources

allocation = plan_resources(
    task_type="video_call",
    urgency=8,
    participants=["alice", "bob"],
    devices=["phone", "laptop"],
    data_size_kb=100
)

print(f"Memory: {allocation.memory_mb}MB")
print(f"Timeout: {allocation.timeout_ms}ms")
print(f"Queue: {allocation.queue_priority}/10")
print(f"Split: {allocation.split_required}")
```

### API

```bash
# Quick planning
curl "http://localhost:8010/planner/plan/quick?task_type=video_call&urgency=8&participants=2&devices=2"

# Full planning
curl -X POST "http://localhost:8010/planner/plan" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"video_call","urgency":8,"participants":["alice","bob"]}'
```

---

## Author

Jasper van de Meent
License: JOSL (JTel Open Source License)
