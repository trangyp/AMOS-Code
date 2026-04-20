from __future__ import annotations

"""AMOS Canon Integration Module.

Loads and exposes canonical definitions from _00_AMOS_CANON:
- AMOS_CANONICAL_GLOSSARY.json - System terminology and definitions
- AMOS_AGENT_REGISTRY.json - Agent registry with module paths
- AMOS_Brain_Master_Os_v0.json - Brain OS with UBI domain engines
- Core/Cognitive_Stack/ - Domain-specific cognitive modules
- Kernels/ - Kernel specifications
- canonical_body_registry.json - Body structure definitions

Usage:
    from amos_canon_integration import get_canon_loader

    loader = get_canon_loader()
    await loader.initialize()

    # Access canonical data
    glossary = loader.get_glossary()
    agents = loader.get_agent_registry()
    brain_os = loader.get_brain_os_spec()
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CANON_DIR = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON")


@dataclass
class CanonLoadStatus:
    """Status of Canon data loading."""

    timestamp: str
    loaded_files: list[str] = field(default_factory=list)
    failed_files: list[str] = field(default_factory=list)
    total_terms: int = 0
    total_agents: int = 0
    total_engines: int = 0
    ready: bool = False


class AMOSCanonLoader:
    """Loads and manages canonical AMOS definitions.

    Provides unified access to:
    - Canonical glossary (system terms, biological mappings, logic)
    - Agent registry (agent definitions and module paths)
    - Brain OS specification (UBI domain engines)
    - Cognitive stack (domain-specific modules)
    - Kernel specifications
    - Body registry
    """

    _instance: AMOSCanonLoader = None
    _lock = asyncio.Lock()

    def __new__(cls) -> AMOSCanonLoader:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._glossary: dict[str, Any] = {}
        self._agent_registry: dict[str, Any] = {}
        self._brain_os: list[dict[str, Any]] = []
        self._body_registry: dict[str, Any] = {}
        self._cognitive_stack: dict[str, Any] = {}
        self._kernels: dict[str, Any] = {}
        self._status: CanonLoadStatus = None
        self._loaded = False

    async def initialize(self) -> bool:
        """Load all canonical definitions.

        Returns:
            bool: True if all critical files loaded successfully
        """
        if self._loaded:
            return True

        print("\n[Canon] Initializing AMOS Canon Integration...")
        print("-" * 50)

        loaded = []
        failed = []

        # Load glossary
        if await self._load_glossary():
            loaded.append("AMOS_CANONICAL_GLOSSARY.json")
        else:
            failed.append("AMOS_CANONICAL_GLOSSARY.json")

        # Load agent registry
        if await self._load_agent_registry():
            loaded.append("AMOS_AGENT_REGISTRY.json")
        else:
            failed.append("AMOS_AGENT_REGISTRY.json")

        # Load brain OS
        if await self._load_brain_os():
            loaded.append("AMOS_Brain_Master_Os_v0.json")
        else:
            failed.append("AMOS_Brain_Master_Os_v0.json")

        # Load body registry
        if await self._load_body_registry():
            loaded.append("canonical_body_registry.json")
        else:
            failed.append("canonical_body_registry.json")

        # Load cognitive stack
        await self._load_cognitive_stack()
        loaded.append("Core/Cognitive_Stack/")

        # Load kernels
        await self._load_kernels()
        loaded.append("Kernels/")

        # Calculate stats
        total_terms = sum(len(layer.get("terms", [])) for layer in self._glossary.get("layers", []))
        total_agents = len(self._agent_registry.get("agents", {}))
        total_engines = 0
        if self._brain_os and len(self._brain_os) > 0:
            components = self._brain_os[0].get("components", {})
            brain_core = components.get("brain_core", {})
            total_engines = len(brain_core.get("engines", {}))

        self._status = CanonLoadStatus(
            timestamp=datetime.now(timezone.utc).isoformat(),
            loaded_files=loaded,
            failed_files=failed,
            total_terms=total_terms,
            total_agents=total_agents,
            total_engines=total_engines,
            ready=len(failed) == 0,
        )

        self._loaded = True

        print(f"  ✅ Loaded: {len(loaded)} file groups")
        print(f"     Terms: {total_terms}")
        print(f"     Agents: {total_agents}")
        print(f"     Engines: {total_engines}")
        if failed:
            print(f"  ⚠️  Failed: {', '.join(failed)}")

        return self._status.ready

    async def _load_glossary(self) -> bool:
        """Load canonical glossary."""
        try:
            path = CANON_DIR / "AMOS_CANONICAL_GLOSSARY.json"
            if not path.exists():
                logger.warning(f"Glossary not found: {path}")
                return False

            with open(path, encoding="utf-8") as f:
                self._glossary = json.load(f)

            logger.info(f"Loaded glossary: {len(self._glossary.get('layers', []))} layers")
            return True

        except Exception as e:
            logger.error(f"Failed to load glossary: {e}")
            return False

    async def _load_agent_registry(self) -> bool:
        """Load agent registry."""
        try:
            path = CANON_DIR / "AMOS_AGENT_REGISTRY.json"
            if not path.exists():
                logger.warning(f"Agent registry not found: {path}")
                return False

            with open(path, encoding="utf-8") as f:
                self._agent_registry = json.load(f)

            logger.info(
                f"Loaded agent registry: {len(self._agent_registry.get('agents', {}))} agents"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load agent registry: {e}")
            return False

    async def _load_brain_os(self) -> bool:
        """Load brain OS specification."""
        try:
            path = CANON_DIR / "Core" / "AMOS_Brain_Master_Os_v0.json"
            if not path.exists():
                logger.warning(f"Brain OS not found: {path}")
                return False

            with open(path, encoding="utf-8") as f:
                self._brain_os = json.load(f)

            logger.info(f"Loaded brain OS: {len(self._brain_os)} root components")
            return True

        except Exception as e:
            logger.error(f"Failed to load brain OS: {e}")
            return False

    async def _load_body_registry(self) -> bool:
        """Load canonical body registry."""
        try:
            path = CANON_DIR / "canonical_body_registry.json"
            if not path.exists():
                logger.warning(f"Body registry not found: {path}")
                return False

            with open(path, encoding="utf-8") as f:
                self._body_registry = json.load(f)

            logger.info(f"Loaded body registry: {len(self._body_registry)} entries")
            return True

        except Exception as e:
            logger.error(f"Failed to load body registry: {e}")
            return False

    async def _load_cognitive_stack(self) -> None:
        """Load cognitive stack modules."""
        stack_dir = CANON_DIR / "Core" / "Cognitive_Stack"
        if not stack_dir.exists():
            return

        for domain_dir in stack_dir.iterdir():
            if domain_dir.is_dir():
                domain_name = domain_dir.name
                self._cognitive_stack[domain_name] = {}

                for json_file in domain_dir.glob("*.json"):
                    try:
                        with open(json_file, encoding="utf-8") as f:
                            self._cognitive_stack[domain_name][json_file.stem] = json.load(f)
                    except Exception as e:
                        logger.debug(f"Failed to load {json_file}: {e}")

        logger.info(f"Loaded cognitive stack: {len(self._cognitive_stack)} domains")

    async def _load_kernels(self) -> None:
        """Load kernel specifications."""
        kernels_dir = CANON_DIR / "Kernels"
        if not kernels_dir.exists():
            return

        # Load main kernel files
        for json_file in kernels_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    self._kernels[json_file.stem] = json.load(f)
            except Exception as e:
                logger.debug(f"Failed to load kernel {json_file}: {e}")

        # Load subdirectories
        for subdir in kernels_dir.iterdir():
            if subdir.is_dir():
                subdir_name = subdir.name
                self._kernels[subdir_name] = {}

                for json_file in subdir.glob("*.json"):
                    try:
                        with open(json_file, encoding="utf-8") as f:
                            self._kernels[subdir_name][json_file.stem] = json.load(f)
                    except Exception as e:
                        logger.debug(f"Failed to load {json_file}: {e}")

        logger.info(f"Loaded kernels: {len(self._kernels)} categories")

    def get_glossary(self) -> dict[str, Any]:
        """Get canonical glossary."""
        return self._glossary

    def get_agent_registry(self) -> dict[str, Any]:
        """Get agent registry."""
        return self._agent_registry

    def get_brain_os_spec(self) -> list[dict[str, Any]]:
        """Get brain OS specification."""
        return self._brain_os

    def get_body_registry(self) -> dict[str, Any]:
        """Get canonical body registry."""
        return self._body_registry

    def get_cognitive_stack(self) -> dict[str, Any]:
        """Get cognitive stack."""
        return self._cognitive_stack

    def get_kernels(self) -> dict[str, Any]:
        """Get kernel specifications."""
        return self._kernels

    def get_term_definition(self, term_name: str) -> dict[str, Any]:
        """Look up a term definition from the glossary."""
        for layer in self._glossary.get("layers", []):
            for term in layer.get("terms", []):
                if term.get("name") == term_name:
                    return term
        return None

    def get_agent_spec(self, agent_name: str) -> dict[str, Any]:
        """Get agent specification by name."""
        return self._agent_registry.get("agents", {}).get(agent_name)

    def get_engine_spec(self, engine_name: str) -> dict[str, Any]:
        """Get engine specification from brain OS."""
        if not self._brain_os or len(self._brain_os) == 0:
            return None

        components = self._brain_os[0].get("components", {})
        brain_core = components.get("brain_core", {})
        engines = brain_core.get("engines", {})

        return engines.get(engine_name)

    def get_status(self) -> CanonLoadStatus:
        """Get loading status."""
        return self._status

    def is_loaded(self) -> bool:
        """Check if canon data is loaded."""
        return self._loaded


# Global singleton instance
_canon_loader: AMOSCanonLoader = None


def get_canon_loader() -> AMOSCanonLoader:
    """Get or create the global Canon loader instance."""
    global _canon_loader
    if _canon_loader is None:
        _canon_loader = AMOSCanonLoader()
    return _canon_loader


async def initialize_canon() -> bool:
    """Initialize AMOS Canon integration.

    Convenience function for bootstrap orchestrator.

    Returns:
        bool: True if initialization successful
    """
    loader = get_canon_loader()
    return await loader.initialize()
