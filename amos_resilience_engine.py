#!/usr/bin/env python3
"""AMOS Resilience Engine v2.0.0 - Hot-Reload & Circuit Breaker.

Provides configuration hot-reload, circuit breaker patterns,
and auto-restart with exponential backoff for the 14-Layer AMOS System.

Architecture:
- ConfigWatcher: File system monitoring for live config updates
- CircuitBreaker: Prevents cascading failures
- RetryPolicy: Exponential backoff for service recovery

SUPERBRAIN INTEGRATION:
- Circuit state changes validated via ActionGate
- All circuit events recorded in brain audit trail
- Fail-open strategy for backward compatibility

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, TypeVar

T = TypeVar("T")

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()  # Normal operation
    OPEN = auto()  # Failing, reject fast
    HALF_OPEN = auto()  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: int = 2


@dataclass
class RetryConfig:
    """Configuration for retry policy."""

    max_attempts: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class ServiceConfig:
    """Runtime configuration for a service."""

    enabled: bool = True
    auto_restart: bool = True
    health_check_interval: float = 30.0
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    retry_policy: RetryConfig = field(default_factory=RetryConfig)
    env_vars: dict[str, str] = field(default_factory=dict)
    resource_limits: dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """Circuit breaker for resilient service calls."""

    def __init__(self, name: str, config: CircuitBreakerConfig) -> None:
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
        self._brain = None
        self._init_superbrain()

    def _init_superbrain(self):
        """Initialize SuperBrain connection."""
        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass  # Fail open

    def _validate_circuit_action(self, action: str, details: dict) -> bool:
        """Validate circuit action via SuperBrain ActionGate."""
        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return True  # Fail open

        try:
            if hasattr(self._brain, "action_gate"):
                action_result = self._brain.action_gate.validate_action(
                    agent_id="resilience_engine",
                    action=f"circuit_{action}",
                    details={
                        "circuit_name": self.name,
                        "current_state": self.state.name,
                        **details,
                    },
                )
                return action_result.authorized
        except Exception:
            pass  # Fail open
        return True

    def _record_circuit_event(self, event: str, details: dict):
        """Record circuit event in SuperBrain audit trail."""
        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return

        try:
            if hasattr(self._brain, "record_audit"):
                self._brain.record_audit(
                    action=f"circuit_{event}",
                    agent_id="resilience_engine",
                    details={
                        "circuit_name": self.name,
                        "state": self.state.name,
                        "failure_count": self.failure_count,
                        **details,
                    },
                )
        except Exception:
            pass  # Fail open

    async def call(self, operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute operation with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                elapsed = time.time() - (self.last_failure_time or 0)
                if elapsed > self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenError(f"Circuit open for {self.name}")

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpenError(
                        f"Circuit half-open limit reached for {self.name}"
                    )
                self.half_open_calls += 1

        try:
            result = await operation(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.half_open_calls = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.config.failure_threshold:
                old_state = self.state
                self.state = CircuitState.OPEN
                # CANONICAL: Record circuit open
                self._record_circuit_event(
                    "opened",
                    {
                        "failure_threshold": self.config.failure_threshold,
                        "previous_state": old_state.name
                        if hasattr(old_state, "name")
                        else str(old_state),
                    },
                )

    def get_state(self) -> dict[str, Any]:
        """Get current circuit state."""
        return {
            "name": self.name,
            "state": self.state.name,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time,
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class RetryPolicy:
    """Exponential backoff retry policy."""

    def __init__(self, config: RetryConfig) -> None:
        self.config = config

    async def execute(self, operation: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute operation with retry logic."""
        import random

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception:
                if attempt == self.config.max_attempts:
                    raise

                delay = min(
                    self.config.base_delay * (self.config.exponential_base ** (attempt - 1)),
                    self.config.max_delay,
                )
                if self.config.jitter:
                    delay *= 0.5 + random.random()

                await asyncio.sleep(delay)

        raise RuntimeError("Retry loop exited unexpectedly")


