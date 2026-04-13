"""AMOS Brain Integration Layer - Connecting ClawSpring to AMOS Cognitive Architecture."""
from .loader import BrainLoader, get_brain
from .kernel_router import KernelRouter
from .prompt_builder import SystemPromptBuilder
from .laws import GlobalLaws
from .expression_translator import ExpressionTranslator, translate_expression
from .integration import AMOSBrainIntegration, get_amos_integration

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
]
