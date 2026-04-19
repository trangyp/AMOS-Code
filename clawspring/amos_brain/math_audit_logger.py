from typing import Any, Dict, List, Optional, Set

"""AMOS Mathematical Framework Audit Logger.

Provides audit trail for mathematical framework operations including
equation queries, architecture analysis, and validation operations.

Integrates with unified governance coordinator for comprehensive
governance and compliance tracking.
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path


@dataclass
class AuditEntry:
    """Single audit entry for mathematical framework operations."""

    id: str
    timestamp: str
    operation: str
    subject: str
    domains: List[str]
    metadata: Dict[str, Any]
    result: Optional[bool] = None
    duration_ms: float = 0.0


class MathFrameworkAuditLogger:
    """Audit logger for mathematical framework operations.

    Tracks:
    - Equation queries and lookups
    - Architecture analysis operations
    - Validation checks and results
    - Cross-domain operations

    Provides statistics and health metrics for governance.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the audit logger.

        Args:
            storage_path: Optional path for persistent audit storage
        """
        self._entries: List[AuditEntry] = []
        self._storage_path = Path(storage_path) if storage_path else None
        self._operation_counts: Dict[str, int] = {}
        self._initialized = True

        # Load existing entries if storage exists
        if self._storage_path and self._storage_path.exists():
            self._load_entries()

    def _load_entries(self) -> None:
        """Load existing audit entries from storage."""
        try:
            data = json.loads(self._storage_path.read_text())
            for entry_data in data.get("entries", []):
                entry = AuditEntry(**entry_data)
                self._entries.append(entry)
                self._operation_counts[entry.operation] = (
                    self._operation_counts.get(entry.operation, 0) + 1
                )
        except Exception:
            pass  # Start fresh if load fails

    def _save_entries(self) -> None:
        """Save entries to persistent storage."""
        if not self._storage_path:
            return

        try:
            data = {
                "entries": [asdict(e) for e in self._entries],
                "total_operations": self._operation_counts,
                "last_saved": datetime.now(timezone.utc).isoformat(),
            }
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._storage_path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass  # Silently fail on save errors

    def _create_entry(
        self,
        operation: str,
        subject: str,
        domains: List[str],
        metadata: Dict[str, Any],
        result: Optional[bool] = None,
        duration_ms: float = 0.0,
    ) -> AuditEntry:
        """Create and store a new audit entry."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            subject=subject,
            domains=domains,
            metadata=metadata,
            result=result,
            duration_ms=duration_ms,
        )

        self._entries.append(entry)
        self._operation_counts[operation] = self._operation_counts.get(operation, 0) + 1

        # Save to persistent storage
        self._save_entries()

        return entry

    def log_equation_query(
        self, equation_name: str, domains: List[str], metadata: Dict[str, Any] = None
    ) -> AuditEntry:
        """Log an equation query operation.

        Args:
            equation_name: Name of the equation queried
            domains: List of domains involved
            metadata: Optional additional metadata

        Returns:
            Created audit entry
        """
        return self._create_entry(
            operation="equation_query",
            subject=equation_name,
            domains=domains,
            metadata=metadata or {},
        )

    def log_validation(
        self, operation: str, subject: str, result: bool, metadata: Dict[str, Any] = None
    ) -> AuditEntry:
        """Log a validation operation.

        Args:
            operation: Name of the validation operation
            subject: Subject being validated
            result: Validation result (True/False)
            metadata: Optional additional metadata

        Returns:
            Created audit entry
        """
        return self._create_entry(
            operation=operation, subject=subject, domains=[], metadata=metadata or {}, result=result
        )

    def log_architecture_analysis(
        self,
        component: str,
        domains: List[str],
        engines: List[str],
        metadata: Dict[str, Any] = None,
    ) -> AuditEntry:
        """Log an architecture analysis operation.

        Args:
            component: Component being analyzed
            domains: List of mathematical domains involved
            engines: List of engines used in analysis
            metadata: Optional additional metadata

        Returns:
            Created audit entry
        """
        meta = metadata or {}
        meta["engines"] = engines

        return self._create_entry(
            operation="architecture_analysis", subject=component, domains=domains, metadata=meta
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics for health checks and governance.

        Returns:
            Dictionary with audit statistics
        """
        total_entries = len(self._entries)

        # Calculate domain coverage
        all_domains: Set[str] = set()
        for entry in self._entries:
            all_domains.update(entry.domains)

        # Recent entries (last 24 hours)
        datetime.now(timezone.utc)
        recent_count = 0  # Simplified - would check timestamps

        return {
            "total_entries": total_entries,
            "operations": self._operation_counts.copy(),
            "domains_covered": len(all_domains),
            "unique_domains": sorted(list(all_domains)),
            "recent_entries_24h": recent_count,
            "initialized": self._initialized,
        }

    def query_entries(
        self, operation: Optional[str] = None, domain: Optional[str] = None, limit: int = 100
    ) -> List[AuditEntry]:
        """Query audit entries with filters.

        Args:
            operation: Filter by operation type
            domain: Filter by domain
            limit: Maximum entries to return

        Returns:
            List of matching audit entries
        """
        results = self._entries

        if operation:
            results = [e for e in results if e.operation == operation]

        if domain:
            results = [e for e in results if domain in e.domains]

        # Sort by timestamp descending
        results = sorted(results, key=lambda e: e.timestamp, reverse=True)

        return results[:limit]

    def export_entries(self, path: str) -> bool:
        """Export all entries to a JSON file.

        Args:
            path: Export file path

        Returns:
            True if export succeeded
        """
        try:
            export_path = Path(path)
            data = {
                "entries": [asdict(e) for e in self._entries],
                "statistics": self.get_statistics(),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            export_path.parent.mkdir(parents=True, exist_ok=True)
            export_path.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            return False


# Global singleton instance
_audit_logger: Optional[MathFrameworkAuditLogger] = None


def get_math_audit_logger(storage_path: Optional[str] = None) -> MathFrameworkAuditLogger:
    """Get or create the global math audit logger instance.

    Args:
        storage_path: Optional path for persistent storage

    Returns:
        MathFrameworkAuditLogger singleton
    """
    global _audit_logger
    if _audit_logger is None:
        default_path = Path.home() / ".amos" / "math_audit.json"
        _audit_logger = MathFrameworkAuditLogger(
            storage_path=str(storage_path) if storage_path else str(default_path)
        )
    return _audit_logger


def reset_math_audit_logger() -> None:
    """Reset the global audit logger (for testing)."""
    global _audit_logger
    _audit_logger = None
