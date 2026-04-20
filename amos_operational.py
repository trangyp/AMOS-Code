#!/usr/bin/env python3
"""AMOS Operational - Complete Production System

Unifies:
- v4 Production Runtime (decision engine)
- Real-World Connectors (data, execution, persistence)
- Continuous operation loop
- Health monitoring
- Graceful shutdown

This is the production-ready AMOS that can run continuously,
ingesting real data, making decisions, executing actions,
and learning from outcomes.
"""

import json
import signal
import sys
import time
from collections import deque
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC, timedelta


class AMOSOperational:
    """Complete operational AMOS system.

    Architecture:
    - v4 Production Runtime (decisions)
    - Connector System (data/execution)
    - Continuous Loop (cycle every N minutes)
    - Health Monitor (self-preservation)
    - State Persistence (survive restarts)
    """

    def __init__(self, config_path: str = "amos_config.json"):
        self.config_path = config_path
        self.running = False
        self.cycle_count = 0
        self.start_time = None

        # Core components
        self.runtime = None
        self.connectors = None

        # Health monitoring
        self.health_status = {
            "identity_drift": 0.0,
            "resource_adequacy": 1.0,
            "decision_quality": 1.0,
            "system_stable": True,
        }
        self.alerts: deque = deque(maxlen=100)

        # Goals (would be loaded from config in production)
        self.goals = self._load_default_goals()

        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_default_goals(self) -> list[dict]:
        """Load default operational goals."""
        return [
            {
                "id": "survival_cash",
                "name": "Maintain Cash Flow",
                "type": "freelance",
                "priority": 1.0,
                "expected_value": 100,
                "resource_cost": {"time": 20, "capital": 0},
                "risk_score": 0.05,
                "description": "Ensure minimum income for survival",
            },
            {
                "id": "asset_building",
                "name": "Build Product/Asset",
                "type": "product",
                "priority": 0.8,
                "expected_value": 300,
                "resource_cost": {"time": 40, "capital": 200},
                "risk_score": 0.3,
                "description": "Create compounding value asset",
            },
            {
                "id": "capability_growth",
                "name": "Learn New Skill",
                "type": "skill",
                "priority": 0.6,
                "expected_value": 150,
                "resource_cost": {"time": 15, "capital": 100},
                "risk_score": 0.1,
                "description": "Increase future capacity",
            },
            {
                "id": "ecosystem",
                "name": "Build Partnerships",
                "type": "ecosystem",
                "priority": 0.5,
                "expected_value": 200,
                "resource_cost": {"time": 10, "capital": 50},
                "risk_score": 0.15,
                "description": "Expand network and opportunities",
            },
        ]

    def initialize(self):
        """Initialize all components."""
        print("=" * 70)
        print("🚀 AMOS OPERATIONAL - Initializing")
        print("=" * 70)

        # Initialize connectors first
        try:
            from amos_connectors import AMOSConnectorSystem

            self.connectors = AMOSConnectorSystem(self.config_path)
            self.connectors.initialize()
            print("✓ Connectors initialized")
        except Exception as e:
            print(f"! Connectors not available: {e}")
            self.connectors = None

        # Initialize v4 production runtime
        try:
            from amos_v4_runtime import AMOSv4ProductionRuntime

            self.runtime = AMOSv4ProductionRuntime(name="AMOS_Operational")
            print("✓ v4 Production Runtime initialized")
        except Exception as e:
            print(f"! v4 Runtime not available: {e}")
            self.runtime = None

        # Start connector services if available
        if self.connectors:
            self.connectors.start()

        print("=" * 70)
        print("✓ AMOS Operational ready")
        print("=" * 70)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n⚠ Signal {signum} received, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)

    def run_cycle(self) -> dict:
        """Execute one complete operational cycle."""
        self.cycle_count += 1
        cycle_start = datetime.now(UTC)

        print(f"\n{'─' * 70}")
        print(f"Cycle {self.cycle_count} | {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'─' * 70}")

        result = {
            "cycle": self.cycle_count,
            "timestamp": cycle_start.isoformat(),
            "status": "success",
            "decisions": [],
            "alerts": [],
        }

        try:
            # 1. Ingest latest data
            signals = []
            if self.connectors:
                aggregated = self.connectors.ingestion.get_aggregated_state()
                # Convert to Signal objects for v4 runtime

                from amos_v4_runtime import Signal

                for source_type, data in aggregated.items():
                    if data:
                        signals.append(
                            Signal(
                                source=source_type,
                                data=data,
                                timestamp=datetime.now(UTC),
                                confidence=0.8,
                                reliability_score=0.8,
                            )
                        )
                print(f"  Ingested {len(signals)} signal sources")

            # 2. Run decision cycle
            if self.runtime:
                decision = self.runtime.cycle(self.goals, signals)
                result["decisions"].append(decision)

                print(f"  Decision: {decision.get('action', 'none')}")
                print(f"  Economic Score: {decision.get('economic_score', 0):.1f}")
                print(f"  Identity Drift: {decision.get('identity_drift', 0):.3f}")

                # Check for alerts
                if decision.get("identity_drift", 0) > 0.1:
                    alert = f"Identity drift detected: {decision['identity_drift']:.3f}"
                    result["alerts"].append(alert)
                    self.alerts.append({"type": "identity", "message": alert})

                # Persist decision
                if self.connectors:
                    self.connectors.persistence.save_decision(decision)

            # 3. Execute decided actions
            if self.connectors and result["decisions"]:
                for decision in result["decisions"]:
                    action_name = decision.get("action", "")
                    if action_name:
                        exec_result = self.connectors.execution.execute(
                            {"type": "create_task", "name": action_name, "data": decision}
                        )
                        print(f"  Execution: {exec_result.get('status', 'unknown')}")

            # 4. Update health status
            self._update_health(result)

            # 5. Send notifications for alerts
            if self.connectors and result["alerts"]:
                for alert in result["alerts"]:
                    self.connectors.notifications.notify(alert, "warning")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"  ✗ Error: {e}")

            if self.connectors:
                self.connectors.notifications.notify(
                    f"Cycle {self.cycle_count} failed: {e}", "error"
                )

        cycle_duration = (datetime.now(UTC) - cycle_start).total_seconds()
        result["duration_seconds"] = cycle_duration

        print(f"  Duration: {cycle_duration:.1f}s")

        return result

    def _update_health(self, cycle_result: dict):
        """Update health monitoring."""
        # Check identity drift
        for decision in cycle_result.get("decisions", []):
            drift = decision.get("identity_drift", 0)
            self.health_status["identity_drift"] = max(self.health_status["identity_drift"], drift)

        # Check decision quality
        if cycle_result["status"] == "success":
            self.health_status["decision_quality"] = min(
                1.0, self.health_status["decision_quality"] + 0.01
            )
        else:
            self.health_status["decision_quality"] *= 0.95

        # Overall stability
        self.health_status["system_stable"] = (
            self.health_status["identity_drift"] < 0.3
            and self.health_status["decision_quality"] > 0.5
        )

    def run_continuous(self, interval_minutes: int = 60):
        """Run continuous operation loop."""
        self.running = True
        self.start_time = datetime.now(UTC)

        print(f"\n🔄 Starting continuous operation (interval: {interval_minutes}min)")
        print("   Press Ctrl+C to stop gracefully\n")

        while self.running:
            try:
                # Run cycle
                self.run_cycle()

                # Check health
                if not self.health_status["system_stable"]:
                    print("\n⚠ System unstable - initiating recovery")
                    self._recovery_procedure()

                # Wait for next cycle
                print(f"\n  [Sleeping for {interval_minutes} minutes...]")
                for _ in range(interval_minutes * 60):
                    if not self.running:
                        break
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\n\n⚠ Interrupted by user")
                self.stop()
                break
            except Exception as e:
                print(f"\n✗ Critical error: {e}")
                if self.connectors:
                    self.connectors.notifications.notify(f"Critical error in cycle: {e}", "error")
                time.sleep(60)  # Wait 1 minute before retry

    def _recovery_procedure(self):
        """Execute recovery when system unstable."""
        print("  → Recovery: Reducing goal complexity")
        # Reduce to survival-only goals
        self.goals = [g for g in self.goals if g["id"] == "survival_cash"]

        print("  → Recovery: Pausing for 5 minutes")
        time.sleep(300)

        print("  → Recovery: Resetting health metrics")
        self.health_status["identity_drift"] *= 0.5

        if self.connectors:
            self.connectors.notifications.notify("Recovery procedure completed", "info")

    def stop(self):
        """Graceful shutdown."""
        print("\n" + "=" * 70)
        print("🛑 AMOS Operational - Shutting Down")
        print("=" * 70)

        self.running = False

        # Save final state
        if self.connectors:
            # Save configuration
            self.connectors.config.save()

            # Stop services
            self.connectors.stop()

        # Print summary
        uptime = datetime.now(UTC) - self.start_time if self.start_time else timedelta(0)
        print("\nOperational Summary:")
        print(f"  Cycles completed: {self.cycle_count}")
        print(f"  Uptime: {uptime}")
        print(f"  Final health: {self.health_status}")
        print(f"  Total alerts: {len(self.alerts)}")

        print("\n✓ AMOS Operational stopped gracefully")
        print("=" * 70)

    def get_status(self) -> dict:
        """Get complete operational status."""
        uptime = datetime.now(UTC) - self.start_time if self.start_time else timedelta(0)

        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "uptime_seconds": uptime.total_seconds(),
            "health": self.health_status,
            "alerts_pending": len(self.alerts),
            "components": {
                "runtime": self.runtime is not None,
                "connectors": self.connectors is not None,
            },
            "goals_active": len(self.goals),
        }

    def run_single(self):
        """Run single cycle and exit."""
        self.initialize()
        result = self.run_cycle()
        return result


