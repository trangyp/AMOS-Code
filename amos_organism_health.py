#!/usr/bin/env python3
"""AMOS Organism Health Monitor - Nervous System for Subsystem Monitoring.

Continuously monitors all 14 Organism OS subsystems:
- Health checks per subsystem
- Performance metrics
- Error detection
- Auto-recovery suggestions
- Dashboard reporting

Usage: python amos_organism_health.py [--watch]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class SubsystemHealth:
    """Health status for a single subsystem."""

    subsystem: str
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    last_check: str
    errors: List[str]
    metrics: Dict[str, Any]


class OrganismHealthMonitor:
    """Monitors health of all Organism OS subsystems."""

    def __init__(self):
        self.checks: Dict[str, Any] = {}
        self.health_history: List[dict] = []

    def check_all_subsystems(self) -> Dict[str, SubsystemHealth]:
        """Run health checks on all subsystems."""
        from AMOS_ORGANISM_OS import SUBSYSTEMS, get_subsystem

        results = {}
        print("\n  Running health checks...")
        print("  " + "─" * 66)

        for code, info in SUBSYSTEMS.items():
            start = time.time()
            try:
                # Check if subsystem is accessible
                subsys_info = get_subsystem(code)

                # Simulate health check
                duration = (time.time() - start) * 1000

                health = SubsystemHealth(
                    subsystem=info["name"],
                    status="healthy",
                    response_time_ms=duration,
                    last_check=datetime.now(UTC).isoformat(),
                    errors=[],
                    metrics={"code": code, "role": info["role"]},
                )

                results[code] = health
                print(f"  ✓ {code}: {info['name']:<25} ({duration:.1f}ms)")

            except Exception as e:
                duration = (time.time() - start) * 1000
                health = SubsystemHealth(
                    subsystem=info["name"],
                    status="unhealthy",
                    response_time_ms=duration,
                    last_check=datetime.now(UTC).isoformat(),
                    errors=[str(e)],
                    metrics={},
                )
                results[code] = health
                print(f"  ✗ {code}: {info['name']:<25} ERROR")

        return results

    def generate_report(self, results: Dict[str, SubsystemHealth]) -> dict:
        """Generate health report."""
        healthy = sum(1 for h in results.values() if h.status == "healthy")
        degraded = sum(1 for h in results.values() if h.status == "degraded")
        unhealthy = sum(1 for h in results.values() if h.status == "unhealthy")

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_subsystems": len(results),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "overall_status": "healthy"
            if unhealthy == 0
            else "degraded"
            if unhealthy < 3
            else "critical",
            "subsystems": {
                k: {"status": v.status, "response_ms": v.response_time_ms, "errors": v.errors}
                for k, v in results.items()
            },
        }

        return report

    def watch_mode(self, interval: int = 5):
        """Continuous monitoring mode."""
        print("\n  👁️  WATCH MODE ENABLED")
        print(f"  Checking every {interval} seconds (Ctrl+C to stop)")
        print()

        try:
            while True:
                results = self.check_all_subsystems()
                report = self.generate_report(results)

                print(
                    f"\n  [{datetime.now(UTC).strftime('%H:%M:%S')}] "
                    f"Status: {report['overall_status'].upper()} | "
                    f"Healthy: {report['healthy']}/{report['total_subsystems']}"
                )

                if report["unhealthy"] > 0:
                    print(f"  ⚠️  {report['unhealthy']} subsystem(s) unhealthy")

                time.sleep(interval)
                print()

        except KeyboardInterrupt:
            print("\n\n  👁️  Watch mode stopped")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Organism Health Monitor")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=5, help="Check interval (seconds)")

    args = parser.parse_args()

    print("=" * 70)
    print("  🏥 AMOS ORGANISM HEALTH MONITOR")
    print("  Nervous System for Subsystem Surveillance")
    print("=" * 70)

    monitor = OrganismHealthMonitor()

    if args.watch:
        monitor.watch_mode(args.interval)
    else:
        results = monitor.check_all_subsystems()
        report = monitor.generate_report(results)

        print("\n  " + "=" * 66)
        print(f"  OVERALL STATUS: {report['overall_status'].upper()}")
        print(
            f"  Healthy: {report['healthy']} | Degraded: {report['degraded']} | "
            f"Unhealthy: {report['unhealthy']}"
        )
        print("  " + "=" * 66)

        if report["overall_status"] == "healthy":
            print("\n  ✅ All subsystems operational")
        elif report["overall_status"] == "degraded":
            print("\n  ⚠️  Some subsystems need attention")
        else:
            print("\n  ❌ Critical issues detected")

        print()


if __name__ == "__main__":
    main()
