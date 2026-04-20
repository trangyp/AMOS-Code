"""Adaptation System — Evolution & Environment Response

Manages organism adaptation to environmental changes.
Implements evolutionary strategies and feedback processing.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from pathlib import Path
from typing import Any


class AdaptationStrategy(Enum):
    """Strategy for adaptation."""

    EVOLUTIONARY = "evolutionary"  # Slow, generational change
    DEVELOPMENTAL = "developmental"  # Learning-based change
    PLASTIC = "plastic"  # Immediate flexible response


@dataclass
class EnvironmentFeedback:
    """Feedback from the environment."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = ""  # Subsystem or external source
    feedback_type: str = ""  # performance, error, success, demand
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Adaptation:
    """An adaptation made by the organism."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trigger: str = ""  # What triggered the adaptation
    strategy: AdaptationStrategy = AdaptationStrategy.DEVELOPMENTAL
    changes: dict[str, Any] = field(default_factory=dict)
    before_state: dict[str, Any] = field(default_factory=dict)
    after_state: dict[str, Any] = field(default_factory=dict)
    successful: bool = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    evaluated_at: str = None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "strategy": self.strategy.value,
        }


class AdaptationSystem:
    """Manages organism adaptation and evolution.

    Processes environmental feedback, determines appropriate
    adaptation strategies, and tracks adaptation success.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.feedback_queue: list[EnvironmentFeedback] = []
        self.processed_feedback: list[EnvironmentFeedback] = []
        self.adaptations: dict[str, Adaptation] = {}
        self.adaptation_patterns: dict[str, list[str]] = {}

        self._init_default_patterns()

    def _init_default_patterns(self):
        """Initialize default adaptation patterns."""
        self.adaptation_patterns = {
            "performance_degradation": [
                "optimize_resource_usage",
                "scale_capacity",
                "offload_tasks",
            ],
            "high_error_rate": [
                "increase_quality_checks",
                "simplify_workflow",
                "add_validation_steps",
            ],
            "resource_shortage": [
                "prioritize_critical_tasks",
                "reduce_non_essential_ops",
                "request_additional_resources",
            ],
            "security_threat": [
                "increase_monitoring",
                "tighten_access_controls",
                "isolate_affected_components",
            ],
        }

    def record_feedback(
        self,
        source: str,
        feedback_type: str,
        data: dict[str, Any],
    ) -> EnvironmentFeedback:
        """Record feedback from environment."""
        feedback = EnvironmentFeedback(
            source=source,
            feedback_type=feedback_type,
            data=data,
        )
        self.feedback_queue.append(feedback)
        return feedback

    def process_feedback(self, feedback_id: str) -> Optional[Adaptation]:
        """Process a feedback item and potentially trigger adaptation."""
        feedback = None
        for f in self.feedback_queue:
            if f.id == feedback_id:
                feedback = f
                break

        if not feedback:
            return None

        self.feedback_queue.remove(feedback)
        self.processed_feedback.append(feedback)

        # Determine if adaptation is needed
        adaptation = self._determine_adaptation(feedback)
        if adaptation:
            self.adaptations[adaptation.id] = adaptation
            self._apply_adaptation(adaptation)

        return adaptation

    def _determine_adaptation(self, feedback: EnvironmentFeedback) -> Optional[Adaptation]:
        """Determine what adaptation is needed based on feedback."""
        # Check if this feedback type has a known pattern
        pattern = self.adaptation_patterns.get(feedback.feedback_type)

        if pattern:
            # Create adaptation based on pattern
            adaptation = Adaptation(
                trigger=f"{feedback.feedback_type}:{feedback.source}",
                strategy=AdaptationStrategy.DEVELOPMENTAL,
                changes={"actions": pattern},
                before_state={"feedback": feedback.to_dict()},
            )
            return adaptation

        # Check for critical thresholds
        if feedback.feedback_type == "performance_degradation":
            perf = feedback.data.get("performance_score", 1.0)
            if perf < 0.5:
                return Adaptation(
                    trigger="critical_performance_drop",
                    strategy=AdaptationStrategy.PLASTIC,
                    changes={"priority": "emergency_optimization"},
                    before_state={"performance": perf},
                )

        return None

    def _apply_adaptation(self, adaptation: Adaptation) -> bool:
        """Apply an adaptation to the organism."""
        # In a real implementation, this would modify actual subsystem behavior
        # For now, we record the intended changes
        adaptation.after_state = {
            "status": "applied",
            "changes_made": list(adaptation.changes.keys()),
        }
        return True

    def evaluate_adaptation(self, adaptation_id: str, successful: bool) -> bool:
        """Evaluate if an adaptation was successful."""
        adaptation = self.adaptations.get(adaptation_id)
        if not adaptation:
            return False

        adaptation.successful = successful
        adaptation.evaluated_at = datetime.now(UTC).isoformat()

        # If successful, reinforce the pattern
        if successful:
            # Could add to reinforced patterns here
            pass

        self._save_adaptations()
        return True

    def auto_adapt(self) -> list[Adaptation]:
        """Process all pending feedback and auto-adapt."""
        adaptations = []

        while self.feedback_queue:
            feedback = self.feedback_queue[0]
            adaptation = self.process_feedback(feedback.id)
            if adaptation:
                adaptations.append(adaptation)

        return adaptations

    def _save_adaptations(self):
        """Save adaptations to disk."""
        adaptations_file = self.data_dir / "adaptations.json"
        data = {
            "adaptations": [a.to_dict() for a in self.adaptations.values()],
            "processed_feedback": [f.to_dict() for f in self.processed_feedback],
            "patterns": self.adaptation_patterns,
            "saved_at": datetime.now(UTC).isoformat(),
        }
        adaptations_file.write_text(json.dumps(data, indent=2))

    def get_status(self) -> dict[str, Any]:
        """Get adaptation system status."""
        pending = len(self.feedback_queue)
        total_adaptations = len(self.adaptations)
        successful = sum(1 for a in self.adaptations.values() if a.successful)
        failed = sum(1 for a in self.adaptations.values() if a.successful is False)

        return {
            "pending_feedback": pending,
            "total_adaptations": total_adaptations,
            "successful": successful,
            "failed": failed,
            "unevaluated": total_adaptations - successful - failed,
            "known_patterns": len(self.adaptation_patterns),
        }


_SYSTEM: Optional[AdaptationSystem] = None


def get_adaptation_system(data_dir: Optional[Path] = None) -> AdaptationSystem:
    """Get or create global adaptation system."""
    global _SYSTEM
    if _SYSTEM is None:
        _SYSTEM = AdaptationSystem(data_dir)
    return _SYSTEM
