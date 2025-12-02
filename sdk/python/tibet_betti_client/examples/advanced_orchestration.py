#!/usr/bin/env python3
"""
Advanced Orchestration Example - TIBET-BETTI SDK v2.0
======================================================

Demonstrates the new Humotica Layer features:
- Automatic intent parsing from raw input
- Dynamic voltage scaling based on urgency
- Thermal monitoring and protection
- Unified orchestration flow

Philosophy:
"Het doorgeefluik voor alle input van data en taak"
- Storage: Vacuum (instant availability)
- RAM: Steady flow (not waterfalls)
- CPU: Adaptive voltage based on Archimedes urgency

Results:
ECO mode:         4368.62 events/sec (15-30W)
PERFORMANCE mode: 5882.50 events/sec (65-95W)
Boost:            +34.6% performance! 🚀
"""

import asyncio
import logging
from tibet_betti_client import (
    TibetBettiClient,
    VoltageController,
    VoltageProfile,
    IntentTechLayer,
    get_voltage_controller,
    get_intent_layer
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_orchestration():
    """
    Demo 1: Basic raw input → intent parsing → execution
    """
    print("\n" + "="*70)
    print("DEMO 1: Basic Orchestration Flow")
    print("="*70)

    # Initialize client
    client = TibetBettiClient(
        betti_url="http://localhost:18081",
        kit_url="http://localhost:8000",
        secret="demo-secret"
    )

    # Test various raw inputs
    test_inputs = [
        "call Jasper van der Meer",
        "what is the temperature in the living room?",
        "search for Python documentation",
        "status check"
    ]

    for raw_input in test_inputs:
        print(f"\n📥 Input: {raw_input}")
        result = await client.process_raw_input(raw_input)

        intent = result["intent"]
        print(f"   Intent Type: {intent.intent_type.value}")
        print(f"   Route: {intent.route.value}")
        print(f"   Urgency: {intent.urgency}/10")
        print(f"   Voltage Profile: {result['voltage_profile']}")

        if "voltage_profile_changed" in result:
            print(f"   ⚡ Profile changed: {result['voltage_profile_changed']['from']} → {result['voltage_profile_changed']['to']}")


async def demo_urgency_mapping():
    """
    Demo 2: Urgency-based automatic voltage scaling

    Archimedes Urgency Scale:
    10 = Emergency call (TURBO)
    7-9 = High priority (PERFORMANCE)
    4-6 = Normal operation (BALANCED)
    1-3 = Low priority (ECO)
    """
    print("\n" + "="*70)
    print("DEMO 2: Urgency-Based Voltage Scaling")
    print("="*70)

    voltage_controller = get_voltage_controller()
    await voltage_controller.start()

    urgency_scenarios = [
        (10, "Emergency call - incoming 112"),
        (8, "Urgent message - user waiting"),
        (5, "Normal query - no rush"),
        (2, "Background task - low priority")
    ]

    for urgency, description in urgency_scenarios:
        profile = await voltage_controller.profile_for_urgency(urgency)
        config = voltage_controller.PROFILES[profile]

        print(f"\n🎯 Urgency {urgency}/10: {description}")
        print(f"   → Profile: {profile.value}")
        print(f"   → CPU Freq: {config.cpu_min_freq_mhz}-{config.cpu_max_freq_mhz} MHz")
        print(f"   → Power Cap: {config.power_cap_watts}W" if config.power_cap_watts else "   → Power Cap: None (max)")
        print(f"   → Governor: {config.cpu_governor}")

    await voltage_controller.stop()


async def demo_thermal_protection():
    """
    Demo 3: Thermal monitoring and automatic throttling
    """
    print("\n" + "="*70)
    print("DEMO 3: Thermal Protection")
    print("="*70)

    voltage_controller = get_voltage_controller()
    await voltage_controller.start()

    # Check current temperature
    temp = await voltage_controller._get_cpu_temperature()
    if temp:
        print(f"\n🌡️  Current CPU Temperature: {temp:.1f}°C")
        print(f"   Thermal Threshold: {voltage_controller.thermal_threshold_celsius}°C")
        print(f"   Critical Threshold: {voltage_controller.thermal_critical_celsius}°C")

        if temp >= voltage_controller.thermal_critical_celsius:
            print("   🔥 CRITICAL! Would trigger emergency throttle")
        elif temp >= voltage_controller.thermal_threshold_celsius:
            print("   ⚠️  HIGH! Would downgrade from TURBO/PERFORMANCE")
        else:
            print("   ✅ SAFE - All profiles available")
    else:
        print("\n⚠️  Temperature monitoring not available (need lm-sensors)")
        print("   Install: apt-get install lm-sensors && sensors-detect")

    await voltage_controller.stop()


async def demo_full_pipeline():
    """
    Demo 4: Complete pipeline with real-world scenario

    Scenario: Emergency call routing system
    """
    print("\n" + "="*70)
    print("DEMO 4: Full Pipeline - Emergency Call Scenario")
    print("="*70)

    client = TibetBettiClient(
        betti_url="http://localhost:18081",
        kit_url="http://localhost:8000",
        secret="emergency-demo"
    )

    # Simulate emergency call sequence
    sequence = [
        ("status check", "1. Pre-flight check"),
        ("call 112 emergency", "2. Emergency call initiated"),
        ("connect to dispatch", "3. Connecting to emergency services"),
        ("what is caller location", "4. Location query"),
        ("background sync", "5. Post-call cleanup")
    ]

    for raw_input, step in sequence:
        print(f"\n{step}")
        print(f"   Input: {raw_input}")

        result = await client.process_raw_input(raw_input, session_id="emergency-001")
        intent = result["intent"]

        print(f"   → Urgency: {intent.urgency}/10")
        print(f"   → Route: {intent.route.value}")
        print(f"   → Voltage: {result['voltage_profile']}")

        if "voltage_profile_changed" in result:
            change = result['voltage_profile_changed']
            print(f"   ⚡ Profile: {change['from']} → {change['to']} ({change['reason']})")

        # Simulate processing time
        await asyncio.sleep(0.5)


async def demo_performance_comparison():
    """
    Demo 5: Performance comparison across voltage profiles

    Based on real benchmark results:
    ECO:         4368.62 events/sec
    PERFORMANCE: 5882.50 events/sec
    Boost:       +34.6%
    """
    print("\n" + "="*70)
    print("DEMO 5: Performance Comparison")
    print("="*70)

    voltage_controller = get_voltage_controller()
    await voltage_controller.start()

    # Benchmark data from server
    profiles_performance = {
        VoltageProfile.ECO: {
            "events_per_sec": 4368.62,
            "power_watts": "15-30W",
            "use_case": "Background tasks, idle"
        },
        VoltageProfile.BALANCED: {
            "events_per_sec": 5125.00,  # Estimated
            "power_watts": "45-65W",
            "use_case": "Normal operation"
        },
        VoltageProfile.PERFORMANCE: {
            "events_per_sec": 5882.50,
            "power_watts": "65-95W",
            "use_case": "High-priority tasks"
        },
        VoltageProfile.TURBO: {
            "events_per_sec": 6200.00,  # Estimated
            "power_watts": "95W+",
            "use_case": "Emergency/critical"
        }
    }

    print("\n📊 Performance Metrics (HP DL360 Server):")
    print("-" * 70)

    baseline = profiles_performance[VoltageProfile.ECO]["events_per_sec"]

    for profile, metrics in profiles_performance.items():
        events = metrics["events_per_sec"]
        boost = ((events - baseline) / baseline) * 100

        print(f"\n{profile.value.upper():15} | {events:8.2f} events/sec | {metrics['power_watts']:8} | {boost:+6.1f}%")
        print(f"                | Use: {metrics['use_case']}")

    print("\n" + "-" * 70)
    print(f"🚀 Total boost from ECO → PERFORMANCE: +34.6%")
    print(f"💡 Power efficiency: ~3x performance per watt (ECO mode)")

    await voltage_controller.stop()


async def demo_context_aware_routing():
    """
    Demo 6: Context-aware intent routing

    Shows how IntentTechLayer routes different tasks:
    - BETTI: Heavy compute (LLM, video)
    - KIT: Knowledge queries
    - DIRECT: Simple CRUD, status
    """
    print("\n" + "="*70)
    print("DEMO 6: Context-Aware Routing")
    print("="*70)

    intent_layer = get_intent_layer()
    await intent_layer.start()

    routing_examples = [
        ("transcribe this audio file", "BETTI", "Heavy compute (speech recognition)"),
        ("what is the capital of France", "KIT", "Knowledge query"),
        ("get user status", "DIRECT", "Simple CRUD operation"),
        ("search documentation for async", "KIT", "Semantic search"),
        ("call emergency contact", "DIRECT", "Direct action"),
        ("analyze this video for faces", "BETTI", "Heavy compute (video processing)")
    ]

    print("\n🔀 Routing Examples:")
    print("-" * 70)

    for raw_input, expected_route, description in routing_examples:
        result = await intent_layer.process(raw_input)
        intent = result["intent"]

        print(f"\n📥 '{raw_input}'")
        print(f"   → Route: {intent.route.value.upper()} ({description})")
        print(f"   → Type: {intent.intent_type.value}")
        print(f"   → Urgency: {intent.urgency}/10")

    await intent_layer.stop()


async def main():
    """
    Run all demos
    """
    print("\n" + "="*70)
    print("TIBET-BETTI SDK v2.0 - Advanced Orchestration Demos")
    print("="*70)
    print("\nHumotica Layer Integration:")
    print("- Voltage Control: Dynamic CPU/GPU performance")
    print("- Intent-Tech Layer: Central data/task orchestration")
    print("- Automatic scaling based on Archimedes urgency")
    print("\n" + "="*70)

    demos = [
        ("Basic Orchestration", demo_basic_orchestration),
        ("Urgency Mapping", demo_urgency_mapping),
        ("Thermal Protection", demo_thermal_protection),
        ("Full Pipeline", demo_full_pipeline),
        ("Performance Comparison", demo_performance_comparison),
        ("Context-Aware Routing", demo_context_aware_routing)
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n\n{'='*70}")
        print(f"Running Demo {i}/{len(demos)}: {name}")
        print(f"{'='*70}")

        try:
            await demo_func()
        except Exception as e:
            logger.error(f"Demo failed: {e}", exc_info=True)

        if i < len(demos):
            print("\n⏳ Next demo in 2 seconds...")
            await asyncio.sleep(2)

    print("\n\n" + "="*70)
    print("✅ All demos completed!")
    print("="*70)
    print("\n💡 Key Takeaways:")
    print("   - Raw input → Intent parsing → Voltage scaling (automatic)")
    print("   - 34.6% performance boost with PERFORMANCE mode")
    print("   - Thermal protection prevents overheating")
    print("   - Smart routing: BETTI (heavy), KIT (knowledge), DIRECT (simple)")
    print("\n🚀 Ready for production!")


if __name__ == "__main__":
    asyncio.run(main())
