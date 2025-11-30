"""
BETTI Natural Laws Engine

Implements the 14 natural physics laws for computing resource allocation.
Based on the research paper by Jasper van de Meent.

Each law is applied to computing in a novel way:
- Kepler's Law → Orbital resource scheduling
- Newton's Gravity → Trust attraction
- Einstein E=mc² → Computation energy equivalence
- etc.
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class NaturalLaw(Enum):
    """The 14 natural laws used in BETTI"""
    KEPLER = 1           # Orbital resource allocation
    NEWTON_GRAVITY = 2   # Trust attraction
    EINSTEIN_EMC2 = 3    # Energy-mass equivalence
    THERMODYNAMICS = 4   # Entropy management
    CONSERVATION = 5     # Energy preservation
    ARCHIMEDES = 6       # Buoyancy-based priority
    OHM = 7              # Data flow resistance
    HOOKE = 8            # Elastic load balancing
    WAVE = 9             # Signal propagation
    DOPPLER = 10         # Velocity-based timing
    PLANCK = 11          # Quantum discretization
    HEISENBERG = 12      # Uncertainty trade-offs
    MAXWELL = 13         # Field coordination
    ENTROPY = 14         # Complexity management


@dataclass
class ResourceAllocation:
    """Result of natural laws resource allocation"""
    power: float          # Watts
    data: float           # MB
    memory: float         # MB
    queue_priority: int   # 1-10 (1 = highest)
    time_window: float    # seconds
    complexity_score: float
    laws_applied: List[NaturalLaw]


class NaturalLawsEngine:
    """
    Core engine that applies 14 natural laws to resource allocation.

    Example:
        engine = NaturalLawsEngine()
        allocation = engine.calculate_resources(
            intent="robot_move",
            context={"urgency": 8, "mass": 50},
            constraints={"max_power": 100}
        )
    """

    # Physical constants (adapted for computing)
    GRAVITATIONAL_CONSTANT = 6.674e-11  # N⋅m²/kg²
    SPEED_OF_LIGHT = 299792458          # m/s
    PLANCK_CONSTANT = 6.626e-34         # J⋅s
    BOLTZMANN_CONSTANT = 1.380649e-23   # J/K

    def __init__(self, profile: str = "default"):
        """
        Initialize the natural laws engine.

        Args:
            profile: Threshold profile (default, strict, relaxed)
        """
        self.profile = profile
        self.thresholds = self._load_thresholds(profile)

    def _load_thresholds(self, profile: str) -> Dict[str, float]:
        """Load threshold values for complexity calculations"""
        profiles = {
            "default": {
                "b0_max": 5,      # Max humans involved
                "b1_max": 10,     # Max devices
                "b2_max": 20,     # Max operations
                "b3_max": 50,     # Max TIBET steps
                "complexity_max": 100.0,
                "alpha": 1.0,     # Human weight
                "beta": 0.8,      # Device weight
                "gamma": 0.5,     # Operation weight
                "delta": 0.3      # Step weight
            },
            "strict": {
                "b0_max": 3,
                "b1_max": 5,
                "b2_max": 10,
                "b3_max": 25,
                "complexity_max": 50.0,
                "alpha": 1.5,
                "beta": 1.2,
                "gamma": 0.8,
                "delta": 0.5
            },
            "relaxed": {
                "b0_max": 10,
                "b1_max": 20,
                "b2_max": 50,
                "b3_max": 100,
                "complexity_max": 200.0,
                "alpha": 0.8,
                "beta": 0.6,
                "gamma": 0.4,
                "delta": 0.2
            }
        }
        return profiles.get(profile, profiles["default"])

    def calculate_resources(
        self,
        intent: str,
        context: Dict[str, Any],
        constraints: Optional[Dict[str, float]] = None
    ) -> ResourceAllocation:
        """
        Calculate resource allocation using all 14 natural laws.

        Args:
            intent: The intent to execute
            context: Context including urgency, mass, devices, etc.
            constraints: Optional resource constraints

        Returns:
            ResourceAllocation with calculated values
        """
        constraints = constraints or {}
        laws_applied = []

        # Extract context values
        urgency = context.get("urgency", 5)  # 1-10
        mass = context.get("mass", 1.0)      # kg (or complexity weight)
        devices = context.get("devices", 1)
        humans = context.get("humans", 1)
        operations = context.get("operations", 1)

        # 1. Kepler's Law - Orbital scheduling
        # T² ∝ a³ (period squared proportional to semi-major axis cubed)
        orbital_period = self._apply_kepler(urgency, mass)
        laws_applied.append(NaturalLaw.KEPLER)

        # 2. Newton's Gravity - Trust attraction
        # F = G(m1*m2)/r²
        trust_force = self._apply_newton_gravity(humans, devices)
        laws_applied.append(NaturalLaw.NEWTON_GRAVITY)

        # 3. Einstein E=mc² - Computation energy
        computation_energy = self._apply_einstein(mass, urgency)
        laws_applied.append(NaturalLaw.EINSTEIN_EMC2)

        # 4. Thermodynamics - Entropy
        entropy = self._apply_thermodynamics(operations, devices)
        laws_applied.append(NaturalLaw.THERMODYNAMICS)

        # 5. Conservation - Energy preservation
        preserved_energy = self._apply_conservation(computation_energy, entropy)
        laws_applied.append(NaturalLaw.CONSERVATION)

        # 6. Archimedes - Priority buoyancy
        priority = self._apply_archimedes(urgency, mass)
        laws_applied.append(NaturalLaw.ARCHIMEDES)

        # 7. Ohm's Law - Data flow
        data_flow = self._apply_ohm(computation_energy, entropy)
        laws_applied.append(NaturalLaw.OHM)

        # 8. Hooke's Law - Load balancing
        load_balance = self._apply_hooke(devices, operations)
        laws_applied.append(NaturalLaw.HOOKE)

        # 9. Wave Equation - Signal timing
        signal_time = self._apply_wave(orbital_period, trust_force)
        laws_applied.append(NaturalLaw.WAVE)

        # 10. Doppler - Velocity adjustment
        velocity_factor = self._apply_doppler(urgency)
        laws_applied.append(NaturalLaw.DOPPLER)

        # 11. Planck - Quantization
        quantum_units = self._apply_planck(computation_energy)
        laws_applied.append(NaturalLaw.PLANCK)

        # 12. Heisenberg - Uncertainty trade-off
        uncertainty = self._apply_heisenberg(priority, signal_time)
        laws_applied.append(NaturalLaw.HEISENBERG)

        # 13. Maxwell - Field coordination
        field_strength = self._apply_maxwell(trust_force, data_flow)
        laws_applied.append(NaturalLaw.MAXWELL)

        # 14. Entropy - Complexity
        complexity = self._apply_entropy(humans, devices, operations, entropy)
        laws_applied.append(NaturalLaw.ENTROPY)

        # Combine all calculations
        power = min(
            preserved_energy * velocity_factor,
            constraints.get("max_power", 1000)
        )

        data = data_flow * quantum_units * (1 + uncertainty)
        memory = load_balance * field_strength * 100  # Scale to MB

        queue_priority = max(1, min(10, int(11 - priority)))
        time_window = signal_time * (1 / velocity_factor)

        return ResourceAllocation(
            power=round(power, 2),
            data=round(data, 2),
            memory=round(memory, 2),
            queue_priority=queue_priority,
            time_window=round(time_window, 3),
            complexity_score=round(complexity, 2),
            laws_applied=laws_applied
        )

    def _apply_kepler(self, urgency: float, mass: float) -> float:
        """Kepler's Third Law: T² = (4π²/GM) × a³"""
        # Higher urgency = shorter orbital period
        a = 10 - urgency  # Semi-major axis inversely related to urgency
        T_squared = (4 * math.pi**2) * (a**3) / (self.GRAVITATIONAL_CONSTANT * mass)
        return math.sqrt(abs(T_squared)) * 0.001  # Scale to reasonable range

    def _apply_newton_gravity(self, humans: int, devices: int) -> float:
        """Newton's Gravity: F = G(m1×m2)/r²"""
        m1 = humans * 10  # Human mass contribution
        m2 = devices * 5  # Device mass contribution
        r = max(1, abs(humans - devices) + 1)  # Distance
        return self.GRAVITATIONAL_CONSTANT * (m1 * m2) / (r**2) * 1e12

    def _apply_einstein(self, mass: float, urgency: float) -> float:
        """Einstein's E=mc²"""
        # Urgency acts as velocity factor
        v = urgency / 10 * self.SPEED_OF_LIGHT * 0.001
        gamma = 1 / math.sqrt(1 - (v**2 / self.SPEED_OF_LIGHT**2))
        return mass * gamma * 10  # Scaled computation energy

    def _apply_thermodynamics(self, operations: int, devices: int) -> float:
        """Second Law of Thermodynamics: ΔS ≥ 0"""
        # Entropy increases with complexity
        return math.log(operations * devices + 1) * self.BOLTZMANN_CONSTANT * 1e25

    def _apply_conservation(self, energy: float, entropy: float) -> float:
        """Conservation of Energy: Ein = Eout + Entropy"""
        return max(0, energy - entropy)

    def _apply_archimedes(self, urgency: float, mass: float) -> float:
        """Archimedes Principle: Fb = ρVg"""
        # Priority floats up based on urgency vs mass
        fluid_density = 10  # System load
        volume = urgency / mass if mass > 0 else urgency
        return min(10, fluid_density * volume * 9.81 / 10)

    def _apply_ohm(self, energy: float, resistance: float) -> float:
        """Ohm's Law: V = IR → I = V/R"""
        voltage = energy
        resistance = max(0.1, resistance)
        return voltage / resistance

    def _apply_hooke(self, devices: int, operations: int) -> float:
        """Hooke's Law: F = -kx"""
        k = 0.5  # Spring constant
        x = devices * operations / 10  # Displacement
        return abs(k * x)

    def _apply_wave(self, period: float, amplitude: float) -> float:
        """Wave Equation: v = fλ"""
        frequency = 1 / max(0.001, period)
        wavelength = amplitude
        return frequency * wavelength * 0.01

    def _apply_doppler(self, urgency: float) -> float:
        """Doppler Effect: f' = f(v+vr)/(v+vs)"""
        # Urgency affects perceived frequency
        v_source = (10 - urgency) / 10
        v_receiver = urgency / 10
        return (1 + v_receiver) / (1 + v_source)

    def _apply_planck(self, energy: float) -> float:
        """Planck's Quantization: E = hf"""
        frequency = energy / self.PLANCK_CONSTANT
        # Return number of quantum units
        return math.log10(abs(frequency) + 1) / 30

    def _apply_heisenberg(self, position: float, momentum: float) -> float:
        """Heisenberg Uncertainty: ΔxΔp ≥ ℏ/2"""
        # Trade-off between precision and flexibility
        hbar = self.PLANCK_CONSTANT / (2 * math.pi)
        uncertainty = hbar / (2 * max(0.001, position * momentum))
        return min(1, uncertainty * 1e35)

    def _apply_maxwell(self, electric: float, magnetic: float) -> float:
        """Maxwell's Equations: Field coordination"""
        return math.sqrt(electric**2 + magnetic**2)

    def _apply_entropy(
        self,
        humans: int,
        devices: int,
        operations: int,
        base_entropy: float
    ) -> float:
        """Calculate Betti complexity using topological analysis"""
        t = self.thresholds

        # Betti numbers
        b0 = humans  # Connected components (humans)
        b1 = devices  # Holes (devices)
        b2 = operations  # Voids (operations)

        # Weighted complexity
        complexity = (
            t["alpha"] * (b0 / t["b0_max"]) +
            t["beta"] * (b1 / t["b1_max"]) +
            t["gamma"] * (b2 / t["b2_max"]) +
            base_entropy
        ) * t["complexity_max"]

        return min(complexity, t["complexity_max"] * 2)


# Convenience function
def calculate_betti_allocation(
    intent: str,
    context: Dict[str, Any],
    profile: str = "default"
) -> ResourceAllocation:
    """
    Quick function to calculate BETTI resource allocation.

    Example:
        allocation = calculate_betti_allocation(
            "robot_move",
            {"urgency": 8, "devices": 3}
        )
        print(f"Power: {allocation.power}W")
    """
    engine = NaturalLawsEngine(profile)
    return engine.calculate_resources(intent, context)