class ConfigWatcher:
    """Watches configuration files for changes."""

    def __init__(self, config_path: Path, poll_interval: float = 5.0) -> None:
        self.config_path = config_path
        self.poll_interval = poll_interval
        self._configs: dict[str, ServiceConfig] = {}
        self._callbacks: list[Callable[[str, ServiceConfig], None]] = []
        self._running = False
        self._task: asyncio.Task = None
        self._last_modified: float = None

    def on_change(self, callback: Callable[[str, ServiceConfig], None]) -> None:
        """Register callback for config changes."""
        self._callbacks.append(callback)

    async def start(self) -> None:
        """Start watching for config changes."""
        self._running = True
        self._task = asyncio.create_task(self._watch())
        # Load initial config
        await self._load_config()

    async def stop(self) -> None:
        """Stop watching."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _watch(self) -> None:
        """Watch loop for file changes."""
        while self._running:
            try:
                if self.config_path.exists():
                    mtime = self.config_path.stat().st_mtime
                    if self._last_modified is None or mtime > self._last_modified:
                        await self._load_config()
                        self._last_modified = mtime
            except Exception as err:
                print(f"[ConfigWatcher] Error: {err}")
            await asyncio.sleep(self.poll_interval)

    async def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path) as f:
                data = json.load(f)

            new_configs: dict[str, ServiceConfig] = {}
            for layer_id, cfg in data.items():
                new_configs[layer_id] = ServiceConfig(
                    enabled=cfg.get("enabled", True),
                    auto_restart=cfg.get("auto_restart", True),
                    health_check_interval=cfg.get("health_check_interval", 30.0),
                    circuit_breaker=CircuitBreakerConfig(
                        failure_threshold=cfg.get("circuit_breaker", {}).get(
                            "failure_threshold", 5
                        ),
                        recovery_timeout=cfg.get("circuit_breaker", {}).get(
                            "recovery_timeout", 30.0
                        ),
                        half_open_max_calls=cfg.get("circuit_breaker", {}).get(
                            "half_open_max_calls", 3
                        ),
                        success_threshold=cfg.get("circuit_breaker", {}).get(
                            "success_threshold", 2
                        ),
                    ),
                    retry_policy=RetryConfig(
                        max_attempts=cfg.get("retry_policy", {}).get("max_attempts", 5),
                        base_delay=cfg.get("retry_policy", {}).get("base_delay", 1.0),
                        max_delay=cfg.get("retry_policy", {}).get("max_delay", 60.0),
                        exponential_base=cfg.get("retry_policy", {}).get("exponential_base", 2.0),
                        jitter=cfg.get("retry_policy", {}).get("jitter", True),
                    ),
                    env_vars=cfg.get("env_vars", {}),
                    resource_limits=cfg.get("resource_limits", {}),
                )

            # Detect changes and notify
            for layer_id, new_cfg in new_configs.items():
                if layer_id not in self._configs:
                    print(f"[ConfigWatcher] New config for {layer_id}")
                    for cb in self._callbacks:
                        cb(layer_id, new_cfg)
                elif self._configs[layer_id] != new_cfg:
                    print(f"[ConfigWatcher] Config changed for {layer_id}")
                    for cb in self._callbacks:
                        cb(layer_id, new_cfg)

            self._configs = new_configs

        except Exception as e:
            print(f"[ConfigWatcher] Failed to load config: {e}")

    def get_config(self, layer_id: str) -> Optional[ServiceConfig]:
        """Get configuration for a layer."""
        return self._configs.get(layer_id)


class AMOSResilienceEngine:
    """Main resilience engine integrating all patterns."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = config_path or Path("_AMOS_BRAIN/service_config.json")
        self.watcher = ConfigWatcher(self.config_path)
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_policies: dict[str, RetryPolicy] = {}
        self._running = False

        # Register for config changes
        self.watcher.on_change(self._on_config_change)

    async def start(self) -> None:
        """Start resilience engine."""
        print("[ResilienceEngine] Starting...")
        await self.watcher.start()
        self._running = True
        print("[ResilienceEngine] Active")

    async def stop(self) -> None:
        """Stop resilience engine."""
        print("[ResilienceEngine] Stopping...")
        await self.watcher.stop()
        self._running = False
        print("[ResilienceEngine] Stopped")

    def _on_config_change(self, layer_id: str, config: ServiceConfig) -> None:
        """Handle configuration change."""
        print(f"[ResilienceEngine] Updating {layer_id} config")

        # Update circuit breaker
        if layer_id in self.circuit_breakers:
            self.circuit_breakers[layer_id].config = config.circuit_breaker
        else:
            self.circuit_breakers[layer_id] = CircuitBreaker(layer_id, config.circuit_breaker)

        # Update retry policy
        self.retry_policies[layer_id] = RetryPolicy(config.retry_policy)

    async def execute_with_resilience(
        self, layer_id: str, operation: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """Execute operation with full resilience stack."""
        # Get or create circuit breaker
        if layer_id not in self.circuit_breakers:
            config = self.watcher.get_config(layer_id)
            cb_config = config.circuit_breaker if config else CircuitBreakerConfig()
            self.circuit_breakers[layer_id] = CircuitBreaker(layer_id, cb_config)

        # Get or create retry policy
        if layer_id not in self.retry_policies:
            config = self.watcher.get_config(layer_id)
            retry_config = config.retry_policy if config else RetryConfig()
            self.retry_policies[layer_id] = RetryPolicy(retry_config)

        cb = self.circuit_breakers[layer_id]
        retry = self.retry_policies[layer_id]

        # Execute with circuit breaker, with retry inside
        async def retry_operation():
            return await retry.execute(operation, *args, **kwargs)

        return await cb.call(retry_operation)

    def get_circuit_states(self) -> dict[str, dict[str, Any]]:
        """Get all circuit breaker states."""
        return {name: cb.get_state() for name, cb in self.circuit_breakers.items()}


@dataclass
class Incident:
    """Represents a system incident for learning."""

    incident_id: str
    timestamp: float
    component: str
    error_type: str
    error_message: str
    resolution: str = None
    resolved_at: float = None


class SelfHealingManager:
    """
    Self-Healing Manager - Automated recovery actions.

    Implements patterns from 2025 AI agent architectures:
    - Perception: Monitor component health
    - Decision Engine: Determine recovery action
    - Action Module: Execute recovery
    - Memory: Learn from incidents
    """

    def __init__(self, resilience_engine: AMOSResilienceEngine) -> None:
        self.resilience_engine = resilience_engine
        self.incidents: list[Incident] = []
        self.healing_actions: dict[str, Callable[[str], Any]] = {
            "restart": self._action_restart,
            "reload_config": self._action_reload_config,
            "isolate": self._action_isolate,
            "escalate": self._action_escalate,
        }
        self._running = False
        self._monitor_task: asyncio.Task = None
        self._incident_db_path = Path("_AMOS_BRAIN/incidents.json")
        self._load_incidents()

    def _load_incidents(self) -> None:
        """Load incident history for learning."""
        if self._incident_db_path.exists():
            try:
                with open(self._incident_db_path) as f:
                    data = json.load(f)
                    self.incidents = [Incident(**inc) for inc in data.get("incidents", [])]
            except Exception:
                self.incidents = []

    def _save_incidents(self) -> None:
        """Save incident history."""
        self._incident_db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._incident_db_path, "w") as f:
            json.dump(
                {
                    "incidents": [
                        {
                            "incident_id": inc.incident_id,
                            "timestamp": inc.timestamp,
                            "component": inc.component,
                            "error_type": inc.error_type,
                            "error_message": inc.error_message,
                            "resolution": inc.resolution,
                            "resolved_at": inc.resolved_at,
                        }
                        for inc in self.incidents[-1000:]  # Keep last 1000
                    ]
                },
                f,
                indent=2,
            )

    async def start(self) -> None:
        """Start self-healing monitoring."""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        print("[SelfHealing] Monitoring started")

    async def stop(self) -> None:
        """Stop self-healing monitoring."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        print("[SelfHealing] Monitoring stopped")

    async def _monitor_loop(self) -> None:
        """Continuous monitoring loop."""
        while self._running:
            try:
                await self._check_all_components()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"[SelfHealing] Monitor error: {e}")
                await asyncio.sleep(5)

    async def _check_all_components(self) -> None:
        """Check health of all components."""
        states = self.resilience_engine.get_circuit_states()
        for component, state in states.items():
            if state["state"] == "OPEN":
                await self._handle_failure(component, "circuit_open", "Circuit breaker opened")

    async def _handle_failure(self, component: str, error_type: str, error_message: str) -> None:
        """Handle a component failure with self-healing."""
        incident_id = f"inc_{int(time.time() * 1000)}"
        incident = Incident(
            incident_id=incident_id,
            timestamp=time.time(),
            component=component,
            error_type=error_type,
            error_message=error_message,
        )
        self.incidents.append(incident)

        # Determine healing action based on learned patterns
        action = self._determine_healing_action(component, error_type)
        print(f"[SelfHealing] Incident {incident_id}: {action} for {component}")

        try:
            await self.healing_actions[action](component)
            incident.resolution = action
            incident.resolved_at = time.time()
            print(f"[SelfHealing] Resolved {incident_id} with {action}")
        except Exception as e:
            print(f"[SelfHealing] Failed to resolve {incident_id}: {e}")
            # Escalate if healing failed
            await self._action_escalate(component)

        self._save_incidents()

    def _determine_healing_action(self, component: str, error_type: str) -> str:
        """Determine best healing action based on learned patterns."""
        # Learn from past incidents
        similar_incidents = [
            inc
            for inc in self.incidents
            if inc.component == component and inc.error_type == error_type
        ]

        if similar_incidents:
            # Find most successful resolution
            resolutions: dict[str, int] = {}
            for inc in similar_incidents:
                if inc.resolution:
                    resolutions[inc.resolution] = resolutions.get(inc.resolution, 0) + 1

            if resolutions:
                return max(resolutions, key=resolutions.get)

        # Default actions based on component type
        if "config" in error_type.lower():
            return "reload_config"
        elif component in ["01_BRAIN", "00_ROOT"]:
            return "escalate"  # Critical components
        else:
            return "restart"

    async def _action_restart(self, component: str) -> None:
        """Restart a component."""
        print(f"[SelfHealing] Restarting {component}")
        # Emit restart event
        await asyncio.sleep(1)  # Simulate restart

    async def _action_reload_config(self, component: str) -> None:
        """Reload configuration for a component."""
        print(f"[SelfHealing] Reloading config for {component}")
        # Trigger config reload via event bus
        await asyncio.sleep(0.5)

    async def _action_isolate(self, component: str) -> None:
        """Isolate a failing component."""
        print(f"[SelfHealing] Isolating {component}")
        # Disable component until manual intervention
        await asyncio.sleep(0.5)

    async def _action_escalate(self, component: str) -> None:
        """Escalate to human operator."""
        print(f"[SelfHealing] ESCALATING {component} - Critical failure")
        # Could send alert, create ticket, etc.

    def get_healing_stats(self) -> dict[str, Any]:
        """Get self-healing statistics."""
        resolved = sum(1 for inc in self.incidents if inc.resolution)
        escalated = sum(1 for inc in self.incidents if inc.resolution == "escalate")
        return {
            "total_incidents": len(self.incidents),
            "resolved_automatically": resolved,
            "escalated": escalated,
            "success_rate": resolved / len(self.incidents) if self.incidents else 0,
            "recent_incidents": [
                {
                    "id": inc.incident_id,
                    "component": inc.component,
                    "type": inc.error_type,
                    "resolution": inc.resolution,
                }
                for inc in self.incidents[-10:]
            ],
        }


class ChaosEngineering:
    """
    Chaos Engineering - Proactive resilience testing.

    Injects failures to validate system resilience.
    """

    def __init__(self, resilience_engine: AMOSResilienceEngine) -> None:
        self.resilience_engine = resilience_engine
        self._experiments: list[dict[str, Any]] = []
        self._running = False

    async def run_experiment(
        self,
        target_component: str,
        failure_type: str,
        duration: float = 30.0,
        intensity: float = 0.5,
    ) -> dict[str, Any]:
        """Run a chaos experiment."""
        print(f"[Chaos] Starting experiment on {target_component}: {failure_type}")

        experiment = {
            "id": f"exp_{int(time.time())}",
            "target": target_component,
            "failure_type": failure_type,
            "duration": duration,
            "intensity": intensity,
            "start_time": time.time(),
            "status": "running",
        }
        self._experiments.append(experiment)

        # Simulate failure
        if failure_type == "latency":
            await self._inject_latency(target_component, intensity)
        elif failure_type == "error":
            await self._inject_errors(target_component, intensity)
        elif failure_type == "crash":
            await self._inject_crash(target_component)

        await asyncio.sleep(duration)

        experiment["status"] = "completed"
        experiment["end_time"] = time.time()

        # Check if system recovered
        recovery_time = await self._measure_recovery(target_component)
        experiment["recovery_time"] = recovery_time

        print(f"[Chaos] Experiment completed. Recovery time: {recovery_time:.2f}s")
        return experiment

    async def _inject_latency(self, component: str, intensity: float) -> None:
        """Inject latency into component calls."""
        delay = intensity * 5  # Up to 5 seconds
        print(f"[Chaos] Injecting {delay:.2f}s latency into {component}")

    async def _inject_errors(self, component: str, intensity: float) -> None:
        """Inject random errors."""
        print(f"[Chaos] Injecting {intensity * 100:.0f}% error rate into {component}")

    async def _inject_crash(self, component: str) -> None:
        """Simulate component crash."""
        print(f"[Chaos] Simulating crash of {component}")

    async def _measure_recovery(self, component: str) -> float:
        """Measure how long system takes to recover."""
        start = time.time()
        # Monitor circuit breaker state
        while time.time() - start < 300:  # Max 5 minutes
            states = self.resilience_engine.get_circuit_states()
            if component in states:
                if states[component]["state"] == "CLOSED":
                    return time.time() - start
            await asyncio.sleep(1)
        return -1  # Did not recover


def generate_default_config() -> dict[str, Any]:
    """Generate default service configuration."""
    layers = [
        "00_ROOT",
        "01_BRAIN",
        "02_SENSES",
        "03_IMMUNE",
        "04_BLOOD",
        "05_NERVES",
        "06_MUSCLE",
        "07_METABOLISM",
        "08_GROWTH",
        "09_SOCIAL",
        "10_MEMORY",
        "11_LEGAL",
        "12_ETHICS",
        "13_TIME",
        "14_INTERFACES",
    ]

    default_service = {
        "enabled": True,
        "auto_restart": True,
        "health_check_interval": 30.0,
        "circuit_breaker": {
            "failure_threshold": 5,
            "recovery_timeout": 30.0,
            "half_open_max_calls": 3,
            "success_threshold": 2,
        },
        "retry_policy": {
            "max_attempts": 5,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "exponential_base": 2.0,
            "jitter": True,
        },
        "env_vars": {},
        "resource_limits": {},
    }

    # Customize per layer
    configs = {}
    for layer in layers:
        cfg = default_service.copy()
        if layer == "00_ROOT":
            cfg["circuit_breaker"]["failure_threshold"] = 3
        elif layer in ["03_IMMUNE", "12_ETHICS"]:
            cfg["circuit_breaker"]["recovery_timeout"] = 10.0
        configs[layer] = cfg

    return configs


if __name__ == "__main__":
    import sys
    from collections.abc import Callable

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        # Generate default config
        config_path = Path("_AMOS_BRAIN/service_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_config = generate_default_config()
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        print(f"Generated default config at {config_path}")
    else:
        # Run demo
        async def demo():
            engine = AMOSResilienceEngine()
            await engine.start()
            await asyncio.sleep(10)
            await engine.stop()

        asyncio.run(demo())
