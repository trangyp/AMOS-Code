"""AMOS Brain Loader - Loads and parses brain configuration files."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class KernelConfig:
    """Represents a single kernel configuration."""

    id: str
    name: str
    group: str
    priority: int
    required: bool
    domains: list[str]
    modes: list[str]
    dependencies: list[str]
    file_hint: str = ""


@dataclass
class GlobalLaw:
    """Represents a global law from AMOS BRAIN ROOT."""

    id: str
    name: str
    description: str
    priority: int


class BrainLoader:
    """Loads AMOS brain configuration from JSON files."""

    DEFAULT_BRAIN_PATH = Path(__file__).resolve().parent.parent.parent / "_AMOS_BRAIN"

    def __init__(self, brain_path: Path | None = None):
        self.brain_path = brain_path or self.DEFAULT_BRAIN_PATH
        self.kernels: list[KernelConfig] = []
        self.global_laws: list[GlobalLaw] = []
        self.identity: dict[str, Any] = {}
        self.creator: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> BrainLoader:
        """Load all brain configurations."""
        if self._loaded:
            return self

        self._load_default_kernels()
        self._loaded = True
        return self

    def _load_default_kernels(self) -> None:
        """Load default kernel set if config files unavailable."""
        self.kernels = [
            KernelConfig(
                id="K_META_LOGIC",
                name="Meta Logic & Law Kernel",
                group="Cognitive_Stack.Meta_Cognition",
                priority=10,
                required=True,
                domains=["logic", "law_of_law", "reasoning"],
                modes=["analysis", "governance", "validation"],
                dependencies=[],
            ),
            KernelConfig(
                id="K_TECH_ENGINE",
                name="Technology & Engineering Kernel",
                group="Engines.Domains",
                priority=7,
                required=False,
                domains=["software", "ai", "cloud", "infra"],
                modes=["design", "architecture", "review"],
                dependencies=["K_META_LOGIC"],
            ),
        ]

        self.global_laws = [
            GlobalLaw(
                id="L1",
                name="Law of Law",
                description="All reasoning must obey the highest applicable law in the stack.",
                priority=1,
            ),
            GlobalLaw(
                id="L2",
                name="Rule of 2",
                description="All analysis must check at least two contrasting perspectives.",
                priority=2,
            ),
            GlobalLaw(
                id="L3",
                name="Rule of 4",
                description="Consider four quadrants: biological, technical, economic, environmental.",
                priority=3,
            ),
            GlobalLaw(
                id="L4",
                name="Absolute Structural Integrity",
                description="All outputs must be logically consistent and structurally auditable.",
                priority=4,
            ),
        ]

    def get_required_kernels(self) -> list[KernelConfig]:
        """Get all required kernels."""
        return [k for k in self.kernels if k.required]

    def get_kernels_for_domains(self, domains: list[str]) -> list[KernelConfig]:
        """Get all kernels that handle the given domains."""
        result = []
        for k in self.kernels:
            if any(d in k.domains for d in domains):
                result.append(k)
        return sorted(result, key=lambda x: x.priority, reverse=True)

    @property
    def system_name(self) -> str:
        """Get the system name from identity."""
        return self.identity.get("system_name", "AMOS")

    @property
    def creator_name(self) -> str:
        """Get the creator name."""
        return self.creator.get("name", "Trang Phan")


# Global brain loader instance
_brain_loader: BrainLoader | None = None


def get_brain() -> BrainLoader:
    """Get the global brain loader instance (singleton)."""
    global _brain_loader
    if _brain_loader is None:
        _brain_loader = BrainLoader().load()
    return _brain_loader