def demo_operational():
    """Demonstrate operational AMOS."""
    print("=" * 70)
    print("🚀 AMOS OPERATIONAL - Production System Demo")
    print("=" * 70)
    print("\nThis demonstrates the complete operational AMOS:")
    print("  • v4 Production Runtime (decisions)")
    print("  • Real-World Connectors (data/execution)")
    print("  • Health monitoring")
    print("  • Single cycle operation")
    print("=" * 70)

    # Create and initialize
    amos = AMOSOperational()
    amos.initialize()

    # Run single cycle
    print("\n[Running Operational Cycle]")
    result = amos.run_cycle()

    # Show status
    print("\n[Operational Status]")
    status = amos.get_status()
    print(f"  Cycles: {status['cycle_count']}")
    print(f"  Health: {json.dumps(status['health'], indent=4)}")
    print(f"  Goals: {status['goals_active']}")
    print(f"  Runtime: {'✓' if status['components']['runtime'] else '✗'}")
    print(f"  Connectors: {'✓' if status['components']['connectors'] else '✗'}")

    print("\n" + "=" * 70)
    print("✅ AMOS OPERATIONAL DEMO COMPLETE")
    print("=" * 70)
    print("\nTo run continuously:")
    print("  amos = AMOSOperational()")
    print("  amos.initialize()")
    print("  amos.run_continuous(interval_minutes=60)")
    print("=" * 70)


if __name__ == "__main__":
    demo_operational()
