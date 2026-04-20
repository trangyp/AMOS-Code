"""State projection - weighted quadrant aggregation"""

from .types import TensorState


def project(state: TensorState, weights: dict[str, float]) -> dict[str, float]:
    """Project tensor state onto weighted quadrants."""
    return {
        "biological": sum(state.biological.values()) * weights.get("biological", 1.0),
        "cognitive": sum(state.cognitive.values()) * weights.get("cognitive", 1.0),
        "system": sum(state.system.values()) * weights.get("system", 1.0),
        "environment": sum(state.environment.values()) * weights.get("environment", 1.0),
    }


def extract_load_capacity(state: TensorState) -> tuple[float, float]:
    """Extract load and capacity from biological quadrant."""
    load = state.biological.get("load", 0.0)
    capacity = state.biological.get("capacity", 1.0)
    return load, capacity


def load_capacity_ratio(state: TensorState) -> float:
    """Calculate load/capacity ratio. Returns inf if capacity is 0."""
    load, capacity = extract_load_capacity(state)
    if capacity <= 0:
        return float("inf")
    return load / capacity
