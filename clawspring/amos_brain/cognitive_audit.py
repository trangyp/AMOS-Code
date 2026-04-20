"""Cognitive audit trail for AMOS brain."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

UTC = timezone.utc


@dataclass
class AuditEntry:
    """Single audit entry."""

    decision: str
    context: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CognitiveAuditTrail:
    """Trail of cognitive decisions."""

    entries: list[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        """Add entry to trail."""
        self.entries.append(entry)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entries": [
                {"decision": e.decision, "context": e.context, "timestamp": e.timestamp}
                for e in self.entries
            ]
        }


def record_cognitive_decision(
    decision: str, context: dict[str, Any], trail: Optional[CognitiveAuditTrail] = None
) -> AuditEntry:
    """Record a cognitive decision."""
    entry = AuditEntry(decision=decision, context=context)
    if trail:
        trail.add(entry)
    return entry


# Global audit trail instance
_global_audit_trail: Optional[CognitiveAuditTrail] = None


def get_audit_trail() -> CognitiveAuditTrail:
    """Get global audit trail instance."""
    global _global_audit_trail
    if _global_audit_trail is None:
        _global_audit_trail = CognitiveAuditTrail()
    return _global_audit_trail


def get_statistics() -> dict[str, Any]:
    """Get audit statistics."""
    trail = get_audit_trail()
    return {
        "total_entries": len(trail.entries),
        "recent": trail.entries[-10:] if trail.entries else [],
    }
