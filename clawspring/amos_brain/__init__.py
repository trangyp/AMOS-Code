"""AMOS Brain Integration Layer - Connecting ClawSpring to AMOS Cognitive Architecture."""
from .loader import BrainLoader, get_brain
from .kernel_router import KernelRouter
from .prompt_builder import SystemPromptBuilder
from .laws import GlobalLaws
from .expression_translator import ExpressionTranslator, translate_expression
from .integration import AMOSBrainIntegration, get_amos_integration
from .engine_executor import EngineExecutor, execute_cognitive_task, ExecutionResult
from .multi_agent_orchestrator import MultiAgentOrchestrator, run_cognitive_consensus, ConsensusResult
from .cognitive_audit import CognitiveAuditTrail, record_cognitive_decision, AuditEntry
from .feedback_loop import CognitiveFeedbackLoop, get_enhanced_engines, get_task_advice
from .audit_exporter import AuditExporter, export_audit

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
