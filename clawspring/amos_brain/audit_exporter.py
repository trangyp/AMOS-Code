"""Audit exporter for AMOS brain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc


@dataclass
class AuditExporter:
    """Export cognitive audit trails."""

    name: str = "default"

    def export(self, audit_data: dict[str, Any]) -> dict[str, Any]:
        """Export audit data."""
        return {
            "exported": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": audit_data,
        }


def export_audit(
    audit_data: dict[str, Any], exporter: AuditExporter | None = None
) -> dict[str, Any]:
    """Export audit using default or provided exporter."""
    if exporter is None:
        exporter = AuditExporter()
    return exporter.export(audit_data)
