"""AMOS Brain - ClawSpring Runtime Integration (Layer 14).

Provides seamless integration between AMOS Brain cognitive OS and
ClawSpring agent execution framework.

This module enables:
- Automatic brain consultation before/after tool execution
- System prompt injection with brain context
- Real-time law enforcement during agent operations
- State synchronization between brain and agent
"""

import functools
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Dict, List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from amos_brain import (
    GlobalLaws,
    get_agent_bridge,
    get_brain,
    get_config,
    get_meta_controller,
    get_monitor,
    get_state_manager,
    process_task,
)


class BrainGuidedToolWrapper:
    """Wraps ClawSpring tools with AMOS Brain cognitive guidance.

    Automatically:
    1. Validates tool calls against global laws (pre-execution)
    2. Records reasoning and outcomes (post-execution)
    3. Monitors for law violations
    4. Provides audit trail

    Usage:
        @BrainGuidedToolWrapper.wrap(tool_name="Read")
        def read_file(file_path: str) -> str:
            return open(file_path).read()
    """

    def __init__(self):
        self.bridge = get_agent_bridge()
        self.monitor = get_monitor()
        self.laws = GlobalLaws()

    @classmethod
    def wrap(cls, tool_name: str, risk_level: str = "medium") -> Callable:
        """Decorator to wrap a tool with brain-guided validation.

        Args:
            tool_name: Name of the tool for law checking
            risk_level: Tool risk level (low/medium/high)

        Returns:
            Decorator function
        """
        wrapper = cls()

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapped_func(*args, **kwargs) -> Any:
                # Pre-execution: Validate with brain
                tool_input = {"args": args, "kwargs": kwargs}

                validation = wrapper.bridge.validate_tool_call(
                    tool_name=tool_name, tool_input=tool_input, context={"risk_level": risk_level}
                )

                if not validation["approved"]:
                    wrapper.monitor.record_tool_decision(
                        tool_name=tool_name,
                        approved=False,
                        risk_level=risk_level,
                        violations=validation.get("violations", []),
                    )
                    raise LawViolationError(
                        f"Tool '{tool_name}' blocked: {validation.get('reason', 'Law violation')}"
                    )

                # Execute the tool
                result = func(*args, **kwargs)

                # Post-execution: Audit
                wrapper.bridge.audit_tool_result(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    result={"status": "success"},
                    context={"execution_time_ms": 0},
                )

                wrapper.monitor.record_tool_decision(
                    tool_name=tool_name, approved=True, risk_level=risk_level, violations=[]
                )

                return result

            # Mark as brain-guided
            wrapped_func._brain_guided = True
            wrapped_func._tool_name = tool_name
            return wrapped_func

        return decorator


class LawViolationError(Exception):
    """Exception raised when a tool call violates global laws."""

    pass


class BrainSystemPromptInjector:
    """Injects AMOS Brain cognitive context into agent system prompts.

    Automatically adds:
    - Active cognitive kernels
    - Law enforcement status
    - Rule of 2/4 requirements
    - Brain reasoning guidelines
    """

    def __init__(self):
        self.brain = get_brain()
        self.config = get_config()

    def inject_context(self, base_prompt: str, domain: str = "general") -> str:
        """Inject brain cognitive context into a system prompt.

        Args:
            base_prompt: Original system prompt
            domain: Cognitive domain for kernel selection

        Returns:
            Enhanced prompt with brain context
        """
        # Get active engines
        engines = self.brain.list_engines()
        # Get domain-relevant engines (first 3)
        domain_engines = engines[:3]

        # Build engine list string
        engine_list = "\n".join(f"  - {e}" for e in domain_engines[:3])

        # Build injection
        brain_context = f"""
[AMOS BRAIN COGNITIVE CONTEXT]

You are operating under the AMOS Brain Cognitive OS with the following constraints:

ACTIVE COGNITIVE KERNELS ({len(domain_engines)}):
{engine_list}

GLOBAL LAWS (Must obey):
  L1: Law of Law - All actions must be lawful
  L2: Rule of 2 - Consider at least 2 perspectives
  L3: Rule of 4 - Analyze through 4 quadrants (Technical/Biological/Economic/Environmental)
  L4: Absolute Structural Integrity - Maintain system coherence
  L5: Post-Theory Communication - Be clear and explicit
  L6: UBI Alignment - Benefit all humanity

REASONING REQUIREMENTS:
  - Before making decisions, apply Rule of 2 (dual perspectives)
  - For complex decisions, apply Rule of 4 (4-quadrant analysis)
  - Validate actions against Global Laws L1-L6
  - Document reasoning chain for audit

[END BRAIN CONTEXT]

{base_prompt}"""

        return brain_context


