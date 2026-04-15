#!/usr/bin/env python3
"""
AMOS Autonomous Governance Orchestrator Ω∞∞∞

The ultimate closed-loop self-governing system integrating:
1. Repo Doctor Ω∞∞∞ (60-dimension architectural verification)
2. AMOS Brain (repair synthesis & decision making)
3. Self-Evolution Engine (safe change implementation)
4. Learning System (experience accumulation & pattern recognition)

This creates a self-diagnosing, self-repairing, self-evolving, self-learning
system that maintains its own architectural integrity autonomously.

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS GOVERNANCE LOOP                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  REPO DOCTOR │───→│  AMOS BRAIN  │───→│SELF-EVOLUTION│     │
│  │  (Detect)    │    │  (Synthesize)│    │  (Implement) │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         ↑                                          │            │
│         └──────────────┐  ┌──────────────┐         └────────    │
│                        └──│   LEARNING   │←──────────────────    │
│                           │  (Improve)   │                       │
│                           └──────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


@dataclass
class GovernanceCycle:
    """One complete cycle of autonomous governance."""

    cycle_id: str
    timestamp: float
    repo_doctor_results: dict[str, Any] = field(default_factory=dict)
    brain_decisions: list[dict[str, Any]] = field(default_factory=list)
    evolution_contracts: list[dict[str, Any]] = field(default_factory=list)
    learning_patterns: list[dict[str, Any]] = field(default_factory=list)
    success: bool = False
    energy_before: float = 0.0
    energy_after: float = 0.0


class AutonomousGovernanceOrchestrator:
    """
    The ultimate self-governing system for AMOS.

    Combines defect detection, repair synthesis, safe evolution,
    and continuous learning into a single autonomous loop.
    """

    def __init__(self, repo_path: str = ".") -> None:
        """Initialize the autonomous governance orchestrator."""
        self.repo_path = Path(repo_path)
        self.cycles: list[GovernanceCycle] = []
        self.is_running = False
        self.governance_log: list[dict] = []

        # Initialize subsystems (lazy loading)
        self._repo_doctor: Any = None
        self._brain: Any = None
        self._evolution: Any = None
        self._learning: Any = None

    def _get_repo_doctor(self) -> Any:
        """Lazy-load Repo Doctor Ω∞∞∞."""
        if self._repo_doctor is None:
            try:
                from repo_doctor_omega.engine import RepoDoctorEngine
                self._repo_doctor = RepoDoctorEngine(str(self.repo_path))
            except ImportError as e:
                print(f"⚠ Repo Doctor not available: {e}")
                return None
        return self._repo_doctor

    def _get_brain(self) -> Any:
        """Lazy-load AMOS Brain."""
        if self._brain is None:
            try:
                from amos_brain.facade import AMOSBrainFacade
                self._brain = AMOSBrainFacade()
            except ImportError as e:
                print(f"⚠ AMOS Brain not available: {e}")
                return None
        return self._brain

    def _get_evolution(self) -> Any:
        """Lazy-load Self-Evolution Engine."""
        if self._evolution is None:
            try:
                from repo_doctor.self_evolution.engine import SelfEvolutionEngine
                self._evolution = SelfEvolutionEngine(str(self.repo_path))
            except ImportError as e:
                print(f"⚠ Self-Evolution Engine not available: {e}")
                return None
        return self._evolution

    def _get_learning(self) -> Any:
        """Lazy-load Learning System."""
        if self._learning is None:
            try:
                from repo_doctor.self_evolution.memory import LearningEngine
                self._learning = LearningEngine()
            except ImportError as e:
                print(f"⚠ Learning Engine not available: {e}")
                return None
        return self._learning

    def diagnose(self) -> dict[str, Any]:
        """
        Phase 1: Diagnose repository state using Repo Doctor Ω∞∞∞.

        Computes state vector across all 60 basis dimensions.
        """
        print("\n[PHASE 1] DIAGNOSIS - Repo Doctor Ω∞∞∞")
        print("-" * 60)

        doctor = self._get_repo_doctor()
        if doctor is None:
            return {"error": "Repo Doctor unavailable"}

        # Compute full state
        state = doctor.compute_state()
        energy = state.compute_energy()
        collapsed = state.collapsed_subsystems()

        # Evaluate key invariants
        invariants = doctor.evaluate_invariants()
        failures = [inv for inv in invariants if not inv.passed]

        results = {
            "energy": energy,
            "releasable": state.is_releaseable(),
            "basis_vectors": len(state.amplitudes),
            "collapsed_count": len(collapsed),
            "collapsed_bases": [b.name for b in collapsed],
            "invariants_checked": len(invariants),
            "invariants_failed": len(failures),
            "violations": [
                {
                    "invariant": v.invariant,
                    "message": v.message,
                    "severity": v.severity,
                }
                for inv in failures
                for v in inv.violations[:3]  # Top 3 per invariant
            ],
        }

        print(f"  ✓ Energy: {energy:.6f}")
        print(f"  ✓ Releasable: {results['releasable']}")
        print(f"  ✓ Collapsed: {results['collapsed_count']}/60 basis vectors")
        print(f"  ✓ Invariant failures: {results['invariants_failed']}")

        return results

    def synthesize_repairs(self, diagnosis: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Phase 2: Synthesize repairs using AMOS Brain.

        Converts Repo Doctor violations into actionable repairs.
        """
        print("\n[PHASE 2] SYNTHESIS - AMOS Brain")
        print("-" * 60)

        brain = self._get_brain()
        if brain is None:
            return []

        repairs = []

        for violation in diagnosis.get("violations", []):
            # Query brain for repair strategy
            try:
                decision = brain.make_decision(
                    context={"violation": violation, "repo_path": str(self.repo_path)},
                    options=["repair", "ignore", "escalate"],
                )

                if decision.get("action") == "repair":
                    repair = {
                        "target": violation.get("invariant"),
                        "issue": violation.get("message"),
                        "strategy": decision.get("strategy", "unknown"),
                        "confidence": decision.get("confidence", 0.0),
                        "patch_plan": decision.get("patch", {}),
                    }
                    repairs.append(repair)
                    print(f"  ✓ Synthesized repair for {repair['target']}")

            except Exception as e:
                print(f"  ⚠ Brain decision failed: {e}")

        print(f"  ✓ Total repairs synthesized: {len(repairs)}")
        return repairs

    def evolve(self, repairs: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Phase 3: Implement repairs using Self-Evolution Engine.

        Safely applies changes with rollback capability.
        """
        print("\n[PHASE 3] EVOLUTION - Self-Evolution Engine")
        print("-" * 60)

        evolution = self._get_evolution()
        if evolution is None:
            return {"error": "Evolution engine unavailable"}

        results = {
            "contracts_created": 0,
            "patches_applied": 0,
            "patches_rolled_back": 0,
            "success": True,
        }

        for repair in repairs:
            try:
                # Create evolution contract
                contract = evolution.create_contract(
                    target=repair["target"],
                    patch_plan=repair.get("patch_plan", {}),
                    rollback_on_failure=True,
                )
                results["contracts_created"] += 1

                # Execute with regression guard
                execution = evolution.execute_contract(contract)

                if execution.success:
                    results["patches_applied"] += 1
                    print(f"  ✓ Applied: {repair['target']}")
                else:
                    results["patches_rolled_back"] += 1
                    print(f"  ↺ Rolled back: {repair['target']}")

            except Exception as e:
                print(f"  ✗ Evolution failed for {repair['target']}: {e}")
                results["success"] = False

        return results

    def learn(self, cycle: GovernanceCycle) -> dict[str, Any]:
        """
        Phase 4: Learn from cycle outcome.

        Accumulates patterns for future governance decisions.
        """
        print("\n[PHASE 4] LEARNING - Pattern Recognition")
        print("-" * 60)

        learning = self._get_learning()
        if learning is None:
            return {"error": "Learning engine unavailable"}

        # Extract patterns from cycle
        patterns = []

        # Pattern 1: Which invariants fail together?
        failed_invs = set()
        for v in cycle.repo_doctor_results.get("violations", []):
            failed_invs.add(v.get("invariant"))

        if len(failed_invs) > 1:
            patterns.append({
                "type": "correlation",
                "invariants": list(failed_invs),
                "energy": cycle.energy_before,
            })

        # Pattern 2: Which repairs succeed?
        for decision in cycle.brain_decisions:
            patterns.append({
                "type": "repair_effectiveness",
                "strategy": decision.get("strategy"),
                "success": cycle.success,
                "confidence": decision.get("confidence"),
            })

        # Store patterns
        for pattern in patterns:
            learning.store_pattern(pattern)

        print(f"  ✓ Learned {len(patterns)} patterns")

        return {
            "patterns_learned": len(patterns),
            "total_patterns": learning.get_pattern_count(),
        }

    def run_cycle(self) -> GovernanceCycle:
        """
        Execute one complete autonomous governance cycle.

        Diagnose → Synthesize → Evolve → Learn
        """
        cycle_id = f"cycle-{int(time.time())}"
        print(f"\n{'='*60}")
        print(f"GOVERNANCE CYCLE: {cycle_id}")
        print(f"{'='*60}")

        cycle = GovernanceCycle(
            cycle_id=cycle_id,
            timestamp=time.time(),
        )

        # Phase 1: Diagnose
        diagnosis = self.diagnose()
        cycle.repo_doctor_results = diagnosis
        cycle.energy_before = diagnosis.get("energy", 0.0)

        # Phase 2: Synthesize
        repairs = self.synthesize_repairs(diagnosis)
        cycle.brain_decisions = repairs

        # Phase 3: Evolve
        evolution_results = self.evolve(repairs)
        cycle.evolution_contracts = [evolution_results]
        cycle.success = evolution_results.get("success", False)

        # Re-diagnose to measure improvement
        if cycle.success:
            post_diagnosis = self.diagnose()
            cycle.energy_after = post_diagnosis.get("energy", cycle.energy_before)
        else:
            cycle.energy_after = cycle.energy_before

        # Phase 4: Learn
        learning_results = self.learn(cycle)
        cycle.learning_patterns = [learning_results]

        # Store cycle
        self.cycles.append(cycle)

        # Print summary
        print(f"\n{'='*60}")
        print("CYCLE SUMMARY")
        print(f"{'='*60}")
        print(f"  Energy: {cycle.energy_before:.6f} → {cycle.energy_after:.6f}")
        print(f"  Repairs: {len(repairs)}")
        print(f"  Success: {cycle.success}")
        print(f"  Patterns learned: {learning_results.get('patterns_learned', 0)}")

        return cycle

    def run_continuous(self, interval: int = 3600, max_cycles: int | None = None) -> None:
        """
        Run continuous autonomous governance.

        Args:
            interval: Seconds between cycles
            max_cycles: Maximum cycles (None = infinite)
        """
        print(f"\n{'='*60}")
        print("AUTONOMOUS GOVERNANCE ACTIVATED")
        print(f"{'='*60}")
        print(f"Interval: {interval}s")
        print(f"Max cycles: {max_cycles or 'unlimited'}")
        print(f"Repository: {self.repo_path}")
        print(f"\nPress Ctrl+C to stop\n")

        self.is_running = True
        cycle_count = 0

        try:
            while self.is_running:
                if max_cycles and cycle_count >= max_cycles:
                    print(f"\nReached max cycles ({max_cycles})")
                    break

                cycle = self.run_cycle()
                cycle_count += 1

                # Save state after each cycle
                self._save_governance_state()

                if self.is_running and (max_cycles is None or cycle_count < max_cycles):
                    print(f"\nWaiting {interval}s until next cycle...")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nGovernance stopped by user")
        finally:
            self.is_running = False
            self._save_governance_state()

    def _save_governance_state(self) -> None:
        """Save governance history to disk."""
        state = {
            "cycles": [
                {
                    "id": c.cycle_id,
                    "timestamp": c.timestamp,
                    "success": c.success,
                    "energy_before": c.energy_before,
                    "energy_after": c.energy_after,
                }
                for c in self.cycles
            ],
            "total_cycles": len(self.cycles),
            "successful_cycles": sum(1 for c in self.cycles if c.success),
        }

        output_path = self.repo_path / ".amos_governance_history.json"
        output_path.write_text(json.dumps(state, indent=2))

    def generate_report(self) -> str:
        """Generate comprehensive governance report."""
        lines = []
        lines.append("="*60)
        lines.append("AUTONOMOUS GOVERNANCE REPORT")
        lines.append("="*60)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Repository: {self.repo_path}")
        lines.append(f"Total cycles: {len(self.cycles)}")
        lines.append("")

        if self.cycles:
            successes = sum(1 for c in self.cycles if c.success)
            avg_energy_before = sum(c.energy_before for c in self.cycles) / len(self.cycles)
            avg_energy_after = sum(c.energy_after for c in self.cycles) / len(self.cycles)

            lines.append(f"Successful cycles: {successes}/{len(self.cycles)}")
            lines.append(f"Average energy before: {avg_energy_before:.6f}")
            lines.append(f"Average energy after: {avg_energy_after:.6f}")
            lines.append(f"Net improvement: {avg_energy_before - avg_energy_after:.6f}")

        lines.append("")
        lines.append("="*60)

        return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMOS Autonomous Governance Orchestrator Ω∞∞∞"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Seconds between cycles (default: 3600 = 1 hour)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Maximum cycles (default: unlimited)",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Run single cycle and exit",
    )

    args = parser.parse_args()

    orchestrator = AutonomousGovernanceOrchestrator(args.repo)

    if args.single:
        orchestrator.run_cycle()
        print("\n" + orchestrator.generate_report())
    else:
        orchestrator.run_continuous(args.interval, args.cycles)


if __name__ == "__main__":
    main()
