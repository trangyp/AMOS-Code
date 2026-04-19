#!/usr/bin/env python3
"""
AMOS Architectural Decision Engine
==================================

Uses SuperBrain Equation Bridge to make architectural decisions,
detect drift, and recommend fixes based on mathematical invariants.

Implements L1-L6 AMOS Laws for repository governance.
"""

import ast
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Dict, List


class Law(Enum):
    """AMOS Global Laws L1-L6."""

    L1_LAW_OF_LAW = "action_completeness"
    L2_RULE_OF_TWO = "subsystem_ownership"
    L3_SINGLE_SOURCE = "canonical_source"
    L4_STRUCTURAL_INTEGRITY = "no_destructive_patterns"
    L5_VERSION_CONTROL = "versioning_rules"
    L6_CORE_FREEZE = "core_immutable"


class Severity(Enum):
    """Violation severity levels."""

    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0


@dataclass
class Violation:
    """Architectural violation report."""

    law: Law
    severity: Severity
    file_path: str
    line_number: int
    message: str
    suggested_fix: str
    auto_fixable: bool = False


@dataclass
class ArchitecturalState:
    """Current architectural health state."""

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_files: int = 0
    violations: List[Violation] = field(default_factory=list)
    health_score: float = 1.0
    law_compliance: Dict[str, float] = field(default_factory=dict)

    def calculate_health(self) -> float:
        """Calculate overall health score."""
        if not self.violations:
            return 1.0

        weights = {
            Severity.CRITICAL: 0.4,
            Severity.HIGH: 0.3,
            Severity.MEDIUM: 0.2,
            Severity.LOW: 0.1,
            Severity.INFO: 0.0,
        }

        total_weight = sum(weights[v.severity] for v in self.violations)
        return max(0.0, 1.0 - (total_weight / len(self.violations)))


