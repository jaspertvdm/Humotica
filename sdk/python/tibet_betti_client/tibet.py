"""
TIBET (Time Intent Based Event Token) classes
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TimeWindow:
    """Time window for TIBET intent execution"""

    start: datetime
    end: datetime

    def duration_seconds(self) -> int:
        """Get duration in seconds"""
        return int((self.end - self.start).total_seconds())

    def is_active(self) -> bool:
        """Check if current time is within window"""
        now = datetime.utcnow()
        return self.start <= now <= self.end

    def time_until_start(self) -> Optional[timedelta]:
        """Time until window starts (None if already started)"""
        now = datetime.utcnow()
        if now >= self.start:
            return None
        return self.start - now

    def time_until_end(self) -> Optional[timedelta]:
        """Time until window ends (None if already ended)"""
        now = datetime.utcnow()
        if now >= self.end:
            return None
        return self.end - now

    @classmethod
    def immediate(cls) -> "TimeWindow":
        """Create immediate time window (30 seconds)"""
        now = datetime.utcnow()
        return cls(
            start=now,
            end=now + timedelta(seconds=30)
        )

    @classmethod
    def from_now(cls, **kwargs) -> "TimeWindow":
        """
        Create time window starting now

        Args:
            **kwargs: Passed to timedelta (hours, minutes, seconds, days)

        Example:
            >>> TimeWindow.from_now(hours=2)  # Next 2 hours
            >>> TimeWindow.from_now(minutes=30)  # Next 30 minutes
        """
        now = datetime.utcnow()
        duration = timedelta(**kwargs)
        return cls(start=now, end=now + duration)

    @classmethod
    def scheduled(
        cls,
        start: datetime,
        duration_minutes: int = 30
    ) -> "TimeWindow":
        """
        Create scheduled time window

        Args:
            start: Start time
            duration_minutes: Duration in minutes

        Example:
            >>> start = datetime(2025, 11, 28, 14, 30)  # 14:30
            >>> TimeWindow.scheduled(start, duration_minutes=60)
        """
        return cls(
            start=start,
            end=start + timedelta(minutes=duration_minutes)
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert to dict"""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_seconds": self.duration_seconds()
        }


@dataclass
class Constraints:
    """Constraints for TIBET intent execution"""

    max_retries: int = 3
    max_duration_seconds: Optional[int] = None
    required_conditions: Dict[str, Any] = field(default_factory=dict)
    safe_fail_action: str = "notify_user"
    priority: int = 5  # 1-10

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "max_retries": self.max_retries,
            "max_duration_seconds": self.max_duration_seconds,
            "required_conditions": self.required_conditions,
            "safe_fail_action": self.safe_fail_action,
            "priority": self.priority
        }


@dataclass
class Tibet:
    """
    TIBET = Time Intent Based Event Token

    A TIBET represents an intent to do something, with:
    - Clear purpose (intent)
    - Time boundaries (when it can happen)
    - Context (why and how)
    - Constraints (limits and requirements)
    """

    intent: str
    context: Dict[str, Any] = field(default_factory=dict)
    time_window: TimeWindow = field(default_factory=TimeWindow.immediate)
    constraints: Constraints = field(default_factory=Constraints)
    humotica: Optional[str] = None  # Human-readable explanation
    trust_token_ref: Optional[str] = None  # FIR/A reference

    def is_valid(self) -> bool:
        """Check if TIBET is valid for execution"""
        return self.time_window.is_active()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for transmission"""
        return {
            "intent": self.intent,
            "context": self.context,
            "time_window": self.time_window.to_dict(),
            "constraints": self.constraints.to_dict(),
            "humotica": self.humotica,
            "trust_token_ref": self.trust_token_ref
        }

    @classmethod
    def create(
        cls,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "Tibet":
        """
        Create TIBET with defaults

        Args:
            intent: Intent name
            context: Context dict
            **kwargs: Additional fields

        Example:
            >>> tibet = Tibet.create(
            ...     intent="turn_on_lights",
            ...     context={"room": "living_room"},
            ...     time_window=TimeWindow.from_now(minutes=5)
            ... )
        """
        return cls(
            intent=intent,
            context=context or {},
            **kwargs
        )
