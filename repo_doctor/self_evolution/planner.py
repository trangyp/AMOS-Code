"""
Self-Patch Planner - Generates Smallest Canonical Mutation Set.

Takes evolution contracts and generates minimal patches to address
the identified structural weaknesses while preserving working behavior.

Planning Strategy:
1. Prefer editing canonical files over creating new ones
2. Merge duplicate logic rather than replicate it
3. Extract shared code to common modules
4. Narrow hot paths without changing cold paths
5. Strengthen contracts without breaking existing code
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contract import EvolutionContract


@dataclass
class PatchAction:
    """A single patch action to apply."""

    action_type: str  # "edit", "create", "merge", "extract", "delete"
    target_file: str
    description: str
    line_start: int | None = None
    line_end: int | None = None
    original_code: str | None = None
    replacement_code: str | None = None
    rationale: str = ""


class SelfPatchPlanner:
    """Plans minimal canonical patches for self-evolution."""

    def __init__(self, amos_root: str) -> None:
        """Initialize planner with AMOS root."""
        self.amos_root = Path(amos_root)

    def plan(self, contract: EvolutionContract) -> list[PatchAction]:
        """Generate patch actions for a contract."""
        patches: list[PatchAction] = []

        # Dispatch based on pattern type
        if "duplicate" in contract.problem_pattern.lower():
            patches.extend(self._plan_duplicate_unification(contract))
        elif "monolith" in contract.problem_pattern.lower():
            patches.extend(self._plan_monolith_split(contract))
        elif "literal" in contract.problem_pattern.lower():
            patches.extend(self._plan_literal_extraction(contract))
        elif "deferred" in contract.problem_pattern.lower():
            patches.extend(self._plan_deferred_work_resolution(contract))
        elif "cycle" in contract.problem_pattern.lower():
            patches.extend(self._plan_cycle_breaking(contract))
        else:
            # Generic patch - mark for manual review
            patches.append(
                PatchAction(
                    action_type="review",
                    target_file=contract.target_files[0],
                    description=f"Manual review needed: {contract.problem_pattern}",
                    rationale="No automatic patch available for this pattern",
                )
            )

        return patches

    def _plan_duplicate_unification(self, contract: EvolutionContract) -> list[PatchAction]:
        """Plan patches to unify duplicate code."""
        patches = []

        # Identify the shared module (use common base or create new)
        target_files = contract.target_files
        if not target_files:
            return patches

        # Find common directory
        common_dir = Path(target_files[0]).parent
        shared_module = common_dir / "_shared.py"

        # Plan: Extract common function to shared module
        patches.append(
            PatchAction(
                action_type="create",
                target_file=str(shared_module),
                description="Create shared module for duplicated code",
                replacement_code="# Auto-extracted shared code\n",
                rationale=f"Unify {len(target_files)} duplicate occurrences",
            )
        )

        # Plan: Update each file to import from shared
        for target_file in target_files[1:]:
            patches.append(
                PatchAction(
                    action_type="edit",
                    target_file=target_file,
                    description="Replace duplicate with import from shared",
                    original_code="# TODO: Extract duplicate code",
                    replacement_code=f"from {shared_module.stem} import shared_function",
                    rationale="Use unified version from shared module",
                )
            )

        return patches

    def _plan_monolith_split(self, contract: EvolutionContract) -> list[PatchAction]:
        """Plan patches to split oversized modules."""
        patches = []

        if not contract.target_files:
            return patches

        target_file = contract.target_files[0]
        target_path = Path(target_file)
        base_dir = target_path.parent
        base_name = target_path.stem

        # Plan: Create submodules directory
        submodules_dir = base_dir / f"{base_name}_modules"
        patches.append(
            PatchAction(
                action_type="create",
                target_file=str(submodules_dir / "__init__.py"),
                description=f"Create submodule package for {base_name}",
                replacement_code="# Split from monolithic module\n",
                rationale="Enable better organization by responsibility",
            )
        )

        # Plan: Mark original for gradual extraction
        patches.append(
            PatchAction(
                action_type="edit",
                target_file=target_file,
                description="Add extraction markers for gradual refactoring",
                line_start=1,
                replacement_code="# NOTE: This module is being split. "
                "New code should go in submodules.\n",
                rationale="Document the ongoing split",
            )
        )

        return patches

    def _plan_literal_extraction(self, contract: EvolutionContract) -> list[PatchAction]:
        """Plan patches to extract repeated literals to constants."""
        patches = []

        if not contract.target_files:
            return patches

        # For each file, plan to add constant at top
        for target_file in contract.target_files[:3]:  # Limit to first 3
            patches.append(
                PatchAction(
                    action_type="edit",
                    target_file=target_file,
                    description="Extract repeated literal to constant",
                    line_start=1,
                    replacement_code="# TODO: Add SHARED_CONSTANT here\n",
                    rationale="Eliminate magic string duplication",
                )
            )

        return patches

    def _plan_deferred_work_resolution(self, contract: EvolutionContract) -> list[PatchAction]:
        """Plan patches to address accumulated TODOs."""
        patches = []

        if not contract.target_files:
            return patches

        target_file = contract.target_files[0]

        # Plan: Add tracking issue reference
        patches.append(
            PatchAction(
                action_type="edit",
                target_file=target_file,
                description="Add evolution tracking for TODOs",
                line_start=1,
                replacement_code="# EVOLUTION: Address deferred work markers\n",
                rationale="File has accumulated TODOs requiring attention",
            )
        )

        return patches

    def _plan_cycle_breaking(self, contract: EvolutionContract) -> list[PatchAction]:
        """Plan patches to break import cycles."""
        patches = []

        if len(contract.target_files) < 2:
            return patches

        file1, file2 = contract.target_files[0], contract.target_files[1]

        # Plan: Extract shared code to third module
        shared_file = str(Path(file1).parent / "_shared_types.py")
        patches.append(
            PatchAction(
                action_type="create",
                target_file=shared_file,
                description="Create shared types module to break cycle",
                replacement_code="# Shared types to break import cycle\n",
                rationale="Both modules can import from here instead of each other",
            )
        )

        return patches

    def estimate_impact(self, patches: list[PatchAction]) -> dict[str, Any]:
        """Estimate impact of planned patches."""
        files_affected = len(set(p.target_file for p in patches))
        edit_count = sum(1 for p in patches if p.action_type == "edit")
        create_count = sum(1 for p in patches if p.action_type == "create")

        return {
            "files_affected": files_affected,
            "edit_actions": edit_count,
            "create_actions": create_count,
            "total_actions": len(patches),
            "risk_level": "low" if len(patches) < 5 else "medium" if len(patches) < 15 else "high",
        }
