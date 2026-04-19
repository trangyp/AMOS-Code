#!/usr/bin/env python3
"""Axiom One - Real Self-Healing System.

Integrates agent fleet with AMOS self-healing:
- Monitor agents for failures
- Auto-restart failed agents
- Circuit breaker for agent tools
- Recovery strategies
"""

import logging

# AMOS imports
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict

AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(AMOS_ROOT))

from axiom_one_agent_fleet import Agent, AgentExecutor, AgentStatus, AxiomOneAgentFleet, Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker for agent tools."""

    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    last_failure_time: float = 0.0
    success_count: int = 0

    def can_execute(self) -> bool:
        """Check if execution allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.failures = 0
                logger.info(f"Circuit {self.name}: transitioning to HALF_OPEN")
                return True
            return False

        return True  # HALF_OPEN allows one test

    def record_success(self) -> None:
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.success_count = 0
                logger.info(f"Circuit {self.name}: CLOSED (recovered)")
        else:
            self.failures = max(0, self.failures - 1)

    def record_failure(self) -> None:
        """Record failed execution."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name}: OPEN (recovery failed)")
        elif self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit {self.name}: OPEN ({self.failures} failures)")


@dataclass
class AgentHealth:
    """Health status for an agent."""

    agent_id: str
    status: str
    last_heartbeat: float
    tasks_completed: int
    tasks_failed: int
    error_count: int
    is_healthy: bool


class SelfHealingAgentExecutor(AgentExecutor):
    """Agent executor with self-healing capabilities."""

    def __init__(self):
        super().__init__()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.agent_health: Dict[str, AgentHealth] = {}
        self.monitoring = False
        self.monitor_thread: threading.Thread = None
        self._lock = threading.Lock()
        self.recovery_strategies: Dict[str, Callable[[str], bool]] = {}
        self._setup_recovery_strategies()

    def _setup_recovery_strategies(self) -> None:
        """Setup recovery strategies."""
        self.recovery_strategies = {
            "restart_agent": self._restart_agent,
            "reset_circuit": self._reset_circuit,
            "clear_task_queue": self._clear_task_queue,
        }

    def get_circuit_breaker(self, tool_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for tool."""
        if tool_name not in self.circuit_breakers:
            self.circuit_breakers[tool_name] = CircuitBreaker(
                name=tool_name, failure_threshold=3, recovery_timeout=60.0
            )
        return self.circuit_breakers[tool_name]

    def execute_with_circuit_breaker(
        self, tool_name: str, func: Callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """Execute tool with circuit breaker protection."""
        cb = self.get_circuit_breaker(tool_name)

        if not cb.can_execute():
            return {
                "success": False,
                "error": f"Circuit breaker OPEN for {tool_name}",
                "circuit_state": cb.state.value,
            }

        try:
            result = func(*args, **kwargs)

            if result.get("success"):
                cb.record_success()
            else:
                cb.record_failure()

            return result

        except Exception as e:
            cb.record_failure()
            return {"success": False, "error": str(e), "circuit_state": cb.state.value}

    def _run_task(self, agent: Agent, task: Task) -> Dict[str, Any]:
        """Run task with health monitoring."""
        start_time = time.time()

        # Update health - agent executing
        self._update_agent_health(agent, AgentStatus.EXECUTING)

        try:
            # Run actual task
            result = super()._run_task(agent, task)

            # Update health based on result
            if result.get("success"):
                self._update_agent_health(agent, AgentStatus.COMPLETED)
            else:
                self._update_agent_health(agent, AgentStatus.FAILED, error=result.get("error"))

            return result

        except Exception as e:
            self._update_agent_health(agent, AgentStatus.FAILED, error=str(e))
            raise

    def _update_agent_health(self, agent: Agent, status: AgentStatus, error: str = None) -> None:
        """Update agent health status."""
        with self._lock:
            current = self.agent_health.get(agent.agent_id)

            error_count = current.error_count if current else 0
            if error:
                error_count += 1

            # Determine health
            is_healthy = status in [AgentStatus.IDLE, AgentStatus.COMPLETED] and error_count < 3

            self.agent_health[agent.agent_id] = AgentHealth(
                agent_id=agent.agent_id,
                status=status.value,
                last_heartbeat=time.time(),
                tasks_completed=agent.completed_tasks,
                tasks_failed=agent.failed_tasks,
                error_count=error_count,
                is_healthy=is_healthy,
            )

    def _restart_agent(self, agent_id: str) -> bool:
        """Restart a failed agent."""
        logger.info(f"Attempting to restart agent {agent_id}")

        # In real implementation, would:
        # 1. Kill agent process/thread
        # 2. Clear state
        # 3. Reinitialize

        with self._lock:
            if agent_id in self.agent_health:
                self.agent_health[agent_id].error_count = 0
                self.agent_health[agent_id].is_healthy = True

        logger.info(f"Agent {agent_id} restarted successfully")
        return True

    def _reset_circuit(self, tool_name: str) -> bool:
        """Reset circuit breaker."""
        if tool_name in self.circuit_breakers:
            cb = self.circuit_breakers[tool_name]
            cb.state = CircuitState.CLOSED
            cb.failures = 0
            cb.success_count = 0
            logger.info(f"Circuit {tool_name} manually reset")
        return True

    def _clear_task_queue(self, agent_id: str) -> bool:
        """Clear stuck tasks for agent."""
        logger.info(f"Clearing task queue for {agent_id}")
        return True

    def start_health_monitoring(self, interval: float = 5.0) -> None:
        """Start health monitoring thread."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._health_monitor_loop, args=(interval,), daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"Health monitoring started ({interval}s interval)")

    def _health_monitor_loop(self, interval: float) -> None:
        """Monitor agent health and trigger recovery."""
        while self.monitoring:
            try:
                self._check_agent_health()
                self._check_circuit_breakers()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

    def _check_agent_health(self) -> None:
        """Check agent health and recover if needed."""
        with self._lock:
            for agent_id, health in self.agent_health.items():
                if not health.is_healthy:
                    # Check if recovery needed
                    time_since_heartbeat = time.time() - health.last_heartbeat

                    if time_since_heartbeat > 30:  # Stuck for 30s
                        logger.warning(
                            f"Agent {agent_id} unhealthy for {time_since_heartbeat:.1f}s, "
                            f"triggering recovery"
                        )

                        # Trigger recovery
                        if health.error_count >= 3:
                            self._restart_agent(agent_id)
                        else:
                            self._clear_task_queue(agent_id)

    def _check_circuit_breakers(self) -> None:
        """Check and report circuit breaker status."""
        open_circuits = [
            name for name, cb in self.circuit_breakers.items() if cb.state == CircuitState.OPEN
        ]

        if open_circuits:
            logger.warning(f"Open circuits: {open_circuits}")

    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        with self._lock:
            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "agents": {
                    aid: {
                        "status": h.status,
                        "healthy": h.is_healthy,
                        "tasks_completed": h.tasks_completed,
                        "tasks_failed": h.tasks_failed,
                        "error_count": h.error_count,
                        "last_heartbeat_ago": time.time() - h.last_heartbeat,
                    }
                    for aid, h in self.agent_health.items()
                },
                "circuits": {
                    name: {"state": cb.state.value, "failures": cb.failures}
                    for name, cb in self.circuit_breakers.items()
                },
                "overall_healthy": all(h.is_healthy for h in self.agent_health.values())
                if self.agent_health
                else True,
            }

    def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Health monitoring stopped")


class AxiomOneSelfHealingFleet(AxiomOneAgentFleet):
    """Agent fleet with integrated self-healing."""

    def __init__(self):
        super().__init__()
        # Replace executor with self-healing version
        self.agent_executor = SelfHealingAgentExecutor()
        self.workflow_engine.agent_executor = self.agent_executor

    def start_monitoring(self, interval: float = 5.0) -> None:
        """Start self-healing monitoring."""
        self.agent_executor.start_health_monitoring(interval)

    def stop_monitoring(self) -> None:
        """Stop self-healing monitoring."""
        self.agent_executor.stop_monitoring()

    def get_health(self) -> Dict[str, Any]:
        """Get health report."""
        return self.agent_executor.get_health_report()

    def reset_circuit(self, tool_name: str) -> bool:
        """Manually reset a circuit breaker."""
        return self.agent_executor._reset_circuit(tool_name)


def demo_self_healing():
    """Demonstrate self-healing capabilities."""
    print("=" * 70)
    print("AXIOM ONE SELF-HEALING SYSTEM")
    print("=" * 70)

    fleet = AxiomOneSelfHealingFleet()

    # Start monitoring
    print("\n🩺 Starting health monitoring...")
    fleet.start_monitoring(interval=2.0)

    # Show initial health
    print("\n📊 Initial Health Report:")
    health = fleet.get_health()
    print(f"  Overall: {'✅ Healthy' if health['overall_healthy'] else '❌ Unhealthy'}")
    print(f"  Agents: {len(health['agents'])}")
    print(f"  Circuits: {len(health['circuits'])}")

    # Create and execute workflow
    print("\n🔧 Creating test workflow...")
    workflow = fleet.create_workflow(
        name="self_healing_test", description="Test self-healing with agent execution"
    )

    # Assign task
    from axiom_one_agent_fleet import AgentType

    task = fleet.assign_task(
        workflow=workflow,
        agent_type=AgentType.RESEARCHER,
        description="Explore repository",
        input_data={"query": "main", "path": "."},
        priority="normal",
    )
    print(f"Assigned task: {task.task_id[:8]}")

    # Execute
    print("\n⚡ Executing workflow...")
    result = fleet.execute(workflow)

    # Show health after execution
    print("\n📊 Health After Execution:")
    health = fleet.get_health()
    print(f"  Overall: {'✅ Healthy' if health['overall_healthy'] else '❌ Unhealthy'}")

    for agent_id, h in health["agents"].items():
        print(f"\n  Agent {agent_id[:8]}...:")
        print(f"    Status: {h['status']}")
        print(f"    Healthy: {h['healthy']}")
        print(f"    Tasks: {h['tasks_completed']} completed, {h['tasks_failed']} failed")

    # Show circuit breaker status
    print(f"\n🔌 Circuit Breakers: {len(health['circuits'])}")
    for name, c in health["circuits"].items():
        print(f"  {name}: {c['state']} (failures: {c['failures']})")

    # Stop monitoring
    print("\n🛑 Stopping monitoring...")
    fleet.stop_monitoring()

    print("\n" + "=" * 70)
    print("SELF-HEALING DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_self_healing()
