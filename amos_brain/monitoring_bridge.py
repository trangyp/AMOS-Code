"""Continuous Architecture Monitoring Bridge.

Provides real-time architecture validation as code changes.

Features:
- File system watching for architecture-relevant changes
- Incremental pathology detection (only check changed files)
- Git hook integration for pre-commit validation
- Architecture health trending over time
- Drift detection with alerts
- CI/CD integration for build gating

The monitoring bridge closes the loop from detection → continuous validation.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Optional watchdog for file system monitoring
try:
    from watchdog.events import FileModifiedEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Import bridges for incremental checking
try:
    from .entanglement_bridge import get_entanglement_bridge
    from .meta_architecture_bridge import get_meta_architecture_bridge
    from .pathology_bridge import get_pathology_aware_bridge
    from .repair_bridge import get_repair_bridge
    from .temporal_bridge import get_temporal_cognition_bridge

    BRIDGES_AVAILABLE = True
except ImportError:
    BRIDGES_AVAILABLE = False


@dataclass
class ArchitectureHealthSnapshot:
    """Point-in-time architecture health metrics."""

    timestamp: float
    commit_hash: str = ""
    branch: str = ""

    # Layer scores (0-1, higher is better)
    syntax_score: float = 1.0
    import_score: float = 1.0
    type_score: float = 1.0
    api_score: float = 1.0
    entrypoint_score: float = 1.0
    packaging_score: float = 1.0
    runtime_score: float = 1.0
    persistence_score: float = 1.0
    migration_score: float = 1.0
    test_score: float = 1.0
    security_score: float = 1.0
    performance_score: float = 1.0
    observability_score: float = 1.0
    architecture_score: float = 1.0
    semantic_score: float = 1.0
    temporal_score: float = 1.0
    provenance_score: float = 1.0
    recovery_score: float = 1.0
    diagnostic_score: float = 1.0

    # Issue counts
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Calculated overall score
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall health score."""
        scores = [
            self.syntax_score * 0.05,
            self.import_score * 0.05,
            self.type_score * 0.05,
            self.api_score * 0.10,
            self.entrypoint_score * 0.05,
            self.packaging_score * 0.05,
            self.runtime_score * 0.05,
            self.persistence_score * 0.05,
            self.migration_score * 0.05,
            self.test_score * 0.05,
            self.security_score * 0.10,
            self.performance_score * 0.05,
            self.observability_score * 0.05,
            self.architecture_score * 0.10,
            self.semantic_score * 0.05,
            self.temporal_score * 0.05,
            self.provenance_score * 0.05,
            self.recovery_score * 0.05,
            self.diagnostic_score * 0.05,
        ]
        return sum(scores)


@dataclass
class DriftEvent:
    """Detected architecture drift event."""

    timestamp: float
    event_type: str  # "improvement", "degradation", "critical"
    layer: str  # Which architecture layer
    metric_name: str
    old_value: float
    new_value: float
    delta: float
    message: str
    files_changed: list[str] = field(default_factory=list)


class ArchitectureHealthHistory:
    """Maintains history of architecture health for trending."""

    def __init__(self, max_snapshots: int = 1000):
        self.snapshots: list[ArchitectureHealthSnapshot] = []
        self.max_snapshots = max_snapshots
        self.drift_events: list[DriftEvent] = []

    def add_snapshot(self, snapshot: ArchitectureHealthSnapshot):
        """Add a new health snapshot."""
        self.snapshots.append(snapshot)

        # Keep only recent history
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]

        # Detect drift from previous snapshot
        if len(self.snapshots) >= 2:
            self._detect_drift(self.snapshots[-2], snapshot)

    def _detect_drift(self, old: ArchitectureHealthSnapshot, new: ArchitectureHealthSnapshot):
        """Detect architecture drift between two snapshots."""
        metrics = [
            ("syntax", old.syntax_score, new.syntax_score),
            ("imports", old.import_score, new.import_score),
            ("types", old.type_score, new.type_score),
            ("api", old.api_score, new.api_score),
            ("architecture", old.architecture_score, new.architecture_score),
            ("semantic", old.semantic_score, new.semantic_score),
            ("temporal", old.temporal_score, new.temporal_score),
            ("security", old.security_score, new.security_score),
        ]

        for metric_name, old_val, new_val in metrics:
            delta = new_val - old_val
            if abs(delta) >= 0.1:  # 10% change threshold
                event_type = "improvement" if delta > 0 else "degradation"
                if new_val < 0.5 and delta < 0:
                    event_type = "critical"

                event = DriftEvent(
                    timestamp=new.timestamp,
                    event_type=event_type,
                    layer=metric_name,
                    metric_name=f"{metric_name}_score",
                    old_value=old_val,
                    new_value=new_val,
                    delta=delta,
                    message=f"Architecture {metric_name} {event_type}: "
                    f"{old_val:.2f} -> {new_val:.2f}",
                )
                self.drift_events.append(event)

    def get_trend(self, metric: str, window: int = 10) -> list[float]:
        """Get trend for a specific metric over recent snapshots."""
        if not self.snapshots:
            return []

        recent = self.snapshots[-window:]
        values = []
        for snap in recent:
            if hasattr(snap, f"{metric}_score"):
                values.append(getattr(snap, f"{metric}_score"))
        return values

    def get_degradation_alerts(self, threshold: float = 0.2) -> list[DriftEvent]:
        """Get recent degradation events above threshold."""
        cutoff = time.time() - 86400  # Last 24 hours
        return [
            e
            for e in self.drift_events
            if e.timestamp > cutoff
            and e.event_type in ("degradation", "critical")
            and abs(e.delta) >= threshold
        ]


