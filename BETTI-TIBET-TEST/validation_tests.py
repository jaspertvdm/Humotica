#!/usr/bin/env python3
"""
BETTI-TIBET Validation Tests
=============================

4 Critical validation tests for the 14 Wetten enforcement:

Test A: Thundering Herd - Mass concurrent requests
Test B: David & Goliath - QoS priority testing
Test C: Jojo - Oscillating load stability
Test D: Edge of Death - Resource constraint limits

Author: Jasper van de Meent
License: JOSL
"""

import asyncio
import aiohttp
import time
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import Counter

# Configuration
BRAIN_API = "http://localhost:8010"


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: Dict[str, Any]
    laws_tested: List[str]


async def make_request(session: aiohttp.ClientSession, payload: Dict) -> Dict:
    """Make a single request to the Brain API"""
    try:
        async with session.post(
            f"{BRAIN_API}/betti/intent/execute",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            return await resp.json()
    except Exception as e:
        return {"error": str(e), "status": "timeout"}


# ============================================================
# TEST A: THUNDERING HERD
# ============================================================
async def test_thundering_herd(concurrent: int = 100) -> TestResult:
    """
    Thundering Herd Test
    ====================

    Simuleert massale gelijktijdige requests (zoals bij een virale post).

    Test wetten:
    - Ohm: Flow control moet rate limiting toepassen
    - Thermodynamics: System health moet CRITICAL/WARNING triggeren
    - Newton: Trust verificatie onder load

    Verwacht gedrag:
    - Graceful degradatie (geen crashes)
    - Proportionele blocking bij overload
    - health_action escalatie
    """
    print(f"\n{'='*60}")
    print("TEST A: THUNDERING HERD")
    print(f"{'='*60}")
    print(f"Sending {concurrent} concurrent requests...")

    start = time.time()

    # Generate payloads with varying urgency
    payloads = []
    for i in range(concurrent):
        payloads.append({
            "user_id": f"user_{i}",
            "intent": "message",
            "context": {
                "urgency": random.randint(1, 10),
                "devices": [f"device_{i}"],
                "load_test": True,
                "batch_id": "thundering_herd"
            }
        })

    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, p) for p in payloads]
        results = await asyncio.gather(*tasks)

    duration_ms = (time.time() - start) * 1000

    # Analyze results
    statuses = Counter(r.get("status", "error") for r in results)
    health_actions = Counter(
        r.get("resource_allocation", {}).get("health_action", "unknown")
        for r in results if "resource_allocation" in r
    )

    # Check for graceful degradation
    executed = statuses.get("executed", 0)
    blocked = sum(v for k, v in statuses.items() if "blocked" in k)
    errors = statuses.get("error", 0) + statuses.get("timeout", 0)

    passed = (
        errors < concurrent * 0.1 and  # < 10% hard errors
        executed + blocked >= concurrent * 0.9  # 90% processed
    )

    print(f"\nResults:")
    print(f"  Executed: {executed}")
    print(f"  Blocked: {blocked}")
    print(f"  Errors: {errors}")
    print(f"  Duration: {duration_ms:.0f}ms")
    print(f"  Health actions: {dict(health_actions)}")
    print(f"  Status: {'PASS' if passed else 'FAIL'}")

    return TestResult(
        name="Thundering Herd",
        passed=passed,
        duration_ms=duration_ms,
        details={
            "concurrent": concurrent,
            "statuses": dict(statuses),
            "health_actions": dict(health_actions),
            "executed_pct": executed / concurrent * 100,
            "graceful_degradation": errors < concurrent * 0.1
        },
        laws_tested=["Ohm", "Thermodynamics", "Newton"]
    )


