"""AMOSL Ledger System - Immutable Trace Recording.

Implements the ledger equation:
    L_t = ⟨Σ_t, a_t, o_t, 𝒰_t, Λ_t, outcome_t⟩

With auditability theorem:
    Explain(L) = Outcome
    Replay(ℓ_0,...,ℓ_n) = X_n
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import json


@dataclass(frozen=True)
class LedgerEntry:
    """Single ledger entry: ℓ_t = ⟨Σ_t, a_t, o_t, 𝒰_t, Λ_t, outcome_t⟩"""
    timestamp: float
    step: int
    state_hash: str
    action: Optional[Dict[str, Any]]
    observation: Optional[Dict[str, Any]]
    uncertainty: Dict[str, float]
    invariants_satisfied: bool
    outcome: Any
    prev_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "step": self.step,
            "state_hash": self.state_hash,
            "action": self.action,
            "observation": self.observation,
            "uncertainty": self.uncertainty,
            "invariants_satisfied": self.invariants_satisfied,
            "outcome": self.outcome,
            "prev_hash": self.prev_hash,
        }
    
    def compute_hash(self) -> str:
        """Compute cryptographic hash of entry."""
        data = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class TraceTensor:
    """Trace tensor for comprehensive recording."""
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    verification: List[bool] = field(default_factory=list)
    outputs: List[Any] = field(default_factory=list)
    
    def append_step(self, input_data, obs, action, constraint, verified, output):
        self.inputs.append(input_data)
        self.observations.append(obs)
        self.actions.append(action)
        self.constraints.append(constraint)
        self.verification.append(verified)
        self.outputs.append(output)


class Ledger:
    """Immutable ledger with chain of entries."""
    
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.trace = TraceTensor()
        self._current_hash = "0" * 16
    
    def record(self,
               step: int,
               state: Any,
               action: Optional[Dict] = None,
               observation: Optional[Dict] = None,
               uncertainty: Optional[Dict[str, float]] = None,
               invariants_satisfied: bool = True,
               outcome: Any = None) -> LedgerEntry:
        """Record a new ledger entry."""
        # Create state hash
        state_hash = self._hash_state(state)
        
        # Create entry
        entry = LedgerEntry(
            timestamp=datetime.now().timestamp(),
            step=step,
            state_hash=state_hash,
            action=action,
            observation=observation,
            uncertainty=uncertainty or {},
            invariants_satisfied=invariants_satisfied,
            outcome=outcome,
            prev_hash=self._current_hash
        )
        
        # Update chain
        self._current_hash = entry.compute_hash()
        self.entries.append(entry)
        
        return entry
    
    def _hash_state(self, state: Any) -> str:
        """Hash state for integrity."""
        try:
            if hasattr(state, 'snapshot'):
                data = json.dumps(state.snapshot(), sort_keys=True, default=str)
            else:
                data = str(state)
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        except:
            return "hash_error_" + str(len(self.entries))
    
    def explain(self, outcome: Any) -> Optional[Dict]:
        """Explain outcome: Explain(L) = Outcome.
        
        Returns the trace that leads to the outcome, or None if
        outcome cannot be explained by this ledger.
        """
        # Find entry with matching outcome
        for entry in reversed(self.entries):
            if entry.outcome == outcome:
                return {
                    "found": True,
                    "step": entry.step,
                    "trace_length": len(self.entries),
                    "explanation": self._reconstruct_trace(entry.step)
                }
        
        return None
    
    def _reconstruct_trace(self, up_to_step: int) -> List[Dict]:
        """Reconstruct trace up to given step."""
        trace = []
        for entry in self.entries:
            if entry.step <= up_to_step:
                trace.append({
                    "step": entry.step,
                    "action": entry.action,
                    "outcome": entry.outcome,
                    "invariants": entry.invariants_satisfied
                })
        return trace
    
    def replay(self, initial_state: Any) -> Any:
        """Replay ledger: Replay(ℓ_0,...,ℓ_n) = X_n.
        
        Reconstructs final state by replaying all actions.
        """
        state = initial_state
        
        for entry in self.entries:
            if entry.action:
                state = self._apply_action(state, entry.action)
        
        return state
    
    def _apply_action(self, state: Any, action: Dict) -> Any:
        """Apply action to state (simplified replay)."""
        # In a full implementation, this would apply the actual
        # state transformation. For now, we return the state.
        return state
    
    def verify_chain(self) -> Tuple[bool, List[str]]:
        """Verify ledger integrity (hash chain)."""
        errors = []
        
        for i, entry in enumerate(self.entries):
            if i == 0:
                continue
            
            prev_entry = self.entries[i - 1]
            expected_prev_hash = prev_entry.compute_hash()
            
            if entry.prev_hash != expected_prev_hash[:16]:
                errors.append(f"Step {i}: hash chain broken")
        
        return len(errors) == 0, errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ledger statistics."""
        total = len(self.entries)
        verified = sum(1 for e in self.entries if e.invariants_satisfied)
        
        return {
            "total_entries": total,
            "verified_steps": verified,
            "chain_valid": self.verify_chain()[0],
            "first_step": self.entries[0].step if self.entries else None,
            "last_step": self.entries[-1].step if self.entries else None,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize ledger."""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "statistics": self.get_statistics()
        }
    
    def query(self, step: Optional[int] = None, 
              outcome_type: Optional[str] = None) -> List[LedgerEntry]:
        """Query ledger entries."""
        results = []
        
        for entry in self.entries:
            if step is not None and entry.step != step:
                continue
            if outcome_type is not None:
                if not isinstance(entry.outcome, dict):
                    continue
                if entry.outcome.get("type") != outcome_type:
                    continue
            results.append(entry)
        
        return results
