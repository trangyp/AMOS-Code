"""
Repair Planning Module - Architecture-Aware Minimal Patch Set Generation

Generates:
- Ordered patch plan
- Smallest safe repair set
- Files affected
- Risk score
- Architecture-aware constraints (boundary preservation, authority reduction, etc.)

Architecture-aware objective:
    min_R [
        c1·EditCost +
        c2·BlastRadius +
        c3·EntanglementRisk +
        c4·RollbackCost +
        c5·RolloutCost +
        c6·AuthorityDuplicationIncrease +
        c7·BoundaryViolationIncrease
        - c8·EnergyReduction
        - c9·ArchitectureIntegrityGain
    ]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .arch_invariants import ArchInvariantResult
from .invariants_legacy import InvariantResult
from .state_vector import RepoStateVector, StateDimension


@dataclass
class RepairAction:
    """A single repair action with architecture-aware constraints."""

    priority: int
    description: str
    files_to_modify: list[str]
    invariant_dimension: StateDimension | None = None
    estimated_risk: str = "medium"  # "low", "medium", "high"
    auto_fixable: bool = False
    fix_suggestion: str = None

    # Architecture-aware repair constraints (from spec section 10)
    restores_local_invariants: bool = True
    restores_arch_invariants: bool = True
    reduces_authority_duplication: bool = True
    preserves_boundary_integrity: bool = True
    preserves_upgrade_admissibility: bool = True
    preserves_rollout_safety: bool = True
    preserves_observability: bool = True

    # Architecture violation context (if any)
    arch_violation_type: str = None
    arch_violation_details: dict[str, Any] = field(default_factory=dict)


@dataclass
class RepairPlan:
    """Complete repair plan for a repository."""

    state: RepoStateVector
    total_score: int
    actions: list[RepairAction]
    total_risk: str
    estimated_time: str
    automated_fixes: list[RepairAction] = field(default_factory=list)
    manual_fixes: list[RepairAction] = field(default_factory=list)


class RepairPlanner:
    """
    Generates repair plans from invariant failures.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()

    def generate_plan(
        self, state: RepoStateVector, invariant_results: list[InvariantResult]
    ) -> RepairPlan:
        """
        Generate a repair plan from current state and invariant failures.
        """
        actions: list[RepairAction] = []

        # Generate actions for each failed invariant
        for result in invariant_results:
            if not result.passed:
                action = self._create_action_for_failure(result)
                if action:
                    actions.append(action)

        # Sort by priority (lower = more urgent)
        actions.sort(key=lambda a: a.priority)

        # Split into automated and manual
        automated = [a for a in actions if a.auto_fixable]
        manual = [a for a in actions if not a.auto_fixable]

        # Calculate total risk
        high_risk_count = sum(1 for a in actions if a.estimated_risk == "high")
        total_risk = "high" if high_risk_count > 0 else "medium" if len(actions) > 3 else "low"

        # Estimate time
        if len(actions) <= 2:
            est_time = "< 1 hour"
        elif len(actions) <= 5:
            est_time = "1-3 hours"
        else:
            est_time = "3+ hours"

        return RepairPlan(
            state=state,
            total_score=state.score(),
            actions=actions,
            total_risk=total_risk,
            estimated_time=est_time,
            automated_fixes=automated,
            manual_fixes=manual,
        )

    def _create_action_for_failure(self, result: InvariantResult) -> RepairAction | None:
        """Create a repair action for a specific invariant failure."""
        if result.dimension == StateDimension.SYNTAX:
            return RepairAction(
                priority=1,
                description=f"Fix syntax errors in {len(result.files_affected)} file(s)",
                files_to_modify=result.files_affected,
                invariant_dimension=result.dimension,
                estimated_risk="low",
                auto_fixable=False,
                fix_suggestion="Fix the reported syntax errors in each file",
            )

        elif result.dimension == StateDimension.IMPORT:
            return RepairAction(
                priority=2,
                description=f"Fix {len(result.details)} unresolved imports",
                files_to_modify=result.files_affected,
                invariant_dimension=result.dimension,
                estimated_risk="medium",
                auto_fixable=False,
                fix_suggestion="Add missing dependencies or fix import paths",
            )

        elif result.dimension == StateDimension.PACKAGING:
            return RepairAction(
                priority=1,
                description="Fix packaging configuration",
                files_to_modify=["pyproject.toml", "setup.py"],
                invariant_dimension=result.dimension,
                estimated_risk="medium",
                auto_fixable=True,
                fix_suggestion=result.details[0] if result.details else None,
            )

        elif result.dimension == StateDimension.CONFIG:
            return RepairAction(
                priority=1,
                description="Fix entrypoint definitions",
                files_to_modify=["pyproject.toml"],
                invariant_dimension=result.dimension,
                estimated_risk="medium",
                auto_fixable=True,
                fix_suggestion="Correct entrypoint module:function paths",
            )

        elif result.dimension == StateDimension.API:
            return RepairAction(
                priority=3,
                description="Fix API contract violations",
                files_to_modify=result.files_affected or ["__init__.py"],
                invariant_dimension=result.dimension,
                estimated_risk="high",
                auto_fixable=False,
                fix_suggestion="Align public API with runtime exports",
            )

        elif result.dimension == StateDimension.BUILD:
            return RepairAction(
                priority=2,
                description="Fix build configuration",
                files_to_modify=["pyproject.toml"],
                invariant_dimension=result.dimension,
                estimated_risk="medium",
                auto_fixable=True,
                fix_suggestion="Validate pyproject.toml structure",
            )

        elif result.dimension == StateDimension.TEST:
            return RepairAction(
                priority=4,
                description="Fix test collection issues",
                files_to_modify=["tests/"],
                invariant_dimension=result.dimension,
                estimated_risk="low",
                auto_fixable=False,
                fix_suggestion="Fix test imports and dependencies",
            )

        elif result.dimension == StateDimension.SECURITY:
            return RepairAction(
                priority=1,
                description="Address security warnings",
                files_to_modify=result.files_affected,
                invariant_dimension=result.dimension,
                estimated_risk="high",
                auto_fixable=False,
                fix_suggestion="Remove dangerous patterns (eval, exec)",
            )

        return None

    def generate_architecture_plan(
        self,
        state: RepoStateVector,
        arch_results: list[ArchInvariantResult],
    ) -> RepairPlan:
        """
        Generate a repair plan from architectural invariant failures.

        Architecture-aware repair planning considers:
        - Authority duplication reduction
        - Boundary integrity preservation
        - Upgrade admissibility
        - Rollout safety
        """
        actions: list[RepairAction] = []

        for result in arch_results:
            if not result.passed:
                action = self._create_arch_action_for_failure(result)
                if action:
                    actions.append(action)

        # Sort by priority and architectural severity
        actions.sort(key=lambda a: (a.priority, not a.preserves_boundary_integrity))

        # Split into automated and manual
        automated = [a for a in actions if a.auto_fixable]
        manual = [a for a in actions if not a.auto_fixable]

        # Calculate total risk considering architecture
        arch_risk_factors = sum(
            1
            for a in actions
            if not a.preserves_boundary_integrity or not a.reduces_authority_duplication
        )
        total_risk = "high" if arch_risk_factors > 2 else "medium" if actions else "low"

        return RepairPlan(
            state=state,
            total_score=state.score(),
            actions=actions,
            total_risk=total_risk,
            estimated_time=self._estimate_arch_time(actions),
            automated_fixes=automated,
            manual_fixes=manual,
        )

    def _create_arch_action_for_failure(self, result: ArchInvariantResult) -> RepairAction | None:
        """Create an architecture-aware repair action for an arch invariant failure."""
        if result.invariant_name == "boundary_integrity":
            return RepairAction(
                priority=2,
                description=f"Fix boundary violation: {result.message}",
                files_to_modify=["architecture.md", "docs/architecture.rst"],
                invariant_dimension=StateDimension.ARCHITECTURE,
                estimated_risk="high",
                auto_fixable=False,
                fix_suggestion="Restructure to ensure components enforce policy only within their declared boundary",
                restores_arch_invariants=True,
                preserves_boundary_integrity=True,
                arch_violation_type="boundary_violation",
                arch_violation_details={"violations": result.violations},
            )

        elif result.invariant_name == "single_authority":
            return RepairAction(
                priority=1,
                description=f"Consolidate authority: {result.message}",
                files_to_modify=["pyproject.toml", "__init__.py"],
                invariant_dimension=StateDimension.ARCHITECTURE,
                estimated_risk="high",
                auto_fixable=False,
                fix_suggestion="Designate exactly one canonical source of truth for each architectural fact",
                restores_arch_invariants=True,
                reduces_authority_duplication=True,
                arch_violation_type="authority_duplication",
            )

        elif result.invariant_name == "plane_separation":
            return RepairAction(
                priority=2,
                description=f"Fix plane separation: {result.message}",
                files_to_modify=[],
                invariant_dimension=StateDimension.ARCHITECTURE,
                estimated_risk="medium",
                auto_fixable=False,
                fix_suggestion="Ensure control/data/execution/observation planes remain distinct",
                restores_arch_invariants=True,
                preserves_boundary_integrity=True,
                arch_violation_type="plane_violation",
            )

        elif result.invariant_name == "hidden_interfaces":
            return RepairAction(
                priority=4,
                description=f"Document hidden interfaces: {result.message}",
                files_to_modify=["docs/interfaces.md"],
                invariant_dimension=StateDimension.HIDDEN_STATE,
                estimated_risk="low",
                auto_fixable=False,
                fix_suggestion="Explicitly declare all operationally significant interfaces",
                restores_arch_invariants=True,
                arch_violation_type="hidden_interface",
            )

        elif result.invariant_name == "folklore_free":
            return RepairAction(
                priority=3,
                description=f"Eliminate folklore: {result.message}",
                files_to_modify=["README.md", "scripts/"],
                invariant_dimension=StateDimension.HIDDEN_STATE,
                estimated_risk="medium",
                auto_fixable=False,
                fix_suggestion="Automate or explicitly document correctness-critical operations",
                restores_arch_invariants=True,
                preserves_rollout_safety=True,
                arch_violation_type="folklore_dependency",
            )

        elif result.invariant_name == "architecture_drift":
            return RepairAction(
                priority=1,
                description=f"Fix architecture drift: {result.message}",
                files_to_modify=["pyproject.toml", "docs/architecture.md"],
                invariant_dimension=StateDimension.ARCHITECTURE,
                estimated_risk="high",
                auto_fixable=False,
                fix_suggestion="Align declared architecture with actual implementation",
                restores_arch_invariants=True,
                preserves_upgrade_admissibility=True,
                arch_violation_type="architecture_drift",
            )

        elif result.invariant_name == "upgrade_geometry":
            return RepairAction(
                priority=2,
                description=f"Fix upgrade geometry: {result.message}",
                files_to_modify=["migrations/", "docs/upgrades.md"],
                invariant_dimension=StateDimension.ARCHITECTURE,
                estimated_risk="high",
                auto_fixable=False,
                fix_suggestion="Ensure all upgrade/rollback paths preserve architectural validity",
                restores_arch_invariants=True,
                preserves_upgrade_admissibility=True,
                preserves_rollout_safety=True,
                arch_violation_type="upgrade_failure",
            )

        return None

    def _estimate_arch_time(self, actions: list[RepairAction]) -> str:
        """Estimate time for architecture repairs based on complexity."""
        if not actions:
            return "< 1 hour"

        high_risk = sum(1 for a in actions if a.estimated_risk == "high")
        arch_complex = sum(1 for a in actions if not a.preserves_boundary_integrity)

        total = len(actions) + high_risk * 2 + arch_complex * 3

        if total <= 3:
            return "1-3 hours"
        elif total <= 8:
            return "3-8 hours"
        else:
            return "8+ hours (architectural refactoring)"

    def get_minimal_patch_set(self, plan: RepairPlan) -> list[RepairAction]:
        """
        Get the minimal set of actions to restore releaseability.
        Focus on hard-fail invariants first.
        """
        hard_fail_dims = {
            StateDimension.SYNTAX,
            StateDimension.IMPORT,
            StateDimension.PACKAGING,
            StateDimension.API,
            StateDimension.CONFIG,
        }

        # Get actions for hard-fail dimensions
        critical = [a for a in plan.actions if a.invariant_dimension in hard_fail_dims]

        # Sort by priority
        critical.sort(key=lambda a: a.priority)

        return critical

    def format_plan(self, plan: RepairPlan) -> str:
        """Format the repair plan as a readable report."""
        lines = [
            "=" * 70,
            "REPAIR PLAN",
            "=" * 70,
            f"Current Score: {plan.total_score}/100",
            f"Total Risk: {plan.total_risk.upper()}",
            f"Estimated Time: {plan.estimated_time}",
            f"Total Actions: {len(plan.actions)}",
            f"Automated: {len(plan.automated_fixes)} | Manual: {len(plan.manual_fixes)}",
            "-" * 70,
        ]

        # Minimal patch set for release
        minimal = self.get_minimal_patch_set(plan)
        if minimal:
            lines.append("\nMINIMAL PATCH SET (for releaseability):")
            lines.append("-" * 70)
            for i, action in enumerate(minimal, 1):
                auto = "[AUTO]" if action.auto_fixable else "[MANUAL]"
                lines.append(f"{i}. [{action.priority}] {auto} {action.description}")
                lines.append(f"   Risk: {action.estimated_risk}")
                if action.files_to_modify:
                    files_str = ", ".join(action.files_to_modify[:3])
                    if len(action.files_to_modify) > 3:
                        files_str += f" (+{len(action.files_to_modify) - 3} more)"
                    lines.append(f"   Files: {files_str}")
                if action.fix_suggestion:
                    lines.append(f"   Suggestion: {action.fix_suggestion}")
                lines.append("")

        # All actions
        if len(plan.actions) > len(minimal):
            lines.append("\nALL REPAIR ACTIONS:")
            lines.append("-" * 70)
            for i, action in enumerate(plan.actions, 1):
                auto = "[AUTO]" if action.auto_fixable else "[MANUAL]"
                lines.append(f"{i}. [{action.priority}] {auto} {action.description}")

        lines.append("=" * 70)

        return "\n".join(lines)

    def export_patch_script(self, plan: RepairPlan, output_path: str | Path) -> bool:
        """
        Export automated fixes as a shell script.
        """
        if not plan.automated_fixes:
            return False

        lines = [
            "#!/bin/bash",
            "# Auto-generated repair script from repo-doctor",
            f"# Generated for: {self.repo_path}",
            "",
            "set -e",
            "",
        ]

        for action in plan.automated_fixes:
            lines.append(f"# {action.description}")
            if action.fix_suggestion:
                lines.append(f"# Suggestion: {action.fix_suggestion}")
            lines.append("")

        lines.append("echo 'Automated repairs complete'")
        lines.append("echo 'Please run repo-doctor scan to verify fixes'")

        try:
            output_path = Path(output_path)
            output_path.write_text("\n".join(lines))
            output_path.chmod(0o755)
            return True
        except Exception:
            return False


