"""Contract mismatch detection - extracted from amos_brain/doctor.py"""

from .types import DriftItem, DriftReport


def detect_contract_mismatch(contract: dict, observed: dict) -> DriftReport:
    """Detect mismatches between contract and observed state."""
    items = []
    for key, expected in contract.items():
        actual = observed.get(key)
        if actual != expected:
            items.append(
                DriftItem(
                    code=f"contract.{key}",
                    message=f"expected={expected!r} actual={actual!r}",
                    severity="fatal",
                )
            )
    return DriftReport(healthy=not items, items=items)


def detect_missing_fields(required: set[str], observed: dict) -> DriftReport:
    """Detect missing required fields."""
    items = []
    missing = required - set(observed.keys())
    for field in missing:
        items.append(
            DriftItem(
                code=f"missing.{field}",
                message=f"Required field '{field}' not found",
                severity="fatal",
            )
        )
    return DriftReport(healthy=not items, items=items)
