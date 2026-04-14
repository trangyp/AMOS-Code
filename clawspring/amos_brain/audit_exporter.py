"""AMOS Audit Data Exporter - Export cognitive audit data for analysis."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .cognitive_audit import AuditEntry, get_audit_trail
except ImportError:
    from cognitive_audit import get_audit_trail


class AuditExporter:
    """Export cognitive audit data in various formats."""

    def __init__(self):
        self.audit = get_audit_trail()

    def to_json(self, output_path: Optional[Path] = None) -> Path:
        """Export full audit history as JSON."""
        entries = self.audit.get_recent(1000)  # Last 1000 entries

        data = {
            "export_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_entries": len(entries),
                "format": "json",
            },
            "entries": [
                {
                    "timestamp": e.timestamp,
                    "task_hash": e.task_hash,
                    "task_preview": e.task_preview,
                    "domain": e.domain,
                    "risk_level": e.risk_level,
                    "engines_selected": e.engines_selected,
                    "consensus_score": e.consensus_score,
                    "laws_checked": e.laws_checked,
                    "violations_found": e.violations_found,
                    "execution_time_ms": e.execution_time_ms,
                    "recommendation": e.final_recommendation,
                }
                for e in entries
            ],
        }

        if output_path is None:
            output_path = Path(f"amos_audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path

    def to_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export audit history as CSV for spreadsheet analysis."""
        entries = self.audit.get_recent(1000)

        if output_path is None:
            output_path = Path(f"amos_audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "domain",
                    "risk_level",
                    "engines",
                    "consensus_score",
                    "violations",
                    "execution_ms",
                    "task_preview",
                ]
            )

            for e in entries:
                writer.writerow(
                    [
                        e.timestamp,
                        e.domain,
                        e.risk_level,
                        "|".join(e.engines_selected),
                        e.consensus_score or "",
                        len(e.violations_found),
                        e.execution_time_ms,
                        e.task_preview[:100],
                    ]
                )

        return output_path

    def to_markdown(self, output_path: Optional[Path] = None) -> Path:
        """Export human-readable markdown report."""
        report = self.audit.generate_report()

        if output_path is None:
            output_path = Path(f"amos_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

        with open(output_path, "w") as f:
            f.write(report)

        return output_path

    def get_summary_stats(self) -> dict:
        """Get summary statistics for quick overview."""
        stats = self.audit.get_statistics()
        entries = self.audit.get_recent(1000)

        # Calculate additional metrics
        domain_trends = {}
        for e in entries:
            day = e.timestamp[:10]  # YYYY-MM-DD
            if day not in domain_trends:
                domain_trends[day] = {}
            domain_trends[day][e.domain] = domain_trends[day].get(e.domain, 0) + 1

        # Engine usage frequency
        engine_usage = {}
        for e in entries:
            for engine in e.engines_selected:
                engine_usage[engine] = engine_usage.get(engine, 0) + 1

        return {
            **stats,
            "engine_usage": engine_usage,
            "daily_activity": domain_trends,
            "last_decision": entries[0].timestamp if entries else None,
        }

    def export_by_domain(self, domain: str, output_path: Optional[Path] = None) -> Path:
        """Export only entries for a specific domain."""
        entries = self.audit.get_by_domain(domain)

        if output_path is None:
            output_path = Path(f"amos_audit_{domain}_{datetime.now().strftime('%Y%m%d')}.json")

        data = {
            "export_metadata": {
                "timestamp": datetime.now().isoformat(),
                "domain_filter": domain,
                "total_entries": len(entries),
            },
            "entries": [
                {
                    "timestamp": e.timestamp,
                    "task_preview": e.task_preview,
                    "risk_level": e.risk_level,
                    "engines": e.engines_selected,
                    "consensus_score": e.consensus_score,
                    "violations": e.violations_found,
                }
                for e in entries
            ],
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path


def export_audit(format: str = "json", output_path: Optional[Path] = None) -> Path:
    """Convenience function to export audit data."""
    exporter = AuditExporter()

    if format == "json":
        return exporter.to_json(output_path)
    elif format == "csv":
        return exporter.to_csv(output_path)
    elif format == "markdown" or format == "md":
        return exporter.to_markdown(output_path)
    else:
        raise ValueError(f"Unknown format: {format}. Use json, csv, or markdown.")


if __name__ == "__main__":
    # Test export functionality
    print("=" * 60)
    print("AMOS Audit Exporter - Test")
    print("=" * 60)

    exporter = AuditExporter()

    # Show summary
    print("\n=== Summary Statistics ===")
    stats = exporter.get_summary_stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Violation rate: {stats['violation_rate']:.1%}")
    print(f"Engine usage: {stats.get('engine_usage', {})}")

    # Test exports
    print("\n=== Test Exports ===")

    json_path = exporter.to_json()
    print(f"JSON: {json_path}")

    csv_path = exporter.to_csv()
    print(f"CSV: {csv_path}")

    md_path = exporter.to_markdown()
    print(f"Markdown: {md_path}")

    # Cleanup test files
    json_path.unlink()
    csv_path.unlink()
    md_path.unlink()
    print("\nTest files cleaned up.")
