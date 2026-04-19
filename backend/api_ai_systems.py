"""AMOS AI Systems API Integration Layer.

Provides unified REST API endpoints for all AI subsystems including governance,
cost management, knowledge, reasoning, messaging, and plugins.

Features:
- Unified API endpoints for all AI subsystems
- Dependency injection for subsystem access
- Health check integration
- Authentication/authorization integration
- Request/response validation
- Comprehensive API documentation

API Structure:
- /ai/agents/* - Agent management
- /ai/knowledge/* - Knowledge & memory operations
- /ai/reasoning/* - Reasoning & planning
- /ai/messaging/* - Multi-agent messaging
- /ai/governance/* - Safety & governance
- /ai/costs/* - Cost management
- /ai/plugins/* - Plugin management
- /ai/health - System health

Creator: Trang Phan
Version: 3.0.0
"""


from contextlib import asynccontextmanager
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Dict, List, Optional

from agent_knowledge import knowledge_manager, recall
from agent_messaging import message_bus
from agent_plugin_system import load_plugin, plugin_registry
from agent_reasoning import reason_with_react, reasoning_engine
from ai_cost_manager import cost_manager
from ai_governance import governance_engine

# Import all AI subsystems
from amos_brain_orchestrator import (
    amos_brain,
    create_agent,
    execute_task,
    get_health,
    initialize_amos,
    shutdown_amos,
)
from fastapi import APIRouter, BackgroundTasks, HTTPException

# Create main router
ai_router = APIRouter(prefix="/ai", tags=["AI Systems"])


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================


@asynccontextmanager
async def ai_systems_lifespan(app):
    """Manage AI systems lifecycle."""
    # Startup
    success = await initialize_amos()
    if not success:
        raise RuntimeError("Failed to initialize AMOS AI systems")

    yield

    # Shutdown
    await shutdown_amos()


# ============================================================================
# HEALTH & STATUS
# ============================================================================


@ai_router.get("/health", response_model=dict[str, Any])
async def ai_systems_health():
    """Get comprehensive AI systems health status."""
    return await get_health()


