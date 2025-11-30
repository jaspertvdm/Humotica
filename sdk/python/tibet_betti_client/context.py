"""
Context and Sense Rule classes for KIT API integration
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Context:
    """
    User context for intent evaluation

    Context contains all relevant information about the user's current state,
    which is used by sense rules to determine which intents to trigger.
    """

    user_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    updated_at: Optional[datetime] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        """Set context value"""
        self.data[key] = value
        self.updated_at = datetime.utcnow()

    def update(self, updates: Dict[str, Any]):
        """Update multiple context values"""
        self.data.update(updates)
        self.updated_at = datetime.utcnow()

    def matches(self, conditions: Dict[str, Any]) -> bool:
        """
        Check if context matches conditions

        Args:
            conditions: Conditions to match

        Returns:
            True if all conditions match

        Example:
            >>> context = Context(user_id="123", data={"temp": 25, "location": "home"})
            >>> context.matches({"location": "home", "temp": {"gte": 20}})
            True
        """
        for key, condition in conditions.items():
            value = self.data.get(key)

            if value is None:
                return False

            # Simple equality
            if not isinstance(condition, dict):
                if value != condition:
                    return False
                continue

            # Comparison operators
            if "eq" in condition and value != condition["eq"]:
                return False
            if "ne" in condition and value == condition["ne"]:
                return False
            if "gt" in condition and value <= condition["gt"]:
                return False
            if "gte" in condition and value < condition["gte"]:
                return False
            if "lt" in condition and value >= condition["lt"]:
                return False
            if "lte" in condition and value > condition["lte"]:
                return False
            if "in" in condition and value not in condition["in"]:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "user_id": self.user_id,
            "data": self.data,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        """Create from dict"""
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            user_id=data["user_id"],
            data=data.get("data", {}),
            updated_at=updated_at
        )


@dataclass
class SenseRule:
    """
    Sense rule for automatic intent triggering

    Sense rules monitor context and automatically trigger intents when
    conditions are met.

    Example:
        >>> rule = SenseRule(
        ...     name="evening_lights",
        ...     conditions={
        ...         "time_of_day": "evening",
        ...         "location": "home",
        ...         "ambient_light": {"lt": 100}
        ...     },
        ...     intent="turn_on_lights",
        ...     intent_context={"brightness": 80, "color": "warm"}
        ... )
    """

    name: str
    conditions: Dict[str, Any]
    intent: str
    intent_context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10 (higher = more important)
    enabled: bool = True
    rule_id: Optional[str] = None

    def evaluate(self, context: Context) -> bool:
        """
        Evaluate rule against context

        Args:
            context: Current user context

        Returns:
            True if rule should trigger
        """
        if not self.enabled:
            return False

        return context.matches(self.conditions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "name": self.name,
            "conditions": self.conditions,
            "intent": self.intent,
            "intent_context": self.intent_context,
            "priority": self.priority,
            "enabled": self.enabled,
            "rule_id": self.rule_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SenseRule":
        """Create from dict"""
        return cls(
            name=data["name"],
            conditions=data["conditions"],
            intent=data["intent"],
            intent_context=data.get("intent_context", {}),
            priority=data.get("priority", 5),
            enabled=data.get("enabled", True),
            rule_id=data.get("rule_id")
        )


class SenseEngine:
    """
    Local sense evaluation engine

    Can evaluate sense rules locally without calling KIT API.
    Useful for offline operation or reducing API calls.
    """

    def __init__(self):
        self.rules: List[SenseRule] = []

    def add_rule(self, rule: SenseRule):
        """Add sense rule"""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """Remove sense rule by name"""
        self.rules = [r for r in self.rules if r.name != rule_name]

    def evaluate(self, context: Context) -> List[str]:
        """
        Evaluate all rules against context

        Args:
            context: Current context

        Returns:
            List of intents that should be triggered
        """
        triggered = []

        # Sort by priority (highest first)
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            if rule.evaluate(context):
                triggered.append(rule.intent)

        return triggered

    def get_triggered_rules(self, context: Context) -> List[SenseRule]:
        """
        Get full rule objects that would trigger

        Args:
            context: Current context

        Returns:
            List of SenseRule objects that matched
        """
        triggered = []

        for rule in self.rules:
            if rule.evaluate(context):
                triggered.append(rule)

        return sorted(triggered, key=lambda r: r.priority, reverse=True)
