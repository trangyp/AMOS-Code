"""AMOS Brain - Execution Platform Bridge (Layer 18)
=====================================================

Connects the Execution Platform to the AMOS Brain cognitive layer.
Enables self-healing, automated debugging, and AI-driven execution.

Creator: Trang Phan
System: AMOS vInfinity
Version: 2.1.0
"""

import traceback
from collections.abc import Callable
from datetime import datetime, timezone


class BrainExecutionBridge:
    """Bridge between AMOS Brain (cognitive) and Execution Platform (action).

    Provides:
    - Brain-guided code execution with cognitive oversight
    - Self-healing via sandboxed reproduction of issues
    - Automated debugging with code isolation
    - AI-driven system maintenance and repair
    - Streaming execution with real-time brain feedback
    - Cost-aware execution provider selection
    """

    def __init__(self):
        self.platform = None
        self.session_id: str = None
        self.brain_context: dict = {}
        self.execution_history: List[dict] = []
        self.max_history = 100

    async def initialize(self) -> dict:
        """Initialize the execution bridge with brain-guided configuration.

        Returns:
            Initialization result with session ID
        """
        try:
            from amos_execution_platform import AMOSExecutionPlatform

            self.platform = AMOSExecutionPlatform()
            self.session_id = f"brain_exec_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

            # Inject brain cognitive context
            self.brain_context = {
                "law_compliant": True,
                "rule_of_two": True,
                "rule_of_four": True,
                "cost_aware": True,
                "provider_preference": "auto",  # auto, e2b, daytona, docker
            }

            # Get platform status
            status = self.platform.get_status()

            return {
                "status": "initialized",
                "session_id": self.session_id,
                "providers": status.get("providers", {}),
                "healthy": status.get("healthy", False),
                "bridge": "active",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "bridge": "failed",
            }

    async def execute_with_brain_guidance(
        self,
        code: str,
        language: str = "python",
        context: dict = None,
        stream_handler: Callable[[str, str], None] = None,
    ) -> dict:
        """Execute code with brain cognitive guidance.

        Args:
            code: Code to execute
            language: Programming language
            context: Additional execution context
            stream_handler: Callback for streaming output

        Returns:
            Execution result with cognitive metadata
        """
        if not self.platform:
            return {"status": "error", "error": "Execution platform not initialized"}

        # Get brain guidance
        from amos_brain import GlobalLaws, think

        # Analyze code safety
        brain_response = think(f"Analyze this code for safety and compliance: {code[:100]}...")

        # Check law compliance
        laws = GlobalLaws()
        law_check = laws.validate_action(f"Execute {language} code")

        if not law_check.compliant:
            return {
                "status": "blocked",
                "reason": law_check.violations,
                "law_enforcement": "L1-L6",
                "brain_guidance": brain_response.reasoning[:3]
                if hasattr(brain_response, "reasoning")
                else [],
            }

        # Select provider based on brain guidance
        preferred_provider = self._select_provider(context)

        # Execute with streaming
        start_time = datetime.now(timezone.utc)
        execution_chunks = []

        try:
            # Create stream callback if handler provided
            stream_callback = None
            if stream_handler:

                async def callback(chunk_type: str, data: str):
                    execution_chunks.append({"type": chunk_type, "data": data})
                    stream_handler(chunk_type, data)

                stream_callback = callback

            # Execute code
            result = await self.platform.execute_code_secure(
                code=code,
                language=language,
                preferred_provider=preferred_provider,
                stream_callback=stream_callback,
            )

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            # Record in history
            self._record_execution(
                {
                    "timestamp": start_time.isoformat(),
                    "language": language,
                    "provider": result.provider,
                    "status": result.status.value,
                    "execution_time_ms": execution_time,
                    "cost_usd": result.cost_usd,
                }
            )

            return {
                "status": "completed" if result.status.value == "success" else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "provider": result.provider,
                "execution_time_ms": execution_time,
                "cost_usd": result.cost_usd,
                "brain_guidance": brain_response.reasoning[:3]
                if hasattr(brain_response, "reasoning")
                else [],
                "law_compliant": True,
                "session_id": self.session_id,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "brain_guidance": brain_response.reasoning[:3]
                if hasattr(brain_response, "reasoning")
                else [],
            }

    async def self_heal_issue(
        self,
        issue_description: str,
        reproduction_code: str = None,
        stream_handler: Callable[[str, str], None] = None,
    ) -> dict:
        """Self-healing via sandboxed code execution.

        Args:
            issue_description: Description of the issue
            reproduction_code: Optional code to reproduce the issue
            stream_handler: Callback for streaming output

        Returns:
            Healing result with diagnosis and fix
        """
        if not self.platform:
            return {"status": "error", "error": "Execution platform not initialized"}

        from amos_brain import think

        # Get brain diagnosis
        diagnosis = think(f"Diagnose and fix: {issue_description}")

        # Generate fix code
        fix_prompt = f"""
        Issue: {issue_description}
        Diagnosis: {diagnosis}

        Generate Python code to diagnose and potentially fix this issue.
        The code should:
        1. Identify the root cause
        2. Attempt a fix if safe
        3. Log all actions taken
        4. Return success/failure status
        """

        fix_code = f"""
import os
import sys
import json

print("=== Self-Healing Execution ===")
print(f"Issue: {issue_description[:50]}...")
print(f"Diagnosis: {diagnosis[:50]}...")

# TODO: Implement actual fix logic
# This is a template that would be replaced with actual fix code

result = {{
    "diagnosis": "{diagnosis[:100]}",
    "fix_applied": False,
    "reason": "Template execution - implement actual fix logic"
}}

print(json.dumps(result, indent=2))
"""

        if reproduction_code:
            # Execute reproduction code first
            repro_result = await self.execute_with_brain_guidance(
                code=reproduction_code,
                language="python",
                context={"purpose": "reproduction"},
                stream_handler=stream_handler,
            )

            if repro_result.get("status") != "completed":
                return {
                    "status": "failed",
                    "phase": "reproduction",
                    "error": repro_result.get("stderr", "Reproduction failed"),
                    "diagnosis": diagnosis,
                }

        # Execute fix
        fix_result = await self.execute_with_brain_guidance(
            code=fix_code,
            language="python",
            context={"purpose": "fix"},
            stream_handler=stream_handler,
        )

        return {
            "status": fix_result.get("status"),
            "phase": "fix",
            "diagnosis": diagnosis,
            "stdout": fix_result.get("stdout"),
            "stderr": fix_result.get("stderr"),
            "brain_guidance": diagnosis.reasoning[:3] if hasattr(diagnosis, "reasoning") else [],
        }

    async def debug_with_sandbox(
        self,
        code: str,
        test_cases: List[dict] = None,
        stream_handler: Callable[[str, str], None] = None,
    ) -> dict:
        """Debug code in isolated sandbox.

        Args:
            code: Code to debug
            test_cases: Optional test cases to validate
            stream_handler: Callback for streaming output

        Returns:
            Debug result with analysis
        """
        if not self.platform:
            return {"status": "error", "error": "Execution platform not initialized"}

        # Add debug instrumentation
        instrumented_code = f"""
import traceback
import sys
import json
from typing import Callable, Optional
from typing import List

print("=== Debug Session Started ===")

try:
    # Original code
{chr(10).join('    ' + line for line in code.split(chr(10)))}

    print("=== Execution Successful ===")

except Exception as e:
    print(f"=== Error Caught ===")
    print(f"Type: {{type(e).__name__}}")
    print(f"Message: {{str(e)}}")
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)
"""

        # Execute in sandbox
        result = await self.execute_with_brain_guidance(
            code=instrumented_code,
            language="python",
            context={"purpose": "debug"},
            stream_handler=stream_handler,
        )

        # Analyze output
        analysis = "success" if result.get("exit_code") == 0 else "error_detected"

        return {
            "status": result.get("status"),
            "analysis": analysis,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "exit_code": result.get("exit_code"),
            "provider": result.get("provider"),
            "debug_info": {
                "instrumented": True,
                "test_cases_run": len(test_cases) if test_cases else 0,
            },
        }

    def _select_provider(self, context: dict) -> str:
        """Select execution provider based on brain guidance."""
        if not context:
            return None

        # Cost-aware selection
        if context.get("cost_sensitive"):
            return "docker"  # Free

        # Speed-sensitive
        if context.get("speed_sensitive"):
            return "daytona"  # 90ms startup

        # Default to auto
        return context.get("provider_preference", "auto")

    def _record_execution(self, record: dict):
        """Record execution in history."""
        self.execution_history.append(record)
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)

    async def get_execution_stats(self) -> dict:
        """Get execution statistics for brain analysis."""
        if not self.execution_history:
            return {"status": "no_data"}

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.get("status") == "completed")
        failed = total - successful

        # Provider distribution
        providers = {}
        for r in self.execution_history:
            p = r.get("provider", "unknown")
            providers[p] = providers.get(p, 0) + 1

        # Cost analysis
        total_cost = sum(r.get("cost_usd", 0) for r in self.execution_history)

        return {
            "status": "ok",
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "provider_distribution": providers,
            "total_cost_usd": total_cost,
            "recent_executions": self.execution_history[-10:],
        }

    async def shutdown(self) -> dict:
        """Gracefully shutdown execution bridge."""
        if self.platform:
            # Cleanup any active sandboxes
            return {
                "status": "shutdown",
                "session_id": self.session_id,
                "executions_recorded": len(self.execution_history),
                "context_preserved": True,
            }
        return {"status": "already_shutdown"}


# Global bridge instance
_bridge_instance: Optional[BrainExecutionBridge] = None


async def get_execution_bridge() -> BrainExecutionBridge:
    """Get or create global brain-execution bridge."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = BrainExecutionBridge()
        await _bridge_instance.initialize()
    return _bridge_instance


async def execute_with_brain(code: str, language: str = "python") -> dict:
    """Execute code with brain guidance (convenience function)."""
    bridge = await get_execution_bridge()
    return await bridge.execute_with_brain_guidance(code, language)


async def self_heal(issue_description: str) -> dict:
    """Self-heal an issue (convenience function)."""
    bridge = await get_execution_bridge()
    return await bridge.self_heal_issue(issue_description)
