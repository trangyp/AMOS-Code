"""Negotiation Engine — Multi-Party Negotiation System

Manages negotiations between multiple parties (agents, humans, systems).
Handles proposal generation, offer evaluation, and agreement formation.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum
from pathlib import Path
from typing import Any


class NegotiationStatus(Enum):
    """Status of a negotiation."""

    PENDING = "pending"
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class NegotiationStrategy(Enum):
    """Strategy for negotiation."""

    COOPERATIVE = "cooperative"  # Win-win focus
    COMPETITIVE = "competitive"  # Win-lose focus
    COMPROMISE = "compromise"  # Middle ground
    AVOIDING = "avoiding"  # Delay/defer


@dataclass
class Proposal:
    """A proposal in a negotiation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    party: str = ""
    terms: dict[str, Any] = field(default_factory=dict)
    value_estimate: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: str = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NegotiationResult:
    """Result of a negotiation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: NegotiationStatus = NegotiationStatus.PENDING
    accepted_proposal: Proposal = None
    final_terms: dict[str, Any] = field(default_factory=dict)
    parties: list[str] = field(default_factory=list)
    rounds: int = 0
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str = None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "accepted_proposal": self.accepted_proposal.to_dict()
            if self.accepted_proposal
            else None,
        }


class NegotiationEngine:
    """Manages multi-party negotiations.

    Handles proposal generation, offer evaluation, counter-proposals,
    and agreement formation.
    """

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.active_negotiations: dict[str, NegotiationResult] = {}
        self.completed_negotiations: dict[str, NegotiationResult] = {}
        self.proposal_history: list[Proposal] = []

    def start_negotiation(
        self,
        parties: list[str],
        topic: str,
        strategy: NegotiationStrategy = NegotiationStrategy.COOPERATIVE,
    ) -> NegotiationResult:
        """Start a new negotiation."""
        negotiation = NegotiationResult(
            parties=parties,
            status=NegotiationStatus.ACTIVE,
        )

        self.active_negotiations[negotiation.id] = negotiation
        return negotiation

    def submit_proposal(
        self,
        negotiation_id: str,
        party: str,
        terms: dict[str, Any],
        value_estimate: float,
    ) -> Proposal:
        """Submit a proposal to an active negotiation."""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation or negotiation.status != NegotiationStatus.ACTIVE:
            return None

        proposal = Proposal(
            party=party,
            terms=terms,
            value_estimate=value_estimate,
        )

        self.proposal_history.append(proposal)
        negotiation.rounds += 1

        # Evaluate if proposal is acceptable to other parties
        self._evaluate_proposal(negotiation, proposal)

        return proposal

    def _evaluate_proposal(
        self,
        negotiation: NegotiationResult,
        proposal: Proposal,
    ) -> None:
        """Evaluate a proposal against other parties' interests."""
        # Simple evaluation: check if proposal meets basic criteria
        # In a real implementation, this would involve more complex logic

        # For now, auto-accept if value is reasonable
        if proposal.value_estimate > 0:
            # Check if all parties would accept
            would_accept = True

            if would_accept:
                negotiation.accepted_proposal = proposal
                negotiation.final_terms = proposal.terms
                negotiation.status = NegotiationStatus.ACCEPTED
                negotiation.completed_at = datetime.now(UTC).isoformat()

                # Move to completed
                del self.active_negotiations[negotiation.id]
                self.completed_negotiations[negotiation.id] = negotiation

                self._save_negotiations()

    def counter_proposal(
        self,
        negotiation_id: str,
        party: str,
        original_proposal_id: str,
        counter_terms: dict[str, Any],
        counter_value: float,
    ) -> Proposal:
        """Submit a counter-proposal."""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation:
            return None

        counter = Proposal(
            party=party,
            terms=counter_terms,
            value_estimate=counter_value,
        )

        self.proposal_history.append(counter)
        negotiation.rounds += 1

        return counter

    def accept_proposal(self, negotiation_id: str, proposal_id: str) -> bool:
        """Accept a proposal and complete negotiation."""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation:
            return False

        # Find the proposal
        proposal = None
        for p in self.proposal_history:
            if p.id == proposal_id:
                proposal = p
                break

        if not proposal:
            return False

        negotiation.accepted_proposal = proposal
        negotiation.final_terms = proposal.terms
        negotiation.status = NegotiationStatus.ACCEPTED
        negotiation.completed_at = datetime.now(UTC).isoformat()

        del self.active_negotiations[negotiation_id]
        self.completed_negotiations[negotiation_id] = negotiation

        self._save_negotiations()
        return True

    def reject_negotiation(self, negotiation_id: str, reason: str = "") -> bool:
        """Reject and terminate a negotiation."""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation:
            return False

        negotiation.status = NegotiationStatus.REJECTED
        negotiation.completed_at = datetime.now(UTC).isoformat()

        del self.active_negotiations[negotiation_id]
        self.completed_negotiations[negotiation_id] = negotiation

        self._save_negotiations()
        return True

    def get_negotiation_status(self, negotiation_id: str) -> dict[str, Any]:
        """Get status of a negotiation."""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation:
            negotiation = self.completed_negotiations.get(negotiation_id)

        if not negotiation:
            return None

        return negotiation.to_dict()

    def _save_negotiations(self):
        """Save negotiations to disk."""
        negotiations_file = self.data_dir / "negotiations.json"
        data = {
            "active": [n.to_dict() for n in self.active_negotiations.values()],
            "completed": [n.to_dict() for n in self.completed_negotiations.values()],
            "saved_at": datetime.now(UTC).isoformat(),
        }
        negotiations_file.write_text(json.dumps(data, indent=2))

    def list_negotiations(self, active_only: bool = False) -> list[dict[str, Any]]:
        """List all negotiations."""
        negotiations = list(self.active_negotiations.values())
        if not active_only:
            negotiations.extend(self.completed_negotiations.values())

        return [n.to_dict() for n in negotiations]

    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        active = len(self.active_negotiations)
        completed = len(self.completed_negotiations)
        total_rounds = sum(n.rounds for n in self.active_negotiations.values())
        total_rounds += sum(n.rounds for n in self.completed_negotiations.values())

        accepted = sum(
            1
            for n in self.completed_negotiations.values()
            if n.status == NegotiationStatus.ACCEPTED
        )

        return {
            "active_negotiations": active,
            "completed_negotiations": completed,
            "total_rounds": total_rounds,
            "success_rate": accepted / max(completed, 1),
            "total_proposals": len(self.proposal_history),
        }


_ENGINE: NegotiationEngine = None


def get_negotiation_engine(data_dir: Path = None) -> NegotiationEngine:
    """Get or create global negotiation engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = NegotiationEngine(data_dir)
    return _ENGINE
