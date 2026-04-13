"""AMOS Brain Integration Layer - Connects cognitive architecture to agent runtime."""

from .loader import BrainLoader, get_brain, get_brain_async, BrainConfig
from .cognitive_stack import CognitiveStack, DomainEngine
from .reasoning import ReasoningEngine, RuleOfTwo, RuleOfFour, Perspective, Quadrant
from .laws import GlobalLaws, UBILaws, Law
from .integration import AMOSBrainIntegration, get_amos_integration
from .kernel_router import KernelRouter, TaskIntent
from .task_processor import BrainTaskProcessor, process_task, TaskResult
from .agent_bridge import (
    AMOSAgentBridge, get_agent_bridge, ToolDecision, ExecutionContext
)
from .state_manager import (
    CognitiveStateManager, get_state_manager,
    ReasoningStep, WorkflowSession
)
from .meta_controller import (
    MetaCognitiveController, get_meta_controller,
    orchestrate_goal, WorkflowPlan, SubTask
)
from .monitor import CognitiveMonitor, get_monitor, MetricPoint, Alert
from .facade import BrainClient, think, validate, decide, BrainResponse, Decision
from .config import CognitiveConfig, get_config, LawEnforcementConfig, FeatureFlags

# Optional: prompt builder (requires brain_loader to be passed)
try:
    from .prompt_builder import SystemPromptBuilder
except ImportError:
    SystemPromptBuilder = None

# Optional: clawspring bridge (only if clawspring is available)
ClawSpringBridge = None
create_amos_agent = None

# Auto-register skills if clawspring available
try:
    from .skill import register_amos_skills
    register_amos_skills()
except Exception:
    pass

__all__ = [
    # Core brain
    "BrainLoader",
    "get_brain",
    "get_brain_async",
    "BrainConfig",
    # Cognitive stack
    "CognitiveStack",
    "DomainEngine",
    # Reasoning
    "ReasoningEngine",
    "RuleOfTwo",
    "RuleOfFour",
    "Perspective",
    "Quadrant",
    # Laws
    "GlobalLaws",
    "UBILaws",
    "Law",
    # Integration
    "AMOSBrainIntegration",
    "get_amos_integration",
    # Router
    "KernelRouter",
    "TaskIntent",
    # Task processor
    "BrainTaskProcessor",
    "process_task",
    "TaskResult",
    # Agent bridge
    "AMOSAgentBridge",
    "get_agent_bridge",
    "ToolDecision",
    "ExecutionContext",
    # State manager
    "CognitiveStateManager",
    "get_state_manager",
    "ReasoningStep",
    "WorkflowSession",
    # Meta controller
    "MetaCognitiveController",
    "get_meta_controller",
    "orchestrate_goal",
    "WorkflowPlan",
    "SubTask",
    # Optional
    "SystemPromptBuilder",
]

# Cookbook workflows (optional import)
try:
    from .cookbook import (
        ArchitectureDecision,
        ProjectPlanner,
        ProblemDiagnosis,
        TechnologySelection,
        RiskAssessment,
        WorkflowResult,
    )
    __all__.extend([
        "ArchitectureDecision",
        "ProjectPlanner",
        "ProblemDiagnosis",
        "TechnologySelection",
        "RiskAssessment",
        "WorkflowResult",
    ])
except Exception:
    pass
