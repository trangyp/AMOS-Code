"""
Repo Doctor Ω∞ - History/Temporal Analysis Module

Temporal evolution:
|Ψ_repo(t+1)⟩ = U_t |Ψ_repo(t)⟩

Drift: ΔΨ(t) = |Ψ_repo(t)⟩ - |Ψ_repo(t-1)⟩

First bad commit: t*_k = min t such that I_k(t-1)=1 and I_k(t)=0
"""

from .drift import DriftAnalyzer, TemporalDrift
from .bisect_runner import BisectRunner, BisectResult
from .path_integral import PathIntegralBlame, CausalityRanker

__all__ = [
    "DriftAnalyzer",
    "TemporalDrift",
    "BisectRunner",
    "BisectResult",
    "PathIntegralBlame",
    "CausalityRanker",
]
