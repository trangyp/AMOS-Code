"""AMOS ORGANISM OS — The 14-Subsystem Digital Organism

A deterministic, auditable, humane intelligence system for high-risk operations.
Based on the AMOS 7-System Organism Blueprint v1.0.0

Primary Loop: BRAIN → SENSES → SKELETON → WORLD_MODEL → QUANTUM_LAYER → MUSCLE → METABOLISM → BRAIN
"""

__version__ = "1.0.0"
__author__ = "Trang"

import sys
from pathlib import Path

ORGANISM_ROOT = Path(__file__).resolve().parent

# Add subsystem paths for imports (transitional pattern)
for _subsystem in [
    "01_BRAIN", "02_SENSES", "03_IMMUNE", "04_BLOOD", "05_SKELETON",
    "06_MUSCLE", "07_METABOLISM", "08_WORLD_MODEL",
    "09_SOCIAL_ENGINE", "09_QUANTUM_LAYER", "10_LIFE_ENGINE",
    "11_LEGAL_BRAIN", "11_LIFE_ENGINE",
    "12_QUANTUM_LAYER", "12_LEGAL_BRAIN", "13_FACTORY", "13_MEMORY_ARCHIVAL",
    "14_INTERFACES", "15_KNOWLEDGE_CORE",
]:
    _path = ORGANISM_ROOT / _subsystem
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

# Core exports
try:
    from .organism import AmosOrganism, OrganismState
except ImportError as e:
    AmosOrganism = None
    OrganismState = None
    print(f"[AMOS Organism] Warning: Could not import core classes: {e}")

# Subsystem exports (optional - may not all be implemented)
try:
    from .BRAIN.brain_os import BrainOS
except ImportError:
    BrainOS = None

try:
    from .BRAIN.router import RoutingDecision, SystemRouter
except ImportError:
    SystemRouter = None
    RoutingDecision = None

try:
    from .SENSES.environment_scanner import EnvironmentScanner
except ImportError:
    EnvironmentScanner = None

try:
    from .MUSCLE.executor import MuscleExecutor
except ImportError:
    MuscleExecutor = None

try:
    from .METABOLISM.pipeline_engine import PipelineEngine
except ImportError:
    PipelineEngine = None

try:
    from .BLOOD.resource_engine import ResourceEngine
except ImportError:
    ResourceEngine = None

try:
    from .IMMUNE.immune_system import ImmuneSystem
except ImportError:
    ImmuneSystem = None

try:
    from .WORLD_MODEL.knowledge_graph import KnowledgeGraph
except ImportError:
    KnowledgeGraph = None

try:
    from .QUANTUM_LAYER.scenario_engine import ScenarioEngine
except ImportError:
    ScenarioEngine = None

try:
    from .FACTORY.agent_factory import AgentFactory
except ImportError:
    AgentFactory = None

try:
    from .MUSCLE.brain_muscle_bridge import BrainMuscleBridge, get_brain_muscle_bridge
except ImportError:
    BrainMuscleBridge = None
    get_brain_muscle_bridge = None

# Canon Integration
try:
    import importlib

    _canon_mod = importlib.import_module("AMOS_ORGANISM_OS.CANON_INTEGRATION")
    CanonBridge = getattr(_canon_mod, "CanonBridge")
    CanonBridgeStatus = getattr(_canon_mod, "CanonBridgeStatus")
    CanonEnforcer = getattr(_canon_mod, "CanonEnforcer")
    StandardsRegistry = getattr(_canon_mod, "StandardsRegistry")
    get_canon_bridge = getattr(_canon_mod, "get_canon_bridge")
    initialize_canon_integration = getattr(_canon_mod, "initialize_canon_integration")
except ImportError:
    CanonBridge = None
    CanonBridgeStatus = None
    CanonEnforcer = None
    StandardsRegistry = None
    get_canon_bridge = None
    initialize_canon_integration = None

# Primary Loop
try:
    from .primary_loop import CycleResult, PrimaryLoop
except ImportError:
    PrimaryLoop = None
    CycleResult = None

