"""Bridge connecting AMOS Brain to ClawSpring agent runtime."""
from __future__ import annotations

from typing import Any

from .integration import get_amos_integration


class AMOSAgentBridge:
    """
    Bridge that wraps clawspring agent with AMOS brain capabilities.

    Provides:
    - Brain-enhanced system prompts
    - Pre/post processing with global laws
    - Reasoning engine integration
    """

    def __init__(self):
        self.amos = get_amos_integration()
        # Lazy import to avoid circular deps and syntax errors
        import sys
        sys.path.insert(0, '/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/clawspring')
        from agent import AgentState
        self.state = AgentState()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build system prompt enhanced with AMOS brain context."""
        base_prompt = """You are an AI assistant with structured reasoning capabilities."""
        return self.amos.enhance_system_prompt(base_prompt)

    def run_with_brain(self, user_message: str, config: dict[str, Any]) -> Any:
        """
        Run agent with AMOS brain pre/post processing.

        Args:
            user_message: User's input message
            config: Agent configuration (model, etc.)

        Yields:
            Agent events with brain-enhanced context
        """
        # Pre-process through brain
        pre_result = self.amos.pre_process(user_message)

        if pre_result.get("blocked"):
            yield {
                "type": "brain_block",
                "reason": pre_result.get("reason"),
                "law": pre_result.get("law")
            }
            return

        # Run through clawspring agent (lazy import)
        from agent import run as agent_run
        for event in agent_run(
            user_message=user_message,
            state=self.state,
            config=config,
            system_prompt=self.system_prompt
        ):
            yield event

    def analyze_problem(self, problem: str) -> dict[str, Any]:
        """Analyze a problem using AMOS reasoning engine."""
        return self.amos.analyze_with_rules(problem)

    def get_brain_status(self) -> dict[str, Any]:
        """Get current brain integration status."""
        return self.amos.get_status()


def create_amos_agent() -> AMOSAgentBridge:
    """Factory function to create AMOS-enhanced agent."""
    return AMOSAgentBridge()
