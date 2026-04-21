"""AMOS Engine Loader - Discovers and loads legacy brain engine configs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EngineCapability:
    """Capability defined in an engine."""
    name: str
    description: str
    equations: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    domain: str = ""


@dataclass
class AMOSEngine:
    """Represents a loaded AMOS engine."""
    name: str
    version: str
    file_path: Path
    capabilities: list[EngineCapability] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)
    domain_tags: list[str] = field(default_factory=list)

    def get_equations(self) -> list[str]:
        """Extract all equations from engine."""
        equations = []
        for cap in self.capabilities:
            equations.extend(cap.equations)
        return equations

    def get_invariants(self) -> list[str]:
        """Extract all invariants from engine."""
        invariants = []
        for cap in self.capabilities:
            invariants.extend(cap.invariants)
        return invariants


class EngineRegistry:
    """Registry for all discovered AMOS engines."""

    def __init__(self) -> None:
        self._engines: dict[str, AMOSEngine] = {}
        self._search_paths: list[Path] = []

    def add_search_path(self, path: Path) -> None:
        """Add a path to search for engine files."""
        self._search_paths.append(path)

    def discover_engines(self) -> int:
        """Discover all engine files in search paths."""
        count = 0
        for search_path in self._search_paths:
            if not search_path.exists():
                continue
            for json_file in search_path.rglob("*.json"):
                if "Engine" in json_file.name or "Kernel" in json_file.name:
                    try:
                        engine = self._load_engine(json_file)
                        if engine:
                            self._engines[engine.name] = engine
                            count += 1
                    except Exception:
                        pass  # Skip invalid files
        return count

    def _load_engine(self, file_path: Path) -> AMOSEngine | None:
        """Load an engine from a JSON file."""
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        # Extract engine metadata
        name = data.get("name", file_path.stem)
        version = data.get("version", "v0")

        # Extract capabilities
        capabilities = []
        caps_data = data.get("capabilities", data.get("equations", {}))
        if isinstance(caps_data, dict):
            for cap_name, cap_info in caps_data.items():
                if isinstance(cap_info, dict):
                    cap = EngineCapability(
                        name=cap_name,
                        description=cap_info.get("description", ""),
                        equations=cap_info.get("equations", []),
                        invariants=cap_info.get("invariants", []),
                        domain=cap_info.get("domain", ""),
                    )
                    capabilities.append(cap)

        # Extract domain tags
        domains = data.get("domains", data.get("domain_tags", []))
        if isinstance(domains, str):
            domains = [domains]

        return AMOSEngine(
            name=name,
            version=version,
            file_path=file_path,
            capabilities=capabilities,
            raw_data=data,
            domain_tags=domains,
        )

    def get_engine(self, name: str) -> AMOSEngine | None:
        """Get engine by name."""
        return self._engines.get(name)

    def list_engines(self, domain: str | None = None) -> list[AMOSEngine]:
        """List all engines, optionally filtered by domain."""
        engines = list(self._engines.values())
        if domain:
            engines = [e for e in engines if domain in e.domain_tags]
        return engines

    def get_all_equations(self) -> dict[str, list[str]]:
        """Get all equations indexed by engine name."""
        result: dict[str, list[str]] = {}
        for name, engine in self._engines.items():
            result[name] = engine.get_equations()
        return result

    def get_all_invariants(self) -> dict[str, list[str]]:
        """Get all invariants indexed by engine name."""
        result: dict[str, list[str]] = {}
        for name, engine in self._engines.items():
            result[name] = engine.get_invariants()
        return result


# Global registry instance
_registry: EngineRegistry | None = None


def get_engine_registry() -> EngineRegistry:
    """Get or create the global engine registry."""
    global _registry
    if _registry is None:
        _registry = EngineRegistry()
        # Add default search paths
        base = Path(
            "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
        )
        paths = [
            base / "_00_AMOS_CANON" / "_LEGACY BRAIN2",
            base / "_00_AMOS_CANON" / "Core",
            base / "_00_AMOS_CANON" / "Cognitive",
            base / "_00_AMOS_CANON" / "Domains",
        ]
        for path in paths:
            _registry.add_search_path(path)
        _registry.discover_engines()
    return _registry
