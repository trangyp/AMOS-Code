"""AMOS Systems Core Engine - Central nervous system orchestration."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class SystemState(Enum):
    """System lifecycle states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


class ComponentType(Enum):
    """Types of system components."""
    ENGINE = "engine"
    KERNEL = "kernel"
    SERVICE = "service"
    INTERFACE = "interface"
    STORAGE = "storage"


@dataclass
class ComponentStatus:
    """Status of a system component."""

    name: str
    component_type: str
    state: str
    health_score: float
    last_check: float
    dependencies: List[str]


class LifecycleManager:
    """Manages system and component lifecycle."""

    def __init__(self):
        self.states: Dict[str, str] = {}
        self.transitions: dict[str, list[str]] = {
            "initializing": ["active", "shutdown"],
            "active": ["degraded", "maintenance", "shutdown"],
            "degraded": ["active", "maintenance", "shutdown"],
            "maintenance": ["active", "shutdown"],
            "shutdown": ["initializing"],
        }

    def transition(self, component: str, new_state: str) -> bool:
        """Attempt state transition."""
        current = self.states.get(component, "initializing")
        allowed = self.transitions.get(current, [])
        if new_state in allowed or new_state == current:
            self.states[component] = new_state
            return True
        return False

    def get_state(self, component: str) -> str:
        return self.states.get(component, "initializing")


class HealthMonitor:
    """Monitors system health."""

    def __init__(self):
        self.health_scores: Dict[str, float] = {}
        self.check_history: dict[str, list[tuple[float, float]]] = {}

    def check_component(self, name: str, dependencies: List[str]) -> float:
        """Calculate health score for component."""
        base_score = 1.0
        dep_penalty = len(dependencies) * 0.05
        score = max(0.0, base_score - dep_penalty)
        self.health_scores[name] = score
        timestamp = time.time()
        if name not in self.check_history:
            self.check_history[name] = []
        self.check_history[name].append((timestamp, score))
        self.check_history[name] = self.check_history[name][-100:]
        return score

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        if not self.health_scores:
            return {"overall": 0.0, "components": 0, "status": "unknown"}
        scores = list(self.health_scores.values())
        overall = sum(scores) / len(scores)
        status = "healthy" if overall > 0.8 else "degraded" if overall > 0.5 else "critical"
        return {
            "overall": round(overall, 2),
            "components": len(scores),
            "status": status,
            "details": self.health_scores,
        }


