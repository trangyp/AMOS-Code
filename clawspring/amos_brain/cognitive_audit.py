"""AMOS Cognitive Audit Trail - Track reasoning and execution history."""

import json
import time
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AuditEntry:
    """Single cognitive decision audit record."""
    timestamp: str
    task_hash: str
    task_preview: str
    domain: str
    risk_level: str
    engines_selected: List[str]
    consensus_score: Optional[float]
    laws_checked: List[str]
    violations_found: List[str]
    execution_time_ms: float
    final_recommendation: str


class CognitiveAuditTrail:
    """Records and queries cognitive decision history."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(".amos_cognitive_audit.jsonl")
        self._session_entries: List[AuditEntry] = []
        self._load_history()

    def _load_history(self):
        """Load previous audit history if exists."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self._session_entries.append(AuditEntry(**data))
            except Exception:
                pass  # Start fresh if corrupted

    def record(
        self,
        task: str,
        domain: str,
        risk_level: str,
        engines: List[str],
        consensus_score: Optional[float],
        laws: List[str],
        violations: List[str],
        exec_time_ms: float,
        recommendation: str
    ) -> AuditEntry:
        """Record a cognitive decision to the audit trail."""
        # Create task hash for deduplication
        task_hash = hashlib.sha256(task.encode()).hexdigest()[:16]
        task_preview = task[:100] + "..." if len(task) > 100 else task

        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            task_hash=task_hash,
            task_preview=task_preview,
            domain=domain,
            risk_level=risk_level,
            engines_selected=engines,
            consensus_score=consensus_score,
            laws_checked=laws,
            violations_found=violations,
            execution_time_ms=exec_time_ms,
            final_recommendation=recommendation
        )

        self._session_entries.append(entry)
        self._persist_entry(entry)
        return entry

    def _persist_entry(self, entry: AuditEntry):
        """Append entry to persistent storage."""
        try:
            with open(self.storage_path, 'a') as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        except Exception:
            pass  # Silent fail for audit non-critical path

    def get_recent(self, n: int = 10) -> List[AuditEntry]:
        """Get N most recent audit entries."""
        return sorted(
            self._session_entries,
            key=lambda x: x.timestamp,
            reverse=True
        )[:n]

    def get_by_domain(self, domain: str) -> List[AuditEntry]:
        """Get all entries for a specific domain."""
        return [e for e in self._session_entries if e.domain == domain]

    def get_violations(self) -> List[AuditEntry]:
        """Get entries with law violations."""
        return [e for e in self._session_entries if e.violations_found]

    def get_statistics(self) -> Dict[str, Any]:
        """Generate audit statistics."""
        if not self._session_entries:
            return {"total": 0}

        total = len(self._session_entries)
        domains = {}
        risk_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        violation_count = 0
        total_exec_time = 0.0

        for entry in self._session_entries:
            domains[entry.domain] = domains.get(entry.domain, 0) + 1
            risk_dist[entry.risk_level] = risk_dist.get(entry.risk_level, 0) + 1
            if entry.violations_found:
                violation_count += 1
            total_exec_time += entry.execution_time_ms

        return {
            "total_entries": total,
            "domains": domains,
            "risk_distribution": risk_dist,
            "violation_rate": violation_count / total,
            "avg_execution_time_ms": total_exec_time / total,
            "entries_with_consensus": sum(
                1 for e in self._session_entries if e.consensus_score is not None
            ),
        }

    def find_similar(self, task: str, threshold: float = 0.7) -> List[AuditEntry]:
        """Find audit entries with similar tasks (simple keyword match)."""
        task_words = set(task.lower().split())
        matches = []

        for entry in self._session_entries:
            entry_words = set(entry.task_preview.lower().split())
            if not task_words or not entry_words:
                continue
            overlap = len(task_words & entry_words) / len(task_words | entry_words)
            if overlap >= threshold:
                matches.append((overlap, entry))

        matches.sort(reverse=True)
        return [m[1] for m in matches[:5]]

    def generate_report(self) -> str:
        """Generate human-readable audit report."""
        stats = self.get_statistics()
        recent = self.get_recent(5)

        lines = [
            "# AMOS Cognitive Audit Report",
            f"Generated: {datetime.now().isoformat()}",
            f"Storage: {self.storage_path}",
            "",
            "## Statistics",
            f"- Total decisions: {stats.get('total_entries', 0)}",
            f"- Violation rate: {stats.get('violation_rate', 0):.1%}",
            f"- Avg execution: {stats.get('avg_execution_time_ms', 0):.1f}ms",
            f"- Consensus entries: {stats.get('entries_with_consensus', 0)}",
        ]

        if stats.get('domains'):
            lines.extend(["", "### Domain Distribution"])
            for domain, count in sorted(stats['domains'].items(), key=lambda x: -x[1]):
                lines.append(f"- {domain}: {count}")

        if recent:
            lines.extend(["", "## Recent Decisions"])
            for entry in recent:
                lines.extend([
                    f"\n**{entry.timestamp[:19]}** | {entry.domain} | {entry.risk_level}",
                    f"Task: {entry.task_preview[:60]}...",
                    f"Engines: {', '.join(entry.engines_selected[:2])}",
                ])
                if entry.violations_found:
                    lines.append(f"⚠️ Violations: {len(entry.violations_found)}")

        violations = self.get_violations()
        if violations:
            lines.extend(["", "## Law Violations (All Time)", f"Count: {len(violations)}"])
            for v in violations[:3]:
                lines.append(f"- {v.timestamp[:19]}: {', '.join(v.violations_found[:2])}")

        return "\n".join(lines)

    def clear_history(self):
        """Clear all audit history."""
        self._session_entries = []
        if self.storage_path.exists():
            self.storage_path.unlink()


# Singleton instance
_audit_trail: Optional[CognitiveAuditTrail] = None


def get_audit_trail() -> CognitiveAuditTrail:
    """Get or create the singleton audit trail."""
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = CognitiveAuditTrail()
    return _audit_trail


def record_cognitive_decision(
    task: str,
    domain: str,
    risk_level: str,
    engines: List[str],
    consensus_score: Optional[float] = None,
    laws: Optional[List[str]] = None,
    violations: Optional[List[str]] = None,
    exec_time_ms: float = 0.0,
    recommendation: str = ""
) -> AuditEntry:
    """Convenience function to record a decision."""
    trail = get_audit_trail()
    return trail.record(
        task=task,
        domain=domain,
        risk_level=risk_level,
        engines=engines,
        consensus_score=consensus_score,
        laws=laws or [],
        violations=violations or [],
        exec_time_ms=exec_time_ms,
        recommendation=recommendation
    )


if __name__ == "__main__":
    # Test the audit trail
    print("=" * 60)
    print("AMOS Cognitive Audit Trail - Test")
    print("=" * 60)

    audit = get_audit_trail()

    # Record some test entries
    record_cognitive_decision(
        task="Design a secure authentication system",
        domain="security",
        risk_level="high",
        engines=["AMOS_Strategy_Game_Engine", "AMOS_Deterministic_Logic_And_Law_Engine"],
        consensus_score=0.85,
        laws=["RULE_OF_2", "RULE_OF_4"],
        violations=[],
        exec_time_ms=12.5,
        recommendation="Proceed with multi-agent review"
    )

    record_cognitive_decision(
        task="Refactor this function",
        domain="software",
        risk_level="low",
        engines=["AMOS_Engineering_And_Mathematics_Engine"],
        consensus_score=None,
        laws=["RULE_OF_2"],
        violations=[],
        exec_time_ms=3.2,
        recommendation="Proceed with single engine"
    )

    print("\n" + audit.generate_report())
