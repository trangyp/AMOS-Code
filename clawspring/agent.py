"""Core agent loop: neutral message format, multi-provider streaming."""

from __future__ import annotations

# AMOS Brain integration (standalone package)
from collections.abc import Generator
from dataclasses import dataclass, field

from clawspring.tool_registry import get_tool_schemas
from compaction import maybe_compact
from providers import AssistantTurn, TextChunk, ThinkingChunk, stream
from tools import execute_tool

# AMOS Brain availability flag
_amos_available = True

# ── Re-export event types (used by clawspring.py) ────────────────────────
__all__ = [
    "AgentState",
    "run",
    "TextChunk",
    "ThinkingChunk",
    "ToolStart",
    "ToolEnd",
    "TurnDone",
    "PermissionRequest",
]


@dataclass
class AgentState:
    """Mutable session state. messages use the neutral provider-independent format."""

    messages: list = field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    turn_count: int = 0


@dataclass
class ToolStart:
    name: str
    inputs: dict


@dataclass
class ToolEnd:
    name: str
    result: str
    permitted: bool = True


@dataclass
class TurnDone:
    input_tokens: int
    output_tokens: int


@dataclass
class PermissionRequest:
    description: str
    granted: bool = False


# ── Agent loop ─────────────────────────────────────────────────────────────


def _get_enhanced_system_prompt(base_prompt: str, use_amos: bool = True) -> str:
    """Enhance system prompt with SuperBrain context if available."""
    if not use_amos or not _amos_available:
        return base_prompt
    try:
        from amos_brain.super_brain import get_super_brain

        brain = get_super_brain()
        state = brain.get_state()

        amos_section = f"""# AMOS SuperBrain (vInfinity)
Brain ID: {state.brain_id if hasattr(state, "brain_id") else "AMOS-SB"}
Status: {state.status}
Core Frozen: {state.core_frozen}
Health Score: {state.health_score:.2f}
Creator: Trang Phan
Gap: No embodiment/consciousness/autonomous action
"""
        return f"{base_prompt}\n\n{amos_section}"
    except Exception:
        return base_prompt


def run(
    user_message: str,
    state: AgentState,
    config: dict,
    system_prompt: str,
    depth: int = 0,
    cancel_check=None,
    use_amos_brain: bool = True,
) -> Generator:
    """Multi-turn agent loop (generator).
        Yields: Union[TextChunk, ThinkingChunk] | ToolStart | ToolEnd |
            PermissionRequest | TurnDone

    Args:
        depth: sub-agent nesting depth, 0 for top-level
        cancel_check: callable returning True to abort the loop early
        use_amos_brain: whether to apply AMOS brain enhancement (default: True)

    """
    # Enhance system prompt with AMOS brain context
    enhanced_prompt = _get_enhanced_system_prompt(system_prompt, use_amos_brain)

    # Pre-process through AMOS brain (laws check, routing)
    if _amos_available and use_amos_brain:
        try:
            from amos_runtime import analyze_task

            amos_result = analyze_task(user_message)
            # Store AMOS analysis in config for potential tool use
            config["_amos_analysis"] = amos_result
        except Exception:
            pass  # Continue even if pre-processing fails

    # Append user turn in neutral format
    user_msg = {"role": "user", "content": user_message}
    # Attach pending image from /image command if present
    pending_img = config.pop("_pending_image", None)
    if pending_img:
        user_msg["images"] = [pending_img]
    state.messages.append(user_msg)

    # Inject runtime metadata into config so tools (e.g. Agent) can access it
    config = {**config, "_depth": depth, "_system_prompt": enhanced_prompt}

    while True:
        if cancel_check and cancel_check():
            return
        state.turn_count += 1
        assistant_turn: Optional[AssistantTurn] = None

        # Compact context if approaching window limit
        maybe_compact(state, config)

        # Stream from provider (auto-detected from model name)
        for event in stream(
            model=config["model"],
            system=enhanced_prompt,
            messages=state.messages,
            tool_schemas=get_tool_schemas(),
            config=config,
        ):
            if isinstance(event, (TextChunk, ThinkingChunk)):
                yield event
            elif isinstance(event, AssistantTurn):
                assistant_turn = event

        if assistant_turn is None:
            break

        # Record assistant turn in neutral format
        state.messages.append(
            {
                "role": "assistant",
                "content": assistant_turn.text,
                "tool_calls": assistant_turn.tool_calls,
            }
        )

        state.total_input_tokens += assistant_turn.in_tokens
        state.total_output_tokens += assistant_turn.out_tokens
        yield TurnDone(assistant_turn.in_tokens, assistant_turn.out_tokens)

        if not assistant_turn.tool_calls:
            break  # No tools → conversation turn complete

        # ── Execute tools ────────────────────────────────────────────────
        for tc in assistant_turn.tool_calls:
            yield ToolStart(tc["name"], tc["input"])

            # Permission gate
            permitted = _check_permission(tc, config)
            if not permitted:
                req = PermissionRequest(description=_permission_desc(tc))
                yield req
                permitted = req.granted

            if not permitted:
                result = "Denied: user rejected this operation"
            else:
                result = execute_tool(
                    tc["name"],
                    tc["input"],
                    permission_mode="accept-all",  # already gate-checked above
                    config=config,
                )

            yield ToolEnd(tc["name"], result, permitted)

            # Append tool result in neutral format
            state.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["name"],
                    "content": result,
                }
            )


# ── Helpers ───────────────────────────────────────────────────────────────


def _check_permission(tc: dict, config: dict) -> bool:
    """Return True if operation is auto-approved (no need to ask user)."""
    perm_mode = config.get("permission_mode", "auto")
    if perm_mode == "accept-all":
        return True
    if perm_mode == "manual":
        return False  # always ask

    # "auto" mode: only ask for writes and non-safe bash
    name = tc["name"]
    if name in ("Read", "Glob", "Grep", "WebFetch", "WebSearch"):
        return True
    if name == "Bash":
        from tools import _is_safe_bash

        return _is_safe_bash(tc["input"].get("command", ""))
    return False  # Write, Edit → ask


def _permission_desc(tc: dict) -> str:
    name = tc["name"]
    inp = tc["input"]
    if name == "Bash":
        return f"Run: {inp.get('command', '')}"
    if name == "Write":
        return f"Write to: {inp.get('file_path', '')}"
    if name == "Edit":
        return f"Edit: {inp.get('file_path', '')}"
    return f"{name}({list(inp.values())[:1]})"
