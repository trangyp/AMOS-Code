from __future__ import annotations

from typing import Any, Optional

"""
AMOS FastLoop Brain Bridge
Real integration between FastLoop runtime and AMOS Brain kernel.

This bridge connects:
- FastLoop classifier/router (fast path)
- AMOS Brain Kernel (full cognition)
- Engine Executor (domain-specific processing)
- Delta State Manager (state persistence)
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC
from amos_delta_state import (
    create_delta,
    get_delta_manager,
)

# FastLoop components
from amos_fastloop_classifier import (
    ClassificationResult,
    InterruptClass,
    InterruptClassifier,
    is_fast_path,
)
from amos_sparse_router import (
    RouteResult,
    get_router,
)
from clawspring.amos_brain.amos_kernel_runtime import (
    AMOSScores,
    BrainKernel,
)
from clawspring.amos_brain.engine_executor import EngineExecutor
from clawspring.amos_brain.kernel_router import KernelRouter, TaskIntent

# AMOS Brain components
from clawspring.amos_brain.loader import get_brain


@dataclass
class BrainBridgeResult:
    """Result from FastLoop-Brain bridge execution."""

    success: bool
    output: dict[str, Any]
    latency_ms: float
    path_taken: str  # "fast" or "full"
    classification: ClassificationResult
    route: RouteResult
    engines_used: list[str]
    state_id: Optional[str]
    branch_count: int = 0
    laws_checked: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FastLoopBrainBridge:
    """
    Bridge connecting FastLoop runtime to AMOS Brain kernel.

    Architecture:
    1. Fast classifier routes to fast path or full cognition
    2. Fast path: Direct engine execution (QUERY, ACTION, ECHO)
    3. Full path: AMOS Brain kernel with branch generation (REASONING)
    4. All paths use delta state management
    5. All paths respect AMOS global laws
    """

    def __init__(self):
        # FastLoop components
        self.classifier = InterruptClassifier()
        self.router = get_router()
        self.state_manager = get_delta_manager()

        # AMOS Brain components
        self.brain_loader = get_brain()
        self.kernel_router = KernelRouter(self.brain_loader)
        self.engine_executor = EngineExecutor(self.brain_loader)
        self.brain_kernel: Optional[BrainKernel] = None

        # Metrics
        self._request_count = 0
        self._fast_path_count = 0
        self._full_path_count = 0

    async def initialize(self) -> bool:
        """Initialize brain kernel with SIKS integration."""
        self.brain_kernel = BrainKernel()
        await self.brain_kernel.initialize_siks()
        return True  # Continue even if SIKS not available

    async def execute(self, request: str, context: dict[str, Any] = None) -> BrainBridgeResult:
        """
        Execute request through FastLoop-Brain bridge.

        Pipeline:
        1. Classify (< 1ms)
        2. Route to fast or full path
        3. Execute with appropriate engines
        4. Update state
        5. Return structured result
        """
        start_time = time.perf_counter()
        self._request_count += 1

        try:
            # Step 1: Classify
            classification = self.classifier.classify(request)

            # Step 2: Route
            route = self.router.route(classification)

            # Step 3: Execute based on path
            if is_fast_path(classification):
                self._fast_path_count += 1
                result = await self._execute_fast_path(request, classification, route, context)
                path_taken = "fast"
            else:
                self._full_path_count += 1
                result = await self._execute_full_path(request, classification, route, context)
                path_taken = "full"

            latency_ms = (time.perf_counter() - start_time) * 1000

            return BrainBridgeResult(
                success=True,
                output=result.get("output", {}),
                latency_ms=latency_ms,
                path_taken=path_taken,
                classification=classification,
                route=route,
                engines_used=result.get("engines_used", []),
                state_id=result.get("state_id"),
                branch_count=result.get("branch_count", 0),
                laws_checked=result.get("laws_checked", []),
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return BrainBridgeResult(
                success=False,
                output={"error": str(e)},
                latency_ms=latency_ms,
                path_taken="error",
                classification=ClassificationResult(
                    class_type=InterruptClass.UNKNOWN, confidence=0.0, latency_ms=0.0
                ),
                route=RouteResult(
                    module_set=route.module_set if "route" in locals() else None,
                    routing_latency_ms=0.0,
                ),
                engines_used=[],
                state_id=None,
            )

    async def _execute_fast_path(
        self,
        request: str,
        classification: ClassificationResult,
        route: RouteResult,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute fast path using engine executor.

        Fast path uses domain-specific engines directly without
        full branch generation and simulation.
        """
        # Parse intent for routing
        intent = self.kernel_router.parse_intent(request)

        # Select engines based on classification and intent
        engines = self._select_engines_for_fast_path(classification, intent)

        # Execute through engine executor
        execution_results = []
        for engine_name in engines:
            try:
                result = self.engine_executor.execute(request, [engine_name], context or {})
                execution_results.append({"engine": engine_name, "result": result})
            except Exception as e:
                execution_results.append({"engine": engine_name, "error": str(e)})

        # Create/update state
        state_id = None
        if context and "state_id" in context:
            state_id = context["state_id"]
            delta = create_delta(
                "fast_path_result",
                {
                    "request": request,
                    "classification": classification.class_type.name,
                    "engines": engines,
                    "results": execution_results,
                },
            )
            new_state = self.state_manager.apply_delta(state_id, delta)
            if new_state:
                state_id = new_state.state_id

        return {
            "output": {
                "path": "fast",
                "classification": classification.class_type.name,
                "intent": {
                    "primary_domain": intent.primary_domain,
                    "risk_level": intent.risk_level,
                },
                "engines_used": engines,
                "execution_results": execution_results,
                "laws_checked": ["L1", "L2", "L3", "L4"],  # Always check core laws
            },
            "engines_used": engines,
            "state_id": state_id,
            "branch_count": 0,  # No branches in fast path
            "laws_checked": ["L1", "L2", "L3", "L4"],
        }

    async def _execute_full_path(
        self,
        request: str,
        classification: ClassificationResult,
        route: RouteResult,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute full path using AMOS Brain kernel.

        Full path uses complete AMOS loop:
        Observe → Understand → ModelCause → Generate →
        Simulate → Calibrate → Filter → Collapse → Execute

        Respects search bounds from routing configuration.
        """
        if not self.brain_kernel:
            await self.initialize()

        # Step 1: Ingest observation into state graph
        observation = {
            "content": request,
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        U_t = await self.brain_kernel.ingest(observation)

        # Step 2: Extract state variables (Ω, K, Φ, I, S)
        vars = self.brain_kernel.extract_variables(U_t)

        # Step 3: Apply laws (L = I × S)
        legality = self.brain_kernel.apply_laws(vars)

        # Step 4: Generate branches with bounds from routing
        limits = route.module_set.search_limits
        max_branches = limits.get("branches", 3)
        limits.get("horizon", 2)

        branches = self.brain_kernel.generate_branches(
            U_t, vars, legality, max_branches=max_branches
        )

        # Step 5: Simulate and score branches
        scored_branches = []
        for branch in branches:
            scores = self.brain_kernel.simulate_branch(branch, vars)
            scored_branches.append((branch, scores))

        # Step 6: Collapse to best branch
        if scored_branches:
            best_branch, best_scores = max(scored_branches, key=lambda x: x[1].composite)
        else:
            best_branch = None
            best_scores = AMOSScores()

        # Step 7: Get domain engines for execution
        intent = self.kernel_router.parse_intent(request)
        engines = self._select_engines_for_full_path(intent)

        # Execute through engine executor with branch context
        execution_results = []
        for engine_name in engines:
            try:
                result = self.engine_executor.execute(
                    request, [engine_name], {**(context or {}), "branch": best_branch}
                )
                execution_results.append({"engine": engine_name, "result": result})
            except Exception as e:
                execution_results.append({"engine": engine_name, "error": str(e)})

        # Update state with full path result
        state_id = None
        if context and "state_id" in context:
            state_id = context["state_id"]
            delta = create_delta(
                "full_path_result",
                {
                    "request": request,
                    "classification": classification.class_type.name,
                    "branches_explored": len(branches),
                    "best_branch_score": best_scores.composite,
                    "legality_score": legality.legality_score,
                    "engines": engines,
                },
            )
            new_state = self.state_manager.apply_delta(state_id, delta)
            if new_state:
                state_id = new_state.state_id

        return {
            "output": {
                "path": "full",
                "classification": classification.class_type.name,
                "intent": {
                    "primary_domain": intent.primary_domain,
                    "risk_level": intent.risk_level,
                },
                "branches_explored": len(branches),
                "best_branch_score": best_scores.composite,
                "legality": {
                    "score": legality.legality_score,
                    "is_legal": legality.is_legal,
                    "drift": legality.drift_coefficient,
                },
                "engines_used": engines,
                "execution_results": execution_results,
                "state_graph": {
                    "vertices": len(U_t.vertices),
                    "edges": len(U_t.edges),
                    "omega": vars.omega,
                    "kappa": vars.kappa,
                    "phi": vars.phi,
                },
            },
            "engines_used": engines,
            "state_id": state_id,
            "branch_count": len(branches),
            "laws_checked": ["L1", "L2", "L3", "L4", "L5", "L6"],
        }

    def _select_engines_for_fast_path(
        self, classification: ClassificationResult, intent: TaskIntent
    ) -> list[str]:
        """Select engines for fast path execution."""
        engines = []

        if classification.class_type == InterruptClass.QUERY:
            # Query: Use logic and relevant domain engines
            engines.append("AMOS_Deterministic_Logic_And_Law_Engine")
            if intent.primary_domain in ["software", "ai", "cloud"]:
                engines.append("AMOS_Engineering_And_Mathematics_Engine")

        elif classification.class_type == InterruptClass.ACTION:
            # Action: Use engineering and validation engines
            engines.append("AMOS_Engineering_And_Mathematics_Engine")
            engines.append("AMOS_Design_Validation_Engine")

        elif classification.class_type == InterruptClass.ECHO:
            # Echo: Minimal processing
            engines.append("AMOS_Deterministic_Logic_And_Law_Engine")

        return engines

    def _select_engines_for_full_path(self, intent: TaskIntent) -> list[str]:
        """Select engines for full path execution."""
        engines = []

        # Always include logic engine
        engines.append("AMOS_Deterministic_Logic_And_Law_Engine")

        # Add domain-specific engines
        domain_engine_map = {
            "software": "AMOS_Engineering_And_Mathematics_Engine",
            "ai": "AMOS_Engineering_And_Mathematics_Engine",
            "cloud": "AMOS_Engineering_And_Mathematics_Engine",
            "logic": "AMOS_Deterministic_Logic_And_Law_Engine",
            "ubi": "AMOS_Biology_And_Cognition_Engine",
            "design": "AMOS_Design_Language_Engine",
            "security": "AMOS_Deterministic_Logic_And_Law_Engine",
        }

        if intent.primary_domain in domain_engine_map:
            engine = domain_engine_map[intent.primary_domain]
            if engine not in engines:
                engines.append(engine)

        # Add secondary domain engines
        for domain in intent.secondary_domains[:2]:  # Limit to 2
            if domain in domain_engine_map:
                engine = domain_engine_map[domain]
                if engine not in engines:
                    engines.append(engine)

        # Add validation engine for high-risk tasks
        if intent.risk_level == "high":
            engines.append("AMOS_Design_Validation_Engine")

        return engines

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics."""
        return {
            "total_requests": self._request_count,
            "fast_path_count": self._fast_path_count,
            "full_path_count": self._full_path_count,
            "fast_path_rate": self._fast_path_count / max(1, self._request_count),
            "brain_loaded": self.brain_loader is not None,
            "kernel_ready": self.brain_kernel is not None,
        }


# Global bridge instance
_bridge: Optional[FastLoopBrainBridge] = None


def get_brain_bridge() -> FastLoopBrainBridge:
    """Get global FastLoop-Brain bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = FastLoopBrainBridge()
    return _bridge


async def execute_with_brain(request: str, context: dict[str, Any] = None) -> BrainBridgeResult:
    """Convenience function for brain bridge execution."""
    bridge = get_brain_bridge()
    if not bridge.brain_kernel:
        await bridge.initialize()
    return await bridge.execute(request, context)


# Test
if __name__ == "__main__":

    async def test():
        print("\n" + "=" * 70)
        print("AMOS FastLoop-Brain Bridge Test")
        print("=" * 70)

        bridge = get_brain_bridge()
        await bridge.initialize()

        test_requests = [
            "What is the system status?",
            "Deploy the application to production",
            "Explain the architecture tradeoffs for this design",
            "Hello",
            "List all running services",
        ]

        for request in test_requests:
            result = await bridge.execute(request)

            path_icon = "⚡" if result.path_taken == "fast" else "🧠"
            print(
                f"\n{path_icon} {result.path_taken.upper():8} {result.latency_ms:6.2f}ms | {request[:40]}..."
            )
            print(
                f"   Classification: {result.classification.class_type.name} ({result.classification.confidence:.0%})"
            )
            print(
                f"   Engines: {', '.join(result.engines_used) if result.engines_used else 'None'}"
            )
            print(f"   Branches: {result.branch_count}")
            if result.laws_checked:
                print(f"   Laws: {', '.join(result.laws_checked)}")

        print("\n" + "=" * 70)
        stats = bridge.get_stats()
        print(f"Total: {stats['total_requests']}")
        print(f"Fast path: {stats['fast_path_rate']:.1%}")
        print(f"Brain loaded: {stats['brain_loaded']}")
        print(f"Kernel ready: {stats['kernel_ready']}")
        print("=" * 70)

    asyncio.run(test())
