"""AMOS Brain Cognitive Facade - Simple SDK for external use."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .loader import get_brain
from .laws import GlobalLaws
from .task_processor import BrainTaskProcessor, TaskResult
from .agent_bridge import get_agent_bridge
from .state_manager import get_state_manager
from .meta_controller import get_meta_controller
from .monitor import get_monitor


@dataclass
class BrainResponse:
    """Simple response from brain operations."""
    success: bool
    content: str
    reasoning: list[str]
    confidence: str
    law_compliant: bool
    violations: list[str]
    metadata: dict[str, Any]
    domain: str = "general"


@dataclass
class Decision:
    """Decision result with full audit."""
    approved: bool
    decision_id: str
    reasoning: str
    risk_level: str
    law_violations: list[str]
    alternative_actions: list[str]


class BrainClient:
    """
    AMOS Brain SDK Client - Unified interface to all 9 layers.
    
    Usage:
        client = BrainClient()
        
        # Simple thinking
        response = client.think("How to design a secure API?")
        
        # Make decision
        decision = client.decide(
            "Should we use microservices?",
            options=["microservices", "monolith", "hybrid"]
        )
        
        # Validate action
        valid, issues = client.validate_action("delete production database")
    """
    
    def __init__(self):
        self.brain = get_brain()
        self.laws = GlobalLaws()
        self.processor = BrainTaskProcessor()
        self.bridge = get_agent_bridge()
        self.state = get_state_manager()
        self.meta = get_meta_controller()
        self.monitor = get_monitor()
    
    def think(
        self,
        query: str,
        domain: str = "general",
        require_law_compliance: bool = True
    ) -> BrainResponse:
        """
        Process a cognitive query through the full brain.
        
        Args:
            query: The question or task to think about
            domain: Domain context (software, science, business, etc.)
            require_law_compliance: Whether to enforce global laws
            
        Returns:
            BrainResponse with reasoning and compliance info
        """
        # Process through brain
        result = self.processor.process(query, domain)
        
        # Monitor the reasoning
        self.monitor.record_reasoning(
            task_description=query,
            processing_time_ms=result.processing_time_ms,
            law_violations=len(result.law_violations),
            confidence=result.confidence,
            kernels_used=result.kernels_used
        )
        
        # Check law compliance
        law_compliant = len(result.law_violations) == 0
        violations = [v["message"] for v in result.law_violations]
        
        # Build content
        content = "\n".join(result.reasoning_steps)
        
        return BrainResponse(
            success=True,
            content=content,
            reasoning=result.reasoning_steps,
            confidence=result.confidence,
            law_compliant=law_compliant,
            violations=violations,
            metadata={
                "processing_time_ms": result.processing_time_ms,
                "kernels_used": result.kernels_used,
                "rule_of_two": result.rule_of_two_check,
                "rule_of_four": result.rule_of_four_check,
            },
            domain=domain
        )
    
    def decide(
        self,
        question: str,
        options: list[str] | None = None,
        context: str = ""
    ) -> Decision:
        """
        Make a decision with full cognitive analysis.
        
        Args:
            question: The decision to make
            options: Available options (auto-generated if not provided)
            context: Additional context for the decision
            
        Returns:
            Decision with reasoning and alternatives
        """
        # Build decision prompt
        if options:
            prompt = f"Decision: {question}\n\nOptions:\n"
            for i, opt in enumerate(options, 1):
                prompt += f"{i}. {opt}\n"
        else:
            prompt = f"Decision: {question}\n\nAnalyze options and recommend best choice."
        
        if context:
            prompt += f"\nContext: {context}"
        
        # Process through brain
        result = self.processor.process(prompt)
        
        # Extract decision from reasoning
        approved = result.confidence in ["high", "medium"]
        reasoning = "\n".join(result.reasoning_steps[:5])
        
        # Determine risk
        risk_level = "low" if not result.law_violations else "medium"
        if len(result.law_violations) > 1:
            risk_level = "high"
        
        violations = [v["law"] for v in result.law_violations]
        
        # Generate alternatives
        alternatives = []
        if options and len(options) > 1:
            # Suggest the second-best option
            alternatives = [f"Consider: {options[1] if len(options) > 1 else 're-evaluate'}"]
        
        return Decision(
            approved=approved,
            decision_id=f"DEC-{hash(question) % 10000:04d}",
            reasoning=reasoning,
            risk_level=risk_level,
            law_violations=violations,
            alternative_actions=alternatives
        )
    
    def validate_action(
        self,
        action_description: str,
        action_type: str = "general"
    ) -> tuple[bool, list[str]]:
        """
        Quick validation if an action complies with global laws.
        
        Args:
            action_description: Description of the action
            action_type: Type of action (tool, command, decision, etc.)
            
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        # L1: Law of Law
        ok, msg = self.laws.check_l1_constraint(action_type)
        if not ok:
            violations.append(f"L1: {msg}")
        
        # L2: Rule of 2 (need alternative perspective)
        ok, msg = self.laws.enforce_l2_dual_check(
            action_description,
            "Alternative considered"
        )
        if not ok:
            violations.append(f"L2: {msg}")
        
        # L5: Communication clarity
        ok, issues = self.laws.l5_communication_check(action_description)
        if not ok:
            violations.extend([f"L5: {i}" for i in issues])
        
        is_valid = len(violations) == 0
        
        # Monitor
        for law_id in ["L1", "L2", "L5"]:
            self.monitor.record_law_compliance(
                law_id=law_id,
                compliant=law_id not in [v[:2] for v in violations],
                context=action_description[:50]
            )
        
        return is_valid, violations
    
    def orchestrate(
        self,
        goal: str,
        max_iterations: int = 10
    ) -> dict[str, Any]:
        """
        Orchestrate a complex goal through meta-cognitive control.
        
        Args:
            goal: High-level goal to achieve
            max_iterations: Maximum execution iterations
            
        Returns:
            Execution result with plan and outcomes
        """
        plan = self.meta.orchestrate(goal, auto_execute=False)
        
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "total_tasks": len(plan.subtasks),
            "completed": sum(1 for t in plan.subtasks if t.status.value == "completed"),
            "failed": sum(1 for t in plan.subtasks if t.status.value == "failed"),
            "tasks": [
                {
                    "id": t.task_id,
                    "description": t.description,
                    "status": t.status.value
                }
                for t in plan.subtasks[:10]
            ]
        }
    
    def get_status(self) -> dict[str, Any]:
        """Get complete brain status."""
        engines = self.brain.list_engines()
        
        # Get monitor summary
        metrics = self.monitor.get_metrics_summary(window_seconds=3600)
        compliance = self.monitor.get_law_compliance_dashboard()
        
        return {
            "status": "operational",
            "layers": {
                "brain_loader": {"engines": len(engines)},
                "task_processor": {"ready": True},
                "agent_bridge": self.bridge.get_execution_report(),
                "state_manager": {"sessions": len(self.state.list_sessions())},
                "meta_controller": self.meta.get_execution_summary(),
                "monitor": metrics,
            },
            "law_compliance": compliance,
            "global_laws": ["L1-Law of Law", "L2-Rule of 2", "L3-Rule of 4",
                            "L4-Absolute Structural Integrity", 
                            "L5-Communication", "L6-UBI Alignment"]
        }


# Convenience functions for simple usage
def think(query: str, domain: str = "general") -> BrainResponse:
    """Quick think function - one line cognitive processing."""
    client = BrainClient()
    return client.think(query, domain)


def validate(action: str) -> tuple[bool, list[str]]:
    """Quick validation function."""
    client = BrainClient()
    return client.validate_action(action)


def decide(question: str, options: list[str] | None = None) -> Decision:
    """Quick decision function."""
    client = BrainClient()
    return client.decide(question, options)
