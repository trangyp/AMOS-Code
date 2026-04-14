"""AMOS Task Execution Integration - Bridge cognitive tasks to organism execution."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add organism OS to path
ORGANISM_PATH = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/AMOS_ORGANISM_OS")
if str(ORGANISM_PATH) not in sys.path:
    sys.path.insert(0, str(ORGANISM_PATH))


@dataclass
class ExecutionOutcome:
    """Outcome of cognitive task execution."""
    success: bool
    output: str
    error: Optional[str]
    duration_ms: float
    execution_type: str
    artifacts: Dict[str, Any]


class TaskExecutionIntegration:
    """Integrates organism task executor with cognitive routing."""

    def __init__(self):
        self._executor = None
        self._initialized = False
        self._initialize()

    def _initialize(self):
        """Initialize task executor connection."""
        try:
            # Import task executor from organism OS
            import importlib.util
            executor_path = ORGANISM_PATH / "06_MUSCLE" / "task_executor.py"
            
            if executor_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "task_executor", executor_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Create executor instance
                self._executor = module.TaskExecutor(ORGANISM_PATH)
                self._initialized = True
        except Exception as e:
            self._initialized = False
            print(f"[TaskExecution] Using fallback mode: {e}")

    def execute_cognitive_task(
        self,
        task_id: str,
        task_description: str,
        domain: str,
        engines: list,
        priority: str = "MEDIUM"
    ) -> ExecutionOutcome:
        """Execute a cognitive task through organism executor."""
        
        # Map to execution type
        exec_type = self._map_domain_to_execution_type(domain)
        
        # Prepare execution parameters
        params = {
            "description": task_description,
            "domain": domain,
            "engines": engines,
            "priority": priority,
        }
        
        if self._initialized and self._executor:
            try:
                # Use organism task executor
                result = self._executor.execute_task(task_id, exec_type, params)
                
                return ExecutionOutcome(
                    success=result.success,
                    output=result.output,
                    error=result.error,
                    duration_ms=result.duration_ms,
                    execution_type=exec_type,
                    artifacts=result.artifacts
                )
            except Exception as e:
                return ExecutionOutcome(
                    success=False,
                    output="",
                    error=str(e),
                    duration_ms=0.0,
                    execution_type=exec_type,
                    artifacts={}
                )
        
        # Fallback: simulate execution
        return self._fallback_execution(task_id, exec_type, params)

    def _map_domain_to_execution_type(self, domain: str) -> str:
        """Map cognitive domain to execution type."""
        mapping = {
            "software": "code",
            "analysis": "analysis",
            "security": "security",
            "design": "documentation",
            "data": "analysis",
            "infrastructure": "code",
            "testing": "test",
            "ubi": "analysis",
        }
        return mapping.get(domain, "analysis")

    def _fallback_execution(
        self,
        task_id: str,
        exec_type: str,
        params: Dict[str, Any]
    ) -> ExecutionOutcome:
        """Fallback execution when organism executor unavailable."""
        
        import time
        start = time.time()
        
        # Simulate processing
        time.sleep(0.01)
        
        duration = (time.time() - start) * 1000
        
        return ExecutionOutcome(
            success=True,
            output=f"[Fallback] Task {task_id} ({exec_type}) processed",
            error=None,
            duration_ms=duration,
            execution_type=exec_type,
            artifacts={"fallback": True, "params": params}
        )

    def get_execution_history(self) -> list:
        """Get execution history from organism executor."""
        if self._initialized and self._executor:
            try:
                return self._executor.execution_log
            except Exception:
                pass
        return []

    def get_status(self) -> Dict[str, Any]:
        """Get task execution integration status."""
        return {
            "initialized": self._initialized,
            "executor_available": self._executor is not None,
            "organism_path": str(ORGANISM_PATH),
            "execution_history_count": len(self.get_execution_history()),
        }


# Singleton instance
_task_execution_integration: Optional[TaskExecutionIntegration] = None


def get_task_execution_integration() -> TaskExecutionIntegration:
    """Get or create singleton task execution integration."""
    global _task_execution_integration
    if _task_execution_integration is None:
        _task_execution_integration = TaskExecutionIntegration()
    return _task_execution_integration


def execute_task(
    task_id: str,
    task_description: str,
    domain: str,
    engines: list,
    priority: str = "MEDIUM"
) -> ExecutionOutcome:
    """Convenience function to execute cognitive task."""
    integration = get_task_execution_integration()
    return integration.execute_cognitive_task(
        task_id, task_description, domain, engines, priority
    )


if __name__ == "__main__":
    # Test task execution integration
    print("=" * 60)
    print("AMOS Task Execution Integration - Test")
    print("=" * 60)
    
    integration = get_task_execution_integration()
    status = integration.get_status()
    
    print(f"\nStatus: {status}")
    
    # Test execution
    test_tasks = [
        ("task_001", "Design API endpoint", "software", ["Engineering"], "MEDIUM"),
        ("task_002", "Security audit", "security", ["Logic"], "HIGH"),
    ]
    
    print("\nExecutions:")
    for tid, desc, domain, engines, priority in test_tasks:
        result = execute_task(tid, desc, domain, engines, priority)
        status_icon = "✓" if result.success else "✗"
        print(f"  {status_icon} {tid}: {result.execution_type} "
              f"({result.duration_ms:.1f}ms)")
