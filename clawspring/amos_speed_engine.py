"""AMOS Speed Engine - Cross-cutting optimization for all engines."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SpeedMode(Enum):
    """Speed optimization modes."""
    MAX_SAFE_SPEED = "max_safe_speed"
    BALANCED_FAST = "balanced_fast"
    PRECISION_PRIORITY = "precision_priority"


class ResponseTier(Enum):
    """Response tiering levels."""
    T1_FLASH = "T1_flash_answer"
    T2_SUMMARY = "T2_structured_summary"
    T3_FULL = "T3_full_framework"


@dataclass
class OptimizationProfile:
    """Optimization profile configuration."""

    name: str
    mode: SpeedMode
    max_reasoning_depth: int
    self_reflection_passes: int
    max_tokens: int


class SpeedEngine:
    """AMOS Speed Engine - System-wide optimization."""

    VERSION = "v1.0.0"
    NAME = "AMOS_SPEED_OMEGA"

    def __init__(self):
        self.profiles: Dict[str, OptimizationProfile] = {
            "max_safe_speed": OptimizationProfile(
                name="max_safe_speed",
                mode=SpeedMode.MAX_SAFE_SPEED,
                max_reasoning_depth=3,
                self_reflection_passes=0,
                max_tokens=900,
            ),
            "balanced_fast": OptimizationProfile(
                name="balanced_fast",
                mode=SpeedMode.BALANCED_FAST,
                max_reasoning_depth=5,
                self_reflection_passes=1,
                max_tokens=900,
            ),
            "precision_priority": OptimizationProfile(
                name="precision_priority",
                mode=SpeedMode.PRECISION_PRIORITY,
                max_reasoning_depth=8,
                self_reflection_passes=2,
                max_tokens=2200,
            ),
        }
        self.metrics: List[dict] = []
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    def select_profile(self, query_complexity: str, user_preference: str  = None) -> OptimizationProfile:
        """Select optimization profile based on query and preference."""
        if user_preference and user_preference in self.profiles:
            return self.profiles[user_preference]
        if query_complexity == "simple":
            return self.profiles["max_safe_speed"]
        elif query_complexity == "complex":
            return self.profiles["precision_priority"]
        return self.profiles["balanced_fast"]

    def select_response_tier(
        self, user_request_type: str, available_tokens: int
    ) -> dict:
        """Select response tier based on user request."""
        tiers = {
            "T1_flash_answer": {
                "description": "Very short, direct answer",
                "max_tokens": 250,
                "style": "flash",
            },
            "T2_structured_summary": {
                "description": "Short intro + numbered points",
                "max_tokens": 900,
                "style": "summary",
            },
            "T3_full_framework": {
                "description": "Complete structured model",
                "max_tokens": 2200,
                "style": "full",
            },
        }
        if "short" in user_request_type or "quick" in user_request_type or "tldr" in user_request_type:
            return tiers["T1_flash_answer"]
        elif "full" in user_request_type or "breakdown" in user_request_type or "plan" in user_request_type:
            return tiers["T3_full_framework"]
        return tiers["T2_structured_summary"]

    def prune_reasoning(self, reasoning_steps: List[str], max_branches: int = 3) -> dict:
        """Prune reasoning steps to essential branches."""
        original_count = len(reasoning_steps)
        pruned = reasoning_steps[:max_branches]
        compression_ratio = len(pruned) / original_count if original_count > 0 else 1.0
        return {
            "original_steps": original_count,
            "pruned_steps": len(pruned),
            "compression_ratio": compression_ratio,
            "pruned": pruned,
        }

    def compress_decision_tree(self, branches: List[dict]) -> dict:
        """Compress decision tree by merging equivalent paths."""
        unique_branches = []
        seen = set()
        for branch in branches:
            key = str(branch.get("outcome", ""))
            if key not in seen:
                seen.add(key)
                unique_branches.append(branch)
        return {
            "original_branches": len(branches),
            "compressed_branches": len(unique_branches),
            "merged_count": len(branches) - len(unique_branches),
            "branches": unique_branches,
        }

    def check_cache(self, query_hash: str, recent_analyses: List[dict]) -> dict:
        """Check if similar query exists in cache."""
        for analysis in recent_analyses:
            if analysis.get("query_hash") == query_hash:
                self.cache_hits += 1
                return {
                    "cache_hit": True,
                    "reusable_result": analysis.get("result"),
                    "confidence": analysis.get("confidence", 0.9),
                }
        self.cache_misses += 1
        return {"cache_hit": False}

    def record_metrics(
        self, latency_ms: float, tokens: int, correction_requested: bool = False
    ) -> dict:
        """Record performance metrics."""
        metric = {
            "latency_ms": latency_ms,
            "tokens": tokens,
            "correction_requested": correction_requested,
            "timestamp": None,  # Would use actual time in production
        }
        self.metrics.append(metric)
        # Self-audit recommendations
        recommendations = []
        if latency_ms > 2000:  # threshold
            recommendations.append("reduce_reasoning_depth_by_1")
        if correction_requested:
            recommendations.append("shift_to_precision_priority_mode")
        return {
            "metric_recorded": True,
            "recommendations": recommendations,
        }

    def get_optimization_advice(self, engine_name: str, query_type: str) -> dict:
        """Get optimization advice for specific engine and query."""
        return {
            "engine": engine_name,
            "query_type": query_type,
            "recommended_profile": "balanced_fast",
            "skip_layers_for_simple": [
                "deep_meta_analysis_layer",
                "long_horizon_forecast_layer",
            ],
            "output_style": {
                "compact_frameworks": True,
                "numbered_steps": True,
                "max_nesting_level": 3,
            },
        }

    def analyze_speed(self, description: str, mode: str  = None) -> Dict[str, Any]:
        """Run speed optimization analysis."""
        profile = self.select_profile("medium", mode)
        tier = self.select_response_tier(description, profile.max_tokens)
        return {
            "query": description[:100],
            "selected_profile": profile.name,
            "max_reasoning_depth": profile.max_reasoning_depth,
            "self_reflection_passes": profile.self_reflection_passes,
            "response_tier": tier["style"],
            "max_tokens": tier["max_tokens"],
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "metrics_collected": len(self.metrics),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Optimization Coverage",
        ]
        optimization_aspects = {
            "selected_profile": "Optimization Profile Selected",
            "max_reasoning_depth": "Maximum Reasoning Depth",
            "self_reflection_passes": "Self-Reflection Passes",
            "response_tier": "Response Tier",
            "max_tokens": "Token Limit",
            "cache_hits": "Cache Hits",
            "cache_misses": "Cache Misses",
        }
        for key, display_name in optimization_aspects.items():
            if key in results:
                lines.append(f"- **{display_name}**: {results[key]}")
        lines.extend([
            "",
            "## Gaps and Limitations",
            "- Real-time latency measurement requires instrumentation",
            "- Cache invalidation on canon updates not automated",
            "- Parallel session management is conceptual only",
            "- Token counting is approximate",
            "",
            "## Safety Disclaimer",
            "Speed optimization never overrides domain engine logic or values. "
            "All optimizations preserve correctness while improving efficiency. "
            "Domain engines always take precedence over speed preferences.",
        ])
        return "\n".join(lines)


# Singleton instance
_speed_engine: Optional[SpeedEngine] = None


def get_speed_engine() -> SpeedEngine:
    """Get or create the Speed Engine singleton."""
from __future__ import annotations

    global _speed_engine
    if _speed_engine is None:
        _speed_engine = SpeedEngine()
    return _speed_engine
