#!/usr/bin/env python3
"""
AMOS Unified Equation Registry Connector.

Integrates:
- Legacy SuperBrain Equation Bridge (Phases 1-14)
- New Phase 15-20 Equation Bridge Completion
- External equation sources (Wolfram, sympy, numpy)

Provides single API for all 180+ equations across 20 phases.
"""

import asyncio
import importlib.util
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

import numpy as np


class EquationProtocol(Protocol):
    """Protocol for equation functions."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class PhaseStatus(Enum):
    """Development phase status."""

    STABLE = auto()
    BETA = auto()
    EXPERIMENTAL = auto()
    DEPRECATED = auto()


@dataclass(frozen=True)
class EquationEntry:
    """Registry entry for an equation."""

    name: str
    phase: int
    domain: str
    formula: str
    function: Callable[..., Any]
    invariants: Tuple[str, ...]
    status: PhaseStatus
    added_date: str


class UnifiedEquationRegistry:
    """
    Unified registry for all AMOS equations.

    Combines:
    - Legacy bridge (amos_superbrain_equation_bridge.py)
    - Completion bridge (amos_equation_bridge_completion.py)
    - Runtime loaded equations
    """

    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._equations: Dict[str, EquationEntry] = {}
        self._phases: Dict[int, list[str]] = {i: [] for i in range(1, 21)}
        self._domains: Dict[str, list[str]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Async initialization of all equation sources."""
        if self._initialized:
            return

        await asyncio.gather(
            self._load_legacy_bridge(),
            self._load_completion_bridge(),
            self._load_builtin_equations(),
        )

        self._initialized = True

    async def _load_legacy_bridge(self) -> None:
        """Load equations from amos_superbrain_equation_bridge.py."""
        legacy_path = self.repo_path / "amos_superbrain_equation_bridge.py"
        if not legacy_path.exists():
            return

        spec = importlib.util.spec_from_file_location("legacy_bridge", legacy_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["legacy_bridge"] = module
            spec.loader.exec_module(module)

            # Extract equation bridge
            if hasattr(module, "EquationBridge"):
                bridge = module.EquationBridge()
                if hasattr(bridge, "equations"):
                    for name, func in bridge.equations.items():
                        meta = getattr(bridge, "metadata", {}).get(name, {})
                        entry = EquationEntry(
                            name=name,
                            phase=meta.get("phase", 1),
                            domain=meta.get("domain", "unknown"),
                            formula=meta.get("formula", "N/A"),
                            function=func,
                            invariants=tuple(meta.get("invariants", [])),
                            status=PhaseStatus.STABLE,
                            added_date=datetime.now(UTC).isoformat(),
                        )
                        self._register(entry)

    async def _load_completion_bridge(self) -> None:
        """Load equations from amos_equation_bridge_completion.py."""
        completion_path = self.repo_path / "amos_equation_bridge_completion.py"
        if not completion_path.exists():
            return

        spec = importlib.util.spec_from_file_location("completion_bridge", completion_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["completion_bridge"] = module
            spec.loader.exec_module(module)

            if hasattr(module, "get_equation_bridge_completion"):
                bridge = module.get_equation_bridge_completion()
                if hasattr(bridge, "equations"):
                    for name, func in bridge.equations.items():
                        meta = bridge.metadata.get(name)
                        if meta:
                            entry = EquationEntry(
                                name=name,
                                phase=meta.phase,
                                domain=meta.domain.name.lower(),
                                formula=meta.formula,
                                function=func,
                                invariants=tuple(meta.invariants),
                                status=PhaseStatus.BETA if meta.phase >= 15 else PhaseStatus.STABLE,
                                added_date=datetime.now(UTC).isoformat(),
                            )
                            self._register(entry)

    async def _load_builtin_equations(self) -> None:
        """Load built-in mathematical equations."""
        builtins = [
            ("gaussian", self._gaussian, "N/A", 1, ["math"]),
            ("softmax", self._softmax, "exp(x_i) / sum(exp(x_j))", 1, ["math", "ml"]),
            ("relu", self._relu, "max(0, x)", 1, ["math", "ml"]),
            ("sigmoid", self._sigmoid, "1 / (1 + exp(-x))", 1, ["math", "ml"]),
        ]

        for name, func, formula, phase, domains in builtins:
            entry = EquationEntry(
                name=name,
                phase=phase,
                domain=domains[0],
                formula=formula,
                function=func,
                invariants=tuple(),
                status=PhaseStatus.STABLE,
                added_date=datetime.now(UTC).isoformat(),
            )
            self._register(entry)

    def _register(self, entry: EquationEntry) -> None:
        """Register an equation entry."""
        self._equations[entry.name] = entry
        self._phases[entry.phase].append(entry.name)

        if entry.domain not in self._domains:
            self._domains[entry.domain] = []
        self._domains[entry.domain].append(entry.name)

    def _gaussian(self, x: np.ndarray, mu: float = 0, sigma: float = 1) -> np.ndarray:
        """Gaussian function."""
        return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax activation."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation."""
        return np.maximum(0, x)

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid activation."""
        return 1 / (1 + np.exp(-x))

    def get(self, name: str) -> Optional[EquationEntry]:
        """Get equation by name."""
        return self._equations.get(name)

    def execute(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute an equation."""
        entry = self.get(name)
        if not entry:
            raise ValueError(f"Equation '{name}' not found")
        return entry.function(*args, **kwargs)

    def list_all(self) -> List[str]:
        """List all registered equation names."""
        return list(self._equations.keys())

    def list_by_phase(self, phase: int) -> List[str]:
        """List equations in a phase."""
        return self._phases.get(phase, [])

    def list_by_domain(self, domain: str) -> List[str]:
        """List equations in a domain."""
        return self._domains.get(domain, [])

    def search(self, query: str) -> List[str]:
        """Search equations by name or formula."""
        results = []
        query_lower = query.lower()
        for name, entry in self._equations.items():
            if query_lower in name.lower() or query_lower in entry.formula.lower():
                results.append(name)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_equations": len(self._equations),
            "by_phase": {phase: len(names) for phase, names in self._phases.items() if names},
            "by_domain": {domain: len(names) for domain, names in self._domains.items()},
            "phases_loaded": len([p for p in self._phases.values() if p]),
        }


# Singleton instance
_registry: Optional[UnifiedEquationRegistry] = None


async def get_unified_registry(repo_path: str = None) -> UnifiedEquationRegistry:
    """Get or create unified registry singleton."""
    global _registry
    if _registry is None:
        _registry = UnifiedEquationRegistry(repo_path)
        await _registry.initialize()
    return _registry


def get_registry_sync(repo_path: str = None) -> UnifiedEquationRegistry:
    """Synchronous access to registry."""
    global _registry
    if _registry is None:
        _registry = UnifiedEquationRegistry(repo_path)
        # Initialize synchronously
        asyncio.run(_registry.initialize())
    return _registry


async def demo() -> None:
    """Demo the unified registry."""
    registry = await get_unified_registry()

    print("AMOS Unified Equation Registry")
    print("=" * 50)

    stats = registry.get_stats()
    print(f"\nTotal Equations: {stats['total_equations']}")
    print(f"Phases Loaded: {stats['phases_loaded']}/20")

    print("\nBy Phase:")
    for phase, count in sorted(stats["by_phase"].items()):
        if count > 0:
            print(f"  Phase {phase}: {count} equations")

    print("\nBy Domain:")
    for domain, count in sorted(stats["by_domain"].items(), key=lambda x: -x[1]):
        print(f"  {domain}: {count} equations")

    # Demo execution
    print("\n" + "=" * 50)
    print("Demo Executions:")

    # Test softmax
    x = np.array([1.0, 2.0, 3.0])
    result = registry.execute("softmax", x)
    print(f"softmax([1,2,3]) = {result}")

    # Test ReLU
    x = np.array([-1.0, 0.0, 1.0])
    result = registry.execute("relu", x)
    print(f"relu([-1,0,1]) = {result}")

    # Search test
    print("\nSearch 'consensus':")
    results = registry.search("consensus")
    for r in results[:3]:
        entry = registry.get(r)
        if entry:
            print(f"  - {r}: {entry.formula}")


if __name__ == "__main__":
    asyncio.run(demo())
