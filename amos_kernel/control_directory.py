"""
AMOS Control Directory System - `.amos/` configuration management

Implements Section 105 from Axiom specification:
- repo.yaml: Repository metadata and scope
- glossary.yaml: Human terms to code mapping
- policies.yaml: Safety constraints and rules
- architecture.yaml: Component structure
- verify.yaml: Verification contract
- ssot.yaml: Single source of truth tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# ============================================================================
# Types and Contracts
# ============================================================================


@dataclass(frozen=True)
class ControlFilePath:
    """Standard control file paths."""

    REPO = "repo.yaml"
    GLOSSARY = "glossary.yaml"
    POLICIES = "policies.yaml"
    ARCHITECTURE = "architecture.yaml"
    VERIFY = "verify.yaml"
    SSOT = "ssot.yaml"


@dataclass
class RepoConfig:
    """repo.yaml: Repository metadata and scope."""

    name: str = ""
    version: str = "0.1.0"
    language: str = "python"
    description: str = ""
    scope: dict[str, Any] = field(default_factory=dict)
    entrypoints: list[str] = field(default_factory=list)
    protected_paths: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RepoConfig:
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "0.1.0"),
            language=data.get("language", "python"),
            description=data.get("description", ""),
            scope=data.get("scope", {}),
            entrypoints=data.get("entrypoints", []),
            protected_paths=data.get("protected_paths", []),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "language": self.language,
            "description": self.description,
            "scope": self.scope,
            "entrypoints": self.entrypoints,
            "protected_paths": self.protected_paths,
        }


@dataclass
class TermMapping:
    """Single term mapping in glossary."""

    human_term: str
    code_scope: str
    file_patterns: list[str]
    examples: list[str]
    confidence: float = 0.9


@dataclass
class GlossaryConfig:
    """glossary.yaml: Human terms to code mapping."""

    terms: list[TermMapping] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GlossaryConfig:
        terms = [
            TermMapping(
                human_term=t.get("term", ""),
                code_scope=t.get("code_scope", ""),
                file_patterns=t.get("file_patterns", []),
                examples=t.get("examples", []),
                confidence=t.get("confidence", 0.9),
            )
            for t in data.get("terms", [])
        ]
        return cls(terms=terms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "terms": [
                {
                    "term": t.human_term,
                    "code_scope": t.code_scope,
                    "file_patterns": t.file_patterns,
                    "examples": t.examples,
                    "confidence": t.confidence,
                }
                for t in self.terms
            ]
        }

    def lookup_term(self, term: str) -> TermMapping | None:
        """Lookup human term in glossary."""
        for t in self.terms:
            if t.human_term.lower() == term.lower():
                return t
        return None


@dataclass
class PolicyRule:
    """Single policy rule."""

    name: str
    condition: str
    action: str
    severity: str = "warning"  # info, warning, error, fatal
    enabled: bool = True


@dataclass
class PoliciesConfig:
    """policies.yaml: Safety constraints and rules."""

    rules: list[PolicyRule] = field(default_factory=list)
    max_risk_score: float = 0.7
    auto_approve_low_risk: bool = True
    require_human_approval: bool = True

    DEFAULT_RULES: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "name": "no_deletion_without_backup",
                "condition": "action.type == 'delete' and not backup.exists",
                "action": "reject",
                "severity": "error",
            },
            {
                "name": "no_direct_production_changes",
                "condition": "target.environment == 'production' and not verified",
                "action": "require_approval",
                "severity": "warning",
            },
            {
                "name": "test_coverage_minimum",
                "condition": "coverage.percentage < 80",
                "action": "warn",
                "severity": "warning",
            },
        ]
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoliciesConfig:
        rules = [
            PolicyRule(
                name=r.get("name", ""),
                condition=r.get("condition", ""),
                action=r.get("action", ""),
                severity=r.get("severity", "warning"),
                enabled=r.get("enabled", True),
            )
            for r in data.get("rules", [])
        ]
        return cls(
            rules=rules,
            max_risk_score=data.get("max_risk_score", 0.7),
            auto_approve_low_risk=data.get("auto_approve_low_risk", True),
            require_human_approval=data.get("require_human_approval", True),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rules": [
                {
                    "name": r.name,
                    "condition": r.condition,
                    "action": r.action,
                    "severity": r.severity,
                    "enabled": r.enabled,
                }
                for r in self.rules
            ],
            "max_risk_score": self.max_risk_score,
            "auto_approve_low_risk": self.auto_approve_low_risk,
            "require_human_approval": self.require_human_approval,
        }


@dataclass
class ComponentDef:
    """Architecture component definition."""

    name: str
    type: str
    path: str
    dependencies: list[str]
    interface: dict[str, Any]


@dataclass
class ArchitectureConfig:
    """architecture.yaml: Component structure."""

    components: list[ComponentDef] = field(default_factory=list)
    layers: list[str] = field(default_factory=list)
    interfaces: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArchitectureConfig:
        components = [
            ComponentDef(
                name=c.get("name", ""),
                type=c.get("type", ""),
                path=c.get("path", ""),
                dependencies=c.get("dependencies", []),
                interface=c.get("interface", {}),
            )
            for c in data.get("components", [])
        ]
        return cls(
            components=components,
            layers=data.get("layers", []),
            interfaces=data.get("interfaces", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "components": [
                {
                    "name": c.name,
                    "type": c.type,
                    "path": c.path,
                    "dependencies": c.dependencies,
                    "interface": c.interface,
                }
                for c in self.components
            ],
            "layers": self.layers,
            "interfaces": self.interfaces,
        }

    def get_component(self, name: str) -> ComponentDef | None:
        """Get component by name."""
        for c in self.components:
            if c.name == name:
                return c
        return None


@dataclass
class VerificationCheck:
    """Single verification check."""

    name: str
    type: str  # syntax, imports, architecture, ssot, lint, typecheck, test, invariant
    command: str
    required: bool = True


@dataclass
class VerifyConfig:
    """verify.yaml: Verification contract."""

    checks: list[VerificationCheck] = field(default_factory=list)
    min_pass_rate: float = 1.0

    DEFAULT_CHECKS: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "name": "syntax",
                "type": "syntax",
                "command": "python -m py_compile",
                "required": True,
            },
            {
                "name": "imports",
                "type": "imports",
                "command": "python -c 'import {{module}}'",
                "required": True,
            },
            {
                "name": "architecture",
                "type": "architecture",
                "command": "amos verify --architecture",
                "required": True,
            },
            {"name": "ssot", "type": "ssot", "command": "amos verify --ssot", "required": True},
            {"name": "lint", "type": "lint", "command": "ruff check", "required": False},
            {"name": "typecheck", "type": "typecheck", "command": "mypy", "required": False},
            {"name": "test", "type": "test", "command": "pytest", "required": False},
            {
                "name": "invariant",
                "type": "invariant",
                "command": "amos verify --invariants",
                "required": True,
            },
        ]
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VerifyConfig:
        checks = [
            VerificationCheck(
                name=c.get("name", ""),
                type=c.get("type", ""),
                command=c.get("command", ""),
                required=c.get("required", True),
            )
            for c in data.get("checks", [])
        ]
        return cls(
            checks=checks,
            min_pass_rate=data.get("min_pass_rate", 1.0),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [
                {
                    "name": c.name,
                    "type": c.type,
                    "command": c.command,
                    "required": c.required,
                }
                for c in self.checks
            ],
            "min_pass_rate": self.min_pass_rate,
        }


@dataclass
class SsotEntry:
    """Single SSOT entry."""

    entity_type: str
    entity_id: str
    canonical_location: str
    mirrors: list[str]
    last_sync: datetime
    hash: str


@dataclass
class SsotConfig:
    """ssot.yaml: Single source of truth tracking."""

    entries: list[SsotEntry] = field(default_factory=list)
    sync_strategy: str = "push"  # push, pull, bidirectional

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SsotConfig:
        entries = [
            SsotEntry(
                entity_type=e.get("entity_type", ""),
                entity_id=e.get("entity_id", ""),
                canonical_location=e.get("canonical_location", ""),
                mirrors=e.get("mirrors", []),
                last_sync=datetime.fromisoformat(e.get("last_sync", "")),
                hash=e.get("hash", ""),
            )
            for e in data.get("entries", [])
        ]
        return cls(
            entries=entries,
            sync_strategy=data.get("sync_strategy", "push"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [
                {
                    "entity_type": e.entity_type,
                    "entity_id": e.entity_id,
                    "canonical_location": e.canonical_location,
                    "mirrors": e.mirrors,
                    "last_sync": e.last_sync.isoformat(),
                    "hash": e.hash,
                }
                for e in self.entries
            ],
            "sync_strategy": self.sync_strategy,
        }

    def get_canonical(self, entity_id: str) -> SsotEntry | None:
        """Get canonical location for entity."""
        for e in self.entries:
            if e.entity_id == entity_id:
                return e
        return None


# ============================================================================
# Control Directory Manager
# ============================================================================


class ControlDirectoryManager:
    """Manages `.amos/` control directory lifecycle."""

    CONTROL_DIR = ".amos"

    def __init__(self, repo_root: Path | str) -> None:
        self.repo_root = Path(repo_root)
        self.control_path = self.repo_root / self.CONTROL_DIR

        # Cached configs
        self._repo: RepoConfig | None = None
        self._glossary: GlossaryConfig | None = None
        self._policies: PoliciesConfig | None = None
        self._architecture: ArchitectureConfig | None = None
        self._verify: VerifyConfig | None = None
        self._ssot: SsotConfig | None = None

    def exists(self) -> bool:
        """Check if control directory exists."""
        return self.control_path.exists()

    def init(self, name: str, language: str = "python") -> None:
        """Initialize new control directory with defaults."""
        self.control_path.mkdir(parents=True, exist_ok=True)

        # repo.yaml
        repo = RepoConfig(
            name=name,
            language=language,
            scope={"include": ["src/", "lib/"], "exclude": ["tests/", "docs/"]},
            entrypoints=["main.py", "__init__.py"],
            protected_paths=[".amos/", ".git/", "secrets/"],
        )
        self._write_yaml(ControlFilePath.REPO, repo.to_dict())

        # glossary.yaml
        glossary = GlossaryConfig(
            terms=[
                TermMapping(
                    human_term="main entry point",
                    code_scope="main.py::main()",
                    file_patterns=["main.py"],
                    examples=["entry point", "starting point", "main function"],
                ),
            ]
        )
        self._write_yaml(ControlFilePath.GLOSSARY, glossary.to_dict())

        # policies.yaml
        policies = PoliciesConfig(rules=[PolicyRule(**r) for r in PoliciesConfig.DEFAULT_RULES])
        self._write_yaml(ControlFilePath.POLICIES, policies.to_dict())

        # architecture.yaml
        architecture = ArchitectureConfig(
            components=[
                ComponentDef(
                    name="core",
                    type="module",
                    path="src/core/",
                    dependencies=[],
                    interface={"exports": ["main"]},
                ),
            ],
            layers=["api", "business", "data"],
        )
        self._write_yaml(ControlFilePath.ARCHITECTURE, architecture.to_dict())

        # verify.yaml
        verify = VerifyConfig(checks=[VerificationCheck(**c) for c in VerifyConfig.DEFAULT_CHECKS])
        self._write_yaml(ControlFilePath.VERIFY, verify.to_dict())

        # ssot.yaml
        ssot = SsotConfig(sync_strategy="push")
        self._write_yaml(ControlFilePath.SSOT, ssot.to_dict())

    def _read_yaml(self, filename: str) -> dict[str, Any]:
        """Read YAML file from control directory."""
        path = self.control_path / filename
        if not path.exists():
            return {}
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _write_yaml(self, filename: str, data: dict[str, Any]) -> None:
        """Write YAML file to control directory."""
        path = self.control_path / filename
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def get_repo(self) -> RepoConfig:
        """Get repo config."""
        if self._repo is None:
            self._repo = RepoConfig.from_dict(self._read_yaml(ControlFilePath.REPO))
        return self._repo

    def get_glossary(self) -> GlossaryConfig:
        """Get glossary config."""
        if self._glossary is None:
            self._glossary = GlossaryConfig.from_dict(self._read_yaml(ControlFilePath.GLOSSARY))
        return self._glossary

    def get_policies(self) -> PoliciesConfig:
        """Get policies config."""
        if self._policies is None:
            self._policies = PoliciesConfig.from_dict(self._read_yaml(ControlFilePath.POLICIES))
        return self._policies

    def get_architecture(self) -> ArchitectureConfig:
        """Get architecture config."""
        if self._architecture is None:
            self._architecture = ArchitectureConfig.from_dict(
                self._read_yaml(ControlFilePath.ARCHITECTURE)
            )
        return self._architecture

    def get_verify(self) -> VerifyConfig:
        """Get verify config."""
        if self._verify is None:
            self._verify = VerifyConfig.from_dict(self._read_yaml(ControlFilePath.VERIFY))
        return self._verify

    def get_ssot(self) -> SsotConfig:
        """Get SSOT config."""
        if self._ssot is None:
            self._ssot = SsotConfig.from_dict(self._read_yaml(ControlFilePath.SSOT))
        return self._ssot

    def save_repo(self, config: RepoConfig) -> None:
        """Save repo config."""
        self._repo = config
        self._write_yaml(ControlFilePath.REPO, config.to_dict())

    def save_glossary(self, config: GlossaryConfig) -> None:
        """Save glossary config."""
        self._glossary = config
        self._write_yaml(ControlFilePath.GLOSSARY, config.to_dict())

    def save_policies(self, config: PoliciesConfig) -> None:
        """Save policies config."""
        self._policies = config
        self._write_yaml(ControlFilePath.POLICIES, config.to_dict())

    def save_architecture(self, config: ArchitectureConfig) -> None:
        """Save architecture config."""
        self._architecture = config
        self._write_yaml(ControlFilePath.ARCHITECTURE, config.to_dict())

    def save_verify(self, config: VerifyConfig) -> None:
        """Save verify config."""
        self._verify = config
        self._write_yaml(ControlFilePath.VERIFY, config.to_dict())

    def save_ssot(self, config: SsotConfig) -> None:
        """Save SSOT config."""
        self._ssot = config
        self._write_yaml(ControlFilePath.SSOT, config.to_dict())

    def ground_term(self, human_term: str) -> TermMapping | None:
        """Ground human term to code scope via glossary."""
        glossary = self.get_glossary()
        return glossary.lookup_term(human_term)

    def check_policy(self, action: dict[str, Any], context: dict[str, Any]) -> list[PolicyRule]:
        """Check action against policies."""
        policies = self.get_policies()
        triggered: list[PolicyRule] = []

        for rule in policies.rules:
            if not rule.enabled:
                continue
            # Simple condition evaluation (placeholder for real eval)
            if self._evaluate_condition(rule.condition, action, context):
                triggered.append(rule)

        return triggered

    def _evaluate_condition(
        self, condition: str, action: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        """Evaluate policy condition against action and context."""
        # Simplified evaluation - in production, use proper expression evaluator
        condition_lower = condition.lower()

        if "delete" in condition_lower and action.get("type") == "delete":
            if "backup" in condition_lower:
                return not context.get("backup", {}).get("exists", False)

        if "production" in condition_lower:
            if context.get("target", {}).get("environment") == "production":
                return not context.get("verified", False)

        if "coverage" in condition_lower:
            coverage = context.get("coverage", {}).get("percentage", 100)
            return coverage < 80

        return False

    def compute_risk_score(self, action: dict[str, Any]) -> float:
        """Compute risk score for action based on policies."""
        context = {
            "target": action.get("target", {}),
            "verified": False,
            "backup": {"exists": False},
        }

        triggered = self.check_policy(action, context)

        if not triggered:
            return 0.0

        severity_scores = {
            "info": 0.1,
            "warning": 0.3,
            "error": 0.6,
            "fatal": 1.0,
        }

        max_score = max(severity_scores.get(r.severity, 0.5) for r in triggered)
        return min(max_score, 1.0)


def get_control_manager(repo_root: Path | str | None = None) -> ControlDirectoryManager:
    """Get control directory manager for repo."""
    if repo_root is None:
        repo_root = Path.cwd()
    return ControlDirectoryManager(repo_root)
