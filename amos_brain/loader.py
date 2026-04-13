"""Brain configuration loader - loads and validates AMOS brain JSON specs."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BrainConfig:
    """Runtime brain configuration."""
    name: str = "AMOS_FULL_BRAIN_OS"
    version: str = "vInfinity_merged_2"
    domains: list[str] = field(default_factory=list)
    ubi_domains: list[str] = field(default_factory=list)
    global_laws: dict = field(default_factory=dict)
    reasoning_constraints: dict = field(default_factory=dict)
    engines: dict = field(default_factory=dict)
    gap_management: dict = field(default_factory=dict)


class BrainLoader:
    """Loads AMOS brain specifications from JSON files."""

    DEFAULT_CORE_CANDIDATES = [
        Path(__file__).resolve().parent / "_AMOS_BRAIN" / "_LEGACY BRAIN" / "Core",
        Path(__file__).resolve().parent / "_AMOS_BRAIN",
        Path(__file__).resolve().parent.parent / "_AMOS_BRAIN" / "_LEGACY BRAIN" / "Core",
        Path(__file__).resolve().parent.parent / "_AMOS_BRAIN",
    ]

    def __init__(self, core_path: Path | None = None):
        self.core_path = core_path or self._resolve_core_path()
        self._config: BrainConfig | None = None
        self._raw_specs: dict[str, Any] = {}

    def _resolve_core_path(self) -> Path:
        for candidate in self.DEFAULT_CORE_CANDIDATES:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            "Could not locate AMOS brain core data. "
            "Pass core_path explicitly or place the data under _AMOS_BRAIN."
        )

    def load(self) -> BrainConfig:
        """Load all brain specifications and merge into runtime config."""
        self._config = BrainConfig()

        # Load master brain OS
        master_path = self.core_path / "AMOS_Brain_Master_Os_v0.json"
        if master_path.exists():
            self._load_master_brain(master_path)

        # Load agent OS
        agent_path = self.core_path / "AMOS_Os_Agent_v0.json"
        if agent_path.exists():
            self._load_agent_os(agent_path)

        # Load 7 Intelligences
        intelligents_path = self.core_path / "7_Intelligents"
        if intelligents_path.exists():
            self._load_intelligences(intelligents_path)

        # Load cognitive stack
        cognitive_path = self.core_path / "Cognitive_Stack"
        if cognitive_path.exists():
            self._load_cognitive_stack(cognitive_path)

        return self._config

    def _load_master_brain(self, path: Path) -> None:
        """Load AMOS_Brain_Master_Os_v0.json."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            spec = data[0]
        else:
            spec = data

        self._raw_specs['master'] = spec
        meta = spec.get('meta', {})

        self._config.name = spec.get('name', self._config.name)
        self._config.version = spec.get('version', self._config.version)
        self._config.domains = meta.get('coverage', {}).get('domains', [])
        self._config.ubi_domains = meta.get('coverage', {}).get('ubi_domains', [])
        self._config.gap_management = spec.get('gap_management', {})

        # Extract engines from components
        components = spec.get('components', {})
        brain_core = components.get('brain_core', {})
        self._config.engines = brain_core.get('engines', {})

    def _load_agent_os(self, path: Path) -> None:
        """Load AMOS_Os_Agent_v0.json for global laws and reasoning constraints."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            spec = data[0]
        else:
            spec = data

        self._raw_specs['agent'] = spec
        components = spec.get('components', {})
        brain_root = components.get('AMOS_BRAIN_ROOT.json', {})

        self._config.global_laws = brain_root.get('global_laws', {})
        self._config.reasoning_constraints = brain_root.get('reasoning_constraints', {})

    def _load_intelligences(self, path: Path) -> None:
        """Load all 7 Intelligences engine specs."""
        for json_file in path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._raw_specs[f"intel_{json_file.stem}"] = data
            except Exception:
                pass  # Skip invalid files

    async def load_async(self, timeout_seconds: float = 5.0) -> BrainConfig:
        """Async load with timeout protection to prevent UI hanging.

        Args:
            timeout_seconds: Maximum time to wait for loading (default 5s)

        Returns:
            BrainConfig instance

        Raises:
            TimeoutError: If loading takes longer than timeout_seconds
        """
        loop = asyncio.get_event_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self.load),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Return a minimal config on timeout to prevent hanging
            self._config = BrainConfig()
            return self._config

    def _load_cognitive_stack(self, path: Path) -> None:
        """Load cognitive stack organization."""
        stack_data: dict[str, Any] = {}
        for category_dir in path.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                stack_data[category_name] = []
                for json_file in category_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            stack_data[category_name].append(json.load(f))
                    except Exception:
                        pass
        self._raw_specs['cognitive_stack'] = stack_data

    def get_raw_spec(self, name: str) -> Any:
        """Get raw specification by name."""
        return self._raw_specs.get(name)

    def list_engines(self) -> list[str]:
        """List available domain engines."""
        return list(self._config.engines.keys()) if self._config else []

    def get_gap_rules(self) -> list[str]:
        """Get irreducible limits from gap management."""
        if self._config:
            return self._config.gap_management.get('irreducible_limits', [])
        return []


# Global singleton
_brain_loader: BrainLoader | None = None


def get_brain() -> BrainLoader:
    """Get or create global brain loader instance.

    Returns:
        BrainLoader instance
    """
    global _brain_loader
    if _brain_loader is None:
        _brain_loader = BrainLoader()
        _brain_loader.load()
    return _brain_loader


async def get_brain_async(timeout_seconds: float = 5.0) -> BrainLoader:
    """Get or create global brain loader instance asynchronously with timeout.

    This prevents the IDE from showing 'taking a long time' messages
    when brain loading is slow due to large JSON files.

    Args:
        timeout_seconds: Maximum time to wait for loading (default 5s)

    Returns:
        BrainLoader instance (may have minimal config if timeout occurred)
    """
    global _brain_loader
    if _brain_loader is None:
        _brain_loader = BrainLoader()
        await _brain_loader.load_async(timeout_seconds)
    return _brain_loader
