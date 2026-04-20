"""Compatibility module for organism imports.

This module re-exports AmosOrganism from AMOS_ORGANISM_OS for backward compatibility.
Tests and legacy code can import from here instead of the full path.
"""

try:
    from AMOS_ORGANISM_OS.organism import AmosOrganism
except ImportError:
    # Fallback to alternative location
    try:
        from amos_organism_runner import AmosOrganism
    except ImportError:
        raise ImportError("AmosOrganism not found. Ensure AMOS_ORGANISM_OS is in the path.")

__all__ = ["AmosOrganism"]
