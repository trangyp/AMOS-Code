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
    # Optional
    "SystemPromptBuilder",
]
