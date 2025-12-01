# BETTI-TIBET Begrippenlijst

**Versie**: 1.0
**Auteur**: Jasper van de Meent
**Licentie**: JOSL

---

## Architectuur

### DABS
**Device → Agent → Brain → Security Layer**

Het 4-laags model voor alle communicatie in het BETTI-TIBET ecosysteem:

| Laag | Component | Voorbeelden |
|------|-----------|-------------|
| **D** - Device | Hardware | Router, Phone, IoT, Laptop, Server |
| **A** - Agent | Software interface | App, Script, Service, Daemon, API Client |
| **B** - Brain | Centrale intelligentie | Brain API, Resource Planner |
| **S** - Security | BETTI Security Layer | SNAFT, BALANS, 14 Wetten |

```
Device sends intent → Agent formats request → Brain processes → Security enforces
```

---

## Frameworks

### BETTI
**Basic Electronic Trust & Transparency Interface**

Framework voor security en resource management gebaseerd op natuurkundige wetten.

### TIBET
**Trust Identity Block Exchange Token**

Protocol voor gedistribueerde identiteit en communicatie.

### JOSL
**JTel Open Source License**

Open source licentie voor JTel projecten.

---

## Security Componenten

### SNAFT
**Sensory Neural Analysis Framework for Trust**

Stap 1 in verwerking: Analyseert input op vertrouwenswaardigheid.

### BALANS
**Behavioral Analysis Layer for Autonomous Network Security**

Stap 3 in verwerking: Maakt beslissing over toestaan/blokkeren.

### 14 Wetten
Natuurkundige wetten die resource allocatie bepalen:

| # | Wet | Functie | Type |
|---|-----|---------|------|
| 1 | Kepler | Scheduling interval | DELAY |
| 2 | Newton | Trust verificatie | BLOCKING |
| 3 | Einstein | CPU boost | ACTIEF |
| 4 | Thermodynamics | System health | BLOCKING |
| 5 | Conservation | Resource tracking | ACTIEF |
| 6 | Archimedes | Queue priority | SIGNAL |
| 7 | Ohm | Flow control | SIGNAL |
| 8 | Hooke | Elastic scaling | SIGNAL |
| 9 | Wave | Propagation delay | DELAY |
| 10 | Doppler | Adaptive timeout | SIGNAL |
| 11 | Planck | Memory quanta | ACTIEF |
| 12 | Heisenberg | Tradeoff validation | BLOCKING |
| 13 | Maxwell | Field coordination | SIGNAL |
| 14 | Betti | Complexity/split | ACTIEF |

---

## Betti Numbers

Topologische complexiteitsmeting:

| Symbol | Betekenis | Voorbeeld |
|--------|-----------|-----------|
| B0 | Connectedness | Aantal humans/participants |
| B1 | Loops/cycles | Aantal devices |
| B2 | Voids | Aantal operaties |
| B3 | Higher complexity | Aantal stappen |
| B4 | Meta-complexity | Betti score zelf |
| B5 | Ultra-complexity | Recursieve diepte |

**Formule**: χ = 3×B0 + 2×B1 + 1.5×B2 + 1×B3

---

## Wet Types

### BLOCKING
Kunnen request volledig afwijzen.
- Newton: trust < 0.3
- Thermodynamics: health = CRITICAL
- Heisenberg: latency×throughput > 0.7

### DELAY
Voegen wachttijd toe aan verwerking.
- Kepler: scheduling_interval_ms / 100
- Wave: propagation_delay_ms (multi-device)

### SIGNAL
Geven waarde door aan downstream systemen.
- Ohm: `_ohm_rate_limit`
- Archimedes: `_archimedes_queue`
- Hooke: `_hooke_scale_signal`
- Doppler: `_doppler_timeout_ms`
- Maxwell: `_maxwell_field`

### ACTIEF
Direct toegepast op resources.
- Einstein: cpu_percent boost
- Conservation: chain_hash tracking
- Planck: memory in 32MB quanta
- Betti: split_required decision

---

## API Endpoints

### Brain API (port 8010)

| Endpoint | Functie |
|----------|---------|
| `/betti/intent/execute` | Hoofdendpoint voor intent verwerking |
| `/planner/plan` | Resource planning met 14 wetten |
| `/planner/plan/quick` | Quick GET planning |
| `/planner/compare` | Vergelijk task types |
| `/planner/laws` | Lijst alle 14 wetten |
| `/health` | Health check |

---

## Validation Tests

### Test A: Thundering Herd
Stress test met massale gelijktijdige requests.
- Test: Ohm, Thermodynamics, Newton
- Verwacht: Graceful degradatie, blocking bij overload

### Test B: David & Goliath
QoS test - kleine urgente vs grote niet-urgente taken.
- Test: Archimedes buoyancy
- Verwacht: Kleine taken "drijven" omhoog

### Test C: Jojo
Stabiliteitstest - oscillerende load.
- Test: Hooke scaling
- Verwacht: Stabiele SCALE_UP/DOWN beslissingen

### Test D: Edge of Death
Resource constraint test - maximale limieten.
- Test: Planck, Heisenberg
- Verwacht: Clean blocking, geen crashes

---

## Auteur

Jasper van de Meent
Licentie: JOSL
