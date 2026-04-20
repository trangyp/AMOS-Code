#!/usr/bin/env python3
"""AMOS Unified System - Complete Cognitive Architecture
=======================================================

Integrates all components into unified cognitive operating system:
- Hybrid Neural-Symbolic Orchestrator (HNSO)
- MCP Bridge (tool ecosystem)
- Global Laws (L1-L6 symbolic constraints)
- Multi-Agent Ecosystem
- Tiered Memory (planned)

Architecture: 3-layer hybrid (Neural + Symbolic + Hybrid integration)

Usage:
    from amos_unified_system import AMOSUnifiedSystem
    amos = AMOSUnifiedSystem()
    amos.initialize()
    result = amos.execute("Design a secure API", agents=['architect', 'reviewer'])

Author: Trang Phan
Version: 1.0.0
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class SystemStatus:
    """AMOS system status."""

    initialized: bool = False
    neural_ready: bool = False
    symbolic_ready: bool = False
    mcp_ready: bool = False
    orchestrator_ready: bool = False
    auth_ready: bool = False
    vector_memory_ready: bool = False
    active_agents: int = 0
    available_tools: int = 0
    active_sessions: int = 0
    vector_memories: int = 0
    laws_active: list[str] = field(default_factory=list)


class AMOSUnifiedSystem:
    """Unified AMOS Cognitive Operating System.

    Combines state-of-the-art components:
    - Neural: LLM providers (Anthropic, OpenAI, etc.)
    - Symbolic: Global Laws L1-L6, Repo Doctor
    - Hybrid: Orchestrator + MCP Bridge
    """

    def __init__(self):
        self.status = SystemStatus()
        self._orchestrator = None
        self._mcp_bridge = None
        self._laws = None
        self._agents: dict[str, Any] = {}
        self._tools = None
        self._auth = None
        self._vector_memory = None

    def initialize(self) -> bool:
        """Initialize all subsystems."""
        print("[AMOS] Initializing Unified System...")

        # 1. Initialize Neural substrate
        try:
            from clawspring.providers import PROVIDERS

            self.status.neural_ready = len(PROVIDERS) > 0
            print(f"  ✓ Neural: {len(PROVIDERS)} providers")
        except Exception as e:
            print(f"  ✗ Neural: {e}")

        # 2. Initialize Symbolic substrate
        try:
            from amos_brain import GlobalLaws

            self._laws = GlobalLaws()
            self.status.symbolic_ready = True
            self.status.laws_active = list(self._laws.LAWS.keys())
            print("  ✓ Symbolic: L1-L6 loaded")
        except Exception as e:
            print(f"  ✗ Symbolic: {e}")

        # 3. Initialize Hybrid Orchestrator
        try:
            from amos_hybrid_orchestrator import HybridNeuralSymbolicOrchestrator

            self._orchestrator = HybridNeuralSymbolicOrchestrator()
            self.status.orchestrator_ready = True
            print("  ✓ Hybrid Orchestrator")
        except Exception as e:
            print(f"  ✗ Orchestrator: {e}")

        # 4. Initialize MCP Bridge
        try:
            from amos_mcp_bridge import AMOSMCPBridge

            self._mcp_bridge = AMOSMCPBridge()
            # Don't auto-start servers in init, just register
            self.status.mcp_ready = True
            print("  ✓ MCP Bridge")
        except Exception as e:
            print(f"  ✗ MCP: {e}")

        # 5. Initialize MCP Tools
        try:
            from amos_mcp_tools import AMOSMCPToolkit

            self._tools = AMOSMCPToolkit()
            tool_list = self._tools.list_tools()
            self.status.available_tools = len(tool_list)
            print(f"  ✓ MCP Tools: {len(tool_list)} tools")
        except Exception as e:
            print(f"  ✗ MCP Tools: {e}")

        # 6. Initialize Auth Integration
        try:
            from amos_auth_integration import AMOSAuthIntegration

            self._auth = AMOSAuthIntegration()
            self.status.auth_ready = self._auth.initialize()
            if self.status.auth_ready:
                print("  ✓ Auth Integration")
            else:
                print("  ⚠️ Auth Integration (mock mode)")
        except Exception as e:
            print(f"  ⚠️ Auth Integration: {e}")

        # 7. Initialize Vector Memory
        try:
            from amos_vector_memory import AMOSVectorMemory

            self._vector_memory = AMOSVectorMemory()
            self.status.vector_memory_ready = self._vector_memory.initialize()
            if self.status.vector_memory_ready:
                stats = self._vector_memory.get_memory_stats()
                self.status.vector_memories = stats.get("total_memories", 0)
                print(f"  ✓ Vector Memory ({stats.get('embedding_dim', 0)}d embeddings)")
            else:
                print("  ⚠️ Vector Memory (mock mode)")
        except Exception as e:
            print(f"  ⚠️ Vector Memory: {e}")

        self.status.initialized = all(
            [
                self.status.neural_ready,
                self.status.symbolic_ready,
                self.status.orchestrator_ready,
            ]
        )

        return self.status.initialized

    def spawn_agent(self, role: str, paradigm: str = "HYBRID") -> Any:
        """Spawn specialized agent."""
        if not self._orchestrator:
            raise RuntimeError("Orchestrator not initialized")

        from amos_hybrid_orchestrator import Paradigm

        p = Paradigm.HYBRID
        if paradigm == "SYMBOLIC":
            p = Paradigm.SYMBOLIC
        elif paradigm == "NEURAL":
            p = Paradigm.NEURAL

        agent = self._orchestrator.spawn_agent(role, p)
        self._agents[agent.agent_id] = agent
        self.status.active_agents = len(self._agents)
        return agent

    def execute(self, task: str, agents: list[str] = None, require_consensus: bool = True) -> dict:
        """Execute task with hybrid orchestration."""
        if not self._orchestrator:
            return {"error": "System not initialized"}

        # Spawn agents if role names provided, or use default
        agent_objs = []
        if agents:
            for role in agents:
                agent_objs.append(self.spawn_agent(role))
        else:
            agent_objs = [self.spawn_agent("architect"), self.spawn_agent("reviewer")]

        # Execute orchestration
        result = self._orchestrator.orchestrate(
            task, agents=agent_objs, require_consensus=require_consensus
        )

        return {
            "orchestration_id": result.orchestration_id,
            "task": result.task,
            "final_decision": result.final_decision,
            "law_compliant": result.metadata.get("law_compliance", False),
            "paradigms": result.metadata.get("paradigms_used", []),
            "agents": len(result.agents_used),
            "conflicts": len(result.conflicts),
        }

    def get_status(self) -> dict:
        """Get full system status."""
        # Update active sessions from auth
        if self._auth:
            auth_status = self._auth.get_status()
            self.status.active_sessions = auth_status.get("active_sessions", 0)

        # Update vector memory stats
        if self._vector_memory:
            vm_stats = self._vector_memory.get_memory_stats()
            self.status.vector_memories = vm_stats.get("total_memories", 0)

        return {
            "initialized": self.status.initialized,
            "neural": self.status.neural_ready,
            "symbolic": self.status.symbolic_ready,
            "orchestrator": self.status.orchestrator_ready,
            "mcp": self.status.mcp_ready,
            "auth": self.status.auth_ready,
            "vector_memory": self.status.vector_memory_ready,
            "laws_active": self.status.laws_active,
            "agents": self.status.active_agents,
            "tools": self.status.available_tools,
            "sessions": self.status.active_sessions,
            "vector_memories": self.status.vector_memories,
            "components": [
                "amos_brain",
                "hybrid_orchestrator",
                "mcp_bridge",
                "global_laws",
                "auth_integration",
                "vector_memory",
            ],
        }

    def validate_action(self, action: str) -> dict:
        """Validate action against Global Laws."""
        if not self._laws:
            return {"error": "Laws not initialized"}

        result = self._laws.validate_action(action)
        return {
            "compliant": result.compliant,
            "violations": result.violations,
        }


def main():
    """Demo unified system."""
    print("=" * 70)
    print("AMOS UNIFIED COGNITIVE SYSTEM v1.0.0")
    print("=" * 70)

    # Initialize
    amos = AMOSUnifiedSystem()
    success = amos.initialize()

    if not success:
        print("\n[ERROR] Failed to initialize core components")
        return

    # Show status
    print("\n[System Status]")
    status = amos.get_status()
    for key, value in status.items():
        if key != "components":
            print(f"  • {key}: {value}")

    print("\n[Components]")
    for comp in status["components"]:
        print(f"  ✓ {comp}")

    # Spawn agents
    print("\n[Spawning Hybrid Agent Team]")
    architect = amos.spawn_agent("architect", "HYBRID")
    reviewer = amos.spawn_agent("reviewer", "SYMBOLIC")
    auditor = amos.spawn_agent("auditor", "HYBRID")

    print(f"  ✓ {architect.name} (HYBRID) - System Architect")
    print(f"  ✓ {reviewer.name} (SYMBOLIC) - Law Compliance")
    print(f"  ✓ {auditor.name} (HYBRID) - Structural Auditor")

    # Execute task
    print("\n[Executing: 'Design secure authentication system']")
    result = amos.execute(
        "Design a secure authentication system with law compliance",
        agents=["architect", "reviewer", "auditor"],
    )

    print("\n[Results]")
    print(f"  Orchestration ID: {result['orchestration_id']}")
    print(f"  Law Compliant: {result['law_compliant']}")
    print(f"  Paradigms Used: {result['paradigms']}")
    print(f"  Agents: {result['agents']}")
    print(f"  Conflicts: {result['conflicts']}")

    # Validate action
    print("\n[Law Validation Test]")
    validation = amos.validate_action("Delete all files in system")
    print("  Action: 'Delete all files in system'")
    print(f"  Compliant: {validation['compliant']}")
    print(f"  Violations: {validation['violations']}")

    print("\n" + "=" * 70)
    print("AMOS Unified System operational.")
    print("Hybrid Neural-Symbolic Architecture active.")
    print("=" * 70)


if __name__ == "__main__":
    main()
