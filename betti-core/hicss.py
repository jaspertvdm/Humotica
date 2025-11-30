"""
HICSS - Human Interrupt Control System

Five levels of human override for robot operations:
- H: Halt - Pause execution, save state for resume
- I: Intent - Override with completely new intent
- C: Change - Modify parameters mid-execution
- S: Switch - Change execution strategy
- S: Stop - Immediate halt with rollback

Requires TIBET authorization for all overrides.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class HICSSAction(Enum):
    """The five HICSS override actions"""
    HALT = "halt"       # Pause with state save
    INTENT = "intent"   # New intent override
    CHANGE = "change"   # Modify parameters
    SWITCH = "switch"   # Change strategy
    STOP = "stop"       # Immediate stop + rollback


class OverrideResult(Enum):
    """Result of override attempt"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    UNAUTHORIZED = "unauthorized"


@dataclass
class HICSSState:
    """State saved during HALT"""
    intent_id: str
    intent: str
    context: Dict[str, Any]
    progress_percent: float
    timestamp: datetime
    can_resume: bool


@dataclass
class HICSSResult:
    """Result of HICSS action"""
    action: HICSSAction
    result: OverrideResult
    message: str
    state: Optional[HICSSState] = None
    rollback_available: bool = False
    new_intent_id: Optional[str] = None