class BrainAgentLifecycle:
    """Manages AMOS Brain integration throughout agent lifecycle.

    Hooks into:
    - Agent initialization: Sets up brain state
    - Agent execution: Provides reasoning context
    - Agent shutdown: Saves state and audit trail
    """

    def __init__(self):
        self.state_manager = get_state_manager()
        self.meta_controller = get_meta_controller()
        self.monitor = get_monitor()
        self.session_id: str = None

    def on_agent_init(self, agent_name: str, goal: str) -> Dict[str, Any]:
        """Called when agent initializes.

        Returns brain context for the agent session.
        """
        # Create brain session
        self.session_id = self.state_manager.start_session(
            goal=f"Agent: {agent_name} - {goal}", domain="agent"
        )

        # Initialize meta-cognitive plan
        plan = self.meta_controller.orchestrate(goal, auto_execute=False)

        # Monitor agent start
        self.monitor.record_reasoning(
            task_description=f"Agent {agent_name} initialized: {goal}",
            processing_time_ms=0,
            law_violations=0,
            confidence="high",
            kernels_used=["agent_lifecycle"],
        )

        return {
            "session_id": self.session_id,
            "brain_plan_id": plan.plan_id,
            "status": "brain_initialized",
        }

    def on_agent_shutdown(self, final_status: str = "completed") -> Dict[str, Any]:
        """Called when agent shuts down.

        Saves state and generates audit report.
        """
        if self.session_id:
            # Save session
            self.state_manager.save_session(self.session_id)

            # Close session
            filepath = self.state_manager.close_session(self.session_id)

            return {
                "session_id": self.session_id,
                "final_status": final_status,
                "audit_file": str(filepath),
                "status": "brain_shutdown",
            }

        return {"status": "no_active_session"}

    def record_agent_step(self, step_description: str, tool_calls: List[dict], reasoning: str):
        """Record an agent execution step in brain state."""
        if self.session_id:
            self.state_manager.record_reasoning_step(
                session_id=self.session_id,
                step_description=step_description,
                perspective="agent",
                law_checks=["L1", "L2"],
                kernel_references=["agent_runtime"],
            )


class BrainClawSpringBridge:
    """Main bridge between AMOS Brain and ClawSpring.

    Provides a unified interface for:
    - Tool wrapping with law enforcement
    - Prompt injection
    - Lifecycle management
    - Configuration

    Usage:
        bridge = BrainClawSpringBridge()

        # Wrap a tool
        @bridge.wrap_tool("Read")
        def read_file(path: str): ...

        # Enhance prompt
        enhanced = bridge.enhance_prompt(base_prompt)

        # Manage lifecycle
        bridge.init_agent("MyAgent", "Analyze data")
        bridge.shutdown_agent()
    """

    def __init__(self):
        self.tool_wrapper = BrainGuidedToolWrapper()
        self.prompt_injector = BrainSystemPromptInjector()
        self.lifecycle = BrainAgentLifecycle()

    def wrap_tool(self, tool_name: str, risk_level: str = "medium") -> Callable:
        """Decorator to wrap a tool with brain guidance."""
        return self.tool_wrapper.wrap(tool_name, risk_level)

    def enhance_prompt(self, base_prompt: str, domain: str = "general") -> str:
        """Enhance a system prompt with brain context."""
        return self.prompt_injector.inject_context(base_prompt, domain)

    def init_agent(self, agent_name: str, goal: str) -> Dict[str, Any]:
        """Initialize brain for an agent session."""
        return self.lifecycle.on_agent_init(agent_name, goal)

    def shutdown_agent(self, status: str = "completed") -> Dict[str, Any]:
        """Shutdown brain for an agent session."""
        return self.lifecycle.on_agent_shutdown(status)

    def think(self, query: str, domain: str = "general") -> Dict[str, Any]:
        """Direct brain consultation for agent reasoning.

        Args:
            query: Question or task to think about
            domain: Cognitive domain

        Returns:
            Brain response with reasoning and compliance info
        """
        result = process_task(query, domain)

        return {
            "reasoning": result.reasoning_steps,
            "confidence": result.confidence,
            "law_compliant": len(result.law_violations) == 0,
            "violations": result.law_violations,
            "kernels_used": result.kernels_used,
            "rule_of_two": result.rule_of_two_check,
            "rule_of_four": result.rule_of_four_check,
        }


# Convenience function for quick integration
def create_brain_guided_agent(agent_name: str, goal: str) -> BrainClawSpringBridge:
    """Create a brain-guided agent environment.

    Args:
        agent_name: Name of the agent
        goal: Agent's high-level goal

    Returns:
        Configured BrainClawSpringBridge instance
    """
    bridge = BrainClawSpringBridge()
    bridge.init_agent(agent_name, goal)
    return bridge