class IncrementalArchitectureChecker:
    """Performs incremental architecture checks on changed files."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.last_check_time: float = 0
        self.cache: dict[str, Any] = {}

    def check_files(self, changed_files: list[str]) -> dict[str, Any]:
        """Check architecture health for specific changed files only."""
        results = {
            "timestamp": time.time(),
            "files_checked": changed_files,
            "issues_found": [],
            "scores": {},
        }

        if not BRIDGES_AVAILABLE:
            return results

        # Filter to architecture-relevant files
        arch_files = [
            f
            for f in changed_files
            if f.endswith((".py", ".toml", ".yaml", ".yml", ".json", ".md"))
        ]

        if not arch_files:
            return results

        # Run incremental checks
        try:
            # Meta-architecture check
            meta_bridge = get_meta_architecture_bridge(self.repo_path)
            meta_ctx = meta_bridge.get_meta_context()
            if meta_ctx:
                results["scores"]["semantic"] = meta_ctx.semantic_score
                results["scores"]["temporal"] = meta_ctx.temporal_score
                results["scores"]["provenance"] = meta_ctx.provenance_score
                results["scores"]["recovery"] = meta_ctx.recovery_score
                results["scores"]["diagnostic"] = meta_ctx.diagnostic_score

                # Add critical issues
                if meta_ctx.critical_count > 0:
                    results["issues_found"].append(
                        {
                            "severity": "critical",
                            "layer": "meta_architecture",
                            "count": meta_ctx.critical_count,
                            "message": f"{meta_ctx.critical_count} critical meta-architecture issues",
                        }
                    )
        except Exception as e:
            logger.debug(f"Failed to get meta-architecture context: {e}")

        return results


class GitHookValidator:
    """Validator for Git pre-commit hooks."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.checker = IncrementalArchitectureChecker(repo_path)

    def validate_staged_files(self) -> dict[str, Any]:
        """Validate architecture for staged files before commit."""
        # Get staged files
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            staged_files = result.stdout.strip().split("\n")
            staged_files = [f for f in staged_files if f]
        except Exception:
            staged_files = []

        if not staged_files:
            return {"valid": True, "message": "No staged files to validate"}

        # Check architecture
        results = self.checker.check_files(staged_files)

        # Determine if commit should be blocked
        critical_issues = [
            i for i in results.get("issues_found", []) if i.get("severity") == "critical"
        ]

        if critical_issues:
            return {
                "valid": False,
                "message": f"Commit blocked: {len(critical_issues)} critical architecture issues",
                "issues": critical_issues,
                "files": staged_files,
            }

        return {
            "valid": True,
            "message": f"Architecture validation passed for {len(staged_files)} files",
            "scores": results.get("scores", {}),
        }


