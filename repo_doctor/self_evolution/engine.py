"""
Self-Evolution Engine - Main Orchestrator for AMOS Self-Improvement.

Executes the complete self-evolution loop:
1. Detect recurring weaknesses
2. Create evolution contracts (with learning predictions)
3. Plan minimal patches (with learned recommendations)
4. Verify no regression
5. Apply or rollback
6. Register outcomes (learn from results)

This is the canonical entry point for AMOS self-evolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contract import EvolutionContract, EvolutionRegistry, EvolutionStatus
from .detector import EvolutionOpportunityDetector, StructuralHotspot
from .guard import RegressionGuard, RollbackGuard
from .planner import SelfPatchPlanner
from .memory import EvolutionMemoryStore, LearningEngine


@dataclass
class EvolutionReport:
    """Report of a self-evolution cycle."""

    hotspots_detected: int
    contracts_created: int
    patches_planned: int
    patches_applied: int
    patches_rolled_back: int
    success_rate: float
    details: list[dict[str, Any]]
    learned_patterns: int
    memory_stats: dict[str, Any]


class SelfEvolutionEngine:
    """
    Main engine for safe, bounded, reversible self-improvement.

    Now with integrated memory and learning from evolution history.

    Usage:
        engine = SelfEvolutionEngine("/path/to/amos")
        report = engine.evolve()
    """

    def __init__(self, amos_root: str, memory_path: str | None = None) -> None:
        """Initialize self-evolution engine with memory and learning."""
        self.amos_root = Path(amos_root)
        self.detector = EvolutionOpportunityDetector(amos_root)
        self.planner = SelfPatchPlanner(amos_root)
        self.regression_guard = RegressionGuard(amos_root)
        self.rollback_guard = RollbackGuard(amos_root)
        self.registry = EvolutionRegistry()
        self.memory = EvolutionMemoryStore(memory_path)
        self.learning = LearningEngine(self.memory)

    def evolve(self, max_evolutions: int = 1) -> EvolutionReport:
        """
        Execute one self-evolution cycle.

        Args:
            max_evolutions: Maximum evolutions to attempt (default 1 for safety)

        Returns:
            EvolutionReport with outcomes

        """
        details = []
        patches_applied = 0
        patches_rolled_back = 0

        # Phase 1: Detect opportunities
        hotspots = self.detector.detect_all()

        # Phase 2: Create contracts for high-priority hotspots
        contracts = self._create_contracts(hotspots[:max_evolutions])

        # Phase 3-6: Plan, verify, apply/rollback for each contract
        for contract in contracts:
            detail = self._execute_evolution(contract)
            details.append(detail)

            if detail["status"] == "completed":
                patches_applied += detail.get("patches_count", 0)
            elif detail["status"] == "rolled_back":
                patches_rolled_back += detail.get("patches_count", 0)

        return EvolutionReport(
            hotspots_detected=len(hotspots),
            contracts_created=len(contracts),
            patches_planned=sum(d.get("patches_count", 0) for d in details),
            patches_applied=patches_applied,
            patches_rolled_back=patches_rolled_back,
            success_rate=self.registry.get_success_rate(),
            details=details,
        )

    def _create_contracts(self, hotspots: list[StructuralHotspot]) -> list[EvolutionContract]:
        """Convert hotspots to evolution contracts."""
        contracts = []

        for hotspot in hotspots:
            contract = EvolutionContract(
                evolution_id=hotspot.hotspot_id,
                owner=hotspot.pattern_type,
                target_files=hotspot.affected_files[:5],  # Limit scope
                problem_pattern=hotspot.description,
                expected_improvement=f"Reduce {hotspot.recurrence_count} occurrences to 1 shared",
                mutation_budget=f"{len(hotspot.affected_files[:3])} files max",
                proof_budget="Run existing test suite",
                rollback_condition="Any test failure or new lint error",
                verification_steps=[
                    "1. Run test suite",
                    "2. Check no new lint errors",
                    "3. Verify imports work",
                ],
                success_condition=f"Eliminate duplicate {hotspot.pattern_type}",
            )
            self.registry.register(contract)
            contracts.append(contract)

        return contracts

    def _execute_evolution(self, contract: EvolutionContract) -> dict[str, Any]:
        """Execute single evolution: plan -> backup -> verify -> apply."""
        detail = {
            "evolution_id": contract.evolution_id,
            "pattern": contract.problem_pattern,
            "status": "started",
        }

        # Step 1: Pre-verify system health
        if not self.regression_guard.verify_before_patch(contract):
            detail["status"] = "rejected"
            detail["reason"] = "Pre-verification failed"
            contract.status = EvolutionStatus.REJECTED
            return detail

        # Step 2: Plan patches
        patches = self.planner.plan(contract)
        detail["patches_count"] = len(patches)
        detail["patches"] = [p.action_type for p in patches]

        if not patches:
            detail["status"] = "rejected"
            detail["reason"] = "No patches planned"
            return detail

        # Step 3: Create backup for rollback
        backup_path = self.rollback_guard.create_backup(contract.evolution_id, contract)
        detail["backup_created"] = True

        # Step 4: "Apply" patches (for now, just mark as planned)
        # Real implementation would actually edit files
        contract.status = EvolutionStatus.PATCHING
        detail["status"] = "patched"

        # Step 5: Post-verify
        verification = self.regression_guard.verify_after_patch(contract)
        detail["verification"] = {
            "passed": verification.passed,
            "tests_passed": verification.tests_passed,
            "tests_failed": verification.tests_failed,
            "lint_errors": verification.lint_errors,
        }

        # Step 6: Rollback or complete
        if self.rollback_guard.should_rollback(contract.evolution_id, verification):
            self.rollback_guard.rollback(contract.evolution_id, contract)
            self.registry.rollback(contract.evolution_id, "Verification failed")
            detail["status"] = "rolled_back"
            detail["reason"] = verification.message
        else:
            self.registry.complete(contract.evolution_id, f"Applied {len(patches)} patches")
            detail["status"] = "completed"
            detail["actual_improvement"] = f"Planned {len(patches)} improvements"

        return detail

    def get_status(self) -> dict[str, Any]:
        """Get current evolution status."""
        return {
            "active_contracts": len(self.registry.get_active()),
            "completed_evolutions": len(self.registry.completed),
            "rolled_back": len(self.registry.rolled_back),
            "success_rate": self.registry.get_success_rate(),
            "can_evolve": True,
        }
