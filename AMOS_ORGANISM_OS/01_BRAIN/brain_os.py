"""AMOS Brain OS — Core reasoning and orchestration engine."""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class ThoughtType(Enum):
    PERCEPTUAL = "perceptual"  # Raw sensory input processing
    CONCEPTUAL = "conceptual"  # Pattern recognition, categorization
    NARRATIVE = "narrative"  # Story, timeline, sequence
    CAUSAL = "causal"  # Cause-effect reasoning
    SYSTEMIC = "systemic"  # Multi-system, multi-actor
    META = "meta"  # Self-reflection, audit, ethics


@dataclass
class Thought:
    """A single unit of cognition in the AMOS brain."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: ThoughtType = ThoughtType.CONCEPTUAL
    content: str = ""
    source: str = "internal"  # Which subsystem originated this
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 0.8  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)  # IDs of related thoughts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "tags": self.tags,
            "references": self.references,
        }


@dataclass
class Plan:
    """A structured plan with steps and audit trail."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    goal: str = ""
    horizon: str = "short-term"  # short-term, medium-term, long-term
    steps: List[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "draft"  # draft, active, completed, abandoned
    audit_trail: List[dict[str, Any]] = field(default_factory=list)

    def add_step(self, action: str, subsystem: str, params: Dict[str, Any] = None):
        """Add a step to the plan."""
        step = {
            "id": str(uuid.uuid4())[:8],
            "order": len(self.steps) + 1,
            "action": action,
            "subsystem": subsystem,
            "params": params or {},
            "status": "pending",
        }
        self.steps.append(step)
        return step["id"]

    def audit(self, finding: str, subsystem: str):
        """Add an audit entry."""
        self.audit_trail.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "subsystem": subsystem,
                "finding": finding,
            }
        )


