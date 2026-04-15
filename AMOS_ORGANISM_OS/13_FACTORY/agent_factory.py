#!/usr/bin/env python3
"""AMOS Agent Factory (13_FACTORY)
===============================

Creates, monitors, and manages AMOS agents.
Handles agent lifecycle: creation, execution, quality checks, retirement.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentSpec:
    """Specification for creating an agent."""

    name: str
    agent_type: str
    kernel_refs: List[str]
    capabilities: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInstance:
    """Running agent instance."""

    id: str
    spec: AgentSpec
    status: str
    created_at: str
    last_active: str
    execution_count: int = 0
    error_count: int = 0


class AgentFactory:
    """Factory for creating and managing AMOS agents.
    Implements quality monitoring and lifecycle management.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.agents_dir = organism_root / "13_FACTORY" / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        self._registry: Dict[str, AgentInstance] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        """Load existing agent registry."""
        registry_file = self.agents_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for agent_data in data.get("agents", []):
                        spec = AgentSpec(**agent_data["spec"])
                        exec_count = agent_data.get("execution_count", 0)
                        err_count = agent_data.get("error_count", 0)
                        instance = AgentInstance(
                            id=agent_data["id"],
                            spec=spec,
                            status=agent_data["status"],
                            created_at=agent_data["created_at"],
                            last_active=agent_data["last_active"],
                            execution_count=exec_count,
                            error_count=err_count,
                        )
                        self._registry[instance.id] = instance
            except Exception:
                pass

    def create_agent(self, spec: AgentSpec) -> AgentInstance:
        """Create a new agent from specification."""
        agent_id = str(uuid.uuid4())[:8]

        instance = AgentInstance(
            id=agent_id,
            spec=spec,
            status="idle",
            created_at=datetime.utcnow().isoformat() + "Z",
            last_active=datetime.utcnow().isoformat() + "Z",
        )

        self._registry[agent_id] = instance
        self._save_agent_file(instance)
        self._persist_registry()

        print(f"[FACTORY] Created agent {agent_id}: {spec.name}")
        return instance

    def _save_agent_file(self, instance: AgentInstance) -> None:
        """Save agent definition to file."""
        agent_file = self.agents_dir / f"agent_{instance.id}.json"

        data = {
            "id": instance.id,
            "spec": {
                "name": instance.spec.name,
                "agent_type": instance.spec.agent_type,
                "kernel_refs": instance.spec.kernel_refs,
                "capabilities": instance.spec.capabilities,
                "constraints": instance.spec.constraints,
            },
            "status": instance.status,
            "created_at": instance.created_at,
            "last_active": instance.last_active,
            "execution_count": instance.execution_count,
            "error_count": instance.error_count,
        }

        with open(agent_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _persist_registry(self) -> None:
        """Save registry to disk."""
        registry_file = self.agents_dir / "registry.json"

        data = {
            "factory_version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "agent_count": len(self._registry),
            "agents": [
                {
                    "id": a.id,
                    "spec": {
                        "name": a.spec.name,
                        "agent_type": a.spec.agent_type,
                        "kernel_refs": a.spec.kernel_refs,
                        "capabilities": a.spec.capabilities,
                        "constraints": a.spec.constraints,
                    },
                    "status": a.status,
                    "created_at": a.created_at,
                    "last_active": a.last_active,
                    "execution_count": a.execution_count,
                    "error_count": a.error_count,
                }
                for a in self._registry.values()
            ],
        }

        with open(registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID."""
        return self._registry.get(agent_id)

    def list_agents(self, status: Optional[str] = None) -> List[AgentInstance]:
        """List all agents, optionally filtered by status."""
        agents = list(self._registry.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return agents

    def update_status(self, agent_id: str, status: str) -> bool:
        """Update agent status."""
        if agent_id not in self._registry:
            return False

        self._registry[agent_id].status = status
        self._registry[agent_id].last_active = datetime.utcnow().isoformat() + "Z"

        self._save_agent_file(self._registry[agent_id])
        self._persist_registry()
        return True

    def record_execution(self, agent_id: str, success: bool) -> None:
        """Record execution result for quality monitoring."""
        if agent_id not in self._registry:
            return

        agent = self._registry[agent_id]
        agent.execution_count += 1
        if not success:
            agent.error_count += 1

        # Auto-retire agents with too many errors
        if agent.execution_count > 10:
            error_rate = agent.error_count / agent.execution_count
            if error_rate > 0.5:
                agent.status = "retired"
                msg = f"[FACTORY] Agent {agent_id} retired: high error rate"
                print(msg)

        agent.last_active = datetime.utcnow().isoformat() + "Z"
        self._save_agent_file(agent)
        self._persist_registry()

    def get_quality_report(self) -> Dict[str, Any]:
        """Generate quality report for all agents."""
        execs = [a.execution_count for a in self._registry.values()]
        total_execs = sum(execs)
        errors = [a.error_count for a in self._registry.values()]
        total_errors = sum(errors)

        return {
            "total_agents": len(self._registry),
            "active_agents": len([a for a in self._registry.values() if a.status == "idle"]),
            "total_executions": total_execs,
            "total_errors": total_errors,
            "overall_error_rate": (total_errors / total_execs if total_execs > 0 else 0),
            "agents_by_type": self._count_by_type(),
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count agents by type."""
        counts: Dict[str, int] = {}
        for agent in self._registry.values():
            t = agent.spec.agent_type
            counts[t] = counts.get(t, 0) + 1
        return counts

    def create_standard_agents(self) -> List[AgentInstance]:
        """Create standard AMOS agents from registry."""
        registry_path = self.root / "agent_registry.json"

        agents = []
        if registry_path.exists():
            try:
                with open(registry_path, encoding="utf-8") as f:
                    data = json.load(f)

                for agent_id, agent_data in data.get("agents", {}).items():
                    spec = AgentSpec(
                        name=agent_data.get("name", agent_id),
                        agent_type=agent_data.get("type", "worker"),
                        kernel_refs=agent_data.get("kernel_refs", []),
                        capabilities=agent_data.get("functions", []),
                    )
                    agents.append(self.create_agent(spec))
            except Exception as e:
                print(f"[FACTORY] Error loading standard agents: {e}")

        return agents


def main() -> int:
    """CLI for Agent Factory."""
    print("AMOS Agent Factory (13_FACTORY)")
    print("=" * 40)

    # Find organism root
    factory_path = Path(__file__).parent
    organism_root = factory_path.parent

    factory = AgentFactory(organism_root)

    # Create standard agents
    print("\nCreating standard agents from registry...")
    agents = factory.create_standard_agents()

    print(f"\nCreated {len(agents)} agents")

    # Show quality report
    report = factory.get_quality_report()
    print("\nQuality Report:")
    print(f"  Total agents: {report['total_agents']}")
    print(f"  Active: {report['active_agents']}")
    print(f"  By type: {report['agents_by_type']}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
