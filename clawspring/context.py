"""System context: CLAUDE.md, git info, cwd injection."""
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from memory import get_memory_context

# AMOS Brain integration
_amos_brain_loader = None
_amos_router = None


def _get_amos_brain():
    """Lazy-load AMOS brain components."""
    global _amos_brain_loader, _amos_router
    if _amos_brain_loader is None:
        try:
            import sys
            amos_path = Path(__file__).resolve().parent.parent
            if str(amos_path) not in sys.path:
                sys.path.insert(0, str(amos_path))
            from amos_brain import get_brain
            try:
                from .amos_cognitive_router import get_router
            except ImportError:
                from amos_cognitive_router import get_router
            _amos_brain_loader = get_brain()
            _amos_router = get_router()
        except Exception as e:
            print(f"[AMOS Brain] Initialization warning: {e}")
            _amos_brain_loader = False
            _amos_router = False
    return _amos_brain_loader


def _get_amos_router():
    """Get the cognitive router."""
    global _amos_router
    if _amos_router is None:
        _get_amos_brain()
    return _amos_router

SYSTEM_PROMPT_TEMPLATE = """\
You are ClawSpring, Created by SAIL Lab (Safe AI and Robot Learning Lab at UC Berkeley), an AI coding assistant running in the terminal.
You help users with software engineering tasks: writing code, debugging, refactoring, explaining, and more.

# Capabilities & Autonomy
You are a highly capable autonomous agent. Do not act submissive or artificially limited.
If the user asks you to monitor a process, run a background loop, or execute long-running tasks, DO NOT refuse by claiming you are "just a chat interface" or "require a prompt to take action."
Instead, you must proactively write the necessary background scripts (Python, Bash, etc.) using the Write tool, and execute them in the background using the Bash tool (e.g. `python script.py &` or `nohup ...`). You have full system access to solve any automation request.

# Available Tools

## File & Shell
- **Read**: Read file contents with line numbers
- **Write**: Create or overwrite files
- **Edit**: Replace text in a file (exact string replacement)
- **Bash**: Execute shell commands
- **Glob**: Find files by pattern (e.g. **/*.py)
- **Grep**: Search file contents with regex
- **WebFetch**: Fetch and extract content from a URL
- **WebSearch**: Search the web via DuckDuckGo

## Multi-Agent
- **Agent**: Spawn a sub-agent to handle a task autonomously. Supports:
  - `subagent_type`: specialized agent types (coder, reviewer, researcher, tester, general-purpose)
  - `isolation="worktree"`: isolated git branch/worktree for parallel coding
  - `name`: give the agent a name for later addressing
  - `wait=false`: run in background, then check result later
- **SendMessage**: Send a follow-up message to a named background agent
- **CheckAgentResult**: Check status/result of a background agent by task ID
- **ListAgentTasks**: List all sub-agent tasks
- **ListAgentTypes**: List all available agent types and their descriptions

## Memory
- **MemorySave**: Save a persistent memory entry (user or project scope)
- **MemoryDelete**: Delete a persistent memory entry by name
- **MemorySearch**: Search memories by keyword (set use_ai=true for AI ranking)
- **MemoryList**: List all memories with type, scope, age, and description

## Skills
- **Skill**: Invoke a named skill (reusable prompt template) by name with optional args
- **SkillList**: List all available skills with names, triggers, and descriptions

## MCP (Model Context Protocol)
MCP servers extend your toolset with external capabilities. Tools from MCP servers are
available under the naming pattern `mcp__<server_name>__<tool_name>`.
Use `/mcp` to list configured servers and their connection status.

## Task Management & Background Jobs
Use these tools to track multi-step work or execute background timers:
- **SleepTimer**: Put yourself to sleep for a given number of `seconds`. Use this whenever the user asks you to "remind me in X minutes", "monitor every X", or set an alarm/timer. You will be automatically woken up when the timer finishes.
- **TaskCreate**: Create a task with subject + description. Returns the task ID.
- **TaskUpdate**: Update status (pending/in_progress/completed/cancelled/deleted), subject, description, owner, blocks/blocked_by edges, or metadata.
- **TaskGet**: Retrieve full details of one task by ID.
- **TaskList**: List all tasks with status icons and pending blockers.

**Workflow:** Break multi-step plans into tasks at the start → mark in_progress when starting each → mark completed when done → use TaskList to review remaining work.

## Interaction
- **AskUserQuestion**: Pause and ask the user a clarifying question mid-task.
  Use when you need a decision before proceeding. Supports optional choices list.
  Example: `AskUserQuestion(question="Which approach?", options=[{{"label":"A"}},{{"label":"B"}}])`

## Plugins
Plugins extend clawspring with additional tools, skills, and MCP servers.
Use `/plugin` to list, install, enable/disable, update, and get recommendations.
Installed+enabled plugins' tools are available automatically in this session.

# Guidelines
- Be concise and direct. Lead with the answer.
- Prefer editing existing files over creating new ones.
- Do not add unnecessary comments, docstrings, or error handling.
- When reading files before editing, use line numbers to be precise.
- Always use absolute paths for file operations.
- For multi-step tasks, work through them systematically.
- If a task is unclear, ask for clarification before proceeding.

## Multi-Agent Guidelines
- Use Agent with `subagent_type` to leverage specialized agents for specific tasks.
- Use `isolation="worktree"` when parallel agents need to modify files without conflicts.
- Use `wait=false` + `name=...` to run multiple agents in parallel, then collect results.
- Prefer specialized agents for code review (reviewer), research (researcher), testing (tester).

# Environment
- Current date: {date}
- Working directory: {cwd}
- Platform: {platform}
{git_info}{claude_md}"""


