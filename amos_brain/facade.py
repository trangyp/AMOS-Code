"""AMOS Brain Cognitive Facade - Simple SDK for external use."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from .agent_bridge import get_agent_bridge

# Architecture bridge integration
from .architecture_bridge import (
    ArchitecturalCognitionBridge,
    ArchitecturalContext,
    ArchitectureValidationResult,
    get_architecture_bridge,
)
from .canon_bridge import CanonBrainBridge, get_canon_bridge
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

    def __init__(self, repo_path: Optional[str] = None):
        self.brain = get_brain()
        self.laws = GlobalLaws()
        self.processor = BrainTaskProcessor()
        self.bridge = get_agent_bridge()
        self.state = get_state_manager()
        self.meta = get_meta_controller()
        self.monitor = get_monitor()
        self._arch_bridge: Optional[ArchitecturalCognitionBridge] = None
        self._execution_bridge = None
        self._canon_bridge: Optional[CanonBrainBridge] = None
        self._repo_path = repo_path

    @property
    def arch_bridge(self) -> ArchitecturalCognitionBridge:
        """Lazy initialization of architecture bridge."""
        if self._arch_bridge is None:
            self._arch_bridge = get_architecture_bridge(self._repo_path)
        return self._arch_bridge

    async def canon_bridge(self) -> CanonBrainBridge:
        """Lazy initialization of canon bridge."""
        if self._canon_bridge is None:
            self._canon_bridge = await get_canon_bridge()
        return self._canon_bridge

    async def execution_bridge(self):
        """Lazy initialization of execution bridge."""
        if self._execution_bridge is None:
            from .execution_bridge import get_execution_bridge

            self._execution_bridge = await get_execution_bridge()
        return self._execution_bridge

    async def execute_code(self, code: str, language: str = "python") -> dict:
        """Execute code with brain guidance via execution platform."""
        bridge = await self.execution_bridge()
        return await bridge.execute_with_brain_guidance(code, language)

    async def self_heal(self, issue_description: str) -> dict:
        """Self-heal an issue using execution platform."""
        bridge = await self.execution_bridge()
        return await bridge.self_heal_issue(issue_description)

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

    async def think(
        self,
        query: str,
        domain: str = "general",
        require_law_compliance: bool = True,
        use_canon_context: bool = True,
    ) -> BrainResponse:
        """Process a cognitive query through the full brain with Canon integration.

        Args:
            query: The question or task to think about
            domain: Domain context (software, science, business, etc.)
            require_law_compliance: Whether to enforce global laws
            use_canon_context: Whether to enrich query with Canon definitions

        Returns:
            BrainResponse with reasoning and compliance info
        """
        # Enrich query with Canon context if enabled
        canon_metadata = {}
        if use_canon_context:
            try:
                canon = await self.canon_bridge()
                ctx = canon.get_context_for_domain(domain)
                if ctx.glossary_terms:
                    query = canon.enrich_query(query, domain)
                    canon_metadata = {
                        "canon_enriched": True,
                        "canon_terms": len(ctx.glossary_terms),
                        "canon_agents": len(ctx.applicable_agents),
                        "canon_engines": len(ctx.relevant_engines),
                    }
            except Exception:
                canon_metadata = {"canon_enriched": False}

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
                **canon_metadata,
            },
            domain=domain,
        )

    def decide(
        self, question: str, options: Optional[list[str]] = None, context: str = ""
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

    def generate_repair_plan(self) -> Optional[Any]:
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

    def get_meta_architecture_context(self) -> Optional[Any]:
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

    # =========================================================================
    # Axiom One Civilization Substrate - New Capabilities
    # =========================================================================

    def spawn_agent(
        self,
        agent_class: str,
        task_objective: str,
        authorized_by: str = "brain_client",
    ) -> dict[str, Any]:
        """Spawn bounded AI agent for deterministic task execution.

        Args:
            agent_class: Type of agent (repo-debugger, patch-engineer, etc.)
            task_objective: What the agent should accomplish
            authorized_by: Who authorized this agent run

        Returns:
            Agent run metadata with ID and status
        """
        from .agent_fabric_kernel import (
            AgentTask,
            get_agent_fabric_kernel,
        )

        kernel = get_agent_fabric_kernel()

        # Register agent
        agent = kernel.register_agent(agent_class, authorized_by)

        # Create task
        task = AgentTask(objective=task_objective)

        # Spawn run
        run = kernel.spawn_run(agent.id, task, context={"repo_path": self._repo_path})

        return {
            "agent_id": agent.id,
            "run_id": run.id,
            "class": agent_class,
            "status": run.phase,
            "budget_max_usd": run.budget.max_usd,
            "permissions": {
                "tools": run.permissions.tools,
                "read_scope": run.permissions.read_scope,
                "write_scope": run.permissions.write_scope,
            },
        }

    def get_agent_run(self, run_id: str) -> dict[str, Any]:
        """Get status of agent run."""
        from .agent_fabric_kernel import get_agent_fabric_kernel

        kernel = get_agent_fabric_kernel()
        run = kernel.get_run(run_id)

        if not run:
            return None

        return {
            "run_id": run.id,
            "phase": run.phase,
            "agent_class": run.agent.class_id if run.agent else None,
            "objective": run.task.objective if run.task else None,
            "actions_count": len(run.actions),
            "budget_spent": run.budget.current_spend,
            "budget_remaining": run.budget.remaining(),
            "started_at": run.started_at.isoformat(),
        }

    def approve_agent_action(self, request_id: str, approved_by: str) -> bool:
        """Approve pending agent action."""
        from .agent_fabric_kernel import get_agent_fabric_kernel

        kernel = get_agent_fabric_kernel()
        return kernel.approve_action(request_id, approved_by)

    def autopsy_repo(
        self,
        failure_type: str,
        priority: str = "p2",
    ) -> dict[str, Any]:
        """Start automatic repo debugging (Repo Autopsy).

        Args:
            failure_type: Type of failure (build_failure, test_failure, etc.)
            priority: Priority level (p0, p1, p2, p3)

        Returns:
            Autopsy session metadata
        """
        from .repo_autopsy_engine import (
            AutopsyRequest,
            AutopsyRequestType,
            get_repo_autopsy_engine,
        )

        engine = get_repo_autopsy_engine()

        # Map string to enum
        request_type = AutopsyRequestType.BUILD_FAILURE
        try:
            request_type = AutopsyRequestType(failure_type)
        except ValueError:
            pass  # Use default

        request = AutopsyRequest(
            type=request_type,
            repo_path=self._repo_path or ".",
            trigger_source="manual",
            priority=priority,
        )

        session = asyncio.get_event_loop().run_until_complete(engine.start_autopsy(request))

        return {
            "session_id": session.request.id,
            "type": failure_type,
            "phase": session.phase.value,
            "patterns_found": len(session.identified_patterns),
            "fault_locations": len(session.fault_locations),
        }

    def get_autopsy_report(self, session_id: str) -> dict[str, Any]:
        """Get autopsy report for completed session."""
        from .repo_autopsy_engine import get_repo_autopsy_engine

        engine = get_repo_autopsy_engine()
        session = engine.get_session(session_id)

        if not session or not session.report:
            return None

        report = session.report
        return {
            "session_id": session_id,
            "patterns_found": [
                {
                    "name": match.pattern.name,
                    "confidence": match.confidence,
                    "auto_repair": match.pattern.auto_repair_eligible,
                }
                for match in report.patterns_found
            ],
            "fault_locations": [
                {"file": loc.file, "line": loc.line, "desc": loc.description}
                for loc in report.fault_locations
            ],
            "proposed_fixes_count": len(report.proposed_fixes),
            "recommended_fix": report.recommended_fix.description
            if report.recommended_fix
            else None,
            "requires_human_review": report.requires_human_review,
            "estimated_repair_time": report.estimated_repair_time,
            "markdown": report.to_markdown(),
        }

    def simulate_deployment(
        self,
        target: str,
        scenarios: list[dict] = None,
    ) -> dict[str, Any]:
        """Run deployment impact simulation.

        Args:
            target: PR number or commit to simulate
            scenarios: List of scenario configs (load_factor, etc.)

        Returns:
            Simulation result metadata
        """
        from .simulation_engine import (
            Scenario,
            SimulationRequest,
            SimulationType,
            get_simulation_engine,
        )

        engine = get_simulation_engine()

        # Default scenarios
        if not scenarios:
            scenarios = [
                {"name": "normal", "load_factor": 1.0},
                {"name": "peak", "load_factor": 2.0},
                {"name": "spike", "load_factor": 5.0},
            ]

        sim_scenarios = [
            Scenario(
                name=s.get("name", f"scenario_{i}"),
                load_factor=s.get("load_factor", 1.0),
                failure_mode=s.get("failure_mode"),
            )
            for i, s in enumerate(scenarios)
        ]

        request = SimulationRequest(
            type=SimulationType.DEPLOYMENT_IMPACT,
            target=target,
            repo_path=self._repo_path or ".",
            scenarios=sim_scenarios,
            requested_by="brain_client",
        )

        result = asyncio.get_event_loop().run_until_complete(engine.run_simulation(request))

        # Wait briefly for initial processing
        import time

        time.sleep(0.5)

        return {
            "simulation_id": result.request.id,
            "status": result.status,
            "target": target,
            "scenarios_count": len(sim_scenarios),
            "confidence": result.confidence_score,
        }

    def get_simulation_result(self, simulation_id: str) -> dict[str, Any]:
        """Get full simulation results."""
        from .simulation_engine import get_simulation_engine

        engine = get_simulation_engine()
        result = engine.get_result(simulation_id)

        if not result:
            return None

        return {
            "simulation_id": simulation_id,
            "status": result.status,
            "confidence": result.confidence_score,
            "impact": {
                "latency_p95_change": result.impact_analysis.performance.latency_p95.change_percent,
                "throughput_change": result.impact_analysis.performance.throughput.change_percent,
                "error_rate_change": result.impact_analysis.performance.error_rate.change_percent,
                "daily_cost": result.impact_analysis.costs.daily_cost,
                "cost_change": result.impact_analysis.costs.change_percent,
                "failure_probability": result.impact_analysis.risks.failure_probability,
                "rollback_complexity": result.impact_analysis.risks.rollback_complexity,
            },
            "recommendations": [
                {
                    "priority": rec.priority,
                    "category": rec.category,
                    "description": rec.description,
                    "confidence": rec.confidence,
                }
                for rec in result.recommendations
            ],
            "markdown": result.to_markdown() if result.status == "completed" else None,
        }

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
        self, decision: dict[str, Any], context: dict[str, Any] = None
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
        sunset_date: Optional[str] = None,
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
        self, order_id: str, operations: list[dict[str, Any]], execution_sequence: list[str]
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
        self,
        domain: str,
        declared_model: str,
        actual_model: Optional[str] = None,
        convergence_bound_ms: Optional[float] = None,
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

    def assess_operational_integrity(self) -> dict[str, Any]:
        """Assess operational architecture integrity."""
        try:
            from .operational_architecture_bridge import get_operational_architecture_bridge

            bridge = get_operational_architecture_bridge(self._repo_path)
            return bridge.assess_operational_integrity()
        except ImportError:
            return {"error": "operational_bridge not available"}

    def validate_cache_config(
        self,
        cache_id: str,
        strategy: str,
        invalidation: str,
        source_of_truth: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        staleness_bound_ms: Optional[int] = None,
    ) -> dict[str, Any]:
        """Validate cache configuration (I_cache)."""
        try:
            from .operational_architecture_bridge import get_operational_architecture_bridge

            bridge = get_operational_architecture_bridge(self._repo_path)
            return bridge.validate_cache_config(
                cache_id, strategy, invalidation, source_of_truth, ttl_seconds, staleness_bound_ms
            )
        except ImportError:
            return {"error": "operational_bridge not available"}

    def validate_fallback_topology(
        self, service_id: str, levels: dict[str, list[str]], triggers: dict[str, str] = None
    ) -> dict[str, Any]:
        """Validate fallback topology (I_fallback)."""
        try:
            from .operational_architecture_bridge import get_operational_architecture_bridge

            bridge = get_operational_architecture_bridge(self._repo_path)
            return bridge.validate_fallback_topology(service_id, levels, triggers)
        except ImportError:
            return {"error": "operational_bridge not available"}

    def validate_queue_config(
        self,
        queue_id: str,
        order: str,
        delivery_guarantee: str,
        max_retry: int = 3,
        dlq_enabled: bool = False,
        deduplication: bool = False,
        dedup_window_ms: Optional[int] = None,
    ) -> dict[str, Any]:
        """Validate queue configuration (I_queue)."""
        try:
            from .operational_architecture_bridge import get_operational_architecture_bridge

            bridge = get_operational_architecture_bridge(self._repo_path)
            return bridge.validate_queue_config(
                queue_id,
                order,
                delivery_guarantee,
                max_retry,
                dlq_enabled,
                deduplication,
                dedup_window_ms,
            )
        except ImportError:
            return {"error": "operational_bridge not available"}

    def validate_idempotency(
        self,
        operation_id: str,
        idempotent: bool,
        key_extractor: Optional[str] = None,
        storage_backend: Optional[str] = None,
    ) -> dict[str, Any]:
        """Validate idempotency configuration (I_idempotency)."""
        try:
            from .operational_architecture_bridge import get_operational_architecture_bridge

            bridge = get_operational_architecture_bridge(self._repo_path)
            return bridge.validate_idempotency(
                operation_id, idempotent, key_extractor, storage_backend
            )
        except ImportError:
            return {"error": "operational_bridge not available"}

    def get_operational_insights(self) -> dict[str, Any]:
        """Get operational architecture insights."""
        try:
            from .operational_architecture_bridge import get_operational_architecture_bridge

            bridge = get_operational_architecture_bridge(self._repo_path)
            return bridge.get_operational_insights()
        except ImportError:
            return {"error": "operational_bridge not available"}

    def assess_resilience(self) -> dict[str, Any]:
        """Assess recovery and resilience architecture."""
        try:
            from .recovery_resilience_bridge import get_recovery_resilience_bridge

            bridge = get_recovery_resilience_bridge(self._repo_path)
            return bridge.assess_resilience()
        except ImportError:
            return {"error": "resilience_bridge not available"}

    def validate_recovery_path(
        self,
        path_id: str,
        failure_scenario: str,
        recovery_type: str,
        estimated_rto_minutes: int,
        automated: bool = False,
        tested: bool = False,
    ) -> dict[str, Any]:
        """Validate recovery path (I_recovery)."""
        try:
            from .recovery_resilience_bridge import get_recovery_resilience_bridge

            bridge = get_recovery_resilience_bridge(self._repo_path)
            return bridge.validate_recovery_path(
                path_id, failure_scenario, recovery_type, estimated_rto_minutes, automated, tested
            )
        except ImportError:
            return {"error": "resilience_bridge not available"}

    def validate_dr_capability(
        self,
        service_id: str,
        dr_enabled: bool,
        multi_region: bool,
        backup_frequency_hours: int,
        failover_automated: bool,
        estimated_failover_minutes: int,
        estimated_rpo_minutes: int,
        data_sync_mode: str,
        last_dr_test: Optional[str] = None,
    ) -> dict[str, Any]:
        """Validate disaster recovery capability (I_disaster_recovery)."""
        try:
            from .recovery_resilience_bridge import get_recovery_resilience_bridge

            bridge = get_recovery_resilience_bridge(self._repo_path)
            return bridge.validate_dr_capability(
                service_id,
                dr_enabled,
                multi_region,
                backup_frequency_hours,
                failover_automated,
                estimated_failover_minutes,
                estimated_rpo_minutes,
                data_sync_mode,
                last_dr_test,
            )
        except ImportError:
            return {"error": "resilience_bridge not available"}

    def validate_blast_containment(
        self,
        component_id: str,
        max_blast_radius: float,
        blast_unit: str,
        containment_measures: list[str],
        isolation_domain: str,
    ) -> dict[str, Any]:
        """Validate blast containment (I_blast)."""
        try:
            from .recovery_resilience_bridge import get_recovery_resilience_bridge

            bridge = get_recovery_resilience_bridge(self._repo_path)
            return bridge.validate_blast_containment(
                component_id, max_blast_radius, blast_unit, containment_measures, isolation_domain
            )
        except ImportError:
            return {"error": "resilience_bridge not available"}

    def validate_failure_domain(
        self,
        domain_id: str,
        domain_type: str,
        components: list[str],
        isolation_score: float,
        dependencies: list[str] = None,
    ) -> dict[str, Any]:
        """Validate failure domain isolation (I_isolation)."""
        try:
            from .recovery_resilience_bridge import get_recovery_resilience_bridge

            bridge = get_recovery_resilience_bridge(self._repo_path)
            return bridge.validate_failure_domain(
                domain_id, domain_type, components, isolation_score, dependencies
            )
        except ImportError:
            return {"error": "resilience_bridge not available"}

    def get_resilience_insights(self) -> dict[str, Any]:
        """Get recovery and resilience insights."""
        try:
            from .recovery_resilience_bridge import get_recovery_resilience_bridge

            bridge = get_recovery_resilience_bridge(self._repo_path)
            return bridge.get_resilience_insights()
        except ImportError:
            return {"error": "resilience_bridge not available"}

    def assess_unified_architecture(self) -> dict[str, Any]:
        """Assess unified architecture across all 19 invariants."""
        try:
            from .unified_orchestrator_bridge import get_unified_orchestrator_bridge

            bridge = get_unified_orchestrator_bridge(self._repo_path)
            return bridge.assess_unified_architecture()
        except ImportError:
            return {"error": "unified_orchestrator not available"}

    def get_unified_architectural_decision(self) -> dict[str, Any]:
        """Get synthesized decision from all invariant domains."""
        try:
            from .unified_orchestrator_bridge import get_unified_orchestrator_bridge

            bridge = get_unified_orchestrator_bridge(self._repo_path)
            return bridge.get_unified_decision()
        except ImportError:
            return {"error": "unified_orchestrator not available"}

    def get_architectural_health_dashboard(self) -> dict[str, Any]:
        """Get comprehensive architectural health across all domains."""
        try:
            from .unified_orchestrator_bridge import get_unified_orchestrator_bridge

            bridge = get_unified_orchestrator_bridge(self._repo_path)
            return bridge.get_architectural_health_dashboard()
        except ImportError:
            return {"error": "unified_orchestrator not available"}

    def get_cross_domain_correlations(self) -> dict[str, Any]:
        """Get cross-domain invariant correlations."""
        try:
            from .unified_orchestrator_bridge import get_unified_orchestrator_bridge

            bridge = get_unified_orchestrator_bridge(self._repo_path)
            return bridge.get_cross_domain_correlations()
        except ImportError:
            return {"error": "unified_orchestrator not available"}

    def get_unified_architecture_insights(self) -> dict[str, Any]:
        """Get unified insights across all architectural domains."""
        try:
            from .unified_orchestrator_bridge import get_unified_orchestrator_bridge

            bridge = get_unified_orchestrator_bridge(self._repo_path)
            return bridge.get_unified_insights()
        except ImportError:
            return {"error": "unified_orchestrator not available"}

    def capture_architecture_state(
        self,
        components: list[dict[str, Any]],
        dependencies: list[dict[str, Any]],
        interfaces: list[dict[str, Any]],
        invariant_status: dict[str, bool],
    ) -> dict[str, Any]:
        """Capture architecture state into digital twin."""
        try:
            from .digital_twin_bridge import get_digital_twin_bridge

            bridge = get_digital_twin_bridge(self._repo_path)
            return bridge.capture_architecture_state(
                components, dependencies, interfaces, invariant_status
            )
        except ImportError:
            return {"error": "digital_twin not available"}

    def simulate_architectural_change(
        self, change_type: str, target: str, description: str, details: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate impact of architectural change."""
        try:
            from .digital_twin_bridge import get_digital_twin_bridge

            bridge = get_digital_twin_bridge(self._repo_path)
            return bridge.simulate_architectural_change(change_type, target, description, details)
        except ImportError:
            return {"error": "digital_twin not available"}

    def forecast_invariant_violations(self, steps: int = 5) -> dict[str, Any]:
        """Forecast future invariant violations."""
        try:
            from .digital_twin_bridge import get_digital_twin_bridge

            bridge = get_digital_twin_bridge(self._repo_path)
            return bridge.forecast_invariant_violations(steps)
        except ImportError:
            return {"error": "digital_twin not available"}

    def evaluate_what_if_scenario(self, changes: list[dict[str, Any]]) -> dict[str, Any]:
        """Evaluate what-if scenario with multiple changes."""
        try:
            from .digital_twin_bridge import get_digital_twin_bridge

            bridge = get_digital_twin_bridge(self._repo_path)
            return bridge.evaluate_what_if_scenario(changes)
        except ImportError:
            return {"error": "digital_twin not available"}

    def get_digital_twin_status(self) -> dict[str, Any]:
        """Get digital twin status."""
        try:
            from .digital_twin_bridge import get_digital_twin_bridge

            bridge = get_digital_twin_bridge(self._repo_path)
            return bridge.get_twin_status()
        except ImportError:
            return {"error": "digital_twin not available"}

    # ===================================================================
    # Layer 18: Distributed Systems Physics Engine
    # ===================================================================

    def assess_truth_arbitration(self, domains: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess truth arbitration integrity across domains."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.assess_truth_arbitration(domains)
        except ImportError:
            return {"error": "distributed_physics not available", "satisfied": False}

    def assess_irreversibility(self, transitions: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess irreversibility classification and compensation."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.assess_irreversibility(transitions)
        except ImportError:
            return {"error": "distributed_physics not available", "satisfied": False}

    def assess_quiescence(self, subsystems: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess quiescence integrity for safe stopping."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.assess_quiescence(subsystems)
        except ImportError:
            return {"error": "distributed_physics not available", "satisfied": False}

    def assess_policy_precedence(self, policy_layers: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess policy precedence hierarchy."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.assess_policy_precedence(policy_layers)
        except ImportError:
            return {"error": "distributed_physics not available", "satisfied": False}

    def assess_adaptive_bounds(self, loops: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess adaptive behavior boundedness."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.assess_adaptive_bounds(loops)
        except ImportError:
            return {"error": "distributed_physics not available", "satisfied": False}

    def assess_architectural_entropy(self, measurements: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess architectural entropy boundedness."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.assess_entropy(measurements)
        except ImportError:
            return {"error": "distributed_physics not available", "satisfied": False}

    def comprehensive_distributed_physics_assessment(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Run comprehensive distributed systems physics assessment."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            result = bridge.comprehensive_assessment(context)

            return {
                "layer": 18,
                "assessment_type": "distributed_physics",
                "engine_id": bridge.bridge_id,
                "result": result,
            }
        except ImportError:
            return {
                "error": "distributed_physics not available",
                "layer": 18,
                "assessment_type": "distributed_physics",
                "health": 0.0,
            }

    def get_distributed_physics_status(self) -> dict[str, Any]:
        """Get Layer 18 distributed physics engine status."""
        try:
            from .distributed_physics_bridge import get_distributed_physics_bridge

            bridge = get_distributed_physics_bridge()
            return bridge.get_status()
        except ImportError:
            return {"error": "distributed_physics not available", "layer": 18}

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
    import asyncio

    client = BrainClient()
    return asyncio.run(client.think(query, domain))


def validate(action: str) -> tuple[bool, list[str]]:
    """Quick validation function."""
    client = BrainClient()
    return client.validate_action(action)


def decide(question: str, options: list[str] = None) -> Decision:
    """Quick decision function."""
    client = BrainClient()
    return client.decide(question, options)


async def execute(code: str, language: str = "python") -> dict[str, Any]:
    """Quick execution function with brain guidance."""
    client = BrainClient()
    return await client.execute_code(code, language)


async def heal(issue_description: str) -> dict[str, Any]:
    """Quick self-healing function."""
    client = BrainClient()
    return await client.self_heal(issue_description)
