"""Compatibility module for organism_bridge imports.

Provides integration between organism and brain components.
"""

from typing import Any


class OrganismBridge:
    """Bridge between organism and AMOS Brain."""

    def __init__(self, organism: Optional[Any] = None):
        """Initialize bridge with optional organism instance."""
        self.organism = organism
        self.status = "ready"

    def connect(self) -> bool:
        """Establish connection to organism."""
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current bridge status."""
        return {"connected": True, "status": self.status}


__all__ = ["OrganismBridge"]
