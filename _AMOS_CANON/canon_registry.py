#!/usr/bin/env python3
"""Canon Registry - Manages canonical registries."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .canon_core import CanonCore, CanonGlossaryEntry, CanonAgent, CanonKernel


@dataclass
class RegistryStats:
    total_entries: int = 0
    active_entries: int = 0
    deprecated_entries: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CanonRegistry:
    def __init__(self, core: CanonCore | None = None):
        self._core = core or CanonCore()

    def register_glossary_entry(self, entry: CanonGlossaryEntry) -> bool:
        try:
            self._core.add_glossary_entry(entry)
            return True
        except Exception:
            return False

    def get_glossary_entry(self, term: str) -> CanonGlossaryEntry | None:
        return self._core.get_glossary_entry(term)

    def search_glossary(self, query: str, search_synonyms: bool = True) -> list[CanonGlossaryEntry]:
        results = []
        query_lower = query.lower()
        for entry in self._core._glossary.values():
            if query_lower in entry.term.lower():
                results.append(entry)
                continue
            if query_lower in entry.definition.lower():
                results.append(entry)
                continue
            if search_synonyms:
                for synonym in entry.synonyms:
                    if query_lower in synonym.lower():
                        results.append(entry)
                        break
        return results

    def get_glossary_stats(self) -> RegistryStats:
        entries = self._core._glossary.values()
        return RegistryStats(
            total_entries=len(entries),
            active_entries=sum(1 for e in entries if e.enabled),
        )

    def register_agent(self, agent: CanonAgent) -> bool:
        try:
            self._core.add_agent(agent)
            return True
        except Exception:
            return False

    def get_agent(self, agent_id: str) -> CanonAgent | None:
        return self._core.get_agent(agent_id)

    def list_agents_by_type(self, agent_type: str) -> list[CanonAgent]:
        return [agent for agent in self._core._agents.values() if agent.agent_type == agent_type]

    def list_agents_by_capability(self, capability: str) -> list[CanonAgent]:
        return [agent for agent in self._core._agents.values() if capability in agent.capabilities]

    def get_agent_stats(self) -> RegistryStats:
        agents = self._core._agents.values()
        return RegistryStats(
            total_entries=len(agents),
            active_entries=sum(1 for a in agents if a.enabled),
        )

    def register_kernel(self, kernel: CanonKernel) -> bool:
        try:
            self._core.add_kernel(kernel)
            return True
        except Exception:
            return False

    def get_kernel(self, kernel_id: str) -> CanonKernel | None:
        return self._core.get_kernel(kernel_id)

    def list_kernels_by_domain(self, domain: str) -> list[CanonKernel]:
        return [kernel for kernel in self._core._kernels.values() if kernel.domain == domain]

    def list_kernels_by_equation(self, equation: str) -> list[CanonKernel]:
        return [kernel for kernel in self._core._kernels.values() if equation in kernel.equations]

    def get_kernel_stats(self) -> RegistryStats:
        kernels = self._core._kernels.values()
        return RegistryStats(
            total_entries=len(kernels),
            active_entries=sum(1 for k in kernels if k.enabled),
        )

    def export_registry(self, registry_type: str) -> dict[str, Any]:
        if registry_type == "glossary":
            return {term: entry.to_dict() for term, entry in self._core._glossary.items()}
        elif registry_type == "agents":
            return {agent_id: agent.to_dict() for agent_id, agent in self._core._agents.items()}
        elif registry_type == "kernels":
            return {kernel_id: kernel.to_dict() for kernel_id, kernel in self._core._kernels.items()}
        return {}

    def get_all_stats(self) -> dict[str, Any]:
        return {
            "glossary": self.get_glossary_stats().__dict__,
            "agents": self.get_agent_stats().__dict__,
            "kernels": self.get_kernel_stats().__dict__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