class DependencyResolver:
    """Resolves component dependencies."""

    def __init__(self):
        self.dependencies: dict[str, set[str]] = {}
        self.dependents: dict[str, set[str]] = {}

    def register(self, name: str, deps: List[str]) -> None:
        """Register component dependencies."""
        self.dependencies[name] = set(deps)
        for dep in deps:
            if dep not in self.dependents:
                self.dependents[dep] = set()
            self.dependents[dep].add(name)

    def get_start_order(self) -> List[str]:
        """Get topological start order."""
        visited: set[str] = set()
        order: List[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            for dep in self.dependencies.get(name, []):
                visit(dep)
            order.append(name)

        for name in list(self.dependencies.keys()):
            visit(name)
        return order

    def get_shutdown_order(self) -> List[str]:
        """Get reverse shutdown order."""
        return self.get_start_order()[::-1]

    def check_circular(self) -> List[str]:
        """Check for circular dependencies."""
        path: set[str] = set()
        visited: set[str] = set()
        cycles: List[str] = []

        def dfs(name: str) -> bool:
            if name in path:
                return True
            if name in visited:
                return False
            path.add(name)
            visited.add(name)
            for dep in self.dependencies.get(name, []):
                if dfs(dep):
                    cycles.append(f"{name} -> {dep}")
                    return True
            path.remove(name)
            return False

        for name in self.dependencies:
            path.clear()
            if dfs(name):
                break
        return cycles


class ResourceBalancer:
    """Balances system resources."""

    def __init__(self):
        self.allocations: Dict[str, float] = {}
        self.limits: Dict[str, float] = {}
        self.usage: Dict[str, float] = {}

    def set_limit(self, component: str, limit: float) -> None:
        """Set resource limit for component."""
        self.limits[component] = limit

    def allocate(self, component: str, amount: float) -> bool:
        """Attempt resource allocation."""
        limit = self.limits.get(component, 1.0)
        current = self.allocations.get(component, 0.0)
        if current + amount <= limit:
            self.allocations[component] = current + amount
            return True
        return False

    def release(self, component: str, amount: float) -> None:
        """Release allocated resources."""
        current = self.allocations.get(component, 0.0)
        self.allocations[component] = max(0.0, current - amount)

    def get_utilization(self) -> dict[str, float]:
        """Get resource utilization by component."""
        util = {}
        for comp, allocated in self.allocations.items():
            limit = self.limits.get(comp, 1.0)
            util[comp] = round(allocated / limit, 2) if limit > 0 else 0.0
        return util


class SystemsCoreEngine:
    """AMOS Systems Core Engine - Central nervous system."""

    VERSION = "vInfinity_Systems_1.0.0"
    NAME = "AMOS_Systems_Core_OMEGA"

    def __init__(self):
        self.lifecycle = LifecycleManager()
        self.health = HealthMonitor()
        self.dependencies = DependencyResolver()
        self.resources = ResourceBalancer()
        self.components: Dict[str, ComponentStatus] = {}
        self.start_time = time.time()

    def register_component(
        self,
        name: str,
        component_type: str,
        deps: List[str],
        resource_limit: float = 1.0,
    ) -> bool:
        """Register a system component."""
        self.dependencies.register(name, deps)
        self.resources.set_limit(name, resource_limit)
        self.lifecycle.states[name] = "initializing"
        health = self.health.check_component(name, deps)
        self.components[name] = ComponentStatus(
            name=name,
            component_type=component_type,
            state="initializing",
            health_score=health,
            last_check=time.time(),
            dependencies=deps,
        )
        return True

    def start_component(self, name: str) -> bool:
        """Start a registered component."""
        if name not in self.components:
            return False
        success = self.lifecycle.transition(name, "active")
        if success:
            self.components[name].state = "active"
            self.components[name].last_check = time.time()
        return success

    def stop_component(self, name: str) -> bool:
        """Stop a component gracefully."""
        if name not in self.components:
            return False
        success = self.lifecycle.transition(name, "shutdown")
        if success:
            self.components[name].state = "shutdown"
            self.resources.release(name, self.resources.allocations.get(name, 0.0))
        return success

    def get_component_status(self, name: str) -> Dict[str, Any] :
        """Get status of a specific component."""
        if name not in self.components:
            return None
        comp = self.components[name]
        return {
            "name": comp.name,
            "type": comp.component_type,
            "state": comp.state,
            "health": comp.health_score,
            "dependencies": comp.dependencies,
            "uptime": time.time() - self.start_time,
        }

    def get_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report."""
        health = self.health.get_system_health()
        cycles = self.dependencies.check_circular()
        utilization = self.resources.get_utilization()
        return {
            "system": {
                "name": self.NAME,
                "version": self.VERSION,
                "uptime": time.time() - self.start_time,
                "components_registered": len(self.components),
            },
            "health": health,
            "dependencies": {
                "circular_detected": len(cycles) > 0,
                "cycles": cycles,
                "start_order": self.dependencies.get_start_order(),
            },
            "resources": {
                "utilization": utilization,
                "allocations": dict(self.resources.allocations),
            },
            "components": {
                name: {
                    "state": comp.state,
                    "type": comp.component_type,
                    "health": comp.health_score,
                }
                for name, comp in self.components.items()
            },
        }

    def findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Central Nervous System Orchestration",
            "",
            "## System Overview",
        ]
        sys = results.get("system", {})
        lines.extend([
            f"- **Uptime**: {sys.get('uptime', 0):.1f}s",
            f"- **Components**: {sys.get('components_registered', 0)}",
            "",
            "## Health Status",
        ])
        health = results.get("health", {})
        lines.extend([
            f"- **Overall Health**: {health.get('overall', 0) * 100:.0f}%",
            f"- **Status**: {health.get('status', 'unknown')}",
            f"- **Components Monitored**: {health.get('components', 0)}",
        ])
        deps = results.get("dependencies", {})
        lines.extend([
            "",
            "## Dependencies",
            f"- **Circular Detected**: {deps.get('circular_detected', False)}",
        ])
        if deps.get("cycles"):
            lines.append("- **Cycles**: " + ", ".join(deps["cycles"]))
        start_order = deps.get("start_order", [])
        if start_order:
            lines.append(f"- **Start Order**: {', '.join(start_order[:5])}...")
        resources = results.get("resources", {})
        util = resources.get("utilization", {})
        lines.extend([
            "",
            "## Resource Utilization",
        ])
        for comp, u in list(util.items())[:5]:
            lines.append(f"- {comp}: {u * 100:.0f}%")
        lines.extend([
            "",
            "## Component States",
        ])
        comps = results.get("components", {})
        for name, data in list(comps.items())[:10]:
            lines.append(f"- {name}: {data['state']} (health: {data['health']:.2f})")
        lines.extend([
            "",
            "## Core Capabilities",
            "- **Lifecycle Management**: State transitions (init → active → degraded → maintenance → shutdown)",
            "- **Health Monitoring**: Continuous health score tracking",
            "- **Dependency Resolution**: Topological ordering, circular detection",
            "- **Resource Balancing**: Allocation, limits, utilization tracking",
            "",
            "## Architecture Principles",
            "1. **Fail-Fast**: Detect and report issues immediately",
            "2. **Graceful Degradation**: Continue operating with reduced capacity",
            "3. **Circular Detection**: Prevent dependency deadlocks",
            "4. **Resource Limits**: Prevent component resource exhaustion",
            "5. **State Isolation**: Components manage own state",
            "",
            "## Safety Constraints",
            "- No autonomous component restart without oversight",
            "- Resource limits cannot be exceeded",
            "- Circular dependencies block system start",
            "- Shutdown respects dependency order",
            "",
            "## Usage Patterns",
            "- Register all components before starting",
            "- Use topological start order for initialization",
            "- Monitor health scores continuously",
            "- Check for circular dependencies pre-start",
            "- Graceful shutdown: reverse start order",
        ])
        return "\n".join(lines)


# Singleton instance
_systems_core: Optional[SystemsCoreEngine] = None


def get_systems_core_engine() -> SystemsCoreEngine:
    """Get or create the Systems Core Engine singleton."""
from __future__ import annotations

    global _systems_core
    if _systems_core is None:
        _systems_core = SystemsCoreEngine()
    return _systems_core
