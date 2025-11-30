"""
BETTI Complexity Analyzer

Uses Betti numbers from algebraic topology to analyze task complexity.

Betti Numbers:
- B0: Number of connected components (humans involved)
- B1: Number of 1-dimensional holes (devices)
- B2: Number of 2-dimensional voids (operations)
- B3: Number of 3-dimensional cavities (TIBET steps)
- B4: Time dimension (duration)
- B5: Communication channels

A task that exceeds complexity thresholds should be split.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class BettiNumbers:
    """Betti numbers for complexity analysis"""
    b0_humans: int = 1         # Connected components
    b1_devices: int = 1        # 1-holes (cycles)
    b2_ops: int = 1            # 2-holes (voids)
    b3_tbet_steps: int = 1     # 3-holes (cavities)
    b4_time_minutes: int = 1   # Time dimension
    b5_channels: int = 1       # Communication channels


@dataclass
class ComplexityResult:
    """Result of complexity analysis"""
    betti: BettiNumbers
    complexity_score: float
    split_required: bool
    split_suggestions: List[str]
    dominant_dimension: str
    risk_level: str  # low, medium, high, critical


class ComplexityAnalyzer:
    """
    Analyze task complexity using Betti numbers.

    Example:
        analyzer = ComplexityAnalyzer()
        result = analyzer.analyze(
            context={"humans": 2, "devices": 5, "operations": 10}
        )
        if result.split_required:
            print("Task too complex, split recommended")
    """

    def __init__(self, profile: str = "default"):
        """Initialize with threshold profile"""
        self.thresholds = self._get_thresholds(profile)
        self.weights = self._get_weights(profile)

    def _get_thresholds(self, profile: str) -> Dict[str, int]:
        """Get maximum thresholds for Betti numbers"""
        profiles = {
            "default": {
                "b0_max": 5,
                "b1_max": 10,
                "b2_max": 20,
                "b3_max": 50,
                "b4_max": 60,    # minutes
                "b5_max": 5,
                "complexity_max": 100
            },
            "strict": {
                "b0_max": 3,
                "b1_max": 5,
                "b2_max": 10,
                "b3_max": 25,
                "b4_max": 30,
                "b5_max": 3,
                "complexity_max": 50
            },
            "relaxed": {
                "b0_max": 10,
                "b1_max": 20,
                "b2_max": 50,
                "b3_max": 100,
                "b4_max": 120,
                "b5_max": 10,
                "complexity_max": 200
            }
        }
        return profiles.get(profile, profiles["default"])

    def _get_weights(self, profile: str) -> Dict[str, float]:
        """Get weights for each Betti dimension"""
        profiles = {
            "default": {
                "alpha": 1.0,   # B0 weight (humans)
                "beta": 0.8,    # B1 weight (devices)
                "gamma": 0.5,   # B2 weight (operations)
                "delta": 0.3,   # B3 weight (steps)
                "epsilon": 0.4, # B4 weight (time)
                "zeta": 0.6     # B5 weight (channels)
            },
            "strict": {
                "alpha": 1.5,
                "beta": 1.2,
                "gamma": 0.8,
                "delta": 0.5,
                "epsilon": 0.6,
                "zeta": 0.9
            },
            "relaxed": {
                "alpha": 0.8,
                "beta": 0.6,
                "gamma": 0.4,
                "delta": 0.2,
                "epsilon": 0.3,
                "zeta": 0.4
            }
        }
        return profiles.get(profile, profiles["default"])

    def analyze(
        self,
        context: Dict[str, Any],
        intent: Optional[str] = None
    ) -> ComplexityResult:
        """
        Analyze complexity of a task.

        Args:
            context: Task context with counts
            intent: Optional intent string

        Returns:
            ComplexityResult with analysis
        """
        # Extract Betti numbers from context
        betti = BettiNumbers(
            b0_humans=context.get("humans", context.get("b0", 1)),
            b1_devices=context.get("devices", context.get("b1", 1)),
            b2_ops=context.get("operations", context.get("b2", 1)),
            b3_tbet_steps=context.get("steps", context.get("b3", 1)),
            b4_time_minutes=context.get("time_minutes", context.get("b4", 1)),
            b5_channels=context.get("channels", context.get("b5", 1))
        )

        # Calculate complexity score
        t = self.thresholds
        w = self.weights

        score = (
            w["alpha"] * (betti.b0_humans / t["b0_max"]) +
            w["beta"] * (betti.b1_devices / t["b1_max"]) +
            w["gamma"] * (betti.b2_ops / t["b2_max"]) +
            w["delta"] * (betti.b3_tbet_steps / t["b3_max"]) +
            w["epsilon"] * (betti.b4_time_minutes / t["b4_max"]) +
            w["zeta"] * (betti.b5_channels / t["b5_max"])
        ) * (t["complexity_max"] / sum(w.values()))

        # Determine if split is required
        split_required = (
            score > t["complexity_max"] or
            betti.b0_humans > t["b0_max"] or
            betti.b1_devices > t["b1_max"] or
            betti.b2_ops > t["b2_max"]
        )

        # Find dominant dimension
        dimensions = [
            ("humans", betti.b0_humans / t["b0_max"]),
            ("devices", betti.b1_devices / t["b1_max"]),
            ("operations", betti.b2_ops / t["b2_max"]),
            ("steps", betti.b3_tbet_steps / t["b3_max"]),
            ("time", betti.b4_time_minutes / t["b4_max"]),
            ("channels", betti.b5_channels / t["b5_max"])
        ]
        dominant = max(dimensions, key=lambda x: x[1])[0]

        # Determine risk level
        if score > t["complexity_max"] * 1.5:
            risk = "critical"
        elif score > t["complexity_max"]:
            risk = "high"
        elif score > t["complexity_max"] * 0.7:
            risk = "medium"
        else:
            risk = "low"

        # Generate split suggestions
        suggestions = self._suggest_splits(betti, t, intent) if split_required else []

        return ComplexityResult(
            betti=betti,
            complexity_score=round(score, 2),
            split_required=split_required,
            split_suggestions=suggestions,
            dominant_dimension=dominant,
            risk_level=risk
        )

    def _suggest_splits(
        self,
        betti: BettiNumbers,
        thresholds: Dict[str, int],
        intent: Optional[str]
    ) -> List[str]:
        """Generate split suggestions"""
        suggestions = []

        if betti.b0_humans > thresholds["b0_max"]:
            suggestions.append(
                f"Reduce human involvement from {betti.b0_humans} to {thresholds['b0_max']}"
            )

        if betti.b1_devices > thresholds["b1_max"]:
            suggestions.append(
                f"Split across fewer devices (max {thresholds['b1_max']})"
            )

        if betti.b2_ops > thresholds["b2_max"]:
            n_splits = (betti.b2_ops // thresholds["b2_max"]) + 1
            suggestions.append(
                f"Break into {n_splits} sequential tasks"
            )

        if betti.b4_time_minutes > thresholds["b4_max"]:
            suggestions.append(
                f"Schedule in {thresholds['b4_max']}-minute chunks"
            )

        return suggestions


# Convenience function
def analyze_complexity(
    humans: int = 1,
    devices: int = 1,
    operations: int = 1,
    profile: str = "default"
) -> ComplexityResult:
    """
    Quick complexity analysis.

    Example:
        result = analyze_complexity(humans=3, devices=10, operations=50)
        print(f"Complexity: {result.complexity_score}")
        print(f"Risk: {result.risk_level}")
    """
    analyzer = ComplexityAnalyzer(profile)
    return analyzer.analyze({
        "humans": humans,
        "devices": devices,
        "operations": operations
    })
