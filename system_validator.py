"""Compatibility module for system_validator imports.

Re-exports SystemValidator from clawspring/amos_brain.
"""

try:
    from clawspring.amos_brain.system_validator import (
        SystemValidator,
        ValidationResult,
    )
except ImportError:
    raise ImportError(
        "SystemValidator not found. Ensure clawspring/amos_brain is available."
    ) from None

__all__ = ["SystemValidator", "ValidationResult"]
