"""
Intent-Tech Layer - Central Hub voor Data & Task Flow
=======================================================

Philosophy: "Het doorgeefluik voor alle input van data en taak"

This layer is the orchestration point where:
- All data inputs arrive (sensors, APIs, users, etc.)
- Intents are parsed and understood
- Tasks are routed to correct subsystems (BETTI, KIT, Direct)
- Context and state are maintained

Storage philosophy (Jasper): "Opslag is een vacuum waar niks is en input nergens
gelijk aan staat maar ineens ruimte inneemt" - treat storage as instant, pre-allocated space

RAM philosophy (Jasper): "RAM moet een constante doorloop zijn, alsof je waterstroom
volgt die steady is ipv watervallen" - steady flow, not burst patterns
"""

import asyncio
import logging
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class IntentRoute(Enum):
    """Where to route the intent"""
    BETTI = "betti"  # Heavy compute (LLM, video processing)
    KIT = "kit"  # Knowledge queries, semantic search
    DIRECT = "direct"  # Simple CRUD, status checks
    MULTI_STAGE = "multi_stage"  # Complex workflows


class IntentType(Enum):
    """Classification of intent types"""
    QUERY = "query"  # Information retrieval
    COMMAND = "command"  # Action to perform
    CONVERSATION = "conversation"  # Chat/dialogue
    SENSOR_DATA = "sensor_data"  # IoT sensor input
    SYSTEM_EVENT = "system_event"  # Internal system events


@dataclass
class ParsedIntent:
    """Result of intent parsing"""
    raw_input: str
    intent_type: IntentType
    route: IntentRoute
    urgency: int  # 1-10, for Archimedes buoyancy
    parameters: Dict[str, Any]
    confidence: float  # 0.0-1.0
    context: Dict[str, Any]
    timestamp: datetime


class IntentParser:
    """
    Parse raw input into structured intents

    Uses hybrid approach:
    - Regex patterns for simple commands
    - NLP/LLM for complex natural language
    - Context awareness for disambiguation
    """

    # Simple regex patterns for common intents
    PATTERNS = {
        r"(call|bel)\s+(.+)": (IntentType.COMMAND, IntentRoute.DIRECT, 9),  # High urgency
        r"(message|stuur)\s+(.+)": (IntentType.COMMAND, IntentRoute.DIRECT, 6),
        r"(search|zoek)\s+(.+)": (IntentType.QUERY, IntentRoute.KIT, 5),
        r"(status|health|check)": (IntentType.QUERY, IntentRoute.DIRECT, 3),
        r"(what|wat|hoe|why|waarom)\s+(.+)": (IntentType.CONVERSATION, IntentRoute.KIT, 5),
        r"temperature|temp|motion|sensor": (IntentType.SENSOR_DATA, IntentRoute.DIRECT, 4),
    }

    def __init__(self):
        self.context_window: List[ParsedIntent] = []
        self.max_context = 10

    async def parse(self, raw_input: str, context: Optional[Dict[str, Any]] = None) -> ParsedIntent:
        """
        Parse raw input into structured intent

        Args:
            raw_input: Raw text/data input
            context: Additional context (user_id, device, etc.)

        Returns:
            ParsedIntent with routing and parameters
        """
        raw_input = raw_input.strip()
        context = context or {}

        # Try regex patterns first (fast path)
        for pattern, (intent_type, route, urgency) in self.PATTERNS.items():
            match = re.search(pattern, raw_input, re.IGNORECASE)
            if match:
                return ParsedIntent(
                    raw_input=raw_input,
                    intent_type=intent_type,
                    route=route,
                    urgency=urgency,
                    parameters={"matches": match.groups()},
                    confidence=0.9,  # High confidence for pattern match
                    context=context,
                    timestamp=datetime.now()
                )

        # Fallback: Treat as conversation (route to KIT/LLM)
        return ParsedIntent(
            raw_input=raw_input,
            intent_type=IntentType.CONVERSATION,
            route=IntentRoute.KIT,
            urgency=5,  # Medium urgency
            parameters={},
            confidence=0.6,  # Lower confidence, needs LLM
            context=context,
            timestamp=datetime.now()
        )

    def add_to_context(self, intent: ParsedIntent):
        """Add intent to context window for future disambiguation"""
        self.context_window.append(intent)
        if len(self.context_window) > self.max_context:
            self.context_window.pop(0)


