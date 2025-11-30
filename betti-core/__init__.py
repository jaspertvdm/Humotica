"""
BETTI Core - 14 Natural Laws Computing Engine

The core algorithms implementing physics-based resource allocation.
"""

from .natural_laws import NaturalLawsEngine
from .complexity import ComplexityAnalyzer, BettiNumbers
from .snaft import SNAFTFirewall
from .balans import BalansDecisionEngine
from .hicss import HICSSController

__version__ = "1.0.0"
__all__ = [
    "NaturalLawsEngine",
    "ComplexityAnalyzer",
    "BettiNumbers",
    "SNAFTFirewall",
    "BalansDecisionEngine",
    "HICSSController"
]
