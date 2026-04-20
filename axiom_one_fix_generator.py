"""Axiom One - Fix Generator

Generates patches and fixes for repository issues found during autopsy.
Integrates with repo_doctor invariants and repair planning.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path
from typing import Any, Optional

from axiom_one_repo_autopsy import IssueCategory, RepoIssue


@dataclass
class GeneratedFix:
    """A generated fix for a repository issue."""

    issue_id: str
    fix_type: str
    description: str
    files_to_modify: list[str]
    patches: list[dict[str, Any]]
    blast_radius: str
    estimated_success_rate: float
    requires_approval: bool
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class FixApplication:
    """Result of applying a fix."""

    fix_id: str
    success: bool
    files_modified: list[str]
    backup_paths: list[str]
    error_message: str = None
    applied_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class FixGenerator:
    """Generates fixes for repository issues."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.backup_dir = self.repo_path / ".axiom_fixes"
        self.backup_dir.mkdir(exist_ok=True)

    def generate_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate a fix for a specific issue."""
        generators = {
            IssueCategory.PACKAGING: self._generate_packaging_fix,
            IssueCategory.IMPORTS: self._generate_import_fix,
            IssueCategory.PATHS: self._generate_path_fix,
            IssueCategory.TESTS: self._generate_test_fix,
            IssueCategory.RUNTIME: self._generate_runtime_fix,
            IssueCategory.CI: self._generate_ci_fix,
        }

        generator = generators.get(issue.category)
        if generator:
            return generator(issue)
        return None

    def _generate_packaging_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate fix for packaging issues."""
        if "No packaging configuration found" in issue.title:
            # Create minimal pyproject.toml
            patches = [
                {
                    "file": "pyproject.toml",
                    "action": "create",
                    "content": """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-project"
version = "0.1.0"
description = "Auto-generated project configuration"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Developer", email = "dev@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.ruff]
line-length = 100
target-version = "py310"
""",
                }
            ]
            return GeneratedFix(
                issue_id=issue.id,
                fix_type="create_pyproject",
                description="Create pyproject.toml with minimal configuration",
                files_to_modify=["pyproject.toml"],
                patches=patches,
                blast_radius="repo",
                estimated_success_rate=0.95,
                requires_approval=True,
            )

        if "Missing dependency" in issue.title:
            # Extract module name
            match = re.search(r"Missing dependency: (\w+)", issue.title)
            if match:
                module = match.group(1)
                patches = [
                    {
                        "file": "pyproject.toml",
                        "action": "edit",
                        "search": r"dependencies = \[",
                        "replace": f'dependencies = [\n    "{module}",',
                    }
                ]
                return GeneratedFix(
                    issue_id=issue.id,
                    fix_type="add_dependency",
                    description=f"Add {module} to dependencies",
                    files_to_modify=["pyproject.toml"],
                    patches=patches,
                    blast_radius="local",
                    estimated_success_rate=0.9,
                    requires_approval=False,
                )

        return None

    def _generate_import_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate fix for import issues."""
        if "circular import" in issue.description.lower():
            return GeneratedFix(
                issue_id=issue.id,
                fix_type="refactor_imports",
                description="Refactor to break circular import",
                files_to_modify=issue.affected_files,
                patches=[],
                blast_radius="module",
                estimated_success_rate=0.7,
                requires_approval=True,
            )
        return None

    def _generate_path_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate fix for path issues."""
        return GeneratedFix(
            issue_id=issue.id,
            fix_type="fix_paths",
            description="Update file paths to match project structure",
            files_to_modify=issue.affected_files,
            patches=[],
            blast_radius="local",
            estimated_success_rate=0.85,
            requires_approval=True,
        )

    def _generate_test_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate fix for test issues."""
        return GeneratedFix(
            issue_id=issue.id,
            fix_type="update_tests",
            description="Update test configuration and imports",
            files_to_modify=issue.affected_files,
            patches=[],
            blast_radius="test",
            estimated_success_rate=0.8,
            requires_approval=True,
        )

    def _generate_runtime_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate fix for runtime issues."""
        return GeneratedFix(
            issue_id=issue.id,
            fix_type="fix_runtime",
            description="Fix runtime configuration",
            files_to_modify=issue.affected_files,
            patches=[],
            blast_radius="system",
            estimated_success_rate=0.75,
            requires_approval=True,
        )

    def _generate_ci_fix(self, issue: RepoIssue) -> Optional[GeneratedFix]:
        """Generate fix for CI issues."""
        return GeneratedFix(
            issue_id=issue.id,
            fix_type="fix_ci",
            description="Update CI workflow configuration",
            files_to_modify=issue.affected_files,
            patches=[],
            blast_radius="repo",
            estimated_success_rate=0.9,
            requires_approval=True,
        )

    def apply_fix(self, fix: GeneratedFix, dry_run: bool = True) -> FixApplication:
        """Apply a generated fix to the repository."""
        files_modified = []
        backup_paths = []

        for patch in fix.patches:
            file_path = self.repo_path / patch["file"]

            if dry_run:
                files_modified.append(str(file_path))
                continue

            # Create backup
            if file_path.exists():
                backup_path = (
                    self.backup_dir
                    / f"{file_path.name}.{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.bak"
                )
                backup_path.write_bytes(file_path.read_bytes())
                backup_paths.append(str(backup_path))

            try:
                if patch["action"] == "create":
                    file_path.write_text(patch["content"])
                    files_modified.append(str(file_path))

                elif patch["action"] == "edit":
                    content = file_path.read_text()
                    new_content = re.sub(
                        patch["search"], patch["replace"], content, flags=re.MULTILINE
                    )
                    file_path.write_text(new_content)
                    files_modified.append(str(file_path))

            except Exception as e:
                return FixApplication(
                    fix_id=f"{fix.issue_id}-fix",
                    success=False,
                    files_modified=files_modified,
                    backup_paths=backup_paths,
                    error_message=str(e),
                )

        return FixApplication(
            fix_id=f"{fix.issue_id}-fix",
            success=True,
            files_modified=files_modified,
            backup_paths=backup_paths,
        )

    def create_pr_branch(self, branch_name: str) -> bool:
        """Create a new git branch for fixes."""
        try:
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def commit_fixes(self, message: str) -> bool:
        """Commit applied fixes."""
        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                capture_output=True,
            )
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False


