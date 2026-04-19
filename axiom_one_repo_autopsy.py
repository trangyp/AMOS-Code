"""Axiom One - Repo Autopsy Engine
Deep repository analysis and repair system."""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from axiom_one_graph import (
    AxiomEdge,
    AxiomGraph,
    AxiomNode,
    DomainType,
    EdgeType,
    NodeType,
    create_repo_node,
    generate_repo_file_node_id,
)


class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(Enum):
    PACKAGING = "packaging"
    IMPORTS = "imports"
    PATHS = "paths"
    TESTS = "tests"
    CI = "ci"
    RUNTIME = "runtime"
    DOCS = "docs"
    DESIGN = "design"


@dataclass
class RepoIssue:
    id: str
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    affected_files: List[str]
    root_cause: str
    suggested_fix: str
    auto_fixable: bool
    evidence: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ValidationResult:
    step: str
    success: bool
    duration_ms: float
    stdout: str
    stderr: str
    exit_code: int
    issues_found: List[RepoIssue] = field(default_factory=list)


@dataclass
class AutopsyReport:
    repo_path: str
    repo_name: str
    started_at: str
    completed_at: str = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    issues: List[RepoIssue] = field(default_factory=list)
    graph_stats: Dict[str, Any] = field(default_factory=dict)
    fix_branch: str = None
    fix_pr_url: str = None

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)

    @property
    def auto_fixable_count(self) -> int:
        return sum(1 for i in self.issues if i.auto_fixable)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_path": self.repo_path,
            "repo_name": self.repo_name,
            "summary": {
                "critical": self.critical_count,
                "high": len([i for i in self.issues if i.severity == IssueSeverity.HIGH]),
                "auto_fixable": self.auto_fixable_count,
            },
            "issues": [
                {"id": i.id, "severity": i.severity.value, "title": i.title} for i in self.issues
            ],
        }


class StaticGraphBuilder:
    """Build unified graph from static repo analysis."""

    def __init__(self, graph: AxiomGraph):
        self.graph = graph
        self.repo_path: Optional[Path] = None

    async def build(self, repo_path: str, repo_name: str, owner_id: str) -> Dict[str, Any]:
        self.repo_path = Path(repo_path)
        repo_node = create_repo_node(repo_path, repo_name, owner_id)
        await self.graph.add_node(repo_node)

        file_nodes = []
        for py_file in self.repo_path.rglob("*.py"):
            rel_path = py_file.relative_to(self.repo_path)
            node = AxiomNode(
                id=generate_repo_file_node_id(str(self.repo_path), str(rel_path)),
                domain=DomainType.CODE,
                node_type=NodeType.FILE,
                name=str(rel_path),
                properties={"absolute_path": str(py_file), "relative_path": str(rel_path)},
            )
            await self.graph.add_node(node)
            file_nodes.append(node)
            await self.graph.add_edge(
                AxiomEdge(source=repo_node.id, target=node.id, edge_type=EdgeType.CONTAINS)
            )

        return {"files": len(file_nodes), "repo_node_id": repo_node.id}


class DynamicValidator:
    """Run dynamic validation steps."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    async def run_full_validation(self) -> List[ValidationResult]:
        results = []
        results.append(await self._validate_install())
        if results[-1].success:
            results.append(await self._validate_lint())
        return results

    async def _validate_install(self) -> ValidationResult:
        start = datetime.now(timezone.utc)
        try:
            if (self.repo_path / "pyproject.toml").exists():
                cmd = ["pip", "install", "-e", "."]
            elif (self.repo_path / "requirements.txt").exists():
                cmd = ["pip", "install", "-r", "requirements.txt"]
            else:
                return ValidationResult(
                    step="install",
                    success=False,
                    duration_ms=0,
                    stdout="",
                    stderr="No packaging config found",
                    exit_code=1,
                    issues_found=[
                        RepoIssue(
                            id="install-001",
                            category=IssueCategory.PACKAGING,
                            severity=IssueSeverity.CRITICAL,
                            title="No packaging config",
                            description="Missing pyproject.toml or requirements.txt",
                            affected_files=[str(self.repo_path)],
                            root_cause="Missing config",
                            suggested_fix="Create pyproject.toml",
                            auto_fixable=True,
                        )
                    ],
                )

            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, timeout=300
            )
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return ValidationResult(
                step="install",
                success=result.returncode == 0,
                duration_ms=duration,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
            )
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return ValidationResult(
                step="install",
                success=False,
                duration_ms=duration,
                stdout="",
                stderr=str(e),
                exit_code=1,
            )

    async def _validate_lint(self) -> ValidationResult:
        start = datetime.now(timezone.utc)
        try:
            result = subprocess.run(
                ["ruff", "check", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return ValidationResult(
                step="lint",
                success=result.returncode == 0,
                duration_ms=duration,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
            )
        except Exception as e:
            return ValidationResult(
                step="lint", success=False, duration_ms=0, stdout="", stderr=str(e), exit_code=1
            )


class RepoAutopsyEngine:
    """Complete repo autopsy pipeline."""

    def __init__(self, graph: AxiomGraph):
        self.graph = graph
        self.static_builder = StaticGraphBuilder(graph)
        self.validator: Optional[DynamicValidator] = None

    async def autopsy(self, repo_path: str, repo_name: str, owner_id: str) -> AutopsyReport:
        started_at = datetime.now(timezone.utc).isoformat()
        graph_stats = await self.static_builder.build(repo_path, repo_name, owner_id)
        self.validator = DynamicValidator(repo_path)
        validation_results = await self.validator.run_full_validation()

        all_issues: List[RepoIssue] = []
        for result in validation_results:
            all_issues.extend(result.issues_found)

        return AutopsyReport(
            repo_path=repo_path,
            repo_name=repo_name,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            validation_results=validation_results,
            issues=all_issues,
            graph_stats=graph_stats,
        )
