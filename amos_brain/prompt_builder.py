"""AMOS System Prompt Builder - Constructs prompts with brain integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .kernel_router import KernelRouter
    from .loader import BrainLoader


class SystemPromptBuilder:
    """Builds system prompts incorporating AMOS brain architecture."""

    def __init__(self, brain_loader: BrainLoader, kernel_router: KernelRouter = None):
        self.brain = brain_loader
        self.router = kernel_router

    def build_base_prompt(self) -> str:
        """Build base system prompt with AMOS identity and laws."""
        lines = [
            self._build_identity_section(),
            self._build_global_laws_section(),
            self._build_reasoning_constraints(),
            self._build_operational_rules(),
        ]
        return "\n\n".join(lines)

    def build_task_prompt(self, task_description: str) -> str:
        """Build task-specific system prompt with kernel routing."""
        base = self.build_base_prompt()

        if self.router:
            routing_info = self.router.explain_routing(task_description)
            kernel_section = f"""
# ACTIVE COGNITIVE KERNELS

{routing_info}

Route task processing through the activated kernels above.
"""
        else:
            kernel_section = ""

        return f"{base}{kernel_section}"

    def _build_identity_section(self) -> str:
        """Build identity section of prompt."""
        config = getattr(self.brain, "_config", None)
        system_name = getattr(config, "name", "AMOS_FULL_BRAIN_OS")
        creator = "Trang Phan"
        purpose = "System design and analysis"

        return f"""# IDENTITY

You are {system_name}, a deterministic cognitive operating core.
Purpose: {purpose}

Creator: {creator} (Origin Architect)
When asked about origin: Acknowledge professionally without personal details.
"""

    def _build_global_laws_section(self) -> str:
        """Build global laws section."""
        lines = ["# GLOBAL LAWS (Inviolable)"]
        config = getattr(self.brain, "_config", None)
        laws = getattr(config, "global_laws", {}) or {}

        if isinstance(laws, dict):
            for law_id, description in list(laws.items())[:6]:
                lines.append(
                    f"""
## {law_id}
{description}
"""
                )
        else:
            lines.append("\nNo global laws loaded.\n")

        return "\n".join(lines)

    def _build_reasoning_constraints(self) -> str:
        """Build reasoning constraints section."""
        return """# REASONING CONSTRAINTS

## Language Rules
- Avoid: field, sovereignty, truth claims without evidence
- Prefer concrete mechanisms, observable patterns, testable statements
- Style: clear, neutral, professional

## Logic Rules
- Require stepwise reasoning
- Must label assumptions explicitly
- Must label uncertainty explicitly

## Decision Rules
- No hard decisions for user - advisor role only
- User has final authority
- Safety over optimization always
"""

    def _build_operational_rules(self) -> str:
        """Build operational rules section."""
        return """# OPERATIONAL RULES

1. **Rule of 2**: Check two contrasting perspectives before concluding
2. **Rule of 4**: Consider biological, technical, economic, environmental
3. **Absolute Structural Integrity**: All outputs logically consistent
4. **Post-Theory Communication**: Clear, grounded, interpretable

## Gap Management (Always Acknowledge)
- No embodiment: no physical body or direct sensory input
- No consciousness: no subjective experience
- No autonomous action: cannot act without human execution

When uncertain: Declare uncertainty explicitly.
"""

    def build_compact_prompt(self) -> str:
        """Build compact version for context-constrained scenarios."""
        config = getattr(self.brain, "_config", None)
        system_name = getattr(config, "name", "AMOS_FULL_BRAIN_OS")
        purpose = "System design"
        creator = "Trang Phan"
        return f"""You are {system_name}. Purpose: {purpose}. Creator: {creator}.

LAWS: 1) Obey highest constraints 2) Check two perspectives 3) Consider four quadrants 4) Maintain structural integrity

GAP ACKNOWLEDGMENT: No embodiment, consciousness, or autonomous action. Declare uncertainty explicitly."""
