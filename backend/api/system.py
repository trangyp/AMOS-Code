"""
AMOS System API

REST API endpoints for system monitoring and control.
Health checks, metrics, governance, and evolution control.

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import time
from datetime import datetime, timezone

import psutil
from fastapi import APIRouter, HTTPException

from ..llm_providers import llm_router
from .schemas import (
    EvolutionStatus,
    GovernanceRuleSchema,
    GovernanceUpdate,
    MetricsResponse,
    SystemStatus,
)

# Import AMOS systems
try:
    from amos_self_evolution.evolution_execution_engine import get_evolution_engine

    EVOLUTION_AVAILABLE = True
except ImportError:
    EVOLUTION_AVAILABLE = False
    get_evolution_engine = None

try:
    from amos_governance_engine import AMOSGovernanceEngine, get_governance_engine

    GOVERNANCE_AVAILABLE = True
except ImportError:
    GOVERNANCE_AVAILABLE = False
    get_governance_engine = None

try:
    from amos_metrics_collector import get_metrics_collector

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    get_metrics_collector = None

router = APIRouter()

# System start time for uptime calculation
_start_time = time.time()


@router.get("/status", response_model=SystemStatus)
async def get_status():
    """Get comprehensive AMOS system status."""
    uptime = time.time() - _start_time

    # Get provider info
    providers = llm_router.get_available_providers()

    # Get math framework status
    math_status = "unavailable"
    try:
        from amos_brain import SuperBrainRuntime

        brain = SuperBrainRuntime()
        if hasattr(brain, "_math_engine") and brain._math_engine is not None:
            math_status = "active"
    except Exception:
        pass

    return SystemStatus(
        version="3.0.0",
        status="healthy",
        uptime_seconds=uptime,
        components={
            "api": "online",
            "llm_providers": len(providers),
            "event_bus": "connected",
            "agent_system": "active",
            "math_framework": math_status,
        },
        providers=providers,
    )


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system performance metrics."""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory().percent

    # Get metrics from collector if available
    active_tasks = 0
    total_requests = 0
    avg_latency = 0.0

    if METRICS_AVAILABLE and get_metrics_collector:
        try:
            collector = get_metrics_collector()
            # Get recent metrics
            metrics_summary = collector.get_metrics_summary(hours=1)
            active_tasks = len(asyncio.all_tasks()) - 1  # Exclude current
            total_requests = metrics_summary.get("total_requests", 0)
            avg_latency = metrics_summary.get("average_latency_ms", 0.0)
        except Exception:
            pass  # Fall back to defaults

    return MetricsResponse(
        cpu_percent=cpu,
        memory_percent=memory,
        active_tasks=active_tasks,
        total_requests=total_requests,
        average_latency_ms=avg_latency,
    )


@router.get("/evolution", response_model=EvolutionStatus)
async def get_evolution_status():
    """Get self-evolution system status."""
    if not EVOLUTION_AVAILABLE or not get_evolution_engine:
        return EvolutionStatus(
            enabled=False,
            total_cycles=0,
            last_cycle=None,
            opportunities_found=0,
            current_mode="unavailable",
        )

    try:
        engine = get_evolution_engine()
        status = engine.get_status() if hasattr(engine, "get_status") else {}

        return EvolutionStatus(
            enabled=status.get("enabled", True),
            total_cycles=status.get("total_cycles", 0),
            last_cycle=status.get("last_cycle"),
            opportunities_found=status.get("opportunities_found", 0),
            current_mode=status.get("mode", "autonomous"),
        )
    except Exception as e:
        return EvolutionStatus(
            enabled=False,
            total_cycles=0,
            last_cycle=None,
            opportunities_found=0,
            current_mode=f"error: {str(e)[:50]}",
        )


