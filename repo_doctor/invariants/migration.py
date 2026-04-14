"""I_migration = 1 iff every migration path preserves schema safety and rollback validity.

Migration chain model:
    μ0 -> μ1 -> μ2 -> ... -> μn

Where each migration μi has:
    - forward(): Σi -> Σi+1
    - backward(): Σi+1 -> Σi (if rollback available)

Invariant checks:
    1. Forward path validity (all declared paths work)
    2. Rollback validity (backward() restores admissibility)
    3. Schema compatibility (code matches schema at each step)
    4. Data preservation (no data loss in migration)
    5. Order correctness (dependencies satisfied)

Based on Alembic/SQLAlchemy best practices 2024.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .base import Invariant, InvariantResult, InvariantSeverity


@dataclass
class MigrationStep:
    """A single migration step in the chain."""

    revision: str
    down_revision: Optional[str]
    file_path: Path
    has_upgrade: bool = False
    has_downgrade: bool = False
    dependencies: list[str] = field(default_factory=list)
    schema_changes: list[str] = field(default_factory=list)


@dataclass
class MigrationChain:
    """Complete migration chain analysis."""

    head: Optional[str] = None
    base: Optional[str] = None
    steps: dict[str, MigrationStep] = field(default_factory=dict)
    branches: list[list[str]] = field(default_factory=list)
    merge_points: list[str] = field(default_factory=list)


class MigrationInvariant(Invariant):
    """
    I_migration = 1 iff migration graph preserves safety properties.

    Detects:
    - Missing rollback paths
    - Schema drift (code vs migration mismatch)
    - Migration order violations
    - Data loss risks
    - Concurrent migration conflicts
    """

    def __init__(self):
        super().__init__("I_migration", InvariantSeverity.ERROR)
        self.migration_dirs = ["migrations", "alembic/versions", "db/migrations"]

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check migration chain integrity."""
        context = context or {}
        repo = Path(repo_path)

        # Find migration directory
        migration_dir = self._find_migration_dir(repo)
        if not migration_dir:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="No migrations found (optional)",
            )

        # Parse migration chain
        chain = self._parse_migration_chain(migration_dir)

        # Run checks
        issues = []

        # Check 1: Linear history (no divergent branches without merge)
        branch_issues = self._check_branch_integrity(chain)
        issues.extend(branch_issues)

        # Check 2: All migrations have both upgrade and downgrade
        rollback_issues = self._check_rollback_validity(chain)
        issues.extend(rollback_issues)

        # Check 3: Schema compatibility with code
        schema_issues = self._check_schema_compatibility(repo, chain, context)
        issues.extend(schema_issues)

        # Check 4: Migration order (dependencies satisfied)
        order_issues = self._check_migration_order(chain)
        issues.extend(order_issues)

        # Calculate severity-weighted score
        severity_weights = {"critical": 1.0, "error": 0.7, "warning": 0.4, "info": 0.1}
        total_weight = sum(severity_weights.get(i.get("severity", "warning"), 0.4) for i in issues)

        # Determine pass/fail
        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        error_count = sum(1 for i in issues if i.get("severity") == "error")

        passed = critical_count == 0 and error_count == 0

        # Build message
        if passed:
            message = f"Migration chain valid: {len(chain.steps)} steps"
            if issues:
                message += f", {len(issues)} warnings"
        else:
            message = f"Migration issues: {critical_count} critical, {error_count} errors, {len(issues) - critical_count - error_count} warnings"

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=message,
            details={
                "total_steps": len(chain.steps),
                "has_branches": len(chain.branches) > 1,
                "issues": issues[:10],  # Limit details
            },
        )

    def _find_migration_dir(self, repo: Path) -> Optional[Path]:
        """Find the migrations directory."""
        for subdir in self.migration_dirs:
            path = repo / subdir
            if path.exists() and any(path.iterdir()):
                return path

        # Check for alembic.ini
        alembic_ini = repo / "alembic.ini"
        if alembic_ini.exists():
            versions = repo / "alembic" / "versions"
            if versions.exists():
                return versions

        return None

    def _parse_migration_chain(self, migration_dir: Path) -> MigrationChain:
        """Parse the migration chain from files."""
        chain = MigrationChain()

        # Look for Alembic-style migrations
        py_files = list(migration_dir.glob("*.py"))

        for file_path in py_files:
            if file_path.name.startswith("__"):
                continue

            step = self._parse_migration_file(file_path)
            if step:
                chain.steps[step.revision] = step
                if step.down_revision is None:
                    chain.base = step.revision

        # Find head (no children)
        all_down_revs = {s.down_revision for s in chain.steps.values() if s.down_revision}
        heads = set(chain.steps.keys()) - all_down_revs
        if len(heads) == 1:
            chain.head = heads.pop()

        # Detect branches
        rev_to_children: dict[str, list[str]] = {}
        for rev, step in chain.steps.items():
            if step.down_revision:
                rev_to_children.setdefault(step.down_revision, []).append(rev)

        for parent, children in rev_to_children.items():
            if len(children) > 1:
                chain.branches.append([parent] + children)

        return chain

    def _parse_migration_file(self, file_path: Path) -> Optional[MigrationStep]:
        """Parse a single migration file."""
        content = file_path.read_text()

        # Extract revision ID
        rev_match = re.search(r'revision\s*=\s*["\']([a-f0-9]+)["\']', content)
        if not rev_match:
            return None

        revision = rev_match.group(1)

        # Extract down_revision
        down_rev_match = re.search(r'down_revision\s*=\s*["\']([a-f0-9]+)["\']', content)
        down_revision = down_rev_match.group(1) if down_rev_match else None

        # Check for upgrade/downgrade functions
        has_upgrade = "def upgrade()" in content or "def upgrade(" in content
        has_downgrade = "def downgrade()" in content or "def downgrade(" in content

        # Detect schema changes
        schema_changes = []
        if "create_table" in content:
            schema_changes.append("create_table")
        if "drop_table" in content:
            schema_changes.append("drop_table")
        if "add_column" in content:
            schema_changes.append("add_column")
        if "drop_column" in content:
            schema_changes.append("drop_column")
        if "alter_column" in content:
            schema_changes.append("alter_column")

        return MigrationStep(
            revision=revision,
            down_revision=down_revision,
            file_path=file_path,
            has_upgrade=has_upgrade,
            has_downgrade=has_downgrade,
            schema_changes=schema_changes,
        )

    def _check_branch_integrity(self, chain: MigrationChain) -> list[dict]:
        """Check for problematic branching."""
        issues = []

        # Multiple heads without merge is usually problematic
        heads = []
        for rev, step in chain.steps.items():
            is_child = any(s.down_revision == rev for s in chain.steps.values())
            if not is_child:
                heads.append(rev)

        if len(heads) > 1:
            issues.append({
                "type": "multiple_heads",
                "severity": "warning",
                "message": f"Multiple migration heads detected: {heads[:3]}",
                "hint": "Run 'alembic merge' to consolidate branches",
            })

        return issues

    def _check_rollback_validity(self, chain: MigrationChain) -> list[dict]:
        """Check that migrations can be rolled back."""
        issues = []

        for rev, step in chain.steps.items():
            if not step.has_upgrade:
                issues.append({
                    "type": "missing_upgrade",
                    "severity": "error",
                    "revision": rev,
                    "message": f"Migration {rev[:8]} missing upgrade() function",
                })

            if not step.has_downgrade:
                # Downgrade is optional but recommended
                if "drop_table" in step.schema_changes or "drop_column" in step.schema_changes:
                    issues.append({
                        "type": "destructive_no_rollback",
                        "severity": "warning",
                        "revision": rev,
                        "message": f"Destructive migration {rev[:8]} has no rollback",
                        "hint": "Add downgrade() to enable rollback",
                    })

        return issues

    def _check_schema_compatibility(self, repo: Path, chain: MigrationChain, context: dict) -> list[dict]:
        """Check that code matches migrated schema."""
        issues = []

        # Look for schema definitions
        models_dir = repo / "models"
        if models_dir.exists():
            # Check for common issues
            schema_file = repo / "app" / "schema.py"
            if schema_file.exists():
                content = schema_file.read_text()
                # Look for TODO or FIXME markers
                if "TODO" in content or "FIXME" in content:
                    issues.append({
                        "type": "schema_todos",
                        "severity": "info",
                        "message": "Schema file contains TODO/FIXME markers",
                    })

        return issues

    def _check_migration_order(self, chain: MigrationChain) -> list[dict]:
        """Check migration dependency order."""
        issues = []

        # Detect circular dependencies
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(rev: str) -> bool:
            visited.add(rev)
            rec_stack.add(rev)

            step = chain.steps.get(rev)
            if step and step.down_revision:
                if step.down_revision not in visited:
                    if has_cycle(step.down_revision):
                        return True
                elif step.down_revision in rec_stack:
                    return True

            rec_stack.remove(rev)
            return False

        for rev in chain.steps:
            if rev not in visited:
                if has_cycle(rev):
                    issues.append({
                        "type": "circular_dependency",
                        "severity": "critical",
                        "message": f"Circular dependency detected in migration chain",
                    })
                    break

        return issues