# 14 Subsystem Registry
SUBSYSTEMS = {
    "00_ROOT": {
        "name": "Root",
        "folder": "00_ROOT",
        "role": "Identity, goals, global config, bootstrap specs.",
    },
    "01_BRAIN": {
        "name": "Brain",
        "folder": "01_BRAIN",
        "role": "Reasoning, planning, decomposition, memory, routing decisions.",
    },
    "02_SENSES": {
        "name": "Senses",
        "folder": "02_SENSES",
        "role": "Filesystem, environment, system load, context, emotion inputs.",
    },
    "03_IMMUNE": {
        "name": "Immune",
        "folder": "03_IMMUNE",
        "role": "Safety, legal, compliance, anomaly and boundary detection.",
    },
    "04_BLOOD": {
        "name": "Blood",
        "folder": "04_BLOOD",
        "role": "Money/blood engine: budgeting, cashflow, investing, forecasting.",
    },
    "05_SKELETON": {
        "name": "Skeleton",
        "folder": "05_SKELETON",
        "role": "Rules, constraints, hierarchy, permissions, time architecture.",
    },
    "06_MUSCLE": {
        "name": "Muscle",
        "folder": "06_MUSCLE",
        "role": "Run commands, write code, deploy and automate workflows.",
    },
    "07_METABOLISM": {
        "name": "Metabolism",
        "folder": "07_METABOLISM",
        "role": "Pipelines, transforms, IO routing and cleanup.",
    },
    "08_WORLD_MODEL": {
        "name": "World Model",
        "folder": "08_WORLD_MODEL",
        "role": "Macroeconomics, geopolitics, sectors, supply chains, global signals.",
    },
    "09_SOCIAL_ENGINE": {
        "name": "Social Engine",
        "folder": "09_SOCIAL_ENGINE",
        "role": "Humans, negotiation, influence, social pattern analysis.",
    },
    "10_LIFE_ENGINE": {
        "name": "Life Engine",
        "folder": "10_LIFE_ENGINE",
        "role": "Sleep, energy, health, mood, routines, cognitive cycles.",
    },
    "11_LEGAL_BRAIN": {
        "name": "Legal Brain",
        "folder": "11_LEGAL_BRAIN",
        "role": "Contracts, IP, compliance, regulatory scanning.",
    },
    "12_QUANTUM_LAYER": {
        "name": "Quantum Layer",
        "folder": "12_QUANTUM_LAYER",
        "role": "Timing, probability flows, synchronicities, collapse logic.",
    },
    "13_FACTORY": {
        "name": "Factory",
        "folder": "13_FACTORY",
        "role": "Agent creation, quality monitoring, self-upgrade and replacement.",
    },
    "14_INTERFACES": {
        "name": "Interfaces",
        "folder": "14_INTERFACES",
        "role": "CLI, API, web dashboard and chat integration.",
    },
    "99_ARCHIVE": {
        "name": "Archive",
        "folder": "99_ARCHIVE",
        "role": "Deprecated or unused artifacts kept for reference.",
    },
}

# Wiring Configuration
WIRING = {
    "primary_loop": [
        "01_BRAIN",
        "02_SENSES",
        "05_SKELETON",
        "08_WORLD_MODEL",
        "12_QUANTUM_LAYER",
        "06_MUSCLE",
        "07_METABOLISM",
        "01_BRAIN",
    ],
    "supporting": {
        "risk": ["03_IMMUNE", "11_LEGAL_BRAIN", "04_BLOOD"],
        "life": ["10_LIFE_ENGINE", "04_BLOOD", "02_SENSES"],
        "social": ["09_SOCIAL_ENGINE", "08_WORLD_MODEL", "10_LIFE_ENGINE"],
        "factory": ["13_FACTORY", "01_BRAIN", "05_SKELETON", "07_METABOLISM"],
        "interfaces": ["14_INTERFACES", "01_BRAIN", "06_MUSCLE", "07_METABOLISM"],
    },
}

# Registry paths (relative to ORGANISM_ROOT)
REGISTRY_PATHS = {
    "system_registry": "system_registry.json",
    "agent_registry": "agent_registry.json",
    "engine_registry": "engine_registry.json",
    "world_state": "world_state.json",
}


def get_subsystem(code: str) -> dict:
    """Get subsystem metadata by code."""
    return SUBSYSTEMS.get(code, {})


def list_primary_loop() -> list:
    """Return the primary circulation loop subsystem codes."""
    return WIRING["primary_loop"]


def list_supporting(category: str) -> list:
    """Return supporting subsystem codes for a category."""
    return WIRING["supporting"].get(category, [])


__all__ = [
    # Core
    "AmosOrganism",
    "OrganismState",
    # Subsystems
    "BrainOS",
    "SystemRouter",
    "RoutingDecision",
    "EnvironmentScanner",
    "MuscleExecutor",
    "PipelineEngine",
    "ResourceEngine",
    "ImmuneSystem",
    "KnowledgeGraph",
    "ScenarioEngine",
    "AgentFactory",
    "BrainMuscleBridge",
    "get_brain_muscle_bridge",
    # Primary Loop
    "PrimaryLoop",
    "CycleResult",
    # Registry
    "SUBSYSTEMS",
    "WIRING",
    "ORGANISM_ROOT",
    # Helpers
    "list_primary_loop",
    "list_supporting",
]
