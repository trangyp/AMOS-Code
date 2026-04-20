"""AMOS Brain-Semantics Bridge - Real integration of Formal Semantics Kernel with Brain.

Connects FormalSemanticsKernel to:
- SuperBrainRuntime (for execution)
- ThinkingKernel (for state transformation)
- ReasoningKernel (for inference)
- MathematicalFrameworkEngine (for equations)

This is REAL integration code, not documentation.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC

from pathlib import Path
from typing import Any, Optional

# Add paths for imports
AMOS_ROOT = Path(__file__).parent
sys.path.insert(0, str(AMOS_ROOT))

# Import Formal Semantics Kernel
from amos_formal_semantics_kernel import (
    get_formal_semantics_kernel,
)

# Import Brain components
try:
    from amos_reasoning_kernel import InferenceRule, Premise, ReasoningKernel
    from amos_thinking_kernel import Goal, ThinkingKernel, quick_think

    THINKING_AVAILABLE = True
except ImportError:
    THINKING_AVAILABLE = False

try:
    from amos_brain.super_brain import SuperBrainRuntime

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


@dataclass
class SemanticsTask:
    """A task for semantic processing."""

    task_id: str
    formal_expressions: list[str]
    goal: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SemanticsResult:
    """Result of semantic processing."""

    task_id: str
    compiled_expressions: dict[str, Any]
    invariants: dict[str, Any]
    objectives: dict[str, Any]
    transitions: dict[str, Any]
    proof_obligations: list[dict[str, Any]]
    semantic_integrity: float
    thinking_result: dict[str, Any] = None
    reasoning_result: dict[str, Any] = None
    processed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BrainSemanticsBridge:
    """
    Real bridge between Formal Semantics Kernel and AMOS Brain.

    This enables the brain to:
    1. Parse formal mathematical expressions
    2. Ground symbols with types and semantics
    3. Compile invariants to runtime-checkable predicates
    4. Compile objectives for optimization
    5. Generate proof obligations
    6. Integrate with thinking and reasoning kernels
    """

    def __init__(self):
        self.semantics_kernel = get_formal_semantics_kernel()
        self.thinking_kernel: Optional[ThinkingKernel] = None
        self.reasoning_kernel: Optional[ReasoningKernel] = None
        self.superbrain: Optional[SuperBrainRuntime] = None
        self._initialized = False
        self._math_engine: Optional[Any] = None

    def initialize(self) -> dict[str, bool]:
        """Initialize all brain connections."""
        status = {
            "semantics_kernel": True,
            "thinking_kernel": False,
            "reasoning_kernel": False,
            "superbrain": False,
            "math_framework": False,
        }

        # Initialize Thinking Kernel
        if THINKING_AVAILABLE:
            try:
                self.thinking_kernel = ThinkingKernel(enable_meta_thinking=True)
                status["thinking_kernel"] = True
            except Exception as e:
                print(f"ThinkingKernel init failed: {e}")

        # Initialize Reasoning Kernel
        try:
            self.reasoning_kernel = ReasoningKernel()
            status["reasoning_kernel"] = True
        except Exception as e:
            print(f"ReasoningKernel init failed: {e}")

        # Initialize SuperBrain
        if SUPERBRAIN_AVAILABLE:
            try:
                self.superbrain = SuperBrainRuntime()
                status["superbrain"] = True
            except Exception as e:
                print(f"SuperBrain init failed: {e}")

        # Load Math Framework
        status["math_framework"] = self._load_math_framework()

        self._initialized = True
        return status

    def _load_math_framework(self) -> bool:
        """Load Mathematical Framework Engine."""
        try:
            import importlib.util

            math_path = AMOS_ROOT / "clawspring" / "amos_brain" / "mathematical_framework_engine.py"
            if math_path.exists():
                spec = importlib.util.spec_from_file_location("math_engine", str(math_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules["math_engine"] = module
                    spec.loader.exec_module(module)
                    self._math_engine = module.get_framework_engine()
                    return True
        except Exception as e:
            print(f"Math framework load failed: {e}")
        return False

    def process_formal_task(self, task: SemanticsTask) -> SemanticsResult:
        """
        Process a formal semantics task through the brain.

        Pipeline:
        1. Compile formal expressions with semantics kernel
        2. Use thinking kernel for analysis
        3. Use reasoning kernel for inference
        4. Return integrated result
        """
        # Step 1: Compile formal expressions
        compiled = self.semantics_kernel.compile_formal_system(task.formal_expressions)

        # Step 2: Thinking analysis (if available)
        thinking_result = None
        if self.thinking_kernel and task.goal:
            try:
                from amos_thinking_kernel import Goal as TGoal

                goals = [TGoal(id="semantic", description=task.goal, priority=1.0)]
                state = self.thinking_kernel.initialize_state(
                    goals=goals, initial_workspace=task.formal_expressions
                )
                t_result = self.thinking_kernel.think(state, max_iterations=5)
                thinking_result = {
                    "converged": t_result.converged,
                    "iterations": t_result.iterations,
                    "quality_progression": t_result.quality_progression,
                }
            except Exception as e:
                thinking_result = {"error": str(e)}

        # Step 3: Reasoning (if available)
        reasoning_result = None
        if self.reasoning_kernel:
            try:
                # Add premises from compiled expressions
                for expr_id, expr in compiled["expressions"].items():
                    premise = Premise(
                        content=expr.raw_text, premise_type="definition", source=expr_id
                    )
                    self.reasoning_kernel.add_premise(premise)

                # Run inference
                conclusions = self.reasoning_kernel.infer(mode="deductive", max_depth=3)
                reasoning_result = {
                    "conclusions": len(conclusions),
                    "premises": len(self.reasoning_kernel.premises),
                }
            except Exception as e:
                reasoning_result = {"error": str(e)}

        # Build result
        understanding_state = compiled.get("understanding_state")
        integrity = 0.0
        if understanding_state:
            integrity = understanding_state.overall_semantic_integrity

        result = SemanticsResult(
            task_id=task.task_id,
            compiled_expressions={
                k: {
                    "kind": v.kind.name,
                    "text": v.raw_text[:100],
                    "free_symbols": v.free_symbols,
                    "mode": v.operational_semantics.mode,
                }
                for k, v in compiled.get("expressions", {}).items()
            },
            invariants={
                k: {
                    "predicate": v.predicate,
                    "severity": v.severity,
                    "on_violation": v.on_violation,
                }
                for k, v in compiled.get("invariants", {}).items()
            },
            objectives={
                k: {
                    "optimize_over": v.optimize_over,
                    "operator": v.operator,
                    "score_function": v.score_function[:100],
                }
                for k, v in compiled.get("objectives", {}).items()
            },
            transitions={
                k: {
                    "state_in": v.state_in,
                    "operator": v.operator,
                    "state_out": v.state_out,
                }
                for k, v in compiled.get("transitions", {}).items()
            },
            proof_obligations=[
                {"id": po.id, "statement": po.statement, "kind": po.kind}
                for po in compiled.get("proof_obligations", [])[:10]
            ],
            semantic_integrity=integrity,
            thinking_result=thinking_result,
            reasoning_result=reasoning_result,
        )

        return result

    def query_equation(self, name: str) -> dict[str, Any]:
        """Query equation from math framework."""
        if not self._math_engine:
            return None

        try:
            eq = self._math_engine.query_equation(name)
            if eq:
                return {
                    "name": eq.name,
                    "domain": eq.domain.name,
                    "latex": eq.latex,
                    "description": eq.description,
                    "parameters": eq.parameters,
                }
        except Exception as e:
            return {"error": str(e)}
        return None

    def validate_invariant(self, invariant_id: str, state: dict[str, Any]) -> bool:
        """Validate a compiled invariant against current state."""
        if invariant_id not in self.semantics_kernel.invariants:
            return False

        inv = self.semantics_kernel.invariants[invariant_id]
        if inv.predicate_fn:
            return inv.predicate_fn(state)
        return False

    def get_semantic_state(self) -> dict[str, Any]:
        """Get current semantic compilation state."""
        return self.semantics_kernel.to_dict()

    def execute_through_superbrain(
        self, task: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Execute task through SuperBrain with semantic awareness."""
        if not self.superbrain:
            return {"error": "SuperBrain not available"}

        try:
            return self.superbrain.execute_task(task, context or {})
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
_bridge: Optional[BrainSemanticsBridge] = None


