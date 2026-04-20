"""Drift detection - extracted from amos_brain/monitor.py"""

from .types import DriftItem, DriftReport


def detect_drift(checks: dict[str, bool]) -> DriftReport:
    """Detect drift from boolean health checks."""
    items = []
    for name, passed in checks.items():
        if not passed:
            items.append(DriftItem(code=name, message=f"{name} drift detected", severity="error"))
    return DriftReport(healthy=not items, items=items)


def detect_state_drift(previous: dict, current: dict, threshold: float = 0.1) -> DriftReport:
    """Detect drift between previous and current state."""
    items = []
    all_keys = set(previous.keys()) | set(current.keys())

    for key in all_keys:
        prev_val = previous.get(key, 0.0)
        curr_val = current.get(key, 0.0)

        if isinstance(prev_val, (int, float)) and isinstance(curr_val, (int, float)):
            diff = abs(curr_val - prev_val)
            if diff > threshold:
                items.append(
                    DriftItem(
                        code=f"state.{key}",
                        message=f"Value changed by {diff:.3f} (threshold: {threshold})",
                        severity="warn" if diff < threshold * 2 else "error",
                    )
                )

    return DriftReport(healthy=not items, items=items)
