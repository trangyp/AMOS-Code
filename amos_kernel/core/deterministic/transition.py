"""State transition - extracted from amos_brain/task_processor.py"""

from .types import TransitionResult


def transition(state: dict, interaction: dict, constraints_ok: bool) -> TransitionResult:
    """Deterministic state transition."""
    if not constraints_ok:
        return TransitionResult(next_state=state, changed=False, reason="constraints_failed")

    next_state = dict(state)
    next_state["interaction"] = interaction
    next_state["transition_count"] = state.get("transition_count", 0) + 1

    return TransitionResult(next_state=next_state, changed=True, reason="deterministic_transition")