class SenseRouter:
    """
    Route intents to correct subsystem

    Routes:
    - BETTI: Heavy computational tasks
    - KIT: Knowledge queries
    - DIRECT: Simple operations
    - MULTI_STAGE: Complex workflows
    """

    def __init__(self):
        self.stats = {
            "total_routed": 0,
            "by_route": {route: 0 for route in IntentRoute}
        }

    async def route(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Route intent to appropriate handler

        Returns:
            Response from the handler
        """
        self.stats["total_routed"] += 1
        self.stats["by_route"][intent.route] += 1

        logger.info(f"📨 Routing intent: {intent.intent_type.value} → {intent.route.value} (urgency: {intent.urgency})")

        # Route based on intent.route
        if intent.route == IntentRoute.BETTI:
            return await self._route_to_betti(intent)
        elif intent.route == IntentRoute.KIT:
            return await self._route_to_kit(intent)
        elif intent.route == IntentRoute.DIRECT:
            return await self._route_direct(intent)
        elif intent.route == IntentRoute.MULTI_STAGE:
            return await self._route_multi_stage(intent)

        return {"error": "Unknown route"}

    async def _route_to_betti(self, intent: ParsedIntent) -> Dict[str, Any]:
        """Route to BETTI for heavy compute"""
        # TODO: Integrate with actual BETTI system
        logger.info(f"🧠 BETTI processing: {intent.raw_input}")
        return {
            "route": "betti",
            "status": "processed",
            "intent": intent.raw_input
        }

    async def _route_to_kit(self, intent: ParsedIntent) -> Dict[str, Any]:
        """Route to KIT for knowledge queries"""
        # TODO: Integrate with KIT system
        logger.info(f"📚 KIT processing: {intent.raw_input}")
        return {
            "route": "kit",
            "status": "processed",
            "intent": intent.raw_input
        }

    async def _route_direct(self, intent: ParsedIntent) -> Dict[str, Any]:
        """Handle directly (simple operations)"""
        logger.info(f"⚡ Direct processing: {intent.raw_input}")
        return {
            "route": "direct",
            "status": "processed",
            "intent": intent.raw_input
        }

    async def _route_multi_stage(self, intent: ParsedIntent) -> Dict[str, Any]:
        """Complex multi-stage workflow"""
        logger.info(f"🔄 Multi-stage processing: {intent.raw_input}")
        return {
            "route": "multi_stage",
            "status": "started",
            "intent": intent.raw_input
        }


class StateManager:
    """
    Manage context and state across conversations

    Philosophy:
    - Storage: Vacuum (instant write, pre-allocated)
    - RAM: Steady flow (constant access patterns)
    """

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.device_cache: Dict[str, Dict[str, Any]] = {}

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "history": [],
                "context": {}
            }
        return self.sessions[session_id]

    async def update_session(self, session_id: str, intent: ParsedIntent, response: Dict[str, Any]):
        """Update session with new interaction"""
        session = await self.get_session(session_id)
        session["history"].append({
            "intent": intent,
            "response": response,
            "timestamp": datetime.now()
        })

        # Keep only last 20 interactions (steady flow, not waterfall)
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]


class IntentTechLayer:
    """
    Main Intent-Tech Layer orchestrator

    Central hub for all data/task input
    """

    def __init__(self):
        self.parser = IntentParser()
        self.router = SenseRouter()
        self.state_manager = StateManager()
        self._started = False

    async def start(self):
        """Start Intent-Tech Layer"""
        if self._started:
            return

        logger.info("🚀 Starting Intent-Tech Layer")
        self._started = True

    async def stop(self):
        """Stop Intent-Tech Layer"""
        logger.info("🛑 Stopping Intent-Tech Layer")
        self._started = False

    async def process(
        self,
        raw_input: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process raw input through full pipeline

        Args:
            raw_input: Raw text/data input
            context: Additional context
            session_id: Session identifier for state management

        Returns:
            Response from routed handler
        """
        if not self._started:
            await self.start()

        # 1. Parse intent
        intent = await self.parser.parse(raw_input, context)
        self.parser.add_to_context(intent)

        # 2. Route to handler
        response = await self.router.route(intent)

        # 3. Update state if session provided
        if session_id:
            await self.state_manager.update_session(session_id, intent, response)

        return {
            "intent": intent,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }


# Global singleton
_intent_layer: Optional[IntentTechLayer] = None


def get_intent_layer() -> IntentTechLayer:
    """Get or create global Intent-Tech Layer"""
    global _intent_layer
    if _intent_layer is None:
        _intent_layer = IntentTechLayer()
    return _intent_layer
