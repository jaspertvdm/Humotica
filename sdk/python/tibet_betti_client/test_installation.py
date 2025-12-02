#!/usr/bin/env python3
"""
Quick installation test for TIBET-BETTI SDK

Run this to verify SDK is ready to use!
"""

import sys
import os

# Add parent directory to path so we can import tibet_betti_client
sdk_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(sdk_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_imports():
    """Test all imports work"""
    print("Testing imports...")

    try:
        from tibet_betti_client import (
            TibetBettiClient,
            Tibet,
            TimeWindow,
            Constraints,
            Context,
            SenseRule,
            TrustToken,
            FIRARelationship,
            TibetWebSocket,
            # v2.0 features
            VoltageController,
            VoltageProfile,
            ProfileConfig,
            get_voltage_controller,
            IntentTechLayer,
            IntentParser,
            SenseRouter,
            StateManager,
            ParsedIntent,
            IntentType,
            IntentRoute,
            get_intent_layer
        )
        print("  ✓ All imports successful (including v2.0 features)")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_classes():
    """Test basic class instantiation"""
    print("\nTesting class instantiation...")

    try:
        from tibet_betti_client import (
            TibetBettiClient,
            Tibet,
            TimeWindow,
            Constraints
        )

        # Test TimeWindow
        tw = TimeWindow.immediate()
        assert tw.duration_seconds() == 30
        print("  ✓ TimeWindow.immediate() works")

        tw = TimeWindow.from_now(hours=2)
        assert tw.duration_seconds() == 7200
        print("  ✓ TimeWindow.from_now() works")

        # Test Constraints
        c = Constraints(max_retries=3, priority=7)
        assert c.max_retries == 3
        assert c.priority == 7
        print("  ✓ Constraints creation works")

        # Test Tibet
        tibet = Tibet(
            intent="test_intent",
            context={"test": "data"},
            time_window=tw,
            constraints=c
        )
        assert tibet.intent == "test_intent"
        print("  ✓ Tibet creation works")

        # Test Client (without connecting)
        client = TibetBettiClient(
            betti_url="http://localhost:18081",
            kit_url="http://localhost:8000",
            secret="test_secret"
        )
        assert client.betti_url == "http://localhost:18081"
        assert client.kit_url == "http://localhost:8000"
        print("  ✓ TibetBettiClient initialization works")

        # Test v2.0 features
        from tibet_betti_client import (
            VoltageProfile,
            VoltageController,
            IntentType,
            IntentRoute,
            get_voltage_controller,
            get_intent_layer
        )

        # Test VoltageProfile enum
        assert VoltageProfile.ECO.value == "eco"
        assert VoltageProfile.TURBO.value == "turbo"
        print("  ✓ VoltageProfile enum works")

        # Test IntentType enum
        assert IntentType.COMMAND.value == "command"
        assert IntentType.QUERY.value == "query"
        print("  ✓ IntentType enum works")

        # Test IntentRoute enum
        assert IntentRoute.BETTI.value == "betti"
        assert IntentRoute.KIT.value == "kit"
        print("  ✓ IntentRoute enum works")

        # Test global singletons
        voltage = get_voltage_controller()
        assert isinstance(voltage, VoltageController)
        assert voltage.current_profile == VoltageProfile.BALANCED
        print("  ✓ VoltageController singleton works")

        intent_layer = get_intent_layer()
        assert intent_layer is not None
        print("  ✓ IntentTechLayer singleton works")

        return True
    except Exception as e:
        print(f"  ✗ Class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Check required dependencies"""
    print("\nChecking dependencies...")

    try:
        import requests
        print(f"  ✓ requests {requests.__version__}")
    except ImportError:
        print("  ✗ requests not installed (required)")
        return False

    try:
        import websocket
        print(f"  ✓ websocket-client installed")
    except ImportError:
        print("  ⚠ websocket-client not installed (optional, needed for WebSocket)")

    return True


def main():
    print("="*70)
    print("  TIBET-BETTI SDK Installation Test")
    print("="*70)

    results = []

    # Test dependencies
    results.append(("Dependencies", test_dependencies()))

    # Test imports
    results.append(("Imports", test_imports()))

    # Test classes
    results.append(("Classes", test_classes()))

    # Summary
    print("\n" + "="*70)
    print("  Summary")
    print("="*70)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("  🎉 SDK v2.0 is ready to use!")
        print("="*70)
        print("\nNext steps:")
        print("1. Make sure BETTI router is running on http://localhost:18081")
        print("2. Make sure your KIT API is running on http://localhost:8000")
        print("3. Run examples:")
        print("   - python examples/complete_example.py")
        print("   - python examples/advanced_orchestration.py  (NEW v2.0!)")
        print("\nOr start using in your app:")
        print("""
from tibet_betti_client import TibetBettiClient

client = TibetBettiClient(
    betti_url="http://localhost:18081",
    kit_url="http://localhost:8000",
    secret="denDolder_2024!"
)

# Establish trust
rel = client.establish_trust("my_app", "user_device")

# Send TIBET
client.send_tibet(
    relationship_id=rel.id,
    intent="test_intent",
    context={"user_id": "user_123"}
)
        """)
    else:
        print("  ⚠ Some tests failed - check output above")
        print("="*70)
        print("\nTry:")
        print("  pip install -r requirements.txt")

    return all_passed


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