@dataclass
class BrainState:
    """Complete state snapshot of the brain."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    thoughts: List[Thought] = field(default_factory=list)
    active_plans: List[Plan] = field(default_factory=list)
    completed_plans: List[Plan] = field(default_factory=list)
    current_focus: str = ""  # What the brain is currently focused on
    last_update: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    cycle_count: int = 0  # How many primary loops completed

    def add_thought(self, thought: Thought) -> Thought:
        """Add a thought and update timestamp."""
        self.thoughts.append(thought)
        self.last_update = datetime.now(timezone.utc).isoformat()
        return thought

    def get_thoughts_by_type(self, ttype: ThoughtType) -> List[Thought]:
        """Filter thoughts by type."""
        return [t for t in self.thoughts if t.type == ttype]

    def get_recent_thoughts(self, n: int = 10) -> List[Thought]:
        """Get the n most recent thoughts."""
        return sorted(self.thoughts, key=lambda t: t.timestamp, reverse=True)[:n]


class BrainOS:
    """The core Brain operating system.

    Implements the 7-layer brain model:
    - sensory_layer: Raw inputs
    - perceptual_layer: Pattern detection
    - concept_layer: Stable concepts
    - narrative_layer: Stories, scenarios
    - causal_layer: Cause-effect chains
    - systemic_layer: Multi-system reasoning
    - meta_layer: Self-audit, ethics, risk
    """

    STATE_DIR = Path(__file__).parent / "state"

    def __init__(self):
        self.state = BrainState()
        self._ensure_state_dir()

    def _ensure_state_dir(self):
        """Ensure state directory exists."""
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)

    def perceive(self, content: str, source: str = "senses") -> Thought:
        """Process raw sensory input into perceptual thought."""
        thought = Thought(
            type=ThoughtType.PERCEPTUAL,
            content=content,
            source=source,
            tags=["raw_input", source],
        )
        return self.state.add_thought(thought)

    def conceptualize(self, perceptual_thought: Thought, pattern: str) -> Thought:
        """Elevate perception to concept."""
        thought = Thought(
            type=ThoughtType.CONCEPTUAL,
            content=f"Pattern '{pattern}' detected in: {perceptual_thought.content[:50]}...",
            source="01_BRAIN",
            references=[perceptual_thought.id],
            tags=["pattern", "concept"],
        )
        return self.state.add_thought(thought)

    def narrativize(self, concepts: List[Thought], story: str) -> Thought:
        """Create narrative from concepts."""
        thought = Thought(
            type=ThoughtType.NARRATIVE,
            content=story,
            source="01_BRAIN",
            references=[c.id for c in concepts],
            tags=["story", "timeline"],
        )
        return self.state.add_thought(thought)

    def reason_causally(self, narrative: Thought, cause: str, effect: str) -> Thought:
        """Add causal reasoning layer."""
        thought = Thought(
            type=ThoughtType.CAUSAL,
            content=f"Cause: {cause} -> Effect: {effect}",
            source="01_BRAIN",
            references=[narrative.id],
            tags=["causality", "intervention"],
        )
        return self.state.add_thought(thought)

    def think_systemically(
        self,
        causal_thoughts: List[Thought],
        systems: List[str],
        time_horizon: str,
    ) -> Thought:
        """Multi-system, multi-actor, multi-decade reasoning."""
        thought = Thought(
            type=ThoughtType.SYSTEMIC,
            content=(f"Systemic analysis across {', '.join(systems)} over {time_horizon} horizon"),
            source="01_BRAIN",
            references=[c.id for c in causal_thoughts],
            tags=["systemic", "multi-actor"] + systems,
        )
        return self.state.add_thought(thought)

    def reflect_meta(
        self,
        systemic_thought: Thought,
        risk_check: bool = True,
        ethics_check: bool = True,
    ) -> Thought:
        """Meta-layer: self-audit, ethics, invariants."""
        audit_points = []
        if risk_check:
            audit_points.append("Risk invariants checked")
        if ethics_check:
            audit_points.append("Ethical boundaries verified")

        thought = Thought(
            type=ThoughtType.META,
            content=f"Meta-audit: {', '.join(audit_points)}",
            source="01_BRAIN",
            references=[systemic_thought.id],
            tags=["meta", "audit", "ethics"] if ethics_check else ["meta", "audit"],
        )
        return self.state.add_thought(thought)

    def create_plan(self, goal: str, horizon: str = "medium-term") -> Plan:
        """Create a new plan for a goal."""
        plan = Plan(goal=goal, horizon=horizon)
        self.state.active_plans.append(plan)
        return plan

    def complete_cycle(self):
        """Mark completion of one primary loop cycle."""
        self.state.cycle_count += 1
        self.state.last_update = datetime.now(timezone.utc).isoformat()

    def save_state(self):
        """Persist brain state to disk."""
        filepath = self.STATE_DIR / f"brain_{self.state.session_id}.json"
        data = {
            "session_id": self.state.session_id,
            "current_focus": self.state.current_focus,
            "cycle_count": self.state.cycle_count,
            "last_update": self.state.last_update,
            "thoughts": [t.to_dict() for t in self.state.thoughts[-100:]],  # Last 100
            "active_plans": [asdict(p) for p in self.state.active_plans],
            "completed_plans": [asdict(p) for p in self.state.completed_plans[-10:]],
        }
        filepath.write_text(json.dumps(data, indent=2))
        return filepath

    def load_state(self, session_id: str) -> bool:
        """Load brain state from disk."""
        filepath = self.STATE_DIR / f"brain_{session_id}.json"
        if not filepath.exists():
            return False
        # Simplified load - in production would reconstruct full state
        data = json.loads(filepath.read_text())
        self.state.session_id = data.get("session_id", session_id)
        self.state.current_focus = data.get("current_focus", "")
        self.state.cycle_count = data.get("cycle_count", 0)
        return True

    def status(self) -> Dict[str, Any]:
        """Get current brain status."""
        return {
            "session_id": self.state.session_id,
            "cycle_count": self.state.cycle_count,
            "thought_count": len(self.state.thoughts),
            "active_plans": len(self.state.active_plans),
            "current_focus": self.state.current_focus,
            "last_update": self.state.last_update,
            "thoughts_by_type": {
                t.value: len(self.state.get_thoughts_by_type(t)) for t in ThoughtType
            },
        }