def get_brain_semantics_bridge() -> BrainSemanticsBridge:
    """Get or create the singleton bridge."""
    global _bridge
    if _bridge is None:
        _bridge = BrainSemanticsBridge()
        _bridge.initialize()
    return _bridge


def process_amos_formalism(expressions: list[str], goal: str = "") -> SemanticsResult:
    """
    High-level function to process AMOS formal expressions.

    Usage:
        result = process_amos_formalism([
            r"\\Psi_t = (V_t, E_t, S_t, \\Lambda_t)",
            r"B^\\star = \\arg\\max_{B_i}[Value_i - Risk_i]",
        ], goal="optimize_branch_selection")
    """
    bridge = get_brain_semantics_bridge()

    task = SemanticsTask(
        task_id=f"task_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        formal_expressions=expressions,
        goal=goal,
    )

    return bridge.process_formal_task(task)


if __name__ == "__main__":
    # Real execution test
    print("=" * 70)
    print("AMOS BRAIN-SEMANTICS BRIDGE - LIVE TEST")
    print("=" * 70)

    # Initialize
    bridge = get_brain_semantics_bridge()
    status = bridge.initialize()

    print("\n📊 Component Status:")
    for component, active in status.items():
        icon = "✅" if active else "❌"
        print(f"  {icon} {component}")

    # Test 1: Process formal expressions
    print("\n🧪 Test 1: Formal Expression Processing")
    test_expressions = [
        r"\Psi_t = (V_t, E_t, S_t, \Lambda_t)",
        r"B^\star = \arg\max_{B_i}[Value_i - Risk_i - Cost_i]",
        r"\frac{dDependency}{dt} \le 0",
    ]

    result = process_amos_formalism(test_expressions, goal="semantic_analysis")

    print(f"\n  Task ID: {result.task_id}")
    print(f"  Compiled Expressions: {len(result.compiled_expressions)}")
    print(f"  Invariants: {len(result.invariants)}")
    print(f"  Objectives: {len(result.objectives)}")
    print(f"  Semantic Integrity: {result.semantic_integrity * 100:.1f}%")

    if result.thinking_result:
        print("\n  Thinking Result:")
        print(f"    Converged: {result.thinking_result.get('converged')}")
        print(f"    Iterations: {result.thinking_result.get('iterations')}")

    if result.reasoning_result:
        print("\n  Reasoning Result:")
        print(f"    Conclusions: {result.reasoning_result.get('conclusions')}")
        print(f"    Premises: {result.reasoning_result.get('premises')}")

    # Test 2: Query equation
    print("\n🧪 Test 2: Math Framework Query")
    eq_result = bridge.query_equation("softmax")
    if eq_result:
        print(f"  Found equation: {eq_result.get('name')}")
        print(f"  Domain: {eq_result.get('domain')}")
    else:
        print("  Math framework not available")

    print("\n" + "=" * 70)
    print("BRIDGE TEST COMPLETE")
    print("=" * 70)
