#!/usr/bin/env python3
"""
AMOS SPEED ENGINE
===============

Optimization and performance monitoring for the AMOS Organism.
Benchmarks, profiles, and accelerates all subsystem operations.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkResult:
    name: str
    duration_ms: float
    memory_bytes: int
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpeedProfile:
    timestamp: str
    overall_score: float
    benchmarks: List[BenchmarkResult]
    recommendations: List[str]


class AmosSpeedEngine:
    """
    Performance optimization engine for AMOS.
    Monitors and accelerates subsystem execution.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.logs_dir = organism_root / "logs"
        self.memory_dir = organism_root / "memory"
        self.benchmarks: List[BenchmarkResult] = []

    def benchmark_cycle(
        self, cycle_func, context: Optional[Dict] = None
    ) -> BenchmarkResult:
        """Benchmark a single orchestrator cycle."""
        start = time.perf_counter()

        try:
            result = cycle_func(context)
            status = "success"
        except Exception as e:
            result = None
            status = f"error: {e}"

        duration = (time.perf_counter() - start) * 1000

        benchmark = BenchmarkResult(
            name="orchestrator_cycle",
            duration_ms=duration,
            memory_bytes=0,
            status=status,
            metadata={"result_count": len(result) if result else 0}
        )
        self.benchmarks.append(benchmark)
        return benchmark

    def benchmark_registry_load(self) -> BenchmarkResult:
        """Benchmark registry file loading."""
        start = time.perf_counter()

        registry_files = [
            self.root / "system_registry.json",
            self.root / "agent_registry.json",
            self.root / "engine_registry.json",
        ]

        total_size = 0
        for f in registry_files:
            if f.exists():
                total_size += f.stat().st_size
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        json.load(fp)
                except Exception:
                    pass

        duration = (time.perf_counter() - start) * 1000

        benchmark = BenchmarkResult(
            name="registry_load",
            duration_ms=duration,
            memory_bytes=total_size,
            status="success",
            metadata={"files_loaded": len(registry_files)}
        )
        self.benchmarks.append(benchmark)
        return benchmark

    def generate_profile(self) -> SpeedProfile:
        """Generate complete speed profile."""
        if not self.benchmarks:
            return SpeedProfile(
                timestamp=datetime.utcnow().isoformat() + "Z",
                overall_score=0.0,
                benchmarks=[],
                recommendations=["No benchmarks run yet"]
            )

        # Calculate overall score (lower is better, normalized to 100)
        avg_duration = sum(b.duration_ms for b in self.benchmarks) / len(
            self.benchmarks
        )
        score = max(0, 100 - avg_duration / 10)

        recommendations: List[str] = []

        # Analyze benchmarks for recommendations
        slow_benchmarks = [b for b in self.benchmarks if b.duration_ms > 1000]
        if slow_benchmarks:
            recommendations.append(
                f"Optimize {len(slow_benchmarks)} slow operations (>1s)"
            )

        failed = [b for b in self.benchmarks if not b.status == "success"]
        if failed:
            recommendations.append(f"Fix {len(failed)} failing benchmarks")

        if score < 50:
            recommendations.append("Consider caching frequently accessed data")

        return SpeedProfile(
            timestamp=datetime.utcnow().isoformat() + "Z",
            overall_score=round(score, 2),
            benchmarks=self.benchmarks,
            recommendations=recommendations
        )

    def save_profile(self) -> Path:
        """Save profile to memory directory."""
        profile = self.generate_profile()

        output_path = self.memory_dir / "speed_profile.json"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": profile.timestamp,
            "overall_score": profile.overall_score,
            "benchmarks": [
                {
                    "name": b.name,
                    "duration_ms": b.duration_ms,
                    "memory_bytes": b.memory_bytes,
                    "status": b.status,
                    "metadata": b.metadata
                }
                for b in profile.benchmarks
            ],
            "recommendations": profile.recommendations
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return output_path

    def optimize_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = [
            "Enable working memory caching for frequent queries",
            "Pre-load canonical engines at startup",
            "Use lazy loading for large JSON files (>1MB)",
            "Implement incremental state updates",
            "Cache subsystem handler instances",
        ]
        return recommendations


def main() -> int:
    """CLI for Speed Engine."""
    print("=" * 60)
    print("AMOS SPEED ENGINE v1.0.0")
    print("=" * 60)

    # Use file-relative path for portability
    root = Path(__file__).resolve().parent
    engine = AmosSpeedEngine(root)

    print("\n[SPEED] Running benchmarks...")

    # Benchmark registry load
    result = engine.benchmark_registry_load()
    print(f"[SPEED] Registry load: {result.duration_ms:.2f}ms")

    # Generate and save profile
    profile = engine.generate_profile()
    output_path = engine.save_profile()

    print(f"\n[SPEED] Overall Score: {profile.overall_score}/100")
    print(f"[SPEED] Benchmarks run: {len(profile.benchmarks)}")

    if profile.recommendations:
        print("\n[SPEED] Recommendations:")
        for rec in profile.recommendations:
            print(f"  - {rec}")

    print(f"\n[SPEED] Profile saved to: {output_path}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