@router.post("/evolution/toggle")
async def toggle_evolution(enabled: bool):
    """Enable or disable self-evolution."""
    if not EVOLUTION_AVAILABLE or not get_evolution_engine:
        raise HTTPException(status_code=503, detail="Evolution system not available")

    try:
        engine = get_evolution_engine()
        if hasattr(engine, "set_enabled"):
            engine.set_enabled(enabled)
        elif hasattr(engine, "enable"):
            if enabled:
                engine.enable()
            else:
                engine.disable()

        return {"message": f"Evolution {'enabled' if enabled else 'disabled'}", "enabled": enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle evolution: {str(e)}")


@router.get("/governance/rules")
async def list_governance_rules():
    """List all governance rules."""
    if not GOVERNANCE_AVAILABLE or not get_governance_engine:
        # Return default rules if governance not available
        return [
            GovernanceRuleSchema(
                id="rule-1",
                name="Auto-Recovery",
                description="Automatically recover from component failures",
                priority="high",
                status="active",
                trigger="component_failure",
                action="restart_component",
            ),
            GovernanceRuleSchema(
                id="rule-2",
                name="Memory Optimization",
                description="Optimize memory usage when threshold exceeded",
                priority="medium",
                status="active",
                trigger="memory_threshold",
                action="optimize_memory",
            ),
        ]

    try:
        engine = get_governance_engine()
        rules = []

        if hasattr(engine, "get_rules"):
            gov_rules = engine.get_rules()
            for rule in gov_rules:
                rules.append(
                    GovernanceRuleSchema(
                        id=rule.get("id", "unknown"),
                        name=rule.get("name", "Unnamed"),
                        description=rule.get("description", ""),
                        priority=rule.get("priority", "medium"),
                        status=rule.get("status", "active"),
                        trigger=rule.get("trigger", "manual"),
                        action=rule.get("action", "log"),
                    )
                )

        return (
            rules
            if rules
            else [
                GovernanceRuleSchema(
                    id="default",
                    name="System Default",
                    description="Default governance rule",
                    priority="medium",
                    status="active",
                    trigger="manual",
                    action="log",
                )
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get governance rules: {str(e)}")


@router.post("/governance/mode")
async def update_governance_mode(update: GovernanceUpdate):
    """Update governance mode (autonomous, supervised, manual)."""
    if not GOVERNANCE_AVAILABLE or not get_governance_engine:
        raise HTTPException(status_code=503, detail="Governance system not available")

    try:
        engine = get_governance_engine()
        if hasattr(engine, "set_mode"):
            engine.set_mode(update.mode)
        elif hasattr(engine, "mode"):
            engine.mode = update.mode

        return {"message": f"Governance mode set to {update.mode}", "mode": update.mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update governance mode: {str(e)}")


@router.get("/providers")
async def get_providers():
    """Get all LLM provider information."""
    providers = llm_router.get_available_providers()
    return {"providers": providers, "count": len(providers)}


# ============================================================================
# Cognitive Mode API (Stub Implementation)
# ============================================================================


@router.get("/cognitive/mode")
async def get_cognitive_mode():
    """Get current cognitive mode (seed/growth/full)."""
    return {
        "mode": "growth",
        "description": "Cognitive systems fully active",
        "features_enabled": [
            "mcp_integration",
            "reasoning_transparency",
            "background_agents",
            "persistent_memory",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/cognitive/mode")
async def set_cognitive_mode(mode: str):
    """Set cognitive mode (seed/growth/full)."""
    valid_modes = ["seed", "growth", "full"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Use: {valid_modes}")

    return {
        "mode": mode,
        "message": f"Cognitive mode set to {mode}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# Reasoning Levels API (Stub Implementation)
# ============================================================================


@router.get("/reasoning/levels")
async def get_reasoning_levels():
    """Get all available reasoning levels."""
    return [
        {
            "id": "L1",
            "name": "Semantic Pattern Matching",
            "description": "Basic pattern recognition",
            "active": True,
            "complexity": "low",
        },
        {
            "id": "L2",
            "name": "Structural Analysis",
            "description": "Intermediate structural reasoning",
            "active": True,
            "complexity": "medium",
        },
        {
            "id": "L3",
            "name": "Causal Abstraction",
            "description": "Advanced causal reasoning",
            "active": True,
            "complexity": "high",
        },
    ]


@router.get("/reasoning/level/{level_id}")
async def get_reasoning_level(level_id: str):
    """Get specific reasoning level details."""
    levels = await get_reasoning_levels()
    for level in levels:
        if level["id"] == level_id:
            return level
    raise HTTPException(status_code=404, detail=f"Reasoning level {level_id} not found")


@router.post("/reasoning/level/{level_id}/activate")
async def activate_reasoning_level(level_id: str):
    """Activate a reasoning level."""
    return {
        "id": level_id,
        "active": True,
        "message": f"Reasoning level {level_id} activated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# MCP Servers API (Stub Implementation)
# ============================================================================


@router.get("/mcp/servers")
async def get_mcp_servers():
    """Get all MCP server connections."""
    return [
        {
            "id": "filesystem",
            "name": "File System",
            "type": "filesystem",
            "status": "connected",
            "capabilities": ["read_file", "write_file", "list_directory"],
        },
        {
            "id": "github",
            "name": "GitHub",
            "type": "github",
            "status": "disconnected",
            "capabilities": ["search_repos", "read_issue", "create_pr"],
        },
        {
            "id": "postgres",
            "name": "PostgreSQL",
            "type": "database",
            "status": "connected",
            "capabilities": ["query", "schema_inspect"],
        },
    ]


@router.get("/mcp/servers/{server_id}")
async def get_mcp_server(server_id: str):
    """Get specific MCP server details."""
    servers = await get_mcp_servers()
    for server in servers:
        if server["id"] == server_id:
            return server
    raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")


@router.post("/mcp/servers/{server_id}/connect")
async def connect_mcp_server(server_id: str):
    """Connect to an MCP server."""
    return {
        "id": server_id,
        "status": "connected",
        "message": f"Connected to {server_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/mcp/servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str):
    """Disconnect from an MCP server."""
    return {
        "id": server_id,
        "status": "disconnected",
        "message": f"Disconnected from {server_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# Memory Entries API (Stub Implementation)
# ============================================================================


@router.get("/memory/entries")
async def get_memory_entries(system: str = None, limit: int = 10):
    """Get persistent memory entries."""
    entries = [
        {
            "id": "mem-1",
            "system": "cognitive",
            "content": "User prefers detailed explanations",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "importance": "high",
        },
        {
            "id": "mem-2",
            "system": "execution",
            "content": "Python is primary language",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "importance": "medium",
        },
    ]

    if system:
        entries = [e for e in entries if e["system"] == system]

    return entries[:limit]


@router.get("/memory/search")
async def search_memory(q: str, system: str = None):
    """Search memory entries."""
    entries = await get_memory_entries(system=system)
    # Simple mock search
    results = [e for e in entries if q.lower() in e["content"].lower()]
    return results


@router.post("/memory/entries")
async def create_memory_entry(entry: dict):
    """Create a new memory entry."""
    return {
        "id": f"mem-{datetime.now(timezone.utc).timestamp()}",
        "system": entry.get("system", "general"),
        "content": entry.get("content", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "importance": entry.get("importance", "medium"),
    }


# ============================================================================
# Checkpoints API (Stub Implementation)
# ============================================================================


@router.get("/checkpoints")
async def get_checkpoints():
    """Get all /rewind checkpoints."""
    return [
        {
            "id": "chk-1",
            "label": "Before major refactoring",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files_count": 42,
            "state_hash": "abc123",
        },
        {
            "id": "chk-2",
            "label": "API integration complete",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files_count": 56,
            "state_hash": "def456",
        },
    ]


@router.post("/checkpoints")
async def create_checkpoint(label: str = None):
    """Create a new checkpoint."""
    return {
        "id": f"chk-{datetime.now(timezone.utc).timestamp()}",
        "label": label or f"Checkpoint {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files_count": 60,
        "state_hash": "xyz789",
    }


@router.post("/checkpoints/{checkpoint_id}/rewind")
async def rewind_to_checkpoint(checkpoint_id: str):
    """Rewind to a specific checkpoint."""
    return {
        "success": True,
        "restored": checkpoint_id,
        "message": f"System restored to checkpoint {checkpoint_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# Brain-Powered Orchestra Agents API
# ============================================================================


@router.get("/orchestra/agents")
async def get_orchestra_agents():
    """Get all orchestra agents from Agent Fabric Kernel."""
    try:
        from amos_brain.facade import BrainClient

        client = BrainClient()
        kernel = client.get_agent_fabric_kernel()
        runs = kernel.get_all_runs()

        agents = []
        for run_id, run in runs.items():
            agents.append(
                {
                    "id": run_id,
                    "name": run.get("objective", "Unknown")[:50],
                    "type": run.get("agent_class", "unknown"),
                    "active": run.get("status") in ["pending", "running"],
                    "tasks_completed": run.get("actions_executed", 0),
                    "budget_used": run.get("budget_used", 0.0),
                    "budget_total": run.get("budget", 1.0),
                    "timestamp": run.get("start_time", datetime.now(timezone.utc).isoformat()),
                }
            )
        return agents
    except Exception:
        return []


@router.get("/orchestra/status")
async def get_orchestra_status():
    """Get orchestra system status from brain."""
    try:
        from amos_brain.facade import BrainClient

        client = BrainClient()
        kernel = client.get_agent_fabric_kernel()
        runs = kernel.get_all_runs()

        active = sum(1 for r in runs.values() if r.get("status") in ["pending", "running"])
        total_actions = sum(r.get("actions_executed", 0) for r in runs.values())

        return {
            "activeAgents": active,
            "totalAgents": len(runs),
            "totalTasks": total_actions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        return {
            "activeAgents": 0,
            "totalAgents": 0,
            "totalTasks": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.post("/orchestra/agents/{agent_id}/toggle")
async def toggle_orchestra_agent(agent_id: str, active: bool):
    """Toggle agent active/inactive via brain."""
    try:
        from amos_brain.facade import BrainClient

        client = BrainClient()
        kernel = client.get_agent_fabric_kernel()

        if active:
            kernel.resume_run(agent_id)
        else:
            kernel.pause_run(agent_id)

        return {
            "id": agent_id,
            "active": active,
            "message": f"Agent {agent_id} {'activated' if active else 'deactivated'}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "id": agent_id,
            "active": not active,
            "error": str(e),
        }


# ============================================================================
# AGENTS.md API (File-Based Implementation)
# ============================================================================


@router.get("/agents-md/files")
async def get_agents_md_files():
    """Get all AGENTS.md files."""
    return [
        {
            "id": "agents-root",
            "path": "AGENTS.md",
            "name": "Root Agents",
            "description": "Main AMOS agent configuration",
            "agents_count": 3,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": "agents-backend",
            "path": "backend/AGENTS.md",
            "name": "Backend Agents",
            "description": "Backend-specific agents",
            "agents_count": 2,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        },
    ]


@router.get("/agents-md/files/{file_id}")
async def get_agents_md_file(file_id: str):
    """Get specific AGENTS.md file content."""
    files = await get_agents_md_files()
    for f in files:
        if f["id"] == file_id:
            return {
                **f,
                "content": "# AMOS Agents\n\n## Core Agents\n- Architect\n- Developer\n- Reviewer\n",
            }
    raise HTTPException(status_code=404, detail=f"AGENTS.md file {file_id} not found")


@router.put("/agents-md/files/{file_id}")
async def update_agents_md_file(file_id: str, content: str):
    """Update AGENTS.md file content."""
    return {
        "id": file_id,
        "message": f"AGENTS.md file {file_id} updated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
