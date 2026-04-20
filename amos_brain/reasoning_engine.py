"""Reasoning Engine - Structured reasoning for brain operations.

Provides reasoning capabilities for the AMOS brain with step-by-step
explanation generation.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timezone

UTC = UTC
from .facade import BrainClient


@dataclass
class ReasoningResult:
    """Result of reasoning process."""

    conclusion: str
    steps: list[str]
    confidence: str
    domain: str
    timestamp: str


class ReasoningEngine:
    """Structured reasoning engine."""

    def __init__(self) -> None:
        self._client: Optional[BrainClient] = None

    def initialize(self) -> None:
        """Initialize the reasoning engine."""
        if self._client is None:
            self._client = BrainClient()

    def reason(self, query: str, domain: str = "general") -> ReasoningResult:
        """Perform structured reasoning.

        Args:
            query: The query to reason about
            domain: Domain for reasoning

        Returns:
            ReasoningResult with conclusion and steps
        """
        self.initialize()

        if self._client is None:
            return ReasoningResult(
                conclusion="Engine not initialized",
                steps=["Initialization failed"],
                confidence="low",
                domain=domain,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        try:
            # Get reasoning from brain
            response = self._client.think(f"Reason step by step: {query}", domain=domain)

            # Extract reasoning steps if available
            steps = []
            if response.reasoning:
                if isinstance(response.reasoning, list):
                    steps = [str(s) for s in response.reasoning]
                else:
                    steps = [str(response.reasoning)]
            else:
                steps = ["Reasoning not available"]

            return ReasoningResult(
                conclusion=response.content,
                steps=steps,
                confidence=response.confidence,
                domain=domain,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            return ReasoningResult(
                conclusion=str(e),
                steps=[f"Error: {type(e).__name__}"],
                confidence="low",
                domain=domain,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )


# Global engine instance
_reasoning_engine: Optional[ReasoningEngine] = None


def get_reasoning_engine() -> ReasoningEngine:
    """Get or create global reasoning engine."""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
