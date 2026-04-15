"""AMOS Brain Cognitive Facade - Simple SDK for external use."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent_bridge import get_agent_bridge

# Architecture bridge integration
from .architecture_bridge import (
    ArchitecturalCognitionBridge,
    ArchitecturalContext,
    ArchitectureValidationResult,
    get_architecture_bridge,
)
from .laws import GlobalLaws
from .loader import get_brain
from .meta_controller import get_meta_controller
from .monitor import get_monitor
from .state_manager import get_state_manager
from .task_processor import BrainTaskProcessor


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
    """AMOS Brain SDK Client - Unified interface to all 9 layers.

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

    def __init__(self, repo_path: str | None = None):
        self.brain = get_brain()
        self.laws = GlobalLaws()
        self.processor = BrainTaskProcessor()
        self.bridge = get_agent_bridge()
        self.state = get_state_manager()
        self.meta = get_meta_controller()
        self.monitor = get_monitor()
        self._arch_bridge: ArchitecturalCognitionBridge | None = None
        self._repo_path = repo_path

    @property
    def arch_bridge(self) -> ArchitecturalCognitionBridge:
        """Lazy initialization of architecture bridge."""
        if self._arch_bridge is None:
            self._arch_bridge = get_architecture_bridge(self._repo_path)
        return self._arch_bridge

    def get_architectural_context(self) -> ArchitecturalContext:
        """Get complete architectural context for the repository."""
        return self.arch_bridge.get_context()

    def validate_architecture(
        self, action: str, target_files: list[str]
    ) -> ArchitectureValidationResult:
        """Validate a proposed action against architectural constraints.

        Args:
            action: Type of action (modify, delete, create, refactor)
            target_files: Files that will be changed

        Returns:
            Validation result with approval status and constraints
        """
        return self.arch_bridge.validate(action, target_files)

    def think(
        self, query: str, domain: str = "general", require_law_compliance: bool = True
    ) -> BrainResponse:
        """Process a cognitive query through the full brain.

        Args:
            query: The question or task to think about
            domain: Domain context (software, science, business, etc.)
            require_law_compliance: Whether to enforce global laws

        Returns:
            BrainResponse with reasoning and compliance info
        """
        # Process through brain
        result = self.processor.process(query)

        # Monitor the reasoning
        self.monitor.record_reasoning(
            task_description=query,
            processing_time_ms=result.processing_time_ms,
            law_violations=len(result.law_violations),
            confidence=result.confidence,
            kernels_used=result.kernels_used,
        )

        # Check law compliance
        law_compliant = len(result.law_violations) == 0
        violations = [v.get("message", "") for v in result.law_violations]

        # Use the processor's actual output as primary content
        content = result.output

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
            domain=domain,
        )

    def decide(
        self, question: str, options: list[str] | None = None, context: str = ""
    ) -> Decision:
        """Make a decision with full cognitive analysis.

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

        violations = [v.get("law", "unknown") for v in result.law_violations]

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
            alternative_actions=alternatives,
        )

    def validate_action(
        self, action_description: str, action_type: str = "general"
    ) -> tuple[bool, list[str]]:
        """Quick validation if an action complies with global laws.

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
        ok, msg = self.laws.enforce_l2_dual_check(action_description, "Alternative considered")
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
                context=action_description[:50],
            )

        return is_valid, violations

    def orchestrate(self, goal: str, max_iterations: int = 10) -> dict[str, Any]:
        """Orchestrate a complex goal through meta-cognitive control.

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
                {"id": t.task_id, "description": t.description, "status": t.status.value}
                for t in plan.subtasks[:10]
            ],
        }

    def generate_repair_plan(self) -> Any | None:
        """Generate automated repair plan from all detections."""
        try:
            from .repair_bridge import get_repair_bridge

            bridge = get_repair_bridge(self._repo_path)
            return bridge.generate_complete_repair_plan()
        except ImportError:
            return None

    def get_auto_fixes(self, max_fixes: int = 10) -> list[Any]:
        """Get repairs that can be safely applied automatically."""
        try:
            from .repair_bridge import get_repair_bridge

            bridge = get_repair_bridge(self._repo_path)
            return bridge.get_safe_auto_fixes(max_fixes)
        except ImportError:
            return []

    def get_meta_architecture_context(self) -> Any | None:
        """Get complete meta-architecture context with all failure classes."""
        try:
            from .meta_architecture_bridge import get_meta_architecture_bridge

            bridge = get_meta_architecture_bridge(self._repo_path)
            return bridge.get_meta_context()
        except ImportError:
            return None

    def check_meta_invariants(self) -> dict[str, bool]:
        """Check all meta-architecture invariants (semantic, temporal, trust, recovery, self-integrity)."""
        try:
            from .meta_architecture_bridge import get_meta_architecture_bridge

            bridge = get_meta_architecture_bridge(self._repo_path)
            return bridge.check_meta_invariants()
        except ImportError:
            return {}

    def get_critical_meta_issues(self) -> list[Any]:
        """Get critical meta-architecture issues (failures of meaning, time, trust, recovery)."""
        try:
            from .meta_architecture_bridge import get_meta_architecture_bridge

            bridge = get_meta_architecture_bridge(self._repo_path)
            return bridge.get_critical_meta_issues()
        except ImportError:
            return []

    def get_architecture_health(self) -> dict[str, Any]:
        """Get complete architecture health snapshot for dashboard."""
        try:
            from .monitoring_bridge import get_monitoring_bridge

            bridge = get_monitoring_bridge(self._repo_path)
            return bridge.get_health_dashboard()
        except ImportError:
            return {"error": "monitoring_bridge not available"}

    def validate_pre_commit(self) -> dict[str, Any]:
        """Validate staged files for pre-commit hook integration."""
        try:
            from .monitoring_bridge import get_monitoring_bridge

            bridge = get_monitoring_bridge(self._repo_path)
            return bridge.validate_pre_commit()
        except ImportError:
            return {"valid": True, "message": "monitoring not available"}

    def predict_architecture_failures(self) -> dict[str, Any]:
        """Predict future architecture failures from current health data."""
        try:
            from .monitoring_bridge import get_monitoring_bridge
            from .predictive_bridge import get_predictive_bridge

            # Get current health data
            monitor = get_monitoring_bridge(self._repo_path)
            health = monitor.get_health_dashboard()

            # Generate predictions
            predictor = get_predictive_bridge(self._repo_path)
            return predictor.predict_from_health(health)
        except ImportError:
            return {"error": "predictive_bridge not available"}

    def assess_change_risk(self, files: list[str]) -> dict[str, Any]:
        """Assess risk of proposed code changes before committing."""
        try:
            from .predictive_bridge import get_predictive_bridge

            bridge = get_predictive_bridge(self._repo_path)
            return bridge.assess_change_risk(files)
        except ImportError:
            return {"error": "predictive_bridge not available"}

    def get_predictive_warnings(self) -> list[dict[str, Any]]:
        """Get active early warnings about impending architecture issues."""
        try:
            from .predictive_bridge import get_predictive_bridge

            bridge = get_predictive_bridge(self._repo_path)
            return bridge.get_active_warnings()
        except ImportError:
            return []

    def evaluate_for_autonomous_action(self, prediction: dict[str, Any]) -> dict[str, Any]:
        """Evaluate prediction for autonomous action."""
        try:
            from .governance_bridge import get_governance_bridge

            bridge = get_governance_bridge(self._repo_path)
            return bridge.evaluate_prediction(prediction)
        except ImportError:
            return {"decision": "recommend", "error": "governance not available"}

    def evaluate_repair_for_auto_apply(self, repair: dict[str, Any]) -> dict[str, Any]:
        """Evaluate repair for autonomous application."""
        try:
            from .governance_bridge import get_governance_bridge

            bridge = get_governance_bridge(self._repo_path)
            return bridge.evaluate_repair(repair)
        except ImportError:
            return {"decision": "recommend", "error": "governance not available"}

    def get_governance_audit(self) -> list[dict[str, Any]]:
        """Get autonomous governance decision audit log."""
        try:
            from .governance_bridge import get_governance_bridge

            bridge = get_governance_bridge(self._repo_path)
            return bridge.get_governance_audit()
        except ImportError:
            return []

    def get_autonomy_stats(self) -> dict[str, Any]:
        """Get statistics on autonomous decisions."""
        try:
            from .governance_bridge import get_governance_bridge

            bridge = get_governance_bridge(self._repo_path)
            return bridge.get_autonomy_stats()
        except ImportError:
            return {}

    def discover_fleet(self, max_depth: int = 2) -> dict[str, Any]:
        """Auto-discover repositories under root path."""
        try:
            from .fleet_bridge import get_fleet_bridge

            bridge = get_fleet_bridge(self._repo_path)
            return bridge.discover_fleet(name="default", max_depth=max_depth)
        except ImportError:
            return {"error": "fleet_bridge not available"}

    def get_fleet_health(self, fleet_name: str = "default") -> dict[str, Any]:
        """Get aggregated health across fleet."""
        try:
            from .fleet_bridge import get_fleet_bridge

            bridge = get_fleet_bridge(self._repo_path)
            return bridge.get_fleet_health(fleet_name)
        except ImportError:
            return {"error": "fleet_bridge not available"}

    def find_cross_repo_patterns(self, fleet_name: str = "default") -> dict[str, Any]:
        """Find patterns common across multiple repos."""
        try:
            from .fleet_bridge import get_fleet_bridge

            bridge = get_fleet_bridge(self._repo_path)
            return bridge.find_cross_repo_patterns(fleet_name)
        except ImportError:
            return {"error": "fleet_bridge not available"}

    def analyze_shared_contracts(self, fleet_name: str = "default") -> dict[str, Any]:
        """Analyze contracts shared across fleet."""
        try:
            from .fleet_bridge import get_fleet_bridge

            bridge = get_fleet_bridge(self._repo_path)
            return bridge.analyze_shared_contracts(fleet_name)
        except ImportError:
            return {"error": "fleet_bridge not available"}

    def get_fleet_remediation_plan(self, fleet_name: str = "default") -> dict[str, Any]:
        """Get coordinated remediation plan for fleet."""
        try:
            from .fleet_bridge import get_fleet_bridge

            bridge = get_fleet_bridge(self._repo_path)
            return bridge.generate_fleet_remediation_plan(fleet_name)
        except ImportError:
            return {"error": "fleet_bridge not available"}

    def explain_decision(
        self, decision: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Explain a decision with reasoning."""
        try:
            from .explanatory_bridge import get_explanatory_bridge

            bridge = get_explanatory_bridge(self._repo_path)
            return bridge.explain_decision(decision, context)
        except ImportError:
            return {"error": "explanatory_bridge not available"}

    def explain_confidence(self, score: float, factors: dict[str, Any]) -> dict[str, Any]:
        """Explain why confidence is at a particular level."""
        try:
            from .explanatory_bridge import get_explanatory_bridge

            bridge = get_explanatory_bridge(self._repo_path)
            return bridge.explain_confidence(score, factors)
        except ImportError:
            return {"error": "explanatory_bridge not available"}

    def get_decision_trace(
        self,
        start_state: dict[str, Any],
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        """Get reasoning trace for a decision."""
        try:
            from .explanatory_bridge import get_explanatory_bridge

            bridge = get_explanatory_bridge(self._repo_path)
            return bridge.trace_reasoning(start_state, decision)
        except ImportError:
            return {"error": "explanatory_bridge not available"}

    def justify_action(
        self, action: str, expected_outcome: str, risks: list[str], benefits: list[str]
    ) -> dict[str, Any]:
        """Get justification for an action."""
        try:
            from .explanatory_bridge import get_explanatory_bridge

            bridge = get_explanatory_bridge(self._repo_path)
            return bridge.justify_action(action, expected_outcome, risks, benefits)
        except ImportError:
            return {"error": "explanatory_bridge not available"}

    def reflect_on_decisions(self) -> dict[str, Any]:
        """Perform meta-cognitive reflection on decision history."""
        try:
            from .meta_cognitive_bridge import get_meta_cognitive_bridge

            bridge = get_meta_cognitive_bridge(self._repo_path)
            return bridge.reflect()
        except ImportError:
            return {"error": "meta_cognitive_bridge not available"}

    def record_decision_outcome(
        self,
        decision_type: str,
        context: dict[str, Any],
        outcome: dict[str, Any],
        confidence: float,
        success: bool,
    ) -> dict[str, Any]:
        """Record a decision for meta-cognitive learning."""
        try:
            from .meta_cognitive_bridge import get_meta_cognitive_bridge

            bridge = get_meta_cognitive_bridge(self._repo_path)
            return bridge.record_decision(decision_type, context, outcome, confidence, success)
        except ImportError:
            return {"error": "meta_cognitive_bridge not available"}

    def get_meta_cognitive_status(self) -> dict[str, Any]:
        """Get meta-cognitive reflection status."""
        try:
            from .meta_cognitive_bridge import get_meta_cognitive_bridge

            bridge = get_meta_cognitive_bridge(self._repo_path)
            return bridge.get_status()
        except ImportError:
            return {"error": "meta_cognitive_bridge not available"}

    def get_self_improvement_suggestions(self) -> dict[str, Any]:
        """Get self-improvement suggestions from meta-cognitive analysis."""
        try:
            from .meta_cognitive_bridge import get_meta_cognitive_bridge

            bridge = get_meta_cognitive_bridge(self._repo_path)
            return bridge.get_improvement_suggestions()
        except ImportError:
            return {"error": "meta_cognitive_bridge not available"}

    def find_causal_root_causes(self, symptom: str, data: dict[str, Any]) -> dict[str, Any]:
        """Find true root causes using causal reasoning (not just correlations)."""
        try:
            from .causal_bridge import get_causal_bridge

            bridge = get_causal_bridge(self._repo_path)
            return bridge.find_root_causes(symptom, data)
        except ImportError:
            return {"error": "causal_bridge not available"}

    def check_correlation_vs_causation(self, var1: str, var2: str) -> dict[str, Any]:
        """Determine if relationship between variables is causal or spurious."""
        try:
            from .causal_bridge import get_causal_bridge

            bridge = get_causal_bridge(self._repo_path)
            return bridge.check_spurious_correlation(var1, var2)
        except ImportError:
            return {"error": "causal_bridge not available"}

    def analyze_causal_intervention(
        self, target: str, new_value: Any, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze expected effects of an intervention using causal reasoning."""
        try:
            from .causal_bridge import get_causal_bridge

            bridge = get_causal_bridge(self._repo_path)
            return bridge.analyze_intervention(target, new_value, context)
        except ImportError:
            return {"error": "causal_bridge not available"}

    def counterfactual_reasoning(
        self, observation: dict[str, Any], target: str, new_value: Any
    ) -> dict[str, Any]:
        """Perform counterfactual reasoning: what if X had been different?"""
        try:
            from .causal_bridge import get_causal_bridge

            bridge = get_causal_bridge(self._repo_path)
            return bridge.counterfactual(observation, target, new_value)
        except ImportError:
            return {"error": "causal_bridge not available"}

    def get_causal_insights(self) -> dict[str, Any]:
        """Get general causal insights about software architecture."""
        try:
            from .causal_bridge import get_causal_bridge

            bridge = get_causal_bridge(self._repo_path)
            return bridge.get_insights()
        except ImportError:
            return {"error": "causal_bridge not available"}

    def assess_constitutional_integrity(self) -> dict[str, Any]:
        """Assess constitutional architecture integrity."""
        try:
            from .constitutional_bridge import get_constitutional_bridge

            bridge = get_constitutional_bridge(self._repo_path)
            return bridge.assess_constitutional_integrity()
        except ImportError:
            return {"error": "constitutional_bridge not available"}

    def check_state_ownership(
        self, domain: str, declared_writers: list[str], observed_writers: list[str]
    ) -> dict[str, Any]:
        """Check if state domain has clear ownership (I_state_ownership)."""
        try:
            from .constitutional_bridge import get_constitutional_bridge

            bridge = get_constitutional_bridge(self._repo_path)
            return bridge.check_state_ownership(domain, declared_writers, observed_writers)
        except ImportError:
            return {"error": "constitutional_bridge not available"}

    def validate_absence_semantics(self, domain: str, required_states: list[str]) -> dict[str, Any]:
        """Validate absence semantics taxonomy (I_absence)."""
        try:
            from .constitutional_bridge import get_constitutional_bridge

            bridge = get_constitutional_bridge(self._repo_path)
            return bridge.validate_absence_semantics(domain, required_states)
        except ImportError:
            return {"error": "constitutional_bridge not available"}

    def check_semantic_versioning(
        self, claimed_version: str, actual_changes: dict[str, Any]
    ) -> dict[str, Any]:
        """Check semantic versioning honesty (I_semver)."""
        try:
            from .constitutional_bridge import get_constitutional_bridge

            bridge = get_constitutional_bridge(self._repo_path)
            return bridge.check_semantic_versioning(claimed_version, actual_changes)
        except ImportError:
            return {"error": "constitutional_bridge not available"}

    def check_protocol_lifecycle(
        self,
        interface: str,
        current_state: str,
        has_replacement: bool = False,
        sunset_date: str | None = None,
    ) -> dict[str, Any]:
        """Check protocol lifecycle completeness (I_protocol_lifecycle)."""
        try:
            from .constitutional_bridge import get_constitutional_bridge

            bridge = get_constitutional_bridge(self._repo_path)
            return bridge.check_protocol_lifecycle(
                interface, current_state, has_replacement, sunset_date
            )
        except ImportError:
            return {"error": "constitutional_bridge not available"}

    def get_constitutional_insights(self) -> dict[str, Any]:
        """Get constitutional architecture insights."""
        try:
            from .constitutional_bridge import get_constitutional_bridge

            bridge = get_constitutional_bridge(self._repo_path)
            return bridge.get_constitutional_insights()
        except ImportError:
            return {"error": "constitutional_bridge not available"}

    def assess_temporal_integrity(self) -> dict[str, Any]:
        """Assess temporal architecture integrity."""
        try:
            from .temporal_architecture_bridge import get_temporal_architecture_bridge

            bridge = get_temporal_architecture_bridge(self._repo_path)
            return bridge.assess_temporal_integrity()
        except ImportError:
            return {"error": "temporal_bridge not available"}

    def validate_partial_order(
        self, order_id: str, operations: list[dict[str, Any]],
        execution_sequence: list[str]
    ) -> dict[str, Any]:
        """Validate execution respects partial order (I_partial_order)."""
        try:
            from .temporal_architecture_bridge import get_temporal_architecture_bridge

            bridge = get_temporal_architecture_bridge(self._repo_path)
            return bridge.validate_partial_order(order_id, operations, execution_sequence)
        except ImportError:
            return {"error": "temporal_bridge not available"}

    def validate_migration_order(
        self, migrations: list[str], execution_order: list[str]
    ) -> dict[str, Any]:
        """Validate migration executes before deploy (I_partial_order)."""
        try:
            from .temporal_architecture_bridge import get_temporal_architecture_bridge

            bridge = get_temporal_architecture_bridge(self._repo_path)
            return bridge.validate_migration_order(migrations, execution_order)
        except ImportError:
            return {"error": "temporal_bridge not available"}

    def check_clock_consistency(self, components: list[dict[str, Any]]) -> dict[str, Any]:
        """Check clock semantics consistency across components (I_clock)."""
        try:
            from .temporal_architecture_bridge import get_temporal_architecture_bridge

            bridge = get_temporal_architecture_bridge(self._repo_path)
            return bridge.check_clock_consistency(components)
        except ImportError:
            return {"error": "temporal_bridge not available"}

    def validate_consistency_model(
        self, domain: str, declared_model: str,
        actual_model: str | None = None, convergence_bound_ms: float | None = None
    ) -> dict[str, Any]:
        """Validate consistency model declaration (I_consistency, I_eventuality)."""
        try:
            from .temporal_architecture_bridge import get_temporal_architecture_bridge

            bridge = get_temporal_architecture_bridge(self._repo_path)
            return bridge.validate_consistency_model(
                domain, declared_model, actual_model, convergence_bound_ms
            )
        except ImportError:
            return {"error": "temporal_bridge not available"}

    def get_temporal_insights(self) -> dict[str, Any]:
        """Get temporal architecture insights."""
        try:
            from .temporal_architecture_bridge import get_temporal_architecture_bridge

            bridge = get_temporal_architecture_bridge(self._repo_path)
            return bridge.get_temporal_insights()
        except ImportError:
            return {"error": "temporal_bridge not available"}

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
            "global_laws": [
                "L1-Law of Law",
                "L2-Rule of 2",
                "L3-Rule of 4",
                "L4-Absolute Structural Integrity",
                "L5-Communication",
                "L6-UBI Alignment",
            ],
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
