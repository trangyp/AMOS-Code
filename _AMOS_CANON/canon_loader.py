#!/usr/bin/env python3
"""Canon Loader - Loads canonical definitions from _00_AMOS_CANON."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .canon_core import CanonCore, CanonAgent, CanonGlossaryEntry, CanonKernel, CanonStatus, CanonCategory, CanonPriority

logger = logging.getLogger(__name__)
CANON_DATA_DIR = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON")

@dataclass
class CanonLoadResult:
    success: bool
    files_loaded: list[str] = field(default_factory=list)
    files_failed: list[str] = field(default_factory=list)
    total_terms: int = 0
    total_agents: int = 0
    total_kernels: int = 0
    message: str = ""

class CanonLoader:
    _instance: CanonLoader | None = None
    _lock = asyncio.Lock()

    def __new__(cls) -> CanonLoader:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, canon_dir: Path | None = None):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.canon_dir = canon_dir or CANON_DATA_DIR
        self._core = CanonCore()
        self._ready = False

    @property
    def ready(self) -> bool:
        return self._ready

    async def initialize(self) -> CanonLoadResult:
        logger.info("Initializing CanonLoader...")
        result = CanonLoadResult(success=True)
        try:
            glossary_result = await self._load_glossary()
            result.files_loaded.extend(glossary_result.files_loaded)
            result.files_failed.extend(glossary_result.files_failed)
            result.total_terms = glossary_result.total_terms
            agent_result = await self._load_agent_registry()
            result.files_loaded.extend(agent_result.files_loaded)
            result.files_failed.extend(agent_result.files_failed)
            result.total_agents = agent_result.total_agents
            kernel_result = await self._load_kernels()
            result.files_loaded.extend(kernel_result.files_loaded)
            result.files_failed.extend(kernel_result.files_failed)
            result.total_kernels = kernel_result.total_kernels
            self._ready = True
            self._core.set_status(CanonStatus.ACTIVE)
            result.message = f"Loaded {result.total_terms} terms, {result.total_agents} agents, {result.total_kernels} kernels"
            logger.info(f"CanonLoader initialized: {result.message}")
        except Exception as e:
            result.success = False
            result.message = str(e)
            logger.error(f"CanonLoader initialization failed: {e}")
        return result

    async def _load_glossary(self) -> CanonLoadResult:
        result = CanonLoadResult(success=True)
        glossary_file = self.canon_dir / "AMOS_CANONICAL_GLOSSARY.json"
        if not glossary_file.exists():
            result.files_failed.append(str(glossary_file))
            return result
        try:
            with open(glossary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for term_id, term_data in data.items():
                entry = CanonGlossaryEntry(
                    id=term_id,
                    name=term_data.get("term", term_id),
                    description=term_data.get("definition", ""),
                    term=term_data.get("term", term_id),
                    definition=term_data.get("definition", ""),
                    category=CanonCategory.COGNITIVE,
                    priority=CanonPriority.MEDIUM,
                    synonyms=term_data.get("synonyms", []),
                    related_terms=term_data.get("related_terms", []),
                )
                self._core.add_glossary_entry(entry)
                result.total_terms += 1
            result.files_loaded.append(str(glossary_file))
        except Exception as e:
            result.files_failed.append(f"{glossary_file}: {e}")
        return result

    async def _load_agent_registry(self) -> CanonLoadResult:
        result = CanonLoadResult(success=True)
        registry_file = self.canon_dir / "AMOS_AGENT_REGISTRY.json"
        if not registry_file.exists():
            result.files_failed.append(str(registry_file))
            return result
        try:
            with open(registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            agents = data.get("agents", {})
            for agent_id, agent_data in agents.items():
                agent = CanonAgent(
                    id=agent_id,
                    name=agent_data.get("name", agent_id),
                    description=agent_data.get("description", ""),
                    agent_type=agent_data.get("type", "generic"),
                    capabilities=agent_data.get("capabilities", []),
                    module_path=agent_data.get("module_path", ""),
                    category=CanonCategory.COGNITIVE,
                    priority=CanonPriority.HIGH,
                )
                self._core.add_agent(agent)
                result.total_agents += 1
            result.files_loaded.append(str(registry_file))
        except Exception as e:
            result.files_failed.append(f"{registry_file}: {e}")
        return result

    async def _load_kernels(self) -> CanonLoadResult:
        result = CanonLoadResult(success=True)
        kernels_dir = self.canon_dir / "Kernels"
        if not kernels_dir.exists():
            result.files_failed.append(str(kernels_dir))
            return result
        try:
            kernel_files = list(kernels_dir.glob("*.json"))
            result.total_kernels = len(kernel_files)
            for kernel_file in kernel_files:
                try:
                    with open(kernel_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    kernel_id = data.get("id", kernel_file.stem)
                    kernel = CanonKernel(
                        id=kernel_id,
                        name=data.get("name", kernel_id),
                        description=data.get("description", ""),
                        kernel_type=data.get("type", "generic"),
                        domain=data.get("domain", "general"),
                        equations=data.get("equations", []),
                        invariants=data.get("invariants", []),
                        category=CanonCategory.COGNITIVE,
                        priority=CanonPriority.HIGH,
                    )
                    self._core.add_kernel(kernel)
                except Exception as e:
                    logger.warning(f"Failed to load kernel {kernel_file}: {e}")
            result.files_loaded.append(str(kernels_dir))
        except Exception as e:
            result.files_failed.append(f"{kernels_dir}: {e}")
        return result

    def get_glossary(self) -> dict[str, CanonGlossaryEntry]:
        return self._core._glossary

    def get_agent_registry(self) -> dict[str, CanonAgent]:
        return self._core._agents

    def get_kernels(self) -> dict[str, CanonKernel]:
        return self._core._kernels

    def get_core(self) -> CanonCore:
        return self._core

    def get_stats(self) -> dict[str, Any]:
        return {"ready": self._ready, "canon_dir": str(self.canon_dir), **self._core.get_stats()}

_loader: CanonLoader | None = None

async def get_canon_loader(canon_dir: Path | None = None) -> CanonLoader:
    global _loader
    if _loader is None:
        _loader = CanonLoader(canon_dir)
        await _loader.initialize()
    return _loader
