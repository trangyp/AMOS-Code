"""Bridge connecting AMOS Brain to ClawSpring agent runtime."""
from __future__ import annotations

from typing import Any

from .integration import get_amos_integration


class AMOSAgentBridge:
    """
    Bridge that wraps clawspring agent with AMOS brain capabilities.

    Provides:
    - Brain-enhanced system prompts
    - Pre-processing with global laws
    - Reasoning engine integration
    """

    def __init__(self):
        self._amos = None
        self._state = None
        self._system_prompt = None

    @property
    def amos(self):
        """Lazy-load AMOS integration to prevent blocking during init."""
        if self._amos is None:
            self._amos = get_amos_integration()
        return self._amos

    def _ensure_clawspring_path(self) -> None:
        """Ensure clawspring package is in sys.path for imports."""
        import sys
        from pathlib import Path
        clawspring_path = str(Path(__file__).resolve().parent.parent / "clawspring")
        if clawspring_path not in sys.path:
            sys.path.insert(0, clawspring_path)

    def _get_state(self):
        """Lazy-load agent state."""
        if self._state is None:
            self._ensure_clawspring_path()
            from agent import AgentState
            self._state = AgentState()
        return self._state

    def _get_system_prompt(self) -> str:
        """Build system prompt enhanced with AMOS brain context."""
        if self._system_prompt is None:
            base_prompt = """You are an AI assistant with structured reasoning capabilities."""
            self._system_prompt = self.amos.enhance_system_prompt(base_prompt)
        return self._system_prompt

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
        self._ensure_clawspring_path()
        from agent import run as agent_run
        for event in agent_run(
            user_message=user_message,
            state=self._get_state(),
            config=config,
            system_prompt=self._get_system_prompt()
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
