"""AMOS Brain Integration Layer - Connecting ClawSpring to AMOS Cognitive Architecture."""
from .loader import BrainLoader
from .kernel_router import KernelRouter
from .prompt_builder import SystemPromptBuilder
from .laws import GlobalLaws
from .expression_translator import ExpressionTranslator, translate_expression

__all__ = [
    "BrainLoader",
    "KernelRouter",
    "SystemPromptBuilder",
    "GlobalLaws",
    "ExpressionTranslator",
    "translate_expression",
]
