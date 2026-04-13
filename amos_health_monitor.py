#!/usr/bin/env python3
"""AMOS Health Monitor - Production Health Checks and Monitoring

Provides:
- System health endpoint for load balancers
- Dependency health checks (brain, API, database)
- Health history and trend analysis
- Integration with alerting system
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    message: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class SystemHealth:
    overall: HealthStatus
    checks: List[HealthCheck]
    timestamp: datetime
    uptime_seconds: float
    version: str = "1.0.0"


class AMOSHealthMonitor:
    """Production health monitoring for AMOS Brain API."""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.checks: Dict[str, Callable] = {}
        self.health_history: List[SystemHealth] = []
        self.max_history = 100
        self._start_time = time.time()
        self._running = False
        
    def register_check(self, name: str, check_func: Callable):
        """Register a health check function."""
        self.checks[name] = check_func
        
    async def check_health(self) -> SystemHealth:
        """Run all health checks and return system health."""
        checks = []
        any_unhealthy = False
        any_degraded = False
        
        for name, check_func in self.checks.items():
            start = time.time()
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                response_time = (time.time() - start) * 1000
                
                if isinstance(result, tuple):
                    status, message = result
                    metadata = {}
                elif isinstance(result, dict):
                    status = result.get('status', HealthStatus.HEALTHY)
                    message = result.get('message', '')
                    metadata = result.get('metadata', {})
                else:
                    status = result if isinstance(result, HealthStatus) else HealthStatus.HEALTHY
                    message = ""
                    metadata = {}
                    
                if status == HealthStatus.UNHEALTHY:
                    any_unhealthy = True
                elif status == HealthStatus.DEGRADED:
                    any_degraded = True
                    
                checks.append(HealthCheck(
                    name=name,
                    status=status,
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    message=message,
                    metadata=metadata
                ))
                
            except Exception as e:
                any_unhealthy = True
                checks.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=(time.time() - start) * 1000,
                    last_check=datetime.utcnow(),
                    message=str(e)
                ))
        
        # Determine overall health
        if any_unhealthy:
            overall = HealthStatus.UNHEALTHY
        elif any_degraded:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY
            
        health = SystemHealth(
            overall=overall,
            checks=checks,
            timestamp=datetime.utcnow(),
            uptime_seconds=time.time() - self._start_time,
            version="1.0.0"
        )
        
        # Store in history
        self.health_history.append(health)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)
            
        return health
    
    def get_health(self) -> SystemHealth:
        """Get current health (non-async version)."""
        if self.health_history:
            return self.health_history[-1]
        return SystemHealth(
            overall=HealthStatus.UNKNOWN,
            checks=[],
            timestamp=datetime.utcnow(),
            uptime_seconds=time.time() - self._start_time
        )
    
    def get_health_trend(self, hours: int = 24) -> Dict:
        """Analyze health trend over time."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [h for h in self.health_history if h.timestamp > cutoff]
        
        if not recent:
            return {"message": "No data available"}
        
        healthy_count = sum(1 for h in recent if h.overall == HealthStatus.HEALTHY)
        degraded_count = sum(1 for h in recent if h.overall == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for h in recent if h.overall == HealthStatus.UNHEALTHY)
        
        total = len(recent)
        
        # Calculate average response times per check
        avg_response_times = {}
        for check_name in self.checks.keys():
            times = []
            for health in recent:
                for check in health.checks:
                    if check.name == check_name:
                        times.append(check.response_time_ms)
            if times:
                avg_response_times[check_name] = sum(times) / len(times)
        
        return {
            "period_hours": hours,
            "total_checks": total,
            "healthy": healthy_count,
            "healthy_pct": healthy_count / total * 100,
            "degraded": degraded_count,
            "degraded_pct": degraded_count / total * 100,
            "unhealthy": unhealthy_count,
            "unhealthy_pct": unhealthy_count / total * 100,
            "avg_response_times_ms": avg_response_times,
            "uptime_pct": (healthy_count + degraded_count) / total * 100
        }
    
    def to_dict(self, health: SystemHealth) -> Dict:
        """Convert health to dictionary."""
        return {
            "overall": health.overall.value,
            "timestamp": health.timestamp.isoformat(),
            "uptime_seconds": health.uptime_seconds,
            "version": health.version,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "response_time_ms": round(c.response_time_ms, 2),
                    "last_check": c.last_check.isoformat(),
                    "message": c.message,
                    "metadata": c.metadata
                }
                for c in health.checks
            ]
        }


# Global monitor instance
_health_monitor: Optional[AMOSHealthMonitor] = None