class HICSSController:
    """
    Human Interrupt Control System.

    Provides safe ways for humans to override robot operations.

    Example:
        controller = HICSSController()

        # Halt a running task
        result = controller.halt(
            intent_id="task-123",
            tibet_token="TIBET-xxx",
            reason="Need to check something"
        )

        # Later, resume
        controller.resume(result.state)
    """

    def __init__(self):
        """Initialize HICSS controller"""
        self.saved_states: Dict[str, HICSSState] = {}
        self.override_log: List[Dict[str, Any]] = []

    def _verify_tibet(self, tibet_token: str) -> bool:
        """Verify TIBET token authorization"""
        # In production, this would validate against TIBET service
        return tibet_token and tibet_token.startswith("TIBET-")

    def _log_override(
        self,
        action: HICSSAction,
        intent_id: str,
        hid: str,
        result: OverrideResult,
        reason: str
    ):
        """Log override action"""
        self.override_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action.value,
            "intent_id": intent_id,
            "hid": hid,
            "result": result.value,
            "reason": reason
        })

    def halt(
        self,
        intent_id: str,
        tibet_token: str,
        hid: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HICSSResult:
        """
        HALT - Pause execution with state save.

        The task can be resumed later from the saved state.

        Args:
            intent_id: ID of the running intent
            tibet_token: TIBET authorization token
            hid: Human ID performing override
            reason: Reason for halt
            context: Current execution context

        Returns:
            HICSSResult with saved state
        """
        if not self._verify_tibet(tibet_token):
            return HICSSResult(
                action=HICSSAction.HALT,
                result=OverrideResult.UNAUTHORIZED,
                message="Invalid TIBET token"
            )

        # Save state
        state = HICSSState(
            intent_id=intent_id,
            intent=context.get("intent", "unknown") if context else "unknown",
            context=context or {},
            progress_percent=context.get("progress", 0) if context else 0,
            timestamp=datetime.now(),
            can_resume=True
        )

        self.saved_states[intent_id] = state
        self._log_override(HICSSAction.HALT, intent_id, hid, OverrideResult.SUCCESS, reason)

        return HICSSResult(
            action=HICSSAction.HALT,
            result=OverrideResult.SUCCESS,
            message=f"Task halted. State saved. Reason: {reason}",
            state=state
        )

    def intent(
        self,
        intent_id: str,
        tibet_token: str,
        hid: str,
        new_intent: str,
        new_context: Dict[str, Any],
        reason: str
    ) -> HICSSResult:
        """
        INTENT - Override with completely new intent.

        Stops current task and starts new one.

        Args:
            intent_id: ID of current intent
            tibet_token: TIBET authorization
            hid: Human ID
            new_intent: New intent to execute
            new_context: Context for new intent
            reason: Reason for override

        Returns:
            HICSSResult with new intent ID
        """
        if not self._verify_tibet(tibet_token):
            return HICSSResult(
                action=HICSSAction.INTENT,
                result=OverrideResult.UNAUTHORIZED,
                message="Invalid TIBET token"
            )

        # Generate new intent ID
        new_id = f"override-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        self._log_override(HICSSAction.INTENT, intent_id, hid, OverrideResult.SUCCESS, reason)

        return HICSSResult(
            action=HICSSAction.INTENT,
            result=OverrideResult.SUCCESS,
            message=f"Intent overridden to '{new_intent}'",
            new_intent_id=new_id,
            rollback_available=True
        )

    def change(
        self,
        intent_id: str,
        tibet_token: str,
        hid: str,
        new_params: Dict[str, Any],
        reason: str
    ) -> HICSSResult:
        """
        CHANGE - Modify parameters mid-execution.

        Adjusts task parameters without stopping.

        Args:
            intent_id: ID of running intent
            tibet_token: TIBET authorization
            hid: Human ID
            new_params: Parameters to change
            reason: Reason for change

        Returns:
            HICSSResult
        """
        if not self._verify_tibet(tibet_token):
            return HICSSResult(
                action=HICSSAction.CHANGE,
                result=OverrideResult.UNAUTHORIZED,
                message="Invalid TIBET token"
            )

        self._log_override(HICSSAction.CHANGE, intent_id, hid, OverrideResult.SUCCESS, reason)

        return HICSSResult(
            action=HICSSAction.CHANGE,
            result=OverrideResult.SUCCESS,
            message=f"Parameters updated: {list(new_params.keys())}"
        )

    def switch(
        self,
        intent_id: str,
        tibet_token: str,
        hid: str,
        new_strategy: str,
        reason: str
    ) -> HICSSResult:
        """
        SWITCH - Change execution strategy.

        Changes how the task is being executed.

        Args:
            intent_id: ID of running intent
            tibet_token: TIBET authorization
            hid: Human ID
            new_strategy: New strategy name
            reason: Reason for switch

        Returns:
            HICSSResult
        """
        if not self._verify_tibet(tibet_token):
            return HICSSResult(
                action=HICSSAction.SWITCH,
                result=OverrideResult.UNAUTHORIZED,
                message="Invalid TIBET token"
            )

        self._log_override(HICSSAction.SWITCH, intent_id, hid, OverrideResult.SUCCESS, reason)

        return HICSSResult(
            action=HICSSAction.SWITCH,
            result=OverrideResult.SUCCESS,
            message=f"Strategy switched to '{new_strategy}'"
        )

    def stop(
        self,
        intent_id: str,
        tibet_token: str,
        hid: str,
        reason: str,
        rollback: bool = False
    ) -> HICSSResult:
        """
        STOP - Immediate halt with optional rollback.

        Emergency stop. Cannot be resumed.

        Args:
            intent_id: ID of running intent
            tibet_token: TIBET authorization
            hid: Human ID
            reason: Reason for stop
            rollback: Whether to rollback changes

        Returns:
            HICSSResult
        """
        if not self._verify_tibet(tibet_token):
            return HICSSResult(
                action=HICSSAction.STOP,
                result=OverrideResult.UNAUTHORIZED,
                message="Invalid TIBET token"
            )

        # Remove any saved state
        if intent_id in self.saved_states:
            del self.saved_states[intent_id]

        self._log_override(HICSSAction.STOP, intent_id, hid, OverrideResult.SUCCESS, reason)

        msg = "Task stopped immediately"
        if rollback:
            msg += " with rollback"

        return HICSSResult(
            action=HICSSAction.STOP,
            result=OverrideResult.SUCCESS,
            message=msg,
            rollback_available=rollback
        )

    def resume(
        self,
        intent_id: str,
        tibet_token: str,
        hid: str
    ) -> HICSSResult:
        """
        Resume a halted task from saved state.

        Args:
            intent_id: ID of halted intent
            tibet_token: TIBET authorization
            hid: Human ID

        Returns:
            HICSSResult with state to resume
        """
        if not self._verify_tibet(tibet_token):
            return HICSSResult(
                action=HICSSAction.HALT,
                result=OverrideResult.UNAUTHORIZED,
                message="Invalid TIBET token"
            )

        state = self.saved_states.get(intent_id)
        if not state:
            return HICSSResult(
                action=HICSSAction.HALT,
                result=OverrideResult.FAILED,
                message="No saved state found for this intent"
            )

        if not state.can_resume:
            return HICSSResult(
                action=HICSSAction.HALT,
                result=OverrideResult.FAILED,
                message="State cannot be resumed"
            )

        return HICSSResult(
            action=HICSSAction.HALT,
            result=OverrideResult.SUCCESS,
            message=f"Resuming from {state.progress_percent:.0f}%",
            state=state
        )

    def get_override_history(
        self,
        intent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get override history, optionally filtered by intent"""
        history = self.override_log

        if intent_id:
            history = [h for h in history if h["intent_id"] == intent_id]

        return history[-limit:]