class CrossDomainImpactAnalyzer:
    """Analyzes impact of changes across all domains."""

    def __init__(self, graph: Any):
        self.graph = graph

    def analyze_impact(
        self,
        source_node_id: str,
        change_type: str,
        max_depth: int = 5,
    ) -> dict[str, Any]:
        """Analyze cross-domain impact of a change."""
        # Build impact tree
        impact = {
            "source": source_node_id,
            "change_type": change_type,
            "affected_domains": {},
            "blast_radius": "local",
            "risk_score": 0.0,
            "requires_approval": False,
        }

        # Simulate traversal
        # In real implementation, would use actual graph queries
        domains = ["HUMAN", "PLANNING", "CODE", "RUNTIME", "DATA", "AI", "BUSINESS", "GOVERNANCE"]

        for domain in domains:
            impact["affected_domains"][domain] = {
                "affected_nodes": [],
                "risk_level": "low",
            }

        # Calculate blast radius
        if change_type in ["delete", "refactor"]:
            impact["blast_radius"] = "repo"
            impact["requires_approval"] = True

        return impact

    def estimate_blast_radius(self, files_changed: list[str]) -> str:
        """Estimate blast radius from files changed."""
        if any("api" in f or "interface" in f for f in files_changed):
            return "system"
        if any("core" in f or "main" in f for f in files_changed):
            return "repo"
        return "local"
