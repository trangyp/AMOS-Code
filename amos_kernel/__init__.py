"""
AMOS Kernel - Kernel-First Architecture + Axiom Integration

Six layers (L0-L5) with strict dependency order:
    law → state → interaction → deterministic → observe → repair

Axiom Extensions:
    - Canonical State Model (coupled hyperbundle)
    - .amos/ Control Directory System
    - 8 OpenClaws Integration Buses
    - Natural Language Processor

All runtime, build, and repair paths validate through this stack.
"""

# AUTO-INTEGRATE ALL 6 REPOSITORIES
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).parent.parent
AMOS_REPOS = REPO_ROOT / "AMOS_REPOS"
for _repo_path in [
    str(AMOS_REPOS / "AMOS-Code"),
    str(AMOS_REPOS / "AMOS-Consulting"),
    str(AMOS_REPOS / "AMOS-Claws"),
    str(AMOS_REPOS / "Mailinhconect"),
    str(AMOS_REPOS / "AMOS-Invest"),
    str(AMOS_REPOS / "AMOS-UNIVERSE"),
]:
    if _repo_path not in sys.path:
        sys.path.insert(0, _repo_path)

# Axiom CLI and MCP Server
from .axiom_cli import main as axiom_cli_main
from .axiom_mcp_server import AxiomMCPServer
from .axiom_mcp_server import main as axiom_mcp_main

# Axiom State Model (Section 104.6)
from .axiom_state import (
    AxiomState,
    BiologicalState,
    ClassicalState,
    HybridState,
    IdentityState,
    LedgerState,
    MetaState,
    QuantumState,
    StateDomain,
    StateManager,
    TemporalState,
    UncertaintyState,
    WorldState,
    get_state_manager,
)
from .client import AMOSKernelClient, create_kernel, get_kernel

# Axiom Control Directory (Section 105)
from .control_directory import (
    ArchitectureConfig,
    ControlDirectoryManager,
    GlossaryConfig,
    PoliciesConfig,
    PolicyRule,
    RepoConfig,
    SsotConfig,
    TermMapping,
    VerificationCheck,
    VerifyConfig,
    get_control_manager,
)
from .core.deterministic import DeterministicCore, TransitionResult
from .core.interaction import InteractionOperator, InteractionResult
from .core.law import UniversalLawKernel, ValidationResult
from .core.observe import DriftReport, detect_drift
from .core.repair import RepairPlan, propose_repairs
from .core.state import IntegrityTensor, TensorState, UniversalStateModel

# Unified Kernel
from .unified_kernel import UnifiedAmosKernel, UnifiedState, get_unified_kernel

# Axiom Integration Buses (Section 103.1)
from .integration_bus import (
    BusCoordinator,
    BusMessage,
    BusPriority,
    BusSubscription,
    BusType,
    FrontendBus,
    IntegrationBus,
    MemoryBus,
    MemoryEntry,
    MemoryStore,
    ModelBus,
    ModelRequest,
    ModelResponse,
    ModelRouter,
    LLMProvider,
    OpenAIProvider,
    LocalProvider,
    MockProvider,
    create_llm_provider,
    PolicyBus,
    ProtocolBus,
    RuntimeBus,
    SyncBus,
    ToolBus,
    ToolDefinition,
    ToolRegistry,
    UIComponent,
    UIEvent,
    get_bus_coordinator,
)

# Axiom Engine Loader (Section 104)
from .engine_loader import (
    AMOSEngine,
    EngineCapability,
    EngineRegistry,
    get_engine_registry,
)

# Legacy Brain Loader (Section 105)
from .legacy_brain_loader import (
    LegacyBrainLoader,
    activate_legacy_brain,
)

# Axiom NL Processor (Section 105)
from .nl_processor import (
    CommandLedger,
    CommandStatus,
    IntentIR,
    NLProcessor,
    PatchProposal,
    RiskLevel,
    VerificationResult,
    get_nl_processor,
)

# Persistence Layer
from .persistence import AxiomPersistence, AxiomPersistenceConfig, get_axiom_persistence

# FastAPI Integration - lazy import to avoid circular dependency
def create_kernel_app(*args, **kwargs):
    from .fastapi_integration import create_kernel_app as _create_app
    return _create_app(*args, **kwargs)

def create_kernel_router(*args, **kwargs):
    from .fastapi_integration import create_kernel_router as _create_router
    return _create_router(*args, **kwargs)

__all__ = [
    # L0 - Law Layer
    "UniversalLawKernel",
    "ValidationResult",
    # L1 - State Layer
    "UniversalStateModel",
    "TensorState",
    "IntegrityTensor",
    # L2 - Interaction Layer
    "InteractionOperator",
    "InteractionResult",
    # L3 - Deterministic Layer
    "DeterministicCore",
    "TransitionResult",
    # L4 - Observe Layer
    "detect_drift",
    "DriftReport",
    # L5 - Repair Layer
    "propose_repairs",
    "RepairPlan",
    # Unified Kernel
    "UnifiedAmosKernel",
    "UnifiedState",
    "get_unified_kernel",
    # Client
    "AMOSKernelClient",
    "get_kernel",
    "create_kernel",
    # FastAPI Integration
    "create_kernel_app",
    "create_kernel_router",
    # Axiom State Model
    "AxiomState",
    "ClassicalState",
    "QuantumState",
    "BiologicalState",
    "HybridState",
    "WorldState",
    "TemporalState",
    "UncertaintyState",
    "LedgerState",
    "IdentityState",
    "MetaState",
    "StateDomain",
    "StateManager",
    "get_state_manager",
    # Axiom Control Directory
    "ControlDirectoryManager",
    "RepoConfig",
    "GlossaryConfig",
    "PoliciesConfig",
    "ArchitectureConfig",
    "VerifyConfig",
    "SsotConfig",
    "TermMapping",
    "PolicyRule",
    "VerificationCheck",
    "get_control_manager",
    # Axiom Integration Buses
    "BusType",
    "BusPriority",
    "BusMessage",
    "BusSubscription",
    "IntegrationBus",
    "ModelBus",
    "ModelRequest",
    "ModelResponse",
    "ModelRouter",
    "LLMProvider",
    "OpenAIProvider",
    "LocalProvider",
    "MockProvider",
    "create_llm_provider",
    "MemoryBus",
    "MemoryEntry",
    "MemoryStore",
    "ToolBus",
    "ToolDefinition",
    "ToolRegistry",
    "ProtocolBus",
    "RuntimeBus",
    "FrontendBus",
    "PolicyBus",
    "SyncBus",
    "UIComponent",
    "UIEvent",
    "BusCoordinator",
    "get_bus_coordinator",
    # Axiom Engine Loader
    "AMOSEngine",
    "EngineCapability",
    "EngineRegistry",
    "get_engine_registry",
    # Legacy Brain Loader
    "LegacyBrainLoader",
    "activate_legacy_brain",
    # Axiom NL Processor
    "RiskLevel",
    "CommandStatus",
    "IntentIR",
    "PatchProposal",
    "VerificationResult",
    "CommandLedger",
    "NLProcessor",
    "get_nl_processor",
    # Axiom CLI and MCP
    "axiom_cli_main",
    "AxiomMCPServer",
    "axiom_mcp_main",
    # Persistence Layer
    "AxiomPersistence",
    "AxiomPersistenceConfig",
    "get_axiom_persistence",
]

__version__ = "7.1.0-kernel"