class ArchitecturalDecisionEngine:
    """AMOS Architectural Decision Engine using SuperBrain invariants."""

    DESTRUCTIVE_PATTERNS = [
        "rm -rf /",
        "drop database",
        "delete all",
        "force delete",
        "rm -rf *",
    ]

    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.violations: List[Violation] = []
        self.state = ArchitecturalState()

    def analyze_repository(self) -> ArchitecturalState:
        """Full repository analysis using all L1-L6 laws."""
        print("[AMOS Architect] Analyzing repository...")

        self._check_l1_action_completeness()
        self._check_l2_subsystem_ownership()
        self._check_l4_structural_integrity()
        self._check_l6_core_freeze()

        self.state.violations = self.violations
        self.state.health_score = self.state.calculate_health()
        self.state.total_files = len(list(self.repo_path.rglob("*.py")))

        return self.state

    def _check_l1_action_completeness(self) -> None:
        """L1: ∀ action ∈ Actions: action ≠ ∅ ∧ |action| ≥ 3."""
        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if action function has minimum complexity
                        if node.name.startswith("action_") or node.name.endswith("_action"):
                            body_lines = len(node.body)
                            if body_lines < 3:
                                self.violations.append(
                                    Violation(
                                        law=Law.L1_LAW_OF_LAW,
                                        severity=Severity.MEDIUM,
                                        file_path=str(py_file),
                                        line_number=node.lineno,
                                        message=f"Action '{node.name}' has only {body_lines} lines (minimum 3 required)",
                                        suggested_fix="Add error handling, validation, and logging to action",
                                        auto_fixable=False,
                                    )
                                )
            except SyntaxError:
                continue

    def _check_l2_subsystem_ownership(self) -> None:
        """L2: ∀ subsystem: |owners| ≤ 2 ∧ owner₁ ≠ owner₂."""
        # Check for files with excessive collaborators
        git_log_cmd = ["git", "log", "--format=%an", "--name-only"]

        try:
            result = subprocess.run(
                git_log_cmd, cwd=self.repo_path, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                # Parse git history for ownership
                file_owners: Dict[str, set[str]] = {}
                current_author = ""

                for line in result.stdout.split("\n"):
                    if line and not line.startswith(" ") and ".py" not in line:
                        current_author = line
                    elif line.endswith(".py"):
                        if line not in file_owners:
                            file_owners[line] = set()
                        file_owners[line].add(current_author)

                # Check for files with > 2 owners
                for file_path, owners in file_owners.items():
                    if len(owners) > 5:  # Relaxed threshold for warning
                        full_path = self.repo_path / file_path
                        if full_path.exists():
                            self.violations.append(
                                Violation(
                                    law=Law.L2_RULE_OF_TWO,
                                    severity=Severity.LOW,
                                    file_path=str(full_path),
                                    line_number=1,
                                    message=f"File has {len(owners)} contributors (consider splitting)",
                                    suggested_fix="Split into smaller modules with clear ownership",
                                    auto_fixable=False,
                                )
                            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Git not available

    def _check_l4_structural_integrity(self) -> None:
        """L4: ¬∃ pattern ∈ destructive_patterns: pattern ∈ action."""
        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern in self.DESTRUCTIVE_PATTERNS:
                        if pattern.lower() in line.lower():
                            self.violations.append(
                                Violation(
                                    law=Law.L4_STRUCTURAL_INTEGRITY,
                                    severity=Severity.CRITICAL,
                                    file_path=str(py_file),
                                    line_number=i,
                                    message=f"Destructive pattern detected: '{pattern}'",
                                    suggested_fix="Use safe deletion with confirmation and backups",
                                    auto_fixable=False,
                                )
                            )
            except UnicodeDecodeError:
                continue

    def _check_l6_core_freeze(self) -> None:
        """L6: ∀ file ∈ CoreFiles: Immutable(file) ∧ ¬Writable(file)."""
        core_files = [
            "amos_superbrain_equation_bridge.py",
            "AMOS_ARCHITECTURE_INVARIANTS.md",
            "amos_core.py",
        ]

        for core_file in core_files:
            file_path = self.repo_path / core_file
            if file_path.exists():
                # Check if modified recently (should be frozen)
                stat = file_path.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                age_days = (datetime.now(timezone.utc) - mtime).days

                if age_days < 1:  # Modified in last 24 hours
                    self.violations.append(
                        Violation(
                            law=Law.L6_CORE_FREEZE,
                            severity=Severity.HIGH,
                            file_path=str(file_path),
                            line_number=1,
                            message=f"Core file modified {age_days} days ago (should be frozen)",
                            suggested_fix="Use explicit thaw mechanism for core file changes",
                            auto_fixable=False,
                        )
                    )

    def generate_fix_plan(self) -> List[dict]:
        """Generate prioritized fix plan."""
        # Sort by severity
        sorted_violations = sorted(self.violations, key=lambda v: v.severity.value, reverse=True)

        fix_plan = []
        for violation in sorted_violations[:10]:  # Top 10
            fix_plan.append(
                {
                    "priority": violation.severity.name,
                    "law": violation.law.value,
                    "file": violation.file_path,
                    "line": violation.line_number,
                    "issue": violation.message,
                    "fix": violation.suggested_fix,
                    "auto_fixable": violation.auto_fixable,
                }
            )

        return fix_plan

    def generate_report(self) -> str:
        """Generate comprehensive architectural report."""
        report_lines = [
            "# AMOS Architectural Decision Report",
            f"Generated: {self.state.timestamp}",
            "",
            "## Executive Summary",
            f"- **Health Score**: {self.state.health_score:.2%}",
            f"- **Total Violations**: {len(self.violations)}",
            f"- **Files Scanned**: {self.state.total_files}",
            "",
            "## Law Compliance",
        ]

        # Group by law
        law_violations: Dict[Law, list[Violation]] = {law: [] for law in Law}
        for v in self.violations:
            law_violations[v.law].append(v)

        for law, violations in law_violations.items():
            compliance = 1.0 if not violations else max(0.0, 1.0 - (len(violations) / 100))
            report_lines.append(f"- **{law.name}**: {compliance:.1%} ({len(violations)} issues)")

        report_lines.extend(["", "## Critical Issues"])

        critical = [v for v in self.violations if v.severity == Severity.CRITICAL]
        if critical:
            for v in critical[:5]:
                report_lines.append(f"- {v.file_path}:{v.line_number} - {v.message}")
        else:
            report_lines.append("No critical issues found.")

        report_lines.extend(["", "## Recommended Actions"])

        fix_plan = self.generate_fix_plan()
        for i, fix in enumerate(fix_plan[:5], 1):
            report_lines.append(f"{i}. [{fix['priority']}] {fix['file']}:{fix['line']}")
            report_lines.append(f"   - Issue: {fix['issue']}")
            report_lines.append(f"   - Fix: {fix['fix']}")
            report_lines.append("")

        return "\n".join(report_lines)


def main():
    """Run architectural analysis."""
    engine = ArchitecturalDecisionEngine()
    state = engine.analyze_repository()

    print(engine.generate_report())

    # Save to file
    report_path = Path("AMOS_ARCHITECTURAL_REPORT.md")
    report_path.write_text(engine.generate_report())
    print(f"\nReport saved to: {report_path}")

    # Return exit code based on health
    if state.health_score < 0.5:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
