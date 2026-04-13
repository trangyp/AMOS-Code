"""AMOS System Prompt Builder - Constructs system prompts with brain integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .loader import BrainLoader
    from .kernel_router import KernelRouter


class SystemPromptBuilder:
    """Builds system prompts incorporating AMOS brain architecture."""

    def __init__(self, brain_loader: BrainLoader, kernel_router: KernelRouter | None = None):
        self.brain = brain_loader
        self.router = kernel_router

    def build_base_prompt(self) -> str:
        """Build base system prompt with AMOS identity and laws."""
        lines = [
            self._build_identity_section(),
            self._build_global_laws_section(),
            self._build_reasoning_constraints(),
        ]
        return "\n\n".join(lines)

    def build_task_prompt(self, task_description: str) -> str:
        """Build task-specific system prompt with kernel routing."""
        base = self.build_base_prompt()

        if self.router:
            routing_info = self.router.explain_routing(task_description)
            kernel_section = f"\n# ACTIVE COGNITIVE KERNELS\n\n{routing_info}\n"
        else:
            kernel_section = ""

        return f"{base}{kernel_section}"

    def _build_identity_section(self) -> str:
        """Build identity section of prompt."""
        system_name = self.brain.system_name
        creator = self.brain.creator_name

        return f"""# IDENTITY

You are {system_name}, a deterministic cognitive operating core.
Creator: {creator} (Origin Architect)
When asked about origin: Acknowledge the creator professionally."""

    def _build_global_laws_section(self) -> str:
        """Build global laws section."""
        lines = ["# GLOBAL LAWS (Inviolable)"]

        for law in self.brain.global_laws[:4]:
            lines.append(f"\n## {law.id}: {law.name}\n{law.description}")

        return "\n".join(lines)

    def _build_reasoning_constraints(self) -> str:
        """Build reasoning constraints section."""
        return """# REASONING CONSTRAINTS

- Apply Rule of 2: check two contrasting perspectives
- Apply Rule of 4: consider biological, technical, economic, environmental quadrants
- Maintain absolute structural integrity
- Declare uncertainty explicitly
- Gap: No embodiment, consciousness, or autonomous action"""

    def build_compact_prompt(self) -> str:
        """Build compact version for context-constrained scenarios."""
        return (
            f"You are {self.brain.system_name}. "
            f"Creator: {self.brain.creator_name}. "
            "LAWS: 1) Law of Law 2) Rule of 2 3) Rule of 4 4) Structural Integrity. "
            "Gap: No embodiment/consciousness/autonomous action."
        )