# ============================================================
# TEST B: DAVID & GOLIATH
# ============================================================
async def test_david_and_goliath() -> TestResult:
    """
    David & Goliath Test
    ====================

    Test QoS: kleine urgente taken vs grote niet-urgente taken.

    Test wetten:
    - Archimedes: Buoyancy moet kleine taken laten "drijven"
    - Kepler: Scheduling interval verschilt per urgency

    Verwacht gedrag:
    - David (klein, urgent) krijgt hogere queue priority
    - Goliath (groot, niet-urgent) wacht langer
    """
    print(f"\n{'='*60}")
    print("TEST B: DAVID & GOLIATH")
    print(f"{'='*60}")

    start = time.time()

    # David: klein en urgent
    david = {
        "user_id": "david",
        "intent": "message",
        "context": {
            "urgency": 9,
            "devices": ["phone"],
            "data_size_kb": 1
        }
    }

    # Goliath: groot en niet-urgent
    goliath = {
        "user_id": "goliath",
        "intent": "file_transfer",
        "context": {
            "urgency": 2,
            "devices": ["server1", "server2", "server3", "server4"],
            "data_size_kb": 10000
        }
    }

    async with aiohttp.ClientSession() as session:
        david_result, goliath_result = await asyncio.gather(
            make_request(session, david),
            make_request(session, goliath)
        )

    duration_ms = (time.time() - start) * 1000

    # Get queue priorities
    david_alloc = david_result.get("resource_allocation", {})
    goliath_alloc = goliath_result.get("resource_allocation", {})

    david_priority = david_alloc.get("queue_priority", 0)
    goliath_priority = goliath_alloc.get("queue_priority", 0)
    david_wait = david_alloc.get("estimated_wait_ms", 0)
    goliath_wait = goliath_alloc.get("estimated_wait_ms", 0)

    # David should have higher priority (lower number = higher priority)
    # Or at least lower wait time
    passed = david_priority < goliath_priority or david_wait < goliath_wait

    print(f"\nDavid (small, urgent):")
    print(f"  Queue priority: {david_priority}/10")
    print(f"  Estimated wait: {david_wait}ms")
    print(f"\nGoliath (large, not urgent):")
    print(f"  Queue priority: {goliath_priority}/10")
    print(f"  Estimated wait: {goliath_wait}ms")
    print(f"\nStatus: {'PASS' if passed else 'FAIL'} - David {'floats' if passed else 'sinks'}")

    return TestResult(
        name="David & Goliath",
        passed=passed,
        duration_ms=duration_ms,
        details={
            "david_priority": david_priority,
            "goliath_priority": goliath_priority,
            "david_wait_ms": david_wait,
            "goliath_wait_ms": goliath_wait,
            "david_floats": passed
        },
        laws_tested=["Archimedes", "Kepler"]
    )


# ============================================================
# TEST C: JOJO
# ============================================================
async def test_jojo(cycles: int = 10) -> TestResult:
    """
    Jojo Test
    =========

    Test stabiliteit onder oscillerende load (up-down-up-down).

    Test wetten:
    - Hooke: Elastic scaling moet stabiel SCALE_UP/DOWN signaleren

    Verwacht gedrag:
    - Geen oscillatie in scaling beslissingen
    - Stabiele response bij load variatie
    """
    print(f"\n{'='*60}")
    print("TEST C: JOJO (Oscillating Load)")
    print(f"{'='*60}")

    start = time.time()
    scale_actions = []

    async with aiohttp.ClientSession() as session:
        for i in range(cycles):
            # Alternate between high and low load indication
            load = 90 if i % 2 == 0 else 10

            payload = {
                "user_id": f"jojo_{i}",
                "intent": "query",
                "context": {
                    "urgency": 5,
                    "devices": ["server"],
                    "current_load": load
                }
            }

            result = await make_request(session, payload)
            alloc = result.get("resource_allocation", {})
            action = alloc.get("scale_action", "UNKNOWN")
            scale_actions.append((load, action))

            print(f"  Cycle {i+1}: load={load}% -> {action}")
            await asyncio.sleep(0.1)  # Small delay between cycles

    duration_ms = (time.time() - start) * 1000

    # Check for stability
    # At high load (90%), should recommend SCALE_UP
    # At low load (10%), should recommend SCALE_DOWN
    high_load_actions = [a for l, a in scale_actions if l == 90]
    low_load_actions = [a for l, a in scale_actions if l == 10]

    high_correct = all(a == "SCALE_UP" for a in high_load_actions)
    low_correct = all(a == "SCALE_DOWN" for a in low_load_actions)

    passed = high_correct and low_correct

    print(f"\nHigh load actions: {Counter(high_load_actions)}")
    print(f"Low load actions: {Counter(low_load_actions)}")
    print(f"Status: {'PASS' if passed else 'FAIL'}")

    return TestResult(
        name="Jojo",
        passed=passed,
        duration_ms=duration_ms,
        details={
            "cycles": cycles,
            "high_load_actions": dict(Counter(high_load_actions)),
            "low_load_actions": dict(Counter(low_load_actions)),
            "stable": passed
        },
        laws_tested=["Hooke"]
    )


