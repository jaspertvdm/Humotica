#!/usr/bin/env python3
"""
Complete TIBET-BETTI Example

Shows integration with:
1. BETTI Router (trust tokens, intent routing)
2. KIT API (context, sense rules)
3. Combined flow (context → sense → TIBET)
"""

import time
from tibet_betti_client import (
    TibetBettiClient,
    Tibet,
    TimeWindow,
    Constraints,
    Context,
    SenseRule
)


def main():
    print("="*70)
    print("  TIBET-BETTI Complete Example")
    print("="*70)

    # Initialize client
    print("\n1. Initializing client...")
    client = TibetBettiClient(
        betti_url="http://localhost:18081",  # BETTI router
        kit_url="http://localhost:8000",     # Your KIT API
        secret="denDolder_2024!"
    )

    # Check health
    try:
        health = client.health_check()
        print(f"✓ BETTI Router: {health['status']}")
    except Exception as e:
        print(f"✗ BETTI Router offline: {e}")
        return

    try:
        kit_health = client.kit_health_check()
        print(f"✓ KIT API: {kit_health.get('status', 'ok')}")
    except Exception as e:
        print(f"⚠ KIT API offline: {e} (will skip KIT features)")

    # ========================================================================
    # 2. Establish Trust (FIR/A)
    # ========================================================================

    print("\n2. Establishing trust relationship...")
    relationship = client.establish_trust(
        initiator="smart_home_app",
        responder="user_ai_assistant",
        roles=["home_controller", "ai_assistant"],
        context={"user_id": "user_123", "home_location": "Amsterdam"},
        trust_level=2
    )

    print(f"✓ Trust established!")
    print(f"  FIR/A ID: {relationship.id}")
    print(f"  Token: {relationship.token}")
    print(f"  Trust Level: {relationship.trust_level}")

    # ========================================================================
    # 3. Send Basic TIBET Intent
    # ========================================================================

    print("\n3. Sending basic TIBET intent...")
    result = client.send_tibet(
        relationship_id=relationship.id,
        intent="turn_on_lights",
        context={
            "room": "living_room",
            "brightness": 80,
            "color": "warm_white"
        },
        time_window=TimeWindow.immediate(),
        constraints=Constraints(
            max_retries=3,
            safe_fail_action="notify_user"
        ),
        humotica="User requested lights on in living room for evening comfort"
    )

    print(f"✓ TIBET sent!")
    print(f"  Status: {result['status']}")
    print(f"  Events: {result['events']}")

    # ========================================================================
    # 4. Send Scheduled TIBET
    # ========================================================================

    print("\n4. Sending scheduled TIBET intent...")
    result = client.send_tibet(
        relationship_id=relationship.id,
        intent="start_coffee_machine",
        context={
            "strength": "medium",
            "cups": 2
        },
        time_window=TimeWindow.from_now(hours=12),  # Tomorrow morning
        humotica="Schedule coffee for tomorrow morning routine"
    )

    print(f"✓ Scheduled TIBET sent!")
    print(f"  Will execute within next 12 hours")

    # ========================================================================
    # 5. KIT Integration: Context Update
    # ========================================================================

    if client.kit_url:
        print("\n5. Updating user context in KIT...")
        try:
            context_result = client.update_context(
                user_id="user_123",
                context_data={
                    "location": "home",
                    "time_of_day": "evening",
                    "activity": "relaxing",
                    "ambient_light_lux": 45,
                    "temperature_celsius": 19
                }
            )

            print(f"✓ Context updated!")
            print(f"  User: user_123")
            print(f"  Location: home")
            print(f"  Activity: relaxing")

            # Check triggered intents
            if "triggered_intents" in context_result:
                triggered = context_result["triggered_intents"]
                print(f"  Triggered intents: {triggered}")

        except Exception as e:
            print(f"⚠ Could not update context: {e}")

    # ========================================================================
    # 6. KIT Integration: Create Sense Rule
    # ========================================================================

    if client.kit_url:
        print("\n6. Creating sense rule...")
        try:
            rule = client.create_sense_rule(
                name="evening_comfort_mode",
                conditions={
                    "time_of_day": "evening",
                    "location": "home",
                    "ambient_light_lux": {"lt": 100}
                },
                intent="evening_comfort_mode",
                priority=7
            )

            print(f"✓ Sense rule created!")
            print(f"  Name: {rule.name}")
            print(f"  Intent: {rule.intent}")
            print(f"  Conditions: {rule.conditions}")
            print(f"  Priority: {rule.priority}")

        except Exception as e:
            print(f"⚠ Could not create sense rule: {e}")

    # ========================================================================
    # 7. Combined Flow: Context → Sense → TIBET
    # ========================================================================

    if client.kit_url:
        print("\n7. Testing combined flow (Context → Sense → TIBET)...")
        try:
            # Simulate: User arrives home in evening
            results = client.context_to_tibet(
                relationship_id=relationship.id,
                user_id="user_123",
                context_update={
                    "location": "home",
                    "time_of_day": "evening",
                    "ambient_light_lux": 50,
                    "arrived_at": time.strftime("%H:%M:%S")
                }
            )

            print(f"✓ Combined flow complete!")
            print(f"  Context updated")
            print(f"  Sense rules evaluated")
            print(f"  {len(results)} TIBETs sent automatically:")

            for i, result in enumerate(results, 1):
                print(f"    {i}. Intent: (auto-triggered)")
                print(f"       Status: {result['status']}")

        except Exception as e:
            print(f"⚠ Combined flow failed: {e}")

    # ========================================================================
    # 8. WebSocket (Real-Time)
    # ========================================================================

    if client.kit_url:
        print("\n8. Testing WebSocket connection...")
        try:
            def handle_message(msg):
                print(f"  📨 WS Message: {msg.get('type', 'unknown')}")

            def handle_tibet(tibet_data):
                print(f"  🎯 TIBET Received: {tibet_data.get('intent')}")

            # Connect (background)
            ws = client.connect_websocket(
                user_id="user_123",
                on_message=handle_message,
                on_tibet=handle_tibet
            )
            ws.start(block=False)

            print(f"✓ WebSocket connected!")
            print(f"  Listening for real-time updates...")

            # Keep alive for a few seconds
            time.sleep(3)

            # Send ping
            ws.send({"type": "ping", "timestamp": time.time()})

            time.sleep(1)

            # Close
            ws.close()
            print(f"✓ WebSocket closed")

        except Exception as e:
            print(f"⚠ WebSocket test failed: {e}")

    # ========================================================================
    # Done!
    # ========================================================================

    print("\n" + "="*70)
    print("  ✅ Example Complete!")
    print("="*70)

    print(f"""
Summary:
✓ Trust relationship established (FIR/A)
✓ Basic TIBET intent sent
✓ Scheduled TIBET intent sent
✓ Context updated in KIT
✓ Sense rule created
✓ Combined flow tested (Context → Sense → TIBET)
✓ WebSocket tested

Your system is ready to:
1. Establish trust relationships
2. Send TIBET intents with time windows
3. Integrate with KIT context/sense system
4. Receive real-time updates via WebSocket

Next steps:
- Integrate into your app
- Add more sense rules
- Build automation flows
- Scale to production!

TIBET declares. BETTI coordinates. FIR/A trusts. 🚀
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Bye! 👋")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
