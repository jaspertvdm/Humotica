"""
BETTI Resource Planner - Functionele 14 Wetten Engine
=====================================================

Dit is de CENTRALE module die alle 14 wetten combineert tot
echte, functionele beslissingen voor het systeem.

Elke intent/taak gaat door deze planner en krijgt:
- Resource allocatie (CPU, RAM, bandwidth)
- Scheduling priority
- Timeout configuratie
- Trust verificatie
- Complexity check
- Queue positie

Dit is GEEN simulatie - dit zijn echte configuraties die
door andere delen van het systeem worden gebruikt.

Author: Jasper van de Meent
License: JOSL
"""

import math
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class TaskType(Enum):
    """Types taken met standaard resource profielen"""
    CALL = "call"
    VIDEO_CALL = "video_call"
    MESSAGE = "message"
    FILE_TRANSFER = "file_transfer"
    IOT_COMMAND = "iot_command"
    QUERY = "query"
    EMERGENCY = "emergency"
    BACKGROUND = "background"


@dataclass
class ResourceAllocation:
    """Output van de Resource Planner - echte configuratie"""
    # Scheduling (Kepler)
    scheduling_interval_ms: float
    priority_class: int  # 1-5 (1=highest)

    # Resources (Einstein + Planck)
    memory_mb: int
    cpu_percent: int
    bandwidth_kbps: int

    # Timing (Doppler)
    timeout_ms: float
    max_retries: int

    # Queue (Archimedes)
    queue_priority: int  # 1-10 (1=highest)
    estimated_wait_ms: float

    # Security (Newton + Conservation)
    trust_score: float
    trust_verified: bool
    chain_hash: str

    # Health (Thermodynamics)
    system_entropy: float
    system_health_percent: float
    health_action: str

    # Complexity (Betti)
    complexity_score: float
    split_required: bool
    sub_tasks: int

    # Flow control (Ohm)
    flow_rate_kbps: float
    resistance: float

    # Trade-offs (Heisenberg)
    latency_precision: float
    throughput_precision: float
    tradeoff_valid: bool

    # Coordination (Maxwell + Wave)
    field_strength: float
    propagation_delay_ms: float

    # Scaling (Hooke)
    scale_action: str
    recommended_instances: int

    # Metadata
    laws_applied: List[str] = field(default_factory=list)
    computation_time_us: float = 0
    timestamp: str = ""
    continuity_hash: str = ""