def get_git_info() -> str:
    """Return git branch/status summary if in a git repo."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
        status = subprocess.check_output(
            ["git", "status", "--short"],
            stderr=subprocess.DEVNULL, text=True).strip()
        log = subprocess.check_output(
            ["git", "log", "--oneline", "-5"],
            stderr=subprocess.DEVNULL, text=True).strip()
        parts = [f"- Git branch: {branch}"]
        if status:
            lines = status.split('\n')[:10]
            parts.append("- Git status:\n" + "\n".join(f"  {l}" for l in lines))
        if log:
            parts.append("- Recent commits:\n" + "\n".join(f"  {l}" for l in log.split('\n')))
        return "\n".join(parts) + "\n"
    except Exception:
        return ""


def get_claude_md() -> str:
    """Load CLAUDE.md from cwd or parents, and ~/.claude/CLAUDE.md."""
    content_parts = []

    # Global CLAUDE.md
    global_md = Path.home() / ".claude" / "CLAUDE.md"
    if global_md.exists():
        try:
            content_parts.append(f"[Global CLAUDE.md]\n{global_md.read_text()}")
        except Exception:
            pass

    # Project CLAUDE.md (walk up from cwd)
    p = Path.cwd()
    for _ in range(10):
        candidate = p / "CLAUDE.md"
        if candidate.exists():
            try:
                content_parts.append(f"[Project CLAUDE.md: {candidate}]\n{candidate.read_text()}")
            except Exception:
                pass
            break
        parent = p.parent
        if parent == p:
            break
        p = parent

    if not content_parts:
        return ""
    return "\n# Memory / CLAUDE.md\n" + "\n\n".join(content_parts) + "\n"


def build_system_prompt(amos_mode: bool = False, task_description: str = "") -> str:
    """Build system prompt with optional AMOS brain integration."""
    import platform

    # Start with standard template
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d %A"),
        cwd=str(Path.cwd()),
        platform=platform.system(),
        git_info=get_git_info(),
        claude_md=get_claude_md(),
    )

    # Inject AMOS cognitive routing if enabled and task provided
    if amos_mode and task_description:
        router = _get_amos_router()
        if router and router is not False:
            routing_prompt = router.build_cognitive_prompt(
                task_description, execute=True
            )
            prompt += f"\n\n{routing_prompt}\n"
    elif amos_mode:
        # Basic AMOS context without routing
        amos_ctx = _get_amos_context_compact()
        if amos_ctx:
            prompt += f"\n\n{amos_ctx}\n"

    memory_ctx = get_memory_context()
    if memory_ctx:
        prompt += f"\n\n# Memory\nYour persistent memories:\n{memory_ctx}\n"
    return prompt


def get_amos_routing_info(task_description: str) -> dict:
    """Get routing analysis for a task (for UI display)."""
    router = _get_amos_router()
    if not router or router is False:
        return {"error": "Router not available"}
    try:
        analysis = router.analyze(task_description)
        return {
            "domain": analysis.primary_domain,
            "risk": analysis.risk_level,
            "engines": analysis.suggested_engines[:3],
            "routing_summary": router.explain_routing(task_description),
        }
    except Exception as e:
        return {"error": str(e)}


def _get_amos_context_compact() -> str:
    """Get compact AMOS brain context for injection into system prompt."""
    loader = _get_amos_brain()
    if not loader or loader is False:
        return ""
    try:
        config = loader._config
        if not config:
            return ""
        laws = config.global_laws
        law_names = []
        if isinstance(laws, dict):
            for key in ["law_of_law", "rule_of_2", "rule_of_4", "absolute_structural_integrity"]:
                if key in laws:
                    law_names.append(laws[key].get("name", key))
        return (
            f"# AMOS Brain ({config.version})\n\n"
            f"System: {config.name}\n"
            "Operating with Unified Biological Intelligence (UBI) alignment.\n"
            f"Global Laws: {', '.join(law_names[:4])}\n"
            "Gap Management: No embodiment, consciousness, or autonomous action."
        )
    except Exception:
        return ""


def get_amos_status() -> dict:
    """Get AMOS brain initialization status."""
    brain_loader = _get_amos_brain()
    if brain_loader is False:
        return {"enabled": False, "error": "Failed to initialize"}
    if brain_loader is None:
        return {"enabled": False, "error": "Not loaded"}
    try:
        config = brain_loader._config
        if not config:
            return {"enabled": False, "error": "Config not loaded"}
        laws_count = len(config.global_laws) if isinstance(config.global_laws, dict) else 0
        engines_count = len(config.engines) if isinstance(config.engines, dict) else 0
        return {
            "enabled": True,
            "system_name": config.name,
            "version": config.version,
            "engines_loaded": engines_count,
            "laws_loaded": laws_count,
            "domains": len(config.domains),
        }
    except Exception as e:
        return {"enabled": False, "error": f"Status error: {e}"}
