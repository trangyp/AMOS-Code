"""
AMOS Compiler: Natural Language to Code Compiler

This package implements the AMOS natural-language-to-code compiler:

  Human Intent -> Intent IR -> Repo Graph -> Grounded Plan -> Verification -> Apply

Usage:
    from amos_compiler import parse_intent, ground_intent, compile_instruction

    # Full pipeline
    result = compile_instruction("make localhost API key optional")

Modules:
    intent_ir: Intent Intermediate Representation
    repo_graph: Codebase graph representation
    grounding: Human-to-code mapping
    cli: Command-line interface
"""

from __future__ import annotations

from typing import Optional

from .grounding import (
    EditScope,
    GroundedConcept,
    GroundedIntent,
    GroundingEngine,
    ground_intent,
)
from .intent_ir import (
    ActionType,
    CheckRequirement,
    Constraint,
    EditLevel,
    IntentIR,
    IntentParser,
    RiskLevel,
    parse_intent,
)
from .repo_graph import (
    Entrypoint,
    Module,
    RepoGraph,
    RepoScanner,
    Symbol,
    build_repo_graph,
)

__version__ = "1.0.0"
__all__ = [
    # Intent IR
    "IntentIR",
    "IntentParser",
    "ActionType",
    "EditLevel",
    "RiskLevel",
    "Constraint",
    "CheckRequirement",
    "parse_intent",
    # Repo Graph
    "RepoGraph",
    "RepoScanner",
    "Symbol",
    "Module",
    "Entrypoint",
    "build_repo_graph",
    # Grounding
    "GroundedIntent",
    "GroundedConcept",
    "EditScope",
    "GroundingEngine",
    "ground_intent",
]


def compile_instruction(
    instruction: str,
    repo_root: Optional[str] = None,
    dry_run: bool = True,
) -> dict:
    """
    Full compiler pipeline: instruction -> grounded plan.

    Args:
        instruction: Natural language instruction
        repo_root: Path to repo root (default: current directory)
        dry_run: If True, only plan without applying changes

    Returns:
        Dictionary with intent_ir, grounded_intent, and plan
    """
    from pathlib import Path

    # Stage 1: Parse intent
    intent = parse_intent(instruction)

    # Stage 2: Build repo graph
    root = Path(repo_root) if repo_root else Path(".")
    repo_graph = build_repo_graph(root)

    # Stage 3: Ground the intent
    grounded = ground_intent(intent, repo_graph)

    return {
        "instruction": instruction,
        "intent_ir": intent.to_dict(),
        "grounded_intent": grounded.to_dict(),
        "plan": {
            "files_to_modify": grounded.edit_scope.files,
            "symbols_to_modify": grounded.edit_scope.symbols,
            "tests_to_run": grounded.edit_scope.tests,
            "docs_to_update": grounded.edit_scope.docs,
        },
        "dry_run": dry_run,
        "can_apply": grounded.confidence > 0.7 and not intent.ambiguities,
    }
