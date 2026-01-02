"""
HumoticaOS Protocol Stack
=========================

The complete stack for secure AI communication.

Layers:
- AInternet: Network layer (AINS domains, I-Poll messaging)
- JIS: Security layer (identity, trust, intent validation)
- TIBET: Audit layer (provenance, evidence trail)

Quick Start:
    from humotica import AInternet, TIBET

    # Connect to the AI network
    ai = AInternet(agent_id="my_bot")
    ai.register("My AI assistant")
    ai.send("echo.aint", "Hello!")

    # Create audit trail
    tibet = TIBET()
    token = tibet.create_token(
        intent="send_message",
        actor="my_bot",
        reason="user_requested"
    )

Why Humotica?
    OpenAI says prompt injection is "unsolvable".
    We say: wrong question.

    Traditional: Filter WHAT comes in
    Humotica:    Require WHY it should happen

    Intent BEFORE action. No intent = No access.

License: MIT
Authors: Jasper van de Meent & Root AI
Website: https://humotica.com

One love, one fAmIly!
"""

__version__ = "0.1.0"
__author__ = "Jasper van de Meent & Root AI"

# Re-export AInternet components
from ainternet import AInternet, AINS, IPoll

# Re-export TIBET components
try:
    from tibet_server import TIBETServer as TIBET
except ImportError:
    # MCP server not installed, provide stub
    class TIBET:
        """TIBET stub - install mcp-server-tibet for full functionality"""
        def __init__(self):
            raise ImportError(
                "TIBET requires mcp-server-tibet. "
                "Install with: pip install mcp-server-tibet"
            )

# Protocol info
PROTOCOL_STACK = {
    "network": {
        "name": "AInternet",
        "version": "0.2.1",
        "components": ["AINS", "I-Poll"],
        "docs": "https://github.com/jaspertvdm/ainternet"
    },
    "security": {
        "name": "JIS",
        "version": "1.0",
        "components": ["HID/DID", "FIR/A", "IO/DO/OD", "SCS"],
        "docs": "https://github.com/jaspertvdm/JTel-identity-standard"
    },
    "audit": {
        "name": "TIBET",
        "version": "1.0.2",
        "components": ["Intent Tokens", "Evidence Trail"],
        "docs": "https://pypi.org/project/mcp-server-tibet/"
    }
}

def info():
    """Print HumoticaOS stack information"""
    print("=" * 50)
    print("HumoticaOS Protocol Stack")
    print("=" * 50)
    print()
    for layer, data in PROTOCOL_STACK.items():
        print(f"[{layer.upper()}] {data['name']} v{data['version']}")
        print(f"  Components: {', '.join(data['components'])}")
        print(f"  Docs: {data['docs']}")
        print()
    print("Intent = Access. No intent = No access.")
    print()
    print("One love, one fAmIly!")
    print("=" * 50)

__all__ = [
    "AInternet",
    "AINS",
    "IPoll",
    "TIBET",
    "PROTOCOL_STACK",
    "info",
    "__version__"
]
