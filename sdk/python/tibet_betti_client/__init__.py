"""
TIBET-BETTI Python SDK

Complete client library for TIBET intent declaration and BETTI coordination.

Usage:
    from tibet_betti_client import TibetBettiClient, Tibet, Context

    # Initialize client
    client = TibetBettiClient(
        betti_url="http://localhost:18081",
        kit_url="http://localhost:8000",  # Your existing API!
        secret="your-secret"
    )

    # Establish relationship
    relationship = client.establish_trust("my_app", "user_device")

    # Send TIBET intent
    client.send_tibet(
        relationship_id=relationship.id,
        intent="turn_on_lights",
        context={"room": "living_room", "brightness": 80}
    )
"""

from .client import TibetBettiClient
from .tibet import Tibet, TimeWindow, Constraints
from .context import Context, SenseRule
from .trust_token import TrustToken, FIRARelationship
from .websocket import TibetWebSocket
from .balancer import ClientBalancer, balanced, configure, get_balancer
from .voltage_controller import (
    VoltageController,
    VoltageProfile,
    ProfileConfig,
    get_voltage_controller
)
from .intent_tech_layer import (
    IntentTechLayer,
    IntentParser,
    SenseRouter,
    StateManager,
    ParsedIntent,
    IntentType,
    IntentRoute,
    get_intent_layer
)

__version__ = "2.0.0"  # Major version bump for new features
__all__ = [
    "TibetBettiClient",
    "Tibet",
    "TimeWindow",
    "Constraints",
    "Context",
    "SenseRule",
    "TrustToken",
    "FIRARelationship",
    "TibetWebSocket",
    "ClientBalancer",
    "balanced",
    "configure",
    "get_balancer",
    # Voltage Control (v2.0)
    "VoltageController",
    "VoltageProfile",
    "ProfileConfig",
    "get_voltage_controller",
    # Intent-Tech Layer (v2.0)
    "IntentTechLayer",
    "IntentParser",
    "SenseRouter",
    "StateManager",
    "ParsedIntent",
    "IntentType",
    "IntentRoute",
    "get_intent_layer"
]