class AutoFixRunner:
    """
    Executes automated fixes using external tools.

    Supports:
    - ruff check --fix (auto-fix linting issues)
    - ruff format (code formatting)
    - black (code formatting)
    - isort (import sorting)
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.results: list[dict] = []

    def run_all(self, dry_run: bool = False) -> list[dict]:
        """
        Run all available auto-fixers.

        Args:
        ----
            dry_run: If True, only show what would be fixed

        Returns:
        -------
            List of fix results

        """
        self.results = []

        # Run ruff fix if available
        if self._is_available("ruff"):
            ruff_fix = self._run_ruff_fix(dry_run)
            if ruff_fix:
                self.results.append(ruff_fix)
            ruff_fmt = self._run_ruff_format(dry_run)
            if ruff_fmt:
                self.results.append(ruff_fmt)

        return self.results

    def _is_available(self, tool: str) -> bool:
        """Check if a tool is available in PATH."""
        import shutil

        return shutil.which(tool) is not None

    def _run_ruff_fix(self, dry_run: bool = False) -> dict:
        """Run ruff check --fix to auto-fix linting issues."""
        if not self._is_available("ruff"):
            return None

        import subprocess

        cmd = ["ruff", "check"]
        if not dry_run:
            cmd.append("--fix")
        cmd.append(".")

        try:
            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, timeout=120
            )

            # Parse output to count fixes
            fixed_count = 0
            if result.stdout:
                # Count lines that indicate fixes
                for line in result.stdout.split("\n"):
                    if "Fixed" in line or "fixed" in line:
                        fixed_count += 1

            return {
                "tool": "ruff",
                "command": " ".join(cmd),
                "success": result.returncode in [0, 1],  # 1 means issues remain
                "fixed_count": fixed_count,
                "output": result.stdout[:500] if result.stdout else "",
                "dry_run": dry_run,
            }

        except subprocess.TimeoutExpired:
            return {
                "tool": "ruff",
                "command": " ".join(cmd),
                "success": False,
                "error": "Timeout (>120s)",
                "dry_run": dry_run,
            }
        except Exception as e:
            return {
                "tool": "ruff",
                "command": " ".join(cmd),
                "success": False,
                "error": str(e),
                "dry_run": dry_run,
            }

    def _run_ruff_format(self, dry_run: bool = False) -> dict:
        """Run ruff format to format code."""
        if not self._is_available("ruff"):
            return None

        import subprocess

        cmd = ["ruff", "format"]
        if dry_run:
            cmd.append("--check")
        cmd.append(".")

        try:
            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, timeout=120
            )

            # Parse output
            files_formatted = 0
            if result.stdout:
                # Look for "X files formatted" in output
                for line in result.stdout.split("\n"):
                    if "files formatted" in line:
                        try:
                            files_formatted = int(line.split()[0])
                        except (ValueError, IndexError):
                            pass

            return {
                "tool": "ruff-format",
                "command": " ".join(cmd),
                "success": result.returncode in [0, 1],
                "files_formatted": files_formatted,
                "output": result.stdout[:500] if result.stdout else "",
                "dry_run": dry_run,
            }

        except subprocess.TimeoutExpired:
            return {
                "tool": "ruff-format",
                "command": " ".join(cmd),
                "success": False,
                "error": "Timeout (>120s)",
                "dry_run": dry_run,
            }
        except Exception as e:
            return {
                "tool": "ruff-format",
                "command": " ".join(cmd),
                "success": False,
                "error": str(e),
                "dry_run": dry_run,
            }

    def get_report(self) -> str:
        """Generate a report of fix results."""
        if not self.results:
            return "No auto-fixes run."

        lines = [
            "=" * 60,
            "AUTO-FIX RESULTS",
            "=" * 60,
        ]

        total_fixed = 0
        for result in self.results:
            tool = result.get("tool", "unknown")
            success = result.get("success", False)
            status = "✓" if success else "✗"

            lines.append(f"\n{status} {tool}")

            if "fixed_count" in result:
                lines.append(f"  Fixed: {result['fixed_count']} issues")
                total_fixed += result["fixed_count"]

            if "files_formatted" in result:
                lines.append(f"  Formatted: {result['files_formatted']} files")

            if "error" in result:
                lines.append(f"  Error: {result['error']}")

            if result.get("dry_run"):
                lines.append("  [DRY RUN - no changes made]")

        lines.append(f"\nTotal issues fixed: {total_fixed}")
        lines.append("=" * 60)

        return "\n".join(lines)