class ResourcePlanner:
    """
    Centrale Resource Planner die alle 14 wetten toepast.

    Gebruik:
        planner = ResourcePlanner()
        allocation = planner.plan(
            task_type="video_call",
            urgency=8,
            participants=["alice", "bob"],
            devices=["phone_1", "laptop_1"]
        )

        # allocation bevat nu alle geconfigureerde resources
        print(f"Memory: {allocation.memory_mb}MB")
        print(f"Timeout: {allocation.timeout_ms}ms")
        print(f"Priority: {allocation.queue_priority}/10")
    """

    # Physics constants
    G = 0.1          # Trust gravity
    C = 1000         # Computing speed of light
    K = 0.01         # Boltzmann constant

    # System state (shared across calls)
    _chain = ["GENESIS"]
    _energy_in = 0
    _energy_out = 0
    _current_load = 50
    _instances = 1

    # Resource profiles per task type
    PROFILES = {
        TaskType.EMERGENCY: {"base_memory": 256, "base_cpu": 80, "base_bw": 10000, "urgency_boost": 10},
        TaskType.VIDEO_CALL: {"base_memory": 512, "base_cpu": 60, "base_bw": 5000, "urgency_boost": 3},
        TaskType.CALL: {"base_memory": 128, "base_cpu": 30, "base_bw": 1000, "urgency_boost": 2},
        TaskType.FILE_TRANSFER: {"base_memory": 256, "base_cpu": 40, "base_bw": 8000, "urgency_boost": 1},
        TaskType.MESSAGE: {"base_memory": 32, "base_cpu": 10, "base_bw": 100, "urgency_boost": 1},
        TaskType.IOT_COMMAND: {"base_memory": 16, "base_cpu": 5, "base_bw": 50, "urgency_boost": 2},
        TaskType.QUERY: {"base_memory": 64, "base_cpu": 20, "base_bw": 200, "urgency_boost": 1},
        TaskType.BACKGROUND: {"base_memory": 64, "base_cpu": 10, "base_bw": 100, "urgency_boost": 0},
    }

    def __init__(self):
        self.laws_applied = []

    def plan(
        self,
        task_type: str = "message",
        urgency: int = 5,
        participants: List[str] = None,
        devices: List[str] = None,
        operations: List[str] = None,
        data_size_kb: float = 10,
        trust_scores: Dict[str, float] = None,
        current_load: int = None,
        network_resistance: float = 1.0
    ) -> ResourceAllocation:
        """
        Plan resources voor een taak met alle 14 wetten.

        Args:
            task_type: Type taak (call, video_call, message, etc.)
            urgency: Urgentie 1-10 (10=hoogst)
            participants: Lijst van deelnemers (HIDs)
            devices: Lijst van devices (DIDs)
            operations: Lijst van operaties
            data_size_kb: Grootte van data in KB
            trust_scores: Dict van entity -> trust score (0-1)
            current_load: Huidige systeem load (0-100)
            network_resistance: Netwerk weerstand (0.1-10)

        Returns:
            ResourceAllocation met alle geconfigureerde resources
        """
        start_time = time.perf_counter_ns()
        self.laws_applied = []

        # Defaults
        participants = participants or ["user"]
        devices = devices or ["device"]
        operations = operations or [task_type]
        trust_scores = trust_scores or {p: 0.8 for p in participants}

        if current_load is not None:
            self._current_load = current_load

        # Get base profile
        try:
            task_enum = TaskType(task_type)
        except ValueError:
            task_enum = TaskType.MESSAGE
        profile = self.PROFILES[task_enum]

        # Effective urgency with boost
        effective_urgency = min(10, urgency + profile["urgency_boost"])

        # ===== WET 1: KEPLER - Scheduling =====
        scheduling = self._apply_kepler(effective_urgency)
        self.laws_applied.append("Kepler")

        # ===== WET 2: NEWTON - Trust =====
        trust = self._apply_newton(participants, trust_scores)
        self.laws_applied.append("Newton")

        # ===== WET 3: EINSTEIN - Energy/Resources =====
        energy = self._apply_einstein(data_size_kb, len(operations))
        base_memory = profile["base_memory"]
        base_cpu = profile["base_cpu"]
        base_bw = profile["base_bw"]
        self.laws_applied.append("Einstein")

        # ===== WET 4: THERMODYNAMICS - System Health =====
        thermo = self._apply_thermodynamics(len(operations), len(devices))
        self.laws_applied.append("Thermodynamics")

        # ===== WET 5: CONSERVATION - Resource Tracking =====
        conservation = self._apply_conservation(base_memory)
        self.laws_applied.append("Conservation")

        # ===== WET 6: ARCHIMEDES - Queue Priority =====
        queue = self._apply_archimedes(effective_urgency, energy["mass"])
        self.laws_applied.append("Archimedes")

        # ===== WET 7: OHM - Flow Control =====
        flow = self._apply_ohm(effective_urgency, network_resistance)
        self.laws_applied.append("Ohm")

        # ===== WET 8: HOOKE - Scaling =====
        scaling = self._apply_hooke(self._current_load)
        self.laws_applied.append("Hooke")

        # ===== WET 9: WAVE - Propagation =====
        wave = self._apply_wave(len(devices), trust["avg_trust"])
        self.laws_applied.append("Wave")

        # ===== WET 10: DOPPLER - Timeout =====
        timeout = self._apply_doppler(effective_urgency)
        self.laws_applied.append("Doppler")

        # ===== WET 11: PLANCK - Memory Quantization =====
        memory = self._apply_planck(base_memory)
        self.laws_applied.append("Planck")

        # ===== WET 12: HEISENBERG - Trade-offs =====
        tradeoff = self._apply_heisenberg(0.8, 0.7)
        self.laws_applied.append("Heisenberg")

        # ===== WET 13: MAXWELL - Field Coordination =====
        field = self._apply_maxwell(trust["total_force"], flow["current"])
        self.laws_applied.append("Maxwell")

        # ===== WET 14: BETTI - Complexity =====
        complexity = self._apply_betti(
            len(participants), len(devices), len(operations)
        )
        self.laws_applied.append("Betti")

        # ===== CHAIN - Continuity Hash =====
        chain = self._apply_chain(task_type, str(participants))

        # Calculate total computation time
        elapsed_us = (time.perf_counter_ns() - start_time) / 1000

        # Build final allocation
        return ResourceAllocation(
            # Scheduling (Kepler)
            scheduling_interval_ms=scheduling["interval_ms"],
            priority_class=scheduling["priority_class"],

            # Resources (Einstein + Planck)
            memory_mb=memory["allocated_mb"],
            cpu_percent=min(100, base_cpu + int(energy["energy"] / 100000)),
            bandwidth_kbps=min(base_bw, int(flow["current"] * 1000)),

            # Timing (Doppler)
            timeout_ms=timeout["timeout_ms"],
            max_retries=3 if effective_urgency >= 7 else 1,

            # Queue (Archimedes)
            queue_priority=queue["position"],
            estimated_wait_ms=queue["estimated_wait_ms"],

            # Security (Newton + Conservation)
            trust_score=trust["avg_trust"],
            trust_verified=trust["verified"],
            chain_hash=chain["hash"],

            # Health (Thermodynamics)
            system_entropy=thermo["entropy"],
            system_health_percent=thermo["health"],
            health_action=thermo["action"],

            # Complexity (Betti)
            complexity_score=complexity["score"],
            split_required=complexity["split_required"],
            sub_tasks=complexity["sub_tasks"],

            # Flow control (Ohm)
            flow_rate_kbps=flow["current"] * 1000,
            resistance=network_resistance,

            # Trade-offs (Heisenberg)
            latency_precision=tradeoff["latency"],
            throughput_precision=tradeoff["throughput"],
            tradeoff_valid=tradeoff["valid"],

            # Coordination (Maxwell + Wave)
            field_strength=field["strength"],
            propagation_delay_ms=wave["delay_ms"],

            # Scaling (Hooke)
            scale_action=scaling["action"],
            recommended_instances=scaling["instances"],

            # Metadata
            laws_applied=self.laws_applied.copy(),
            computation_time_us=round(elapsed_us, 2),
            timestamp=datetime.now().isoformat(),
            continuity_hash=chain["hash"]
        )

    # =========================================================================
    # Individual Law Implementations
    # =========================================================================

    def _apply_kepler(self, priority: int) -> Dict[str, Any]:
        """Wet 1: T² = a³/10 - Orbital scheduling"""
        a = 10 - priority  # Semi-major axis
        T_squared = max(0.1, a ** 3 / 10)
        interval_ms = math.sqrt(T_squared) * 1000  # Convert to ms

        # Priority class 1-5
        if priority >= 9:
            pclass = 1
        elif priority >= 7:
            pclass = 2
        elif priority >= 5:
            pclass = 3
        elif priority >= 3:
            pclass = 4
        else:
            pclass = 5

        return {
            "interval_ms": round(interval_ms, 2),
            "priority_class": pclass
        }

    def _apply_newton(self, participants: List[str], trust_scores: Dict[str, float]) -> Dict[str, Any]:
        """Wet 2: F = Gm1m2/r² - Trust attraction"""
        total_force = 0
        verified = True

        for i, p1 in enumerate(participants):
            t1 = trust_scores.get(p1, 0.5)
            for p2 in participants[i+1:]:
                t2 = trust_scores.get(p2, 0.5)
                force = self.G * (t1 * t2) / 1.0  # r=1
                total_force += force

            if t1 < 0.3:
                verified = False

        avg_trust = sum(trust_scores.values()) / len(trust_scores) if trust_scores else 0.5

        return {
            "total_force": round(total_force, 4),
            "avg_trust": round(avg_trust, 2),
            "verified": verified
        }

    def _apply_einstein(self, data_kb: float, complexity: int) -> Dict[str, Any]:
        """Wet 3: E = mc² - Computation energy"""
        mass = data_kb * complexity
        energy = mass * (self.C ** 2) * 0.001  # Scaled

        return {
            "mass": mass,
            "energy": round(energy, 0)
        }

    def _apply_thermodynamics(self, operations: int, devices: int) -> Dict[str, Any]:
        """Wet 4: S = k ln(Ω) - Entropy"""
        omega = operations * devices + 1
        entropy = math.log(omega) * self.K * 1000
        health = max(0, 100 - entropy)

        if health < 30:
            action = "CRITICAL"
        elif health < 60:
            action = "WARNING"
        else:
            action = "OK"

        return {
            "entropy": round(entropy, 2),
            "health": round(health, 1),
            "action": action
        }

    def _apply_conservation(self, memory_mb: int) -> Dict[str, Any]:
        """Wet 5: E_in = E_out - Resource tracking"""
        self._energy_in += memory_mb
        leaked = self._energy_in - self._energy_out

        return {
            "tracked": True,
            "total_in": self._energy_in,
            "total_out": self._energy_out,
            "leaked": leaked
        }

    def _apply_archimedes(self, urgency: int, mass: float) -> Dict[str, Any]:
        """Wet 6: Fb = ρVg - Priority buoyancy"""
        density = mass / max(0.1, urgency + 0.1)
        buoyancy = 10 / max(0.01, density)
        position = max(1, min(10, int(11 - buoyancy)))
        wait_ms = position * 50  # 50ms per position

        return {
            "position": position,
            "buoyancy": round(buoyancy, 2),
            "estimated_wait_ms": wait_ms
        }

    def _apply_ohm(self, urgency: int, resistance: float) -> Dict[str, Any]:
        """Wet 7: I = V/R - Flow control"""
        voltage = urgency * 10
        current = voltage / max(0.1, resistance)

        return {
            "voltage": voltage,
            "resistance": resistance,
            "current": round(current, 2)  # MB/s
        }

    def _apply_hooke(self, load: int) -> Dict[str, Any]:
        """Wet 8: F = -kx - Elastic scaling"""
        baseline = 50
        k = 0.5
        displacement = load - baseline
        force = -k * displacement

        instances = self._instances
        action = "STABLE"

        if force < -15 and instances < 5:
            instances += 1
            action = "SCALE_UP"
        elif force > 15 and instances > 1:
            instances -= 1
            action = "SCALE_DOWN"

        self._instances = instances

        return {
            "force": round(force, 2),
            "action": action,
            "instances": instances
        }

    def _apply_wave(self, nodes: int, amplitude: float) -> Dict[str, Any]:
        """Wet 9: v = fλ - Propagation"""
        frequency = 10
        wavelength = amplitude * 10
        speed = frequency * wavelength
        delay_ms = (nodes / max(0.1, speed)) * 100

        return {
            "speed": round(speed, 2),
            "delay_ms": round(delay_ms, 2)
        }

    def _apply_doppler(self, urgency: int) -> Dict[str, Any]:
        """Wet 10: f' = f(v+vr)/(v+vs) - Adaptive timeout"""
        base_timeout = 30000

        v_source = (10 - urgency) / 10
        v_receiver = urgency / 10
        doppler = (1 + v_receiver) / (1 + v_source)

        timeout = base_timeout / doppler

        return {
            "doppler_factor": round(doppler, 2),
            "timeout_ms": round(timeout, 0)
        }

    def _apply_planck(self, requested_mb: int, quantum: int = 32) -> Dict[str, Any]:
        """Wet 11: E = nhf - Quantum allocation"""
        quanta = (requested_mb // quantum) + (1 if requested_mb % quantum else 0)
        allocated = quanta * quantum

        return {
            "requested_mb": requested_mb,
            "allocated_mb": allocated,
            "quanta": quanta,
            "overhead_mb": allocated - requested_mb
        }

    def _apply_heisenberg(self, latency: float, throughput: float) -> Dict[str, Any]:
        """Wet 12: ΔxΔp ≥ ℏ/2 - Trade-off validation"""
        product = latency * throughput
        valid = product <= 0.7  # Can't have both at max

        return {
            "latency": latency,
            "throughput": throughput,
            "product": round(product, 2),
            "valid": valid
        }

    def _apply_maxwell(self, electric: float, magnetic: float) -> Dict[str, Any]:
        """Wet 13: |F| = √(E²+B²) - Field coordination"""
        strength = math.sqrt(electric**2 + (magnetic * 10)**2)

        return {
            "electric": round(electric, 2),
            "magnetic": round(magnetic, 2),
            "strength": round(strength, 2)
        }

    def _apply_betti(self, humans: int, devices: int, operations: int, steps: int = 5) -> Dict[str, Any]:
        """Wet 14: χ = αB0 + βB1 + γB2 + δB3 - Complexity"""
        alpha, beta, gamma, delta = 3.0, 2.0, 1.5, 1.0
        score = alpha * humans + beta * devices + gamma * operations + delta * steps

        split_required = score > 50
        sub_tasks = 1 if not split_required else min(5, int(score / 50) + 1)

        return {
            "score": score,
            "split_required": split_required,
            "sub_tasks": sub_tasks
        }

    def _apply_chain(self, task_type: str, data: str) -> Dict[str, Any]:
        """HMAC Chain - Continuity verification"""
        prev = self._chain[-1]
        chain_data = f"{prev}:{task_type}:{data}:{time.time()}"
        new_hash = hashlib.sha256(chain_data.encode()).hexdigest()[:16]
        self._chain.append(new_hash)

        if len(self._chain) > 1000:
            self._chain = self._chain[-1000:]

        return {
            "previous": prev,
            "hash": new_hash,
            "position": len(self._chain)
        }

    def release_resources(self, memory_mb: int):
        """Track resource release for Conservation law"""
        self._energy_out += memory_mb

    def reset_state(self):
        """Reset planner state"""
        self._chain = ["GENESIS"]
        self._energy_in = 0
        self._energy_out = 0
        self._current_load = 50
        self._instances = 1


# =============================================================================
# Convenience function for direct use
# =============================================================================

_planner = ResourcePlanner()


def plan_resources(**kwargs) -> ResourceAllocation:
    """
    Plan resources for a task.

    Example:
        allocation = plan_resources(
            task_type="video_call",
            urgency=8,
            participants=["alice", "bob"],
            devices=["phone", "laptop"]
        )
    """
    return _planner.plan(**kwargs)


def get_allocation_dict(**kwargs) -> Dict[str, Any]:
    """Get allocation as dictionary"""
    return asdict(_planner.plan(**kwargs))
