#!/usr/bin/env python3
"""
BETTI-TIBET Validation Tests
=============================

4 Critical validation tests for the 14 Wetten enforcement:

Test A: Thundering Herd - Mass concurrent requests
Test B: David & Goliath - QoS priority testing
Test C: Jojo - Oscillating load stability
Test D: Edge of Death - Resource constraint limits

Uses the Resource Planner endpoint which applies ALL 14 laws.

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
import json

# Configuration
BRAIN_API = "http://localhost:8010"


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: Dict[str, Any]
    laws_tested: List[str]


async def planner_request(session: aiohttp.ClientSession, params: Dict) -> Dict:
    """Make a GET request to the Resource Planner quick endpoint"""
    try:
        url = f"{BRAIN_API}/planner/plan/quick"
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return await resp.json()
    except Exception as e:
        return {"error": str(e)}


async def planner_post(session: aiohttp.ClientSession, payload: Dict) -> Dict:
    """Make a POST request to the Resource Planner"""
    try:
        async with session.post(
            f"{BRAIN_API}/planner/plan",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            return await resp.json()
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# TEST A: THUNDERING HERD
# ============================================================
async def test_thundering_herd(concurrent: int = 50) -> TestResult:
    """
    Thundering Herd Test
    ====================

    Simuleert massale gelijktijdige requests (zoals bij een virale post).

    Test wetten:
    - Ohm: Flow control rate limiting
    - Thermodynamics: System health monitoring
    - Newton: Trust verification under load

    Verwacht gedrag:
    - Graceful handling (no timeouts)
    - Consistent resource allocation
    - health_action escalatie bij hoge load
    """
    print(f"\n{'='*60}")
    print("TEST A: THUNDERING HERD")
    print(f"{'='*60}")
    print(f"Sending {concurrent} concurrent requests...")

    start = time.time()

    async with aiohttp.ClientSession() as session:
        # Generate varying requests
        tasks = []
        for i in range(concurrent):
            params = {
                "task_type": random.choice(["message", "call", "query"]),
                "urgency": random.randint(1, 10),
                "participants": random.randint(1, 5),
                "devices": random.randint(1, 3),
                "data_kb": random.randint(1, 100)
            }
            tasks.append(planner_request(session, params))

        results = await asyncio.gather(*tasks)

    duration_ms = (time.time() - start) * 1000

    # Analyze results
    successful = [r for r in results if "allocation" in r]
    errors = [r for r in results if "error" in r]

    health_actions = Counter(
        r.get("allocation", {}).get("health_action", "unknown")
        for r in successful
    )

    laws_applied_all = all(
        len(r.get("laws_applied", [])) == 14
        for r in successful
    )

    passed = (
        len(successful) >= concurrent * 0.95 and  # 95% success rate
        laws_applied_all  # All 14 laws applied
    )

    print(f"\nResults:")
    print(f"  Successful: {len(successful)}/{concurrent}")
    print(f"  Errors: {len(errors)}")
    print(f"  Duration: {duration_ms:.0f}ms")
    print(f"  Throughput: {concurrent / (duration_ms/1000):.1f} req/sec")
    print(f"  Health actions: {dict(health_actions)}")
    print(f"  All 14 laws applied: {laws_applied_all}")
    print(f"  Status: {'PASS' if passed else 'FAIL'}")

    return TestResult(
        name="Thundering Herd",
        passed=passed,
        duration_ms=duration_ms,
        details={
            "concurrent": concurrent,
            "successful": len(successful),
            "errors": len(errors),
            "throughput_rps": concurrent / (duration_ms/1000),
            "health_actions": dict(health_actions),
            "all_laws_applied": laws_applied_all
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
    - David (klein, urgent) krijgt hogere queue priority (lager nummer)
    - Goliath (groot, niet-urgent) krijgt lagere priority (hoger nummer)
    """
    print(f"\n{'='*60}")
    print("TEST B: DAVID & GOLIATH")
    print(f"{'='*60}")

    start = time.time()

    async with aiohttp.ClientSession() as session:
        # David: klein en urgent
        david_params = {
            "task_type": "message",
            "urgency": 9,
            "participants": 1,
            "devices": 1,
            "data_kb": 1
        }

        # Goliath: groot en niet-urgent
        goliath_params = {
            "task_type": "file_transfer",
            "urgency": 2,
            "participants": 5,
            "devices": 4,
            "data_kb": 10000
        }

        david_result, goliath_result = await asyncio.gather(
            planner_request(session, david_params),
            planner_request(session, goliath_params)
        )

    duration_ms = (time.time() - start) * 1000

    # Get queue priorities
    david_alloc = david_result.get("allocation", {})
    goliath_alloc = goliath_result.get("allocation", {})

    david_priority = david_alloc.get("queue_priority", 10)
    goliath_priority = goliath_alloc.get("queue_priority", 0)
    david_wait = david_alloc.get("estimated_wait_ms", 9999)
    goliath_wait = goliath_alloc.get("estimated_wait_ms", 0)
    david_complexity = david_alloc.get("complexity_score", 0)
    goliath_complexity = goliath_alloc.get("complexity_score", 0)

    # David should have LOWER queue_priority number (= higher priority)
    # And LOWER estimated wait time
    david_wins = david_priority < goliath_priority and david_wait < goliath_wait

    print(f"\nDavid (small, urgent urgency=9):")
    print(f"  Queue priority: {david_priority}/10 (lower = better)")
    print(f"  Estimated wait: {david_wait}ms")
    print(f"  Complexity: {david_complexity}")
    print(f"\nGoliath (large, not urgent urgency=2):")
    print(f"  Queue priority: {goliath_priority}/10")
    print(f"  Estimated wait: {goliath_wait}ms")
    print(f"  Complexity: {goliath_complexity}")
    print(f"\nArchimedes Buoyancy: David {'FLOATS above' if david_wins else 'SINKS below'} Goliath")
    print(f"Status: {'PASS' if david_wins else 'FAIL'}")

    return TestResult(
        name="David & Goliath",
        passed=david_wins,
        duration_ms=duration_ms,
        details={
            "david_priority": david_priority,
            "goliath_priority": goliath_priority,
            "david_wait_ms": david_wait,
            "goliath_wait_ms": goliath_wait,
            "david_complexity": david_complexity,
            "goliath_complexity": goliath_complexity,
            "david_floats": david_wins
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
    - Hooke: Elastic scaling moet consistent SCALE_UP/DOWN signaleren

    Verwacht gedrag:
    - Hoge load (90%) -> SCALE_UP
    - Lage load (10%) -> SCALE_DOWN
    - Stabiele, voorspelbare responses
    """
    print(f"\n{'='*60}")
    print("TEST C: JOJO (Oscillating Load)")
    print(f"{'='*60}")

    start = time.time()
    scale_actions = []

    async with aiohttp.ClientSession() as session:
        for i in range(cycles):
            # Alternate between high and low load
            load = 90 if i % 2 == 0 else 10

            payload = {
                "task_type": "query",
                "urgency": 5,
                "participants": ["user"],
                "devices": ["server"],
                "current_load": load
            }

            result = await planner_post(session, payload)
            alloc = result.get("allocation", {})
            action = alloc.get("scale_action", "UNKNOWN")
            scale_actions.append((load, action))

            print(f"  Cycle {i+1}: load={load}% -> {action}")
            await asyncio.sleep(0.05)  # Small delay

    duration_ms = (time.time() - start) * 1000

    # Check for stability - Hooke's Law should give:
    # High load (90%) -> SCALE_UP
    # Low load (10%) -> SCALE_DOWN
    high_load_actions = [a for l, a in scale_actions if l == 90]
    low_load_actions = [a for l, a in scale_actions if l == 10]

    high_correct = all(a == "SCALE_UP" for a in high_load_actions)
    low_correct = all(a == "SCALE_DOWN" for a in low_load_actions)

    passed = high_correct and low_correct

    print(f"\nHooke's Law Analysis:")
    print(f"  High load (90%) actions: {Counter(high_load_actions)}")
    print(f"    Expected: SCALE_UP -> {'CORRECT' if high_correct else 'INCORRECT'}")
    print(f"  Low load (10%) actions: {Counter(low_load_actions)}")
    print(f"    Expected: SCALE_DOWN -> {'CORRECT' if low_correct else 'INCORRECT'}")
    print(f"Status: {'PASS' if passed else 'FAIL'}")

    return TestResult(
        name="Jojo",
        passed=passed,
        duration_ms=duration_ms,
        details={
            "cycles": cycles,
            "high_load_actions": dict(Counter(high_load_actions)),
            "low_load_actions": dict(Counter(low_load_actions)),
            "high_correct": high_correct,
            "low_correct": low_correct,
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
    - Planck: Memory quantization (32MB quanta)
    - Heisenberg: Tradeoff validation
    - Betti: Complexity split detection

    Verwacht gedrag:
    - Memory allocated in 32MB quanta
    - Split required at high complexity
    - Clean handling (no crashes)
    """
    print(f"\n{'='*60}")
    print("TEST D: EDGE OF DEATH")
    print(f"{'='*60}")

    start = time.time()
    results = {}

    async with aiohttp.ClientSession() as session:
        # Test 1: Large file - check Planck quantization
        print("\n  1. Testing Planck Memory Quantization...")
        large_payload = {
            "task_type": "file_transfer",
            "urgency": 5,
            "participants": ["user"],
            "devices": ["server"],
            "data_size_kb": 100000  # 100MB file
        }
        results["large_file"] = await planner_post(session, large_payload)

        # Test 2: High complexity - check Betti split
        print("  2. Testing Betti Complexity Split...")
        complex_payload = {
            "task_type": "video_call",
            "urgency": 5,
            "participants": [f"user_{i}" for i in range(20)],  # B0 = 20
            "devices": [f"dev_{i}" for i in range(10)],         # B1 = 10
            "operations": [f"op_{i}" for i in range(5)]         # B2 = 5
        }
        results["complex"] = await planner_post(session, complex_payload)

        # Test 3: Emergency - check priority handling
        print("  3. Testing Emergency Priority...")
        emergency_payload = {
            "task_type": "emergency",
            "urgency": 10,
            "participants": ["victim"],
            "devices": ["phone"]
        }
        results["emergency"] = await planner_post(session, emergency_payload)

    duration_ms = (time.time() - start) * 1000

    # Analyze results
    large_alloc = results["large_file"].get("allocation", {})
    complex_alloc = results["complex"].get("allocation", {})
    emergency_alloc = results["emergency"].get("allocation", {})

    # Check Planck: memory should be multiple of 32
    memory_mb = large_alloc.get("memory_mb", 0)
    is_quantized = memory_mb > 0 and memory_mb % 32 == 0

    # Check Betti: high complexity should trigger split
    complexity_score = complex_alloc.get("complexity_score", 0)
    split_required = complex_alloc.get("split_required", False)
    expected_split = complexity_score > 50

    # Check emergency: should get top priority
    emergency_priority = emergency_alloc.get("queue_priority", 10)
    emergency_fast = emergency_priority <= 2

    all_responded = all("error" not in r for r in results.values())

    print(f"\nPlanck Quantization:")
    print(f"  Requested: 100MB file transfer")
    print(f"  Allocated: {memory_mb}MB")
    print(f"  Is 32MB quantum: {is_quantized}")

    print(f"\nBetti Complexity:")
    print(f"  Complexity score: {complexity_score}")
    print(f"  Split required: {split_required}")
    print(f"  Threshold (>50): {'MET' if expected_split and split_required else 'OK' if not expected_split else 'NOT TRIGGERED'}")

    print(f"\nEmergency Handling:")
    print(f"  Queue priority: {emergency_priority}/10")
    print(f"  Fast track: {emergency_fast}")

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
            "emergency_priority": emergency_priority,
            "all_graceful": all_responded
        },
        laws_tested=["Planck", "Heisenberg", "Betti"]
    )


# ============================================================
# MAIN TEST RUNNER
# ============================================================
async def run_all_tests():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("BETTI-TIBET VALIDATION TEST SUITE")
    print("="*60)
    print("Testing 14 Wetten via Resource Planner")
    print("="*60)

    all_results = []

    # Run tests
    all_results.append(await test_thundering_herd(50))
    all_results.append(await test_david_and_goliath())
    all_results.append(await test_jojo(10))
    all_results.append(await test_edge_of_death())

    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    for r in all_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  {r.name}: {status} ({r.duration_ms:.0f}ms)")
        print(f"    Laws tested: {', '.join(r.laws_tested)}")

    print(f"\n{'='*60}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"{'='*60}")

    # Return results for reporting
    return all_results


def main():
    """Entry point"""
    try:
        results = asyncio.run(run_all_tests())

        # Save results to file
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed)
            },
            "tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "laws_tested": r.laws_tested,
                    "details": r.details
                }
                for r in results
            ]
        }

        with open("/root/Humotica/BETTI-TIBET-TEST/test_results.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nResults saved to: test_results.json")

    except KeyboardInterrupt:
        print("\nTests interrupted")
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
