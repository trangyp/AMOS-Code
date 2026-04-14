"""AMOS Brain Integration Layer - Connecting ClawSpring to AMOS Cognitive Architecture."""
from .audit_exporter import AuditExporter, export_audit
from .cognitive_audit import AuditEntry, CognitiveAuditTrail, record_cognitive_decision
from .engine_executor import EngineExecutor, ExecutionResult, execute_cognitive_task
from .expression_translator import ExpressionTranslator, translate_expression
from .feedback_loop import CognitiveFeedbackLoop, get_enhanced_engines, get_task_advice
from .integration import AMOSBrainIntegration, get_amos_integration
from .kernel_router import KernelRouter
from .laws import GlobalLaws
from .loader import BrainLoader, get_brain
from .multi_agent_orchestrator import (
    ConsensusResult,
    MultiAgentOrchestrator,
    run_cognitive_consensus,
)
from .prompt_builder import SystemPromptBuilder

__all__ = [
    "BrainLoader",
    "get_brain",
    "KernelRouter",
    "SystemPromptBuilder",
    "GlobalLaws",
    "ExpressionTranslator",
    "translate_expression",
    "AMOSBrainIntegration",
    "get_amos_integration",
    "EngineExecutor",
    "execute_cognitive_task",
    "ExecutionResult",
    "MultiAgentOrchestrator",
    "run_cognitive_consensus",
    "ConsensusResult",
    "CognitiveAuditTrail",
    "record_cognitive_decision",
    "AuditEntry",
    "CognitiveFeedbackLoop",
    "get_enhanced_engines",
    "get_task_advice",
    "AuditExporter",
    "export_audit",
]
