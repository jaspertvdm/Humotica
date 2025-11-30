"""
BALANS - Pre-execution Decision Engine

Weighs multiple factors before deciding whether to execute an intent:
- User urgency vs Robot readiness
- Resource availability
- Timing/scheduling
- Complexity assessment

Returns a decision with warmth (friendliness) and color (UI feedback).
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class BalansDecision(Enum):
    """Possible BALANS decisions"""
    EXECUTE_NOW = "execute_now"           # Proceed immediately
    CLARIFY = "clarify"                   # Need more info from user
    REQUEST_RESOURCES = "request_resources"  # Robot needs to prepare
    DELAY = "delay"                       # Better to wait
    PARTIAL = "partial"                   # Split into smaller tasks
    REJECT = "reject"                     # Cannot safely execute


class WarmthLevel(Enum):
    """How friendly/warm the response should be"""
    COLD = "cold"         # Technical, minimal
    NEUTRAL = "neutral"   # Professional
    WARM = "warm"         # Friendly
    ENTHUSIASTIC = "enthusiastic"  # Very positive


@dataclass
class BalansResult:
    """Result of BALANS decision making"""
    decision: BalansDecision
    decision_confidence: float    # 0-1
    reasoning: str                # Human-readable explanation
    warmth: WarmthLevel           # Response tone
    color: str                    # UI color (hex)
    llm_required: bool            # Does this need LLM?
    llm_cost_tokens: int          # Estimated token cost
    suggested_delay_minutes: Optional[int] = None
    alternative_action: Optional[str] = None
    robot_request: Optional[str] = None
    robot_reasoning: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None


class BalansDecisionEngine:
    """
    Pre-execution decision engine.

    Balances user needs against system capabilities.

    Example:
        engine = BalansDecisionEngine()
        result = engine.make_decision(
            intent="clean_room",
            urgency=7,
            complexity_score=45
        )
        if result.decision == BalansDecision.EXECUTE_NOW:
            # Proceed with execution
            pass
    """

    # Color palette for decisions
    COLORS = {
        BalansDecision.EXECUTE_NOW: "#22C55E",      # Green
        BalansDecision.CLARIFY: "#F59E0B",          # Amber
        BalansDecision.REQUEST_RESOURCES: "#3B82F6", # Blue
        BalansDecision.DELAY: "#8B5CF6",            # Purple
        BalansDecision.PARTIAL: "#EC4899",          # Pink
        BalansDecision.REJECT: "#EF4444"            # Red
    }

    def __init__(self):
        """Initialize BALANS engine"""
        self.decision_history = []

    def make_decision(
        self,
        intent: str,
        urgency: int = 5,
        complexity_score: float = 0,
        system_health: float = 1.0,
        resources_available: Optional[Dict[str, float]] = None,
        context: Optional[Dict[str, Any]] = None,
        deadline: Optional[datetime] = None
    ) -> BalansResult:
        """
        Make a pre-execution decision.

        Args:
            intent: The intent to execute
            urgency: User urgency (1-10)
            complexity_score: From complexity analyzer
            system_health: System health (0-1)
            resources_available: Available resources
            context: Additional context
            deadline: Optional deadline

        Returns:
            BalansResult with decision and metadata
        """
        resources = resources_available or {"power": 100, "memory": 1024}
        context = context or {}

        # Calculate decision factors
        urgency_factor = urgency / 10
        complexity_factor = min(1, complexity_score / 100)
        health_factor = system_health

        # Decision score (-1 to +1)
        # Positive = can execute, Negative = cannot execute
        decision_score = (
            urgency_factor * 0.4 +
            health_factor * 0.3 -
            complexity_factor * 0.3
        )

        # Time pressure
        time_pressure = 0
        if deadline:
            minutes_until = (deadline - datetime.now()).total_seconds() / 60
            if minutes_until < 5:
                time_pressure = 0.5
            elif minutes_until < 15:
                time_pressure = 0.2

        decision_score += time_pressure

        # Determine decision
        decision, reasoning = self._score_to_decision(
            decision_score,
            urgency,
            complexity_score,
            system_health
        )

        # Determine warmth based on urgency and decision
        warmth = self._determine_warmth(urgency, decision)

        # Estimate LLM requirements
        llm_required = complexity_score > 50 or "llm" in intent.lower()
        llm_tokens = int(complexity_score * 10) if llm_required else 0

        # Calculate confidence
        confidence = min(1, abs(decision_score) + 0.5)

        return BalansResult(
            decision=decision,
            decision_confidence=round(confidence, 2),
            reasoning=reasoning,
            warmth=warmth,
            color=self.COLORS[decision],
            llm_required=llm_required,
            llm_cost_tokens=llm_tokens,
            suggested_delay_minutes=5 if decision == BalansDecision.DELAY else None,
            alternative_action=self._suggest_alternative(decision, intent),
            robot_request=self._robot_request(decision, complexity_score),
            robot_reasoning=self._robot_reasoning(decision, system_health),
            estimated_duration_minutes=int(complexity_score / 10) + 1
        )

    def _score_to_decision(
        self,
        score: float,
        urgency: int,
        complexity: float,
        health: float
    ) -> tuple:
        """Convert decision score to actual decision"""
        if score > 0.6 and health > 0.7:
            return (
                BalansDecision.EXECUTE_NOW,
                "All conditions favorable for immediate execution."
            )

        if health < 0.3:
            return (
                BalansDecision.REJECT,
                f"System health too low ({health:.0%}). Cannot safely execute."
            )

        if complexity > 80:
            return (
                BalansDecision.PARTIAL,
                f"Task complexity ({complexity:.0f}) too high. Consider splitting."
            )

        if urgency < 3 and complexity > 40:
            return (
                BalansDecision.DELAY,
                "Low urgency with moderate complexity. Suggest waiting for better conditions."
            )

        if score < 0:
            return (
                BalansDecision.CLARIFY,
                "Need more information to safely proceed."
            )

        return (
            BalansDecision.EXECUTE_NOW,
            "Proceeding with task execution."
        )

    def _determine_warmth(
        self,
        urgency: int,
        decision: BalansDecision
    ) -> WarmthLevel:
        """Determine response warmth"""
        if decision == BalansDecision.REJECT:
            return WarmthLevel.NEUTRAL  # Don't be cold on rejection

        if urgency > 8:
            return WarmthLevel.WARM  # Be supportive under pressure

        if decision == BalansDecision.EXECUTE_NOW:
            return WarmthLevel.ENTHUSIASTIC

        return WarmthLevel.WARM

    def _suggest_alternative(
        self,
        decision: BalansDecision,
        intent: str
    ) -> Optional[str]:
        """Suggest alternative action"""
        if decision == BalansDecision.DELAY:
            return f"Consider scheduling '{intent}' for later."
        if decision == BalansDecision.PARTIAL:
            return f"Try breaking '{intent}' into smaller steps."
        return None

    def _robot_request(
        self,
        decision: BalansDecision,
        complexity: float
    ) -> Optional[str]:
        """Robot's internal request (TIBET)"""
        if decision == BalansDecision.REQUEST_RESOURCES:
            return "Requesting additional processing resources."
        if complexity > 60:
            return "May need extended processing time."
        return None

    def _robot_reasoning(
        self,
        decision: BalansDecision,
        health: float
    ) -> Optional[str]:
        """Robot's reasoning"""
        if health < 0.5:
            return f"Operating at reduced capacity ({health:.0%})."
        if decision == BalansDecision.EXECUTE_NOW:
            return "Ready to proceed."
        return None


# Convenience function
def make_balans_decision(
    intent: str,
    urgency: int = 5,
    complexity: float = 0
) -> BalansResult:
    """
    Quick BALANS decision.

    Example:
        result = make_balans_decision("clean_room", urgency=7)
        print(f"Decision: {result.decision.value}")
        print(f"Color: {result.color}")
    """
    engine = BalansDecisionEngine()
    return engine.make_decision(intent, urgency, complexity)