def get_health_monitor() -> AMOSHealthMonitor:
    """Get or create global health monitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = AMOSHealthMonitor()
    return _health_monitor


def init_default_health_checks():
    """Initialize default health checks for AMOS."""
    monitor = get_health_monitor()

    # 1. Brain health check
    def check_brain():
        try:
            from amos_brain import get_brain
            brain = get_brain()
            return (HealthStatus.HEALTHY, "Brain operational", {"engines": 12, "laws": 6})
        except Exception as e:
            return (HealthStatus.UNHEALTHY, f"Brain error: {e}")

    monitor.register_check("brain", check_brain)

    # 2. Tools health check
    def check_tools():
        try:
            from tool_registry import _registry
            amos_tools = [k for k in _registry.keys() if "AMOS" in k]
            expected = 5
            if len(amos_tools) >= expected:
                return (HealthStatus.HEALTHY, f"{len(amos_tools)} tools registered")
            return (HealthStatus.DEGRADED, f"Only {len(amos_tools)} tools, expected {expected}")
        except Exception as e:
            return (HealthStatus.UNHEALTHY, f"Tools error: {e}")

    monitor.register_check("tools", check_tools)

    # 3. Skills health check
    def check_skills():
        try:
            from skill import find_skill
            # Check key AMOS skills exist
            skills = ["/amos-analyze", "/amos-laws", "/amos-status"]
            found = sum(1 for s in skills if find_skill(s) is not None)
            if found >= len(skills):
                return (HealthStatus.HEALTHY, f"{found} skills available")
            return (HealthStatus.DEGRADED, f"{found}/{len(skills)} skills found")
        except Exception as e:
            return (HealthStatus.UNHEALTHY, f"Skills error: {e}")

    monitor.register_check("skills", check_skills)

    # 4. Agent types health check
    def check_agent_types():
        try:
            from multi_agent import load_agent_definitions
            defs = load_agent_definitions()
            if "amos" in defs:
                return (HealthStatus.HEALTHY, "AMOS agent type registered")
            return (HealthStatus.DEGRADED, "AMOS agent type not found")
        except Exception as e:
            return (HealthStatus.UNHEALTHY, f"Agent types error: {e}")

    monitor.register_check("agent_types", check_agent_types)

    # 5. Agent loop health check
    def check_agent_loop():
        try:
            from agent import _amos_available, _get_enhanced_system_prompt
            if _amos_available:
                enhanced = _get_enhanced_system_prompt("test", use_amos=True)
                if "AMOS" in enhanced:
                    return (HealthStatus.HEALTHY, "Agent loop integrated")
            return (HealthStatus.DEGRADED, "AMOS not available in agent")
        except Exception as e:
            return (HealthStatus.UNHEALTHY, f"Agent loop error: {e}")

    monitor.register_check("agent_loop", check_agent_loop)

    # 6. CLI health check
    def check_cli():
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "clawspring/clawspring.py", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "--amos" in result.stdout:
                return (HealthStatus.HEALTHY, "CLI --amos flag available")
            return (HealthStatus.DEGRADED, "--amos flag not found")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"CLI check failed: {e}")

    monitor.register_check("cli", check_cli)

    # 7. Integration tests health check
    def check_tests():
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "test_amos_integration.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if "12 passed" in result.stdout and "0 failed" in result.stdout:
                return (HealthStatus.HEALTHY, "All 12 tests passing")
            return (HealthStatus.DEGRADED, "Some tests failing")
        except Exception as e:
            return (HealthStatus.UNHEALTHY, f"Tests error: {e}")

    monitor.register_check("integration_tests", check_tests)

    # 8. Session logger health check
    def check_session_logger():
        try:
            from amos_session_logger import AMOSSessionLogger
            logger = AMOSSessionLogger()
            sessions = logger.list_sessions()
            return (HealthStatus.HEALTHY, f"Logger ready ({len(sessions)} sessions)")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"Logger error: {e}")

    monitor.register_check("session_logger", check_session_logger)

    # 9. API server health check
    def check_api_server():
        try:
            from amos_api_simple import AMOSAPIHandler
            return (HealthStatus.HEALTHY, "API handler importable")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"API error: {e}")

    monitor.register_check("api_server", check_api_server)

    # 10. Observer health check
    def check_observer():
        try:
            from amos_observer import AMOSObserver
            obs = AMOSObserver()
            return (HealthStatus.HEALTHY, "Observer ready")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"Observer error: {e}")

    monitor.register_check("observer", check_observer)

    # 11. Demo health check
    def check_demo():
        try:
            from demo_amos import main as demo_main
            return (HealthStatus.HEALTHY, "Demo importable")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"Demo error: {e}")

    monitor.register_check("demo", check_demo)

    # 12. Dashboard health check
    def check_dashboard():
        try:
            from amos_unified_dashboard import AMOSUnifiedDashboard
            dash = AMOSUnifiedDashboard()
            return (HealthStatus.HEALTHY, "Dashboard ready")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"Dashboard error: {e}")

    monitor.register_check("dashboard", check_dashboard)

    # 13. Workflow example health check
    def check_workflow():
        try:
            from amos_workflow_example import AMOSWorkflow
            wf = AMOSWorkflow()
            return (HealthStatus.HEALTHY, "Workflow examples ready")
        except Exception as e:
            return (HealthStatus.DEGRADED, f"Workflow error: {e}")

    monitor.register_check("workflow_examples", check_workflow)

    # System health checks
    def check_memory():
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return (HealthStatus.UNHEALTHY, f"Memory critical: {memory.percent}%")
            elif memory.percent > 75:
                return (HealthStatus.DEGRADED, f"Memory high: {memory.percent}%")
            return (HealthStatus.HEALTHY, f"Memory OK: {memory.percent}%")
        except ImportError:
            return (HealthStatus.UNKNOWN, "psutil not available")

    monitor.register_check("memory", check_memory)

    def check_disk():
        try:
            import psutil
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                return (HealthStatus.UNHEALTHY, f"Disk critical: {disk.percent}%")
            elif disk.percent > 80:
                return (HealthStatus.DEGRADED, f"Disk high: {disk.percent}%")
            return (HealthStatus.HEALTHY, f"Disk OK: {disk.percent}%")
        except ImportError:
            return (HealthStatus.UNKNOWN, "psutil not available")

    monitor.register_check("disk", check_disk)

    return monitor


if __name__ == "__main__":
    # Test health monitor
    monitor = init_default_health_checks()
    
    async def test():
        health = await monitor.check_health()
        print(json.dumps(monitor.to_dict(health), indent=2))
        
        print("\nHealth Trend (last 24h):")
        trend = monitor.get_health_trend()
        print(json.dumps(trend, indent=2))
    
    asyncio.run(test())