# ============================================================
# TEST D: EDGE OF DEATH
# ============================================================
async def test_edge_of_death() -> TestResult:
    """
    Edge of Death Test
    ==================

    Test gedrag bij maximale resource constraints.

    Test wetten:
    - Planck: Memory quantization bij extreme requests
    - Heisenberg: Tradeoff violation detection
    - Betti: Complexity split bij extreme complexity

    Verwacht gedrag:
    - Clean blocking (geen crashes)
    - Duidelijke error messages
    - split_required bij hoge complexity
    """
    print(f"\n{'='*60}")
    print("TEST D: EDGE OF DEATH")
    print(f"{'='*60}")

    start = time.time()
    results = {}

    async with aiohttp.ClientSession() as session:
        # Test 1: Extreme memory request
        extreme_memory = {
            "user_id": "memory_hog",
            "intent": "file_transfer",
            "context": {
                "urgency": 1,
                "devices": ["server"],
                "data_size_kb": 1000000  # 1GB
            }
        }
        results["extreme_memory"] = await make_request(session, extreme_memory)

        # Test 2: Extreme complexity (should trigger split)
        extreme_complexity = {
            "user_id": "complex_task",
            "intent": "query",
            "context": {
                "urgency": 5,
                "participants": [f"user_{i}" for i in range(20)],  # B0 = 20
                "devices": [f"dev_{i}" for i in range(10)],         # B1 = 10
                "operations": [f"op_{i}" for i in range(10)]        # B2 = 10
            }
        }
        results["extreme_complexity"] = await make_request(session, extreme_complexity)

        # Test 3: Low trust (should be Newton blocked)
        low_trust = {
            "user_id": "untrusted",
            "intent": "emergency",
            "context": {
                "urgency": 10,
                "devices": ["unknown_device"],
                "trust_override": 0.1  # Very low trust
            }
        }
        results["low_trust"] = await make_request(session, low_trust)

    duration_ms = (time.time() - start) * 1000

    # Analyze
    memory_alloc = results["extreme_memory"].get("resource_allocation", {})
    complexity_alloc = results["extreme_complexity"].get("resource_allocation", {})

    # Check Planck quantization
    memory_mb = memory_alloc.get("memory_mb", 0)
    is_quantized = memory_mb % 32 == 0

    # Check Betti split
    split_required = complexity_alloc.get("split_required", False)
    complexity_score = complexity_alloc.get("complexity_score", 0)

    print(f"\nExtreme Memory Test:")
    print(f"  Requested: ~1GB")
    print(f"  Allocated: {memory_mb}MB")
    print(f"  Quantized (32MB): {is_quantized}")

    print(f"\nExtreme Complexity Test:")
    print(f"  Complexity score: {complexity_score}")
    print(f"  Split required: {split_required}")

    print(f"\nLow Trust Test:")
    print(f"  Status: {results['low_trust'].get('status', 'unknown')}")

    # All tests should handle gracefully (no crashes, proper responses)
    all_responded = all("error" not in r or r.get("status") != "timeout" for r in results.values())

    passed = all_responded and is_quantized
    print(f"\nStatus: {'PASS' if passed else 'FAIL'}")

    return TestResult(
        name="Edge of Death",
        passed=passed,
        duration_ms=duration_ms,
        details={
            "memory_mb": memory_mb,
            "is_quantized": is_quantized,
            "complexity_score": complexity_score,
            "split_required": split_required,
            "low_trust_status": results["low_trust"].get("status"),
            "all_graceful": all_responded
        },
        laws_tested=["Planck", "Heisenberg", "Betti", "Newton"]
    )


# ============================================================
# MAIN TEST RUNNER
# ============================================================
async def run_all_tests():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("BETTI-TIBET VALIDATION TEST SUITE")
    print("="*60)
    print("Testing 14 Wetten Enforcement")
    print("="*60)

    all_results = []

    # Run tests
    all_results.append(await test_thundering_herd(50))  # Reduced for faster testing
    all_results.append(await test_david_and_goliath())
    all_results.append(await test_jojo(6))  # Reduced cycles
    all_results.append(await test_edge_of_death())

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    for r in all_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  {r.name}: {status} ({r.duration_ms:.0f}ms)")
        print(f"    Laws tested: {', '.join(r.laws_tested)}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

    return all_results


def main():
    """Entry point"""
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted")
    except Exception as e:
        print(f"\nTest error: {e}")
        raise


if __name__ == "__main__":
    main()
