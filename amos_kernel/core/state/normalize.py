"""State normalization - converts raw input to TensorState"""

from .types import TensorState


class UniversalStateModel:
    """Normalizes raw state into canonical tensor representation."""

    def normalize(self, raw: dict) -> TensorState:
        """Convert raw dict to TensorState with quadrant extraction."""
        return TensorState(
            biological=raw.get("biological", {}),
            cognitive=raw.get("cognitive", {}),
            system=raw.get("system", {}),
            environment=raw.get("environment", {}),
            metadata=raw.get("metadata", {}),
        )

    def validate_quadrants(self, state: TensorState) -> bool:
        """Check if state has at least one quadrant populated."""
        return any(
            [
                state.biological,
                state.cognitive,
                state.system,
                state.environment,
            ]
        )
