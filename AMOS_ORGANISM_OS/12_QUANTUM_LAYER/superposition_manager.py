"""Superposition Manager — Multiple potential state management

Manages superposition states where multiple possibilities
exist simultaneously until collapse/decision.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SuperpositionStatus(Enum):
    """Status of a superposition state."""

    ACTIVE = "active"
    COLLAPSING = "collapsing"
    COLLAPSED = "collapsed"
    OBSOLETE = "obsolete"


@dataclass
class PotentialState:
    """A single potential state within superposition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    probability: float = 0.5  # 0-1
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SuperpositionState:
    """A superposition containing multiple potential states."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    context: str = ""  # What is being decided/considered
    potential_states: List[PotentialState] = field(default_factory=list)
    status: SuperpositionStatus = SuperpositionStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    collapsed_at: str = None
    collapsed_to: str = None  # ID of chosen state
    collapse_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "potential_states": [p.to_dict() for p in self.potential_states],
        }


class SuperpositionManager:
    """Manages superposition states for ambiguous situations.

    Maintains multiple potential states until observation
    or decision causes collapse to a single outcome.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.superpositions: List[SuperpositionState] = []

        self._load_data()

    def _load_data(self):
        """Load superposition data from disk."""
        data_file = self.data_dir / "superpositions.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for s_data in data.get("superpositions", []):
                    potentials = []
                    for p_data in s_data.get("potential_states", []):
                        p = PotentialState(
                            id=p_data["id"],
                            name=p_data["name"],
                            description=p_data.get("description", ""),
                            probability=p_data.get("probability", 0.5),
                            attributes=p_data.get("attributes", {}),
                            created_at=p_data["created_at"],
                        )
                        potentials.append(p)

                    sp = SuperpositionState(
                        id=s_data["id"],
                        context=s_data["context"],
                        potential_states=potentials,
                        status=SuperpositionStatus(s_data["status"]),
                        created_at=s_data["created_at"],
                        collapsed_at=s_data.get("collapsed_at"),
                        collapsed_to=s_data.get("collapsed_to"),
                        collapse_reason=s_data.get("collapse_reason", ""),
                    )
                    self.superpositions.append(sp)
            except Exception as e:
                print(f"[SUPERPOSITION] Error loading data: {e}")

    def save(self):
        """Save superposition data to disk."""
        data_file = self.data_dir / "superpositions.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "superpositions": [s.to_dict() for s in self.superpositions],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def create_superposition(
        self,
        context: str,
        potential_states: List[PotentialState],
    ) -> SuperpositionState:
        """Create a new superposition state."""
        # Normalize probabilities
        total = sum(p.probability for p in potential_states)
        if total > 0:
            for p in potential_states:
                p.probability /= total

        sp = SuperpositionState(
            context=context,
            potential_states=potential_states,
        )
        self.superpositions.append(sp)
        self.save()
        return sp

    def get_superposition(self, sp_id: str) -> Optional[SuperpositionState]:
        """Get a superposition by ID."""
        for sp in self.superpositions:
            if sp.id == sp_id:
                return sp
        return None

    def collapse(
        self,
        sp_id: str,
        chosen_state_id: str,
        reason: str = "",
    ) -> Optional[SuperpositionState]:
        """Collapse superposition to a specific state."""
        sp = self.get_superposition(sp_id)
        if not sp or sp.status != SuperpositionStatus.ACTIVE:
            return None

        # Verify chosen state exists
        state_ids = [p.id for p in sp.potential_states]
        if chosen_state_id not in state_ids:
            return None

        sp.status = SuperpositionStatus.COLLAPSED
        sp.collapsed_at = datetime.now(UTC).isoformat()
        sp.collapsed_to = chosen_state_id
        sp.collapse_reason = reason

        self.save()
        return sp

    def probabilistic_collapse(self, sp_id: str) -> Optional[SuperpositionState]:
        """Collapse based on probability weights."""
        import random

        sp = self.get_superposition(sp_id)
        if not sp or sp.status != SuperpositionStatus.ACTIVE:
            return None

        if not sp.potential_states:
            return None

        # Weighted random selection
        weights = [p.probability for p in sp.potential_states]
        chosen = random.choices(sp.potential_states, weights=weights, k=1)[0]

        return self.collapse(sp_id, chosen.id, "probabilistic")

    def get_active_superpositions(self) -> list[dict[str, Any]]:
        """Get all active (non-collapsed) superpositions."""
        active = [s for s in self.superpositions if s.status == SuperpositionStatus.ACTIVE]
        return [s.to_dict() for s in active]

    def get_collapse_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent collapse events."""
        collapsed = [s for s in self.superpositions if s.status == SuperpositionStatus.COLLAPSED]
        collapsed.sort(key=lambda x: x.collapsed_at or "", reverse=True)
        return [s.to_dict() for s in collapsed[:limit]]

    def get_uncertainty_for_context(self, context: str) -> Dict[str, Any]:
        """Get uncertainty metrics for a context."""
        relevant = [
            s
            for s in self.superpositions
            if context in s.context and s.status == SuperpositionStatus.ACTIVE
        ]

        if not relevant:
            return {"uncertainty": 0, "active_superpositions": 0}

        # Calculate uncertainty based on probability distribution
        total_entropy = 0
        for sp in relevant:
            # Shannon entropy
            import math

            entropy = 0
            for p in sp.potential_states:
                if p.probability > 0:
                    entropy -= p.probability * math.log2(p.probability)
            total_entropy += entropy

        avg_entropy = total_entropy / len(relevant)

        return {
            "uncertainty": round(avg_entropy, 3),
            "active_superpositions": len(relevant),
            "max_possible_states": max(len(s.potential_states) for s in relevant),
        }


# Global instance
_MANAGER: Optional[SuperpositionManager] = None


def get_superposition_manager(data_dir: Optional[Path] = None) -> SuperpositionManager:
    """Get or create global superposition manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = SuperpositionManager(data_dir)
    return _MANAGER


if __name__ == "__main__":
    print("Superposition Manager (12_QUANTUM_LAYER)")
    print("=" * 40)

    manager = get_superposition_manager()

    # Create a superposition
    states = [
        PotentialState(name="Option A", description="Fast but risky", probability=0.3),
        PotentialState(name="Option B", description="Slow but safe", probability=0.7),
    ]
    sp = manager.create_superposition("Task execution strategy", states)

    print(f"\nCreated superposition: {sp.context}")
    print(f"States: {[p.name for p in sp.potential_states]}")

    print(f"\nActive superpositions: {len(manager.get_active_superpositions())}")
