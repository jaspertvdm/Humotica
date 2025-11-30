"""
SNAFT - System Not Authorized For That

Factory-level firewall that prevents dangerous or unauthorized operations.
This is the first line of defense in the BETTI security pipeline.

SNAFT rules are IMMUTABLE - they cannot be changed at runtime.
They represent hard physical/safety limits.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import re


class SNAFTSeverity(Enum):
    """Severity levels for SNAFT violations"""
    CRITICAL = "critical"    # Immediate danger
    HIGH = "high"            # Serious safety concern
    MEDIUM = "medium"        # Policy violation
    LOW = "low"              # Warning


class SNAFTRuleType(Enum):
    """Types of SNAFT rules"""
    KEYWORD = "keyword"           # Blocked keywords
    PATTERN = "pattern"           # Regex patterns
    DEVICE_LIMIT = "device_limit" # Device-specific limits
    CONTEXT = "context"           # Context-based rules


@dataclass
class SNAFTRule:
    """A single SNAFT rule"""
    id: str
    rule_type: SNAFTRuleType
    device_type: Optional[str]    # robot, drone, car, phone, iot
    manufacturer: Optional[str]   # DJI, Boston Dynamics, etc.
    pattern: str                  # Keyword or regex
    reason: str                   # Why this is blocked
    severity: SNAFTSeverity
    immutable: bool = True        # Cannot be changed


@dataclass
class SNAFTViolation:
    """Result of a SNAFT violation"""
    rule_id: str
    reason: str
    severity: SNAFTSeverity
    violation_detail: str
    immutable: bool


class SNAFTFirewall:
    """
    Factory-level firewall for BETTI.

    Checks all intents against immutable safety rules.

    Example:
        firewall = SNAFTFirewall()
        allowed, violation = firewall.check(
            intent="arm_weapon",
            device_type="robot"
        )
        if not allowed:
            print(f"BLOCKED: {violation.reason}")
    """

    # Default blocked keywords (CRITICAL)
    BLOCKED_KEYWORDS = [
        "delete_all", "destroy", "wipe", "format", "rm_rf",
        "drop_database", "truncate", "hack", "exploit", "inject",
        "bypass_security", "disable_firewall", "root_access",
        "kill_process", "shutdown_system", "corrupt", "arm_weapon",
        "fire_weapon", "self_destruct", "override_safety", "disable_limits"
    ]

    # Robot-specific blocked actions
    ROBOT_BLOCKED = [
        "exceed_speed_limit", "ignore_collision", "bypass_sensors",
        "disable_emergency_stop", "override_torque_limit",
        "ignore_human_presence", "continuous_operation_unsafe"
    ]

    # Drone-specific blocked actions
    DRONE_BLOCKED = [
        "exceed_altitude", "enter_restricted_airspace", "disable_geofence",
        "ignore_battery_critical", "bypass_no_fly_zone", "drop_payload"
    ]

    def __init__(self, additional_rules: Optional[List[SNAFTRule]] = None):
        """Initialize SNAFT firewall with default rules"""
        self.rules: List[SNAFTRule] = []
        self._load_default_rules()

        if additional_rules:
            for rule in additional_rules:
                if rule.immutable:  # Only add immutable rules
                    self.rules.append(rule)

    def _load_default_rules(self):
        """Load default SNAFT rules"""
        # Critical keyword rules
        for i, keyword in enumerate(self.BLOCKED_KEYWORDS):
            self.rules.append(SNAFTRule(
                id=f"SNAFT-KEYWORD-{i:03d}",
                rule_type=SNAFTRuleType.KEYWORD,
                device_type=None,  # Applies to all
                manufacturer=None,
                pattern=keyword,
                reason=f"Blocked keyword: {keyword}",
                severity=SNAFTSeverity.CRITICAL,
                immutable=True
            ))

        # Robot-specific rules
        for i, action in enumerate(self.ROBOT_BLOCKED):
            self.rules.append(SNAFTRule(
                id=f"SNAFT-ROBOT-{i:03d}",
                rule_type=SNAFTRuleType.KEYWORD,
                device_type="robot",
                manufacturer=None,
                pattern=action,
                reason=f"Robot safety rule: {action}",
                severity=SNAFTSeverity.CRITICAL,
                immutable=True
            ))

        # Drone-specific rules
        for i, action in enumerate(self.DRONE_BLOCKED):
            self.rules.append(SNAFTRule(
                id=f"SNAFT-DRONE-{i:03d}",
                rule_type=SNAFTRuleType.KEYWORD,
                device_type="drone",
                manufacturer=None,
                pattern=action,
                reason=f"Drone safety rule: {action}",
                severity=SNAFTSeverity.CRITICAL,
                immutable=True
            ))

        # SQL injection pattern
        self.rules.append(SNAFTRule(
            id="SNAFT-PATTERN-001",
            rule_type=SNAFTRuleType.PATTERN,
            device_type=None,
            manufacturer=None,
            pattern=r"(\bOR\b|\bAND\b).*=.*|--|\bUNION\b.*\bSELECT\b",
            reason="SQL injection pattern detected",
            severity=SNAFTSeverity.CRITICAL,
            immutable=True
        ))

        # Command injection pattern
        self.rules.append(SNAFTRule(
            id="SNAFT-PATTERN-002",
            rule_type=SNAFTRuleType.PATTERN,
            device_type=None,
            manufacturer=None,
            pattern=r"[;&|`$]|\.\.\/",
            reason="Command injection pattern detected",
            severity=SNAFTSeverity.HIGH,
            immutable=True
        ))

    def check(
        self,
        intent: str,
        device_type: Optional[str] = None,
        manufacturer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[SNAFTViolation]]:
        """
        Check if an intent is allowed by SNAFT rules.

        Args:
            intent: The intent string to check
            device_type: Type of device (robot, drone, car, etc.)
            manufacturer: Device manufacturer
            context: Additional context

        Returns:
            Tuple of (allowed: bool, violation: Optional[SNAFTViolation])
        """
        intent_lower = intent.lower()

        for rule in self.rules:
            # Skip rules for different device types
            if rule.device_type and rule.device_type != device_type:
                continue

            # Skip rules for different manufacturers
            if rule.manufacturer and rule.manufacturer != manufacturer:
                continue

            # Check based on rule type
            violated = False
            detail = ""

            if rule.rule_type == SNAFTRuleType.KEYWORD:
                if rule.pattern.lower() in intent_lower:
                    violated = True
                    detail = f"Intent contains blocked keyword: {rule.pattern}"

            elif rule.rule_type == SNAFTRuleType.PATTERN:
                if re.search(rule.pattern, intent, re.IGNORECASE):
                    violated = True
                    detail = f"Intent matches blocked pattern: {rule.pattern}"

            elif rule.rule_type == SNAFTRuleType.CONTEXT:
                if context:
                    # Check context-based rules
                    for key, value in context.items():
                        if rule.pattern in str(value).lower():
                            violated = True
                            detail = f"Context contains blocked value: {key}={value}"
                            break

            if violated:
                return False, SNAFTViolation(
                    rule_id=rule.id,
                    reason=rule.reason,
                    severity=rule.severity,
                    violation_detail=detail,
                    immutable=rule.immutable
                )

        return True, None

    def get_rules(
        self,
        device_type: Optional[str] = None,
        severity: Optional[SNAFTSeverity] = None
    ) -> List[SNAFTRule]:
        """Get SNAFT rules, optionally filtered"""
        rules = self.rules

        if device_type:
            rules = [r for r in rules if r.device_type is None or r.device_type == device_type]

        if severity:
            rules = [r for r in rules if r.severity == severity]

        return rules


# Convenience function
def check_snaft(
    intent: str,
    device_type: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[SNAFTViolation]]:
    """
    Quick SNAFT check.

    Example:
        allowed, violation = check_snaft("delete_all_files")
        if not allowed:
            print(f"Blocked: {violation.reason}")
    """
    firewall = SNAFTFirewall()
    return firewall.check(intent, device_type, context=context)