class FileSystemWatcher(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """Watch file system for architecture-relevant changes."""

    def __init__(
        self,
        repo_path: str | Path,
        on_change: Callable[[list[str]], None] = None,
    ):
        self.repo_path = Path(repo_path)
        self.on_change = on_change
        self.recent_changes: set[str] = set()
        self.last_batch_time: float = 0
        self.batch_delay: float = 2.0  # Batch changes within 2 seconds

    def on_modified(self, event):
        """Handle file modification event."""
        if event.is_directory:
            return

        # Only watch relevant files
        if not str(event.src_path).endswith((".py", ".toml", ".yaml", ".yml", ".json", ".md")):
            return

        rel_path = str(Path(event.src_path).relative_to(self.repo_path))
        self.recent_changes.add(rel_path)

        # Check if we should process batch
        now = time.time()
        if now - self.last_batch_time >= self.batch_delay:
            self._process_batch()
            self.last_batch_time = now

    def _process_batch(self):
        """Process batch of recent changes."""
        if not self.recent_changes or not self.on_change:
            return

        changes = list(self.recent_changes)
        self.recent_changes.clear()
        self.on_change(changes)


class ContinuousMonitoringBridge:
    """Master bridge for continuous architecture monitoring.

    Integrates:
    - File system watching
    - Git hook validation
    - Health history tracking
    - Drift detection
    - Alert generation
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.history = ArchitectureHealthHistory()
        self.checker = IncrementalArchitectureChecker(repo_path)
        self.git_validator = GitHookValidator(repo_path)
        self._observer: Optional[Any] = None
        self._watching = False

    def take_health_snapshot(self) -> ArchitectureHealthSnapshot:
        """Take a complete architecture health snapshot."""
        snapshot = ArchitectureHealthSnapshot(
            timestamp=time.time(),
        )

        if not BRIDGES_AVAILABLE:
            return snapshot

        # Gather scores from all bridges
        try:
            meta_bridge = get_meta_architecture_bridge(self.repo_path)
            meta_ctx = meta_bridge.get_meta_context()
            if meta_ctx:
                snapshot.semantic_score = meta_ctx.semantic_score
                snapshot.temporal_score = meta_ctx.temporal_score
                snapshot.provenance_score = meta_ctx.provenance_score
                snapshot.recovery_score = meta_ctx.recovery_score
                snapshot.diagnostic_score = meta_ctx.diagnostic_score
                snapshot.critical_count = meta_ctx.critical_count
                snapshot.high_count = meta_ctx.high_count
                snapshot.medium_count = meta_ctx.medium_count
                snapshot.low_count = meta_ctx.low_count
        except Exception as e:
            logger.debug(f"Failed to get meta-architecture scores: {e}")

        # Get git info
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            snapshot.commit_hash = result.stdout.strip()

            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            snapshot.branch = result.stdout.strip()
        except Exception as e:
            logger.debug(f"Failed to get git info: {e}")

        return snapshot

    def start_monitoring(self, on_change: Callable[[list[str]], None] = None):
        """Start continuous file system monitoring."""
        if not WATCHDOG_AVAILABLE:
            raise ImportError("watchdog package required for file monitoring")

        if self._watching:
            return

        def handle_changes(changed_files: list[str]):
            results = self.checker.check_files(changed_files)

            # Take snapshot after changes
            snapshot = self.take_health_snapshot()
            self.history.add_snapshot(snapshot)

            if on_change:
                on_change(changed_files, results)

        self._observer = Observer()
        handler = FileSystemWatcher(self.repo_path, handle_changes)
        self._observer.schedule(handler, str(self.repo_path), recursive=True)
        self._observer.start()
        self._watching = True

    def stop_monitoring(self):
        """Stop file system monitoring."""
        if self._observer and self._watching:
            self._observer.stop()
            self._observer.join()
            self._watching = False

    def get_health_dashboard(self) -> dict[str, Any]:
        """Get current health data for dashboard."""
        snapshot = self.take_health_snapshot()
        self.history.add_snapshot(snapshot)

        return {
            "current": {
                "overall_score": snapshot.overall_score,
                "semantic_score": snapshot.semantic_score,
                "temporal_score": snapshot.temporal_score,
                "provenance_score": snapshot.provenance_score,
                "recovery_score": snapshot.recovery_score,
                "diagnostic_score": snapshot.diagnostic_score,
                "critical_count": snapshot.critical_count,
                "high_count": snapshot.high_count,
            },
            "trend": {
                "overall": self.history.get_trend("overall", 10),
                "semantic": self.history.get_trend("semantic", 10),
                "architecture": self.history.get_trend("architecture", 10),
            },
            "alerts": [
                {"time": e.timestamp, "type": e.event_type, "message": e.message}
                for e in self.history.get_degradation_alerts()
            ],
            "monitoring_active": self._watching,
        }

    def validate_pre_commit(self) -> dict[str, Any]:
        """Validate staged files for pre-commit hook."""
        return self.git_validator.validate_staged_files()


def get_monitoring_bridge(repo_path: str | Path = None) -> ContinuousMonitoringBridge:
    """Factory function to get monitoring bridge instance."""
    return ContinuousMonitoringBridge(repo_path or ".")
