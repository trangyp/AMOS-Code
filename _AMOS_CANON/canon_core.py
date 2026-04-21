#!/usr/bin/env python3
"""Canon Core - Core canonical definitions and types.

Defines the fundamental types and structures for the AMOS canonical system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CanonPriority(Enum):
    """Priority levels for canonical rules."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CanonCategory(Enum):
    """Categories of canonical definitions."""

    SYNTAX = "syntax"
    SEMANTICS = "semantics"
    INTEGRITY = "integrity"
    SECURITY = "security"
    PERFORMANCE = "performance"
    GOVERNANCE = "governance"
    COGNITIVE = "cognitive"
    OPERATIONAL = "operational"


class CanonStatus(Enum):
    """Status of canonical operations."""

    PENDING = "pending"
    ACTIVE = "active"
    ENFORCING = "enforcing"
    VIOLATED = "violated"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"


@dataclass
class CanonDefinition:
    """Base class for all canonical definitions."""

    id: str
    name: str
    description: str
    category: CanonCategory
    priority: CanonPriority
    version: str = "1.0.0"
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "version": self.version,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class CanonRule(CanonDefinition):
    """A canonical rule with enforcement logic."""

    condition: str = ""
    action: str = ""
    auto_remediate: bool = False


@dataclass
class CanonStandard(CanonDefinition):
    """A canonical standard specification."""

    specification: str = ""
    compliance_check: str = ""
    applicable_domains: list[str] = field(default_factory=list)


@dataclass
class CanonGlossaryEntry(CanonDefinition):
    """A glossary entry for canonical terminology."""

    term: str = ""
    definition: str = ""
    synonyms: list[str] = field(default_factory=list)
    related_terms: list[str] = field(default_factory=list)


@dataclass
class CanonAgent(CanonDefinition):
    """A canonical agent definition."""

    agent_type: str = ""
    capabilities: list[str] = field(default_factory=list)
    module_path: str = ""
    config_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonKernel(CanonDefinition):
    """A canonical kernel specification."""

    kernel_type: str = ""
    domain: str = ""
    equations: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)


class CanonCore:
    """Central management for canonical operations."""

    _instance: CanonCore | None = None

    def __new__(cls) -> CanonCore:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._rules: dict[str, CanonRule] = {}
        self._standards: dict[str, CanonStandard] = {}
        self._glossary: dict[str, CanonGlossaryEntry] = {}
        self._agents: dict[str, CanonAgent] = {}
        self._kernels: dict[str, CanonKernel] = {}
        self._status = CanonStatus.PENDING

    @property
    def status(self) -> CanonStatus:
        return self._status

    def add_rule(self, rule: CanonRule) -> None:
        self._rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> CanonRule | None:
        return self._rules.get(rule_id)

    def list_rules(
        self,
        category: CanonCategory | None = None,
        priority: CanonPriority | None = None,
    ) -> list[CanonRule]:
        rules = list(self._rules.values())
        if category:
            rules = [r for r in rules if r.category == category]
        if priority:
            rules = [r for r in rules if r.priority == priority]
        return rules

    def add_standard(self, standard: CanonStandard) -> None:
        self._standards[standard.id] = standard

    def get_standard(self, standard_id: str) -> CanonStandard | None:
        return self._standards.get(standard_id)

    def add_glossary_entry(self, entry: CanonGlossaryEntry) -> None:
        self._glossary[entry.id] = entry

    def get_glossary_entry(self, term: str) -> CanonGlossaryEntry | None:
        return self._glossary.get(term)

    def add_agent(self, agent: CanonAgent) -> None:
        self._agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> CanonAgent | None:
        return self._agents.get(agent_id)

    def add_kernel(self, kernel: CanonKernel) -> None:
        self._kernels[kernel.id] = kernel

    def get_kernel(self, kernel_id: str) -> CanonKernel | None:
        return self._kernels.get(kernel_id)

    def get_stats(self) -> dict[str, Any]:
        return {
            "status": self._status.value,
            "total_rules": len(self._rules),
            "total_standards": len(self._standards),
            "total_glossary_entries": len(self._glossary),
            "total_agents": len(self._agents),
            "total_kernels": len(self._kernels),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def set_status(self, status: CanonStatus) -> None:
        self._status = status