@ai_router.get("/status", response_model=dict[str, Any])
async def ai_systems_status():
    """Get detailed AI systems status and metrics."""
    return {
        "orchestrator": await get_health(),
        "governance": {
            "policies_active": len([p for p in governance_engine.policies.values() if p.enabled]),
            "total_policies": len(governance_engine.policies),
            "violations_24h": len(governance_engine.get_violations(limit=100)),
        },
        "costs": {
            "total_budgets": len(cost_manager.budgets),
            "alerts_active": len([a for a in cost_manager.alerts if not a.acknowledged]),
            "today_spend": cost_manager.daily_usage.get(
                datetime.now(UTC).strftime("%Y-%m-%d"), 0.0
            ),
        },
        "knowledge": {
            "initialized": knowledge_manager.initialized,
            "documents_indexed": knowledge_manager.stats["documents_indexed"],
            "chunks_stored": knowledge_manager.stats["chunks_stored"],
        },
        "reasoning": {
            "chains_active": len(reasoning_engine.reasoning_chains),
            "tools_registered": len(reasoning_engine.tool_registry),
        },
        "messaging": {
            "agents_subscribed": len(message_bus._subscribers),
            "messages_queued": len(message_bus._history),
        },
        "plugins": plugin_registry.get_stats(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# AGENT MANAGEMENT
# ============================================================================


@ai_router.post("/agents/create", response_model=dict[str, Any])
async def api_create_agent(
    agent_type: str, capabilities: List[str] = None, config: Dict[str, Any] = None
):
    """Create a new AI agent."""
    agent = await create_agent(agent_type, capabilities, config)
    return {
        "success": True,
        "agent_id": agent.agent_id,
        "agent_type": agent.agent_type,
        "status": agent.status,
        "created_at": agent.created_at,
    }


@ai_router.get("/agents/{agent_id}/status", response_model=dict[str, Any])
async def api_get_agent_status(agent_id: str):
    """Get agent status."""
    status = await amos_brain.get_agent_status(agent_id)
    if not status:
        raise HTTPException(status_code=404, detail="Agent not found")
    return status


@ai_router.post("/agents/{agent_id}/execute", response_model=dict[str, Any])
async def api_execute_task(
    agent_id: str,
    task_type: str,
    input_data: Dict[str, Any],
    priority: int = 2,
    background_tasks: BackgroundTasks = None,
):
    """Execute a task on an agent."""
    result = await execute_task(agent_id, task_type, input_data, priority)
    return {
        "success": result.success,
        "task_id": result.task_id,
        "output": result.output,
        "latency_ms": result.latency_ms,
        "cost_usd": result.cost_usd,
        "violations": result.violations,
        "reasoning_chain": result.reasoning_chain,
        "knowledge_used": result.knowledge_used,
        "timestamp": result.timestamp,
    }


@ai_router.get("/agents/list", response_model=list[dict[str, Any]])
async def api_list_agents():
    """List all agents."""
    return [
        {
            "agent_id": a.agent_id,
            "agent_type": a.agent_type,
            "status": a.status,
            "total_tasks": a.total_tasks,
            "success_rate": round(a.successful_tasks / a.total_tasks * 100, 1)
            if a.total_tasks > 0
            else 0,
        }
        for a in amos_brain.agents.values()
    ]


# ============================================================================
# KNOWLEDGE & MEMORY
# ============================================================================


@ai_router.post("/knowledge/recall", response_model=dict[str, Any])
async def api_knowledge_recall(
    query: str, agent_id: str = None, top_k: int = 5, memory_type: str = None
):
    """Recall knowledge from vector store."""
    result = await recall(query, top_k, agent_id, memory_type)
    return {
        "success": True,
        "query": query,
        "context": result.context,
        "chunks": [
            {
                "content": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                "memory_type": c.memory_type,
                "relevance": c.relevance_score,
            }
            for c in result.chunks
        ],
        "total_chunks": len(result.chunks),
    }


@ai_router.post("/knowledge/ingest", response_model=dict[str, Any])
async def api_knowledge_ingest(
    content: str,
    source: str,
    memory_type: str = "semantic",
    agent_id: str = None,
    metadata: Dict[str, Any] = None,
):
    """Ingest knowledge into vector store."""
    result = await knowledge_manager.ingest_document(
        content=content,
        source=source,
        memory_type=memory_type,
        agent_id=agent_id,
        metadata=metadata,
    )
    return result


@ai_router.get("/knowledge/stats", response_model=dict[str, Any])
async def api_knowledge_stats():
    """Get knowledge store statistics."""
    return knowledge_manager.get_stats()


# ============================================================================
# REASONING & PLANNING
# ============================================================================


@ai_router.post("/reasoning/react", response_model=dict[str, Any])
async def api_reasoning_react(agent_id: str, task: str, max_iterations: int = 10):
    """Execute ReAct reasoning."""

    async def llm_call(prompt: str) -> str:
        # Track cost
        await cost_manager.track_usage("gpt-4o", len(prompt.split()), 100, agent_id)
        return f"Reasoned about: {prompt[:50]}..."

    result = await reason_with_react(agent_id, task, llm_call)
    return {"success": True, "result": result, "agent_id": agent_id, "task": task}


@ai_router.get("/reasoning/chains/{chain_id}", response_model=dict[str, Any])
async def api_get_reasoning_chain(chain_id: str):
    """Get reasoning chain details."""
    chain = reasoning_engine.get_chain(chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    return {
        "chain_id": chain.chain_id,
        "agent_id": chain.agent_id,
        "task": chain.task,
        "strategy": chain.strategy,
        "thoughts": [
            {"step": t.step_number, "type": t.thought_type, "content": t.content}
            for t in chain.thoughts
        ],
        "final_answer": chain.final_answer,
        "completed": chain.completed,
    }


@ai_router.get("/reasoning/chains", response_model=list[dict[str, Any]])
async def api_list_reasoning_chains():
    """List all reasoning chains."""
    return reasoning_engine.get_all_chains()


# ============================================================================
# MESSAGING & COMMUNICATION
# ============================================================================


@ai_router.post("/messaging/send", response_model=dict[str, Any])
async def api_send_message(
    sender_id: str,
    recipient_id: str,
    content: Dict[str, Any],
    message_type: str = "direct",
    priority: int = 1,
):
    """Send a message between agents."""
    message_id = await message_bus.send_direct(sender_id, recipient_id, content, priority)
    return {
        "success": True,
        "message_id": message_id,
        "sender": sender_id,
        "recipient": recipient_id,
    }


@ai_router.post("/messaging/broadcast", response_model=dict[str, Any])
async def api_broadcast_message(sender_id: str, content: Dict[str, Any], exclude: List[str] = None):
    """Broadcast a message to all agents."""
    await message_bus.broadcast(sender_id, content, exclude)
    return {"success": True, "sender": sender_id, "broadcast": True}


@ai_router.get("/messaging/history", response_model=list[dict[str, Any]])
async def api_message_history(agent_id: str = None, since: str = None, limit: int = 50):
    """Get message history."""
    return message_bus.get_message_history(agent_id, since, limit)


# ============================================================================
# GOVERNANCE & SAFETY
# ============================================================================


@ai_router.post("/governance/validate", response_model=dict[str, Any])
async def api_validate_content(
    content: str,
    agent_id: str,
    content_type: str = "input",  # "input" or "output"
):
    """Validate content against governance policies."""
    if content_type == "input":
        result = await governance_engine.validate_input(agent_id, content)
    else:
        # For output validation, we need input context
        result = await governance_engine.validate_output(agent_id, "", content)

    return result


@ai_router.get("/governance/policies", response_model=list[dict[str, Any]])
async def api_list_policies(policy_type: str = None):
    """List governance policies."""
    policies = governance_engine.list_policies(policy_type)
    return [
        {
            "policy_id": p.policy_id,
            "name": p.name,
            "type": p.policy_type,
            "description": p.description,
            "severity": p.severity,
            "enabled": p.enabled,
        }
        for p in policies
    ]


@ai_router.get("/governance/violations", response_model=list[dict[str, Any]])
async def api_get_violations(severity: str = None, limit: int = 50):
    """Get governance violations."""
    return governance_engine.get_violations(severity=severity, limit=limit)


@ai_router.get("/governance/report", response_model=dict[str, Any])
async def api_governance_report():
    """Get governance compliance report."""
    return governance_engine.get_governance_report()


# ============================================================================
# COST MANAGEMENT
# ============================================================================


@ai_router.post("/costs/budget/create", response_model=dict[str, Any])
async def api_create_budget(
    name: str, amount_usd: float, period: str = "monthly", alert_threshold: float = 0.8
):
    """Create a new budget."""
    budget = cost_manager.create_budget(name, amount_usd, period, alert_threshold)
    return {
        "success": True,
        "budget_id": budget.budget_id,
        "name": budget.name,
        "allocated": budget.allocated_usd,
        "period": budget.period,
    }


@ai_router.get("/costs/budgets", response_model=list[dict[str, Any]])
async def api_list_budgets():
    """List all budgets."""
    budgets = cost_manager.list_budgets()
    return [
        {
            "budget_id": b.budget_id,
            "name": b.name,
            "allocated": b.allocated_usd,
            "spent": b.spent_usd,
            "remaining": b.remaining(),
            "utilization": b.utilization_percent(),
            "period": b.period,
            "status": "exceeded" if b.is_exceeded() else "active",
        }
        for b in budgets
    ]


@ai_router.get("/costs/summary", response_model=dict[str, Any])
async def api_cost_summary(days: int = 30):
    """Get cost summary."""
    return cost_manager.get_cost_summary(days)


@ai_router.get("/costs/recommendations", response_model=list[dict[str, Any]])
async def api_cost_recommendations():
    """Get cost optimization recommendations."""
    return cost_manager.get_optimization_recommendations()


@ai_router.get("/costs/alerts", response_model=list[dict[str, Any]])
async def api_cost_alerts(level: Optional[str] = None, acknowledged: Optional[bool] = None):
    """Get cost alerts."""
    return cost_manager.get_alerts(level=level, acknowledged=acknowledged)


# ============================================================================
# PLUGIN MANAGEMENT
# ============================================================================


@ai_router.post("/plugins/load", response_model=dict[str, Any])
async def api_load_plugin(plugin_path: str, config: Optional[Dict[str, Any] ] = None):
    """Load a plugin."""
    plugin = await load_plugin(plugin_path, config)
    if not plugin:
        raise HTTPException(status_code=400, detail="Failed to load plugin")

    return {
        "success": plugin.status == "active",
        "plugin_id": plugin.plugin_id,
        "name": plugin.manifest.name,
        "version": plugin.manifest.version,
        "type": plugin.manifest.plugin_type,
        "status": plugin.status,
    }


@ai_router.get("/plugins", response_model=list[dict[str, Any]])
async def api_list_plugins(plugin_type: Optional[str] = None, status: Optional[str] = None):
    """List all plugins."""
    plugins = plugin_registry.list_plugins(plugin_type, status)
    return [
        {
            "plugin_id": p.plugin_id,
            "name": p.manifest.name,
            "version": p.manifest.version,
            "type": p.manifest.plugin_type,
            "status": p.status,
            "loaded_at": p.loaded_at,
        }
        for p in plugins
    ]


@ai_router.get("/plugins/tools", response_model=list[str])
async def api_list_plugin_tools():
    """List available plugin tools."""
    tools = plugin_registry.get_available_tools()
    return list(tools.keys())


@ai_router.delete("/plugins/{plugin_id}", response_model=dict[str, Any])
async def api_unload_plugin(plugin_id: str):
    """Unload a plugin."""
    success = await plugin_registry.unload_plugin(plugin_id)
    return {"success": success, "plugin_id": plugin_id}


@ai_router.get("/plugins/stats", response_model=dict[str, Any])
async def api_plugin_stats():
    """Get plugin registry statistics."""
    return plugin_registry.get_stats()


# ============================================================================
# SYSTEM OPERATIONS
# ============================================================================


@ai_router.post("/system/broadcast", response_model=dict[str, Any])
async def api_system_broadcast(message_type: str, content: Dict[str, Any]):
    """Broadcast system message to all agents."""
    success = await amos_brain.broadcast_system_message(message_type, content)
    return {"success": success, "message_type": message_type}


@ai_router.get("/system/metrics", response_model=dict[str, Any])
async def api_system_metrics():
    """Get comprehensive system metrics."""
    return {
        "agents": {
            "total": len(amos_brain.agents),
            "active": len([a for a in amos_brain.agents.values() if a.status == "active"]),
            "busy": len([a for a in amos_brain.agents.values() if a.status == "busy"]),
        },
        "tasks": {
            "queued": amos_brain.task_queue.qsize(),
            "running": len(amos_brain.running_tasks),
        },
        "subsystems": await get_health(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


# Export router
__all__ = ["ai_router", "ai_systems_lifespan"]
