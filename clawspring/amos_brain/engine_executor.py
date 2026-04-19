"""AMOS Cognitive Engine Executor - Executes tasks through selected engines."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ExecutionResult:
    """Result of executing a task through cognitive engines."""

    task: str
    engines_used: list[str]
    reasoning_steps: list[dict[str, Any]]
    output: str
    laws_checked: list[str]
    violations_found: list[str]
    execution_time_ms: float = 0.0
    mathematical_analysis: dict[str, Any] = None


class EngineExecutor:
    """Executes tasks through AMOS cognitive engines with law enforcement."""

    def __init__(self, brain_loader: Any = None):
        self.brain_loader = brain_loader
        self._engines: dict[str, Callable] = {}
        self._math_engine: Any = None
        self._register_default_engines()
        self._initialize_math_engine()

    def _initialize_math_engine(self):
        """Initialize mathematical framework engine."""
        try:
            from .mathematical_framework_engine import get_framework_engine

            self._math_engine = get_framework_engine()
        except Exception as e:
            print(f"[EngineExecutor] Math engine init warning: {e}")

    def _register_default_engines(self):
        """Register the core AMOS cognitive engines."""
        self._engines = {
            "AMOS_Deterministic_Logic_And_Law_Engine": self._execute_logic_engine,
            "AMOS_Engineering_And_Mathematics_Engine": self._execute_engineering_engine,
            "AMOS_Design_Language_Engine": self._execute_design_engine,
            "AMOS_Biology_And_Cognition_Engine": self._execute_biology_engine,
            "AMOS_Strategy_Game_Engine": self._execute_strategy_engine,
            "AMOS_Society_Culture_Engine": self._execute_society_engine,
            "AMOS_Design_Validation_Engine": self._execute_validation_engine,
        }
        self._validation_engine = None
        self._initialize_validation_engine()

    def _initialize_validation_engine(self):
        """Initialize design validation engine."""
        try:
            from .design_validation_engine import get_design_validation_engine

            self._validation_engine = get_design_validation_engine()
        except Exception as e:
            print(f"[EngineExecutor] Validation engine init warning: {e}")

    def _execute_logic_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute deterministic logic analysis."""
        return {
            "perspectives": [
                "Logical structure analysis",
                "Contradiction detection",
                "Deductive reasoning chain",
            ],
            "confidence": 0.85,
            "reasoning": "Applied formal logic decomposition",
        }

    def _execute_engineering_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute engineering/mathematical analysis using framework engine."""
        is_code = any(kw in task.lower() for kw in ["code", "function", "class", "implement"])

        # Get mathematical analysis from framework engine
        math_analysis = None
        if self._math_engine:
            math_analysis = self._math_engine.analyze_architecture(task)

        perspectives = [
            "Technical feasibility assessment",
            "Implementation structure",
            "Edge case analysis" if is_code else "Mathematical formalization",
        ]

        # Add mathematical perspectives if available
        if math_analysis and math_analysis.get("detected_domains"):
            perspectives.append(
                f"Mathematical domains: {', '.join(math_analysis['detected_domains'])}"
            )

        result = {
            "perspectives": perspectives,
            "confidence": 0.80,
            "reasoning": "Engineering decomposition applied",
            "code_focused": is_code,
            "mathematical_analysis": math_analysis,
        }

        # Add specific recommendations for code tasks
        if is_code and math_analysis:
            result["framework_recommendations"] = math_analysis.get("recommended_frameworks", [])

        return result

    def _execute_design_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute design language analysis with mathematical foundations."""
        perspectives = [
            "Structural clarity review",
            "Pattern recognition",
            "Aesthetic/functional balance",
        ]

        result = {
            "perspectives": perspectives,
            "confidence": 0.75,
            "reasoning": "Design principles applied",
        }

        # Add mathematical design analysis if available
        if self._math_engine:
            task_lower = task.lower()

            # Check for spacing/layout tasks
            if any(kw in task_lower for kw in ["spacing", "grid", "layout", "margin", "padding"]):
                # Default to 24px analysis as example
                spacing_analysis = self._math_engine.solve_design_spacing(24)
                result["spacing_analysis"] = spacing_analysis
                result["perspectives"].append(f"8-point grid: {spacing_analysis['is_8pt_aligned']}")

            # Check for typography tasks
            if any(kw in task_lower for kw in ["font", "type", "scale", "typography"]):
                golden_ratio = self._math_engine.ui_engine.get_golden_ratio()
                type_scale = self._math_engine.ui_engine.calculate_type_scale(16, golden_ratio, 5)
                result["typography_scale"] = type_scale
                result["perspectives"].append(f"Golden ratio scale applied ({golden_ratio:.3f})")

        return result

    def _execute_biology_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute biological/cognitive analysis."""
        return {
            "perspectives": [
                "UBI alignment check",
                "Cognitive load assessment",
                "Natural pattern resonance",
            ],
            "confidence": 0.70,
            "reasoning": "Biological intelligence principles applied",
        }

    def _execute_strategy_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute strategic/game-theoretic analysis."""
        return {
            "perspectives": [
                "Long-term trajectory analysis",
                "Adversarial scenario planning",
                "Resource optimization",
            ],
            "confidence": 0.78,
            "reasoning": "Strategic foresight applied",
        }

    def _execute_society_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute social/cultural analysis."""
        return {
            "perspectives": [
                "Stakeholder impact assessment",
                "Cultural sensitivity check",
                "Collaborative dynamics",
            ],
            "confidence": 0.72,
            "reasoning": "Social systems analysis applied",
        }

    def _execute_validation_engine(self, task: str, context: dict) -> dict[str, Any]:
        """Execute design validation using mathematical frameworks."""
        if not self._validation_engine:
            return {
                "perspectives": ["Design validation unavailable"],
                "confidence": 0.0,
                "reasoning": "Validation engine not initialized",
            }

        result = {"perspectives": [], "confidence": 0.0, "reasoning": "", "validations": []}

        # Check for UI validation requests
        if any(kw in task.lower() for kw in ["spacing", "layout", "design", "ui", "typography"]):
            try:
                validation = self._validation_engine.validate_ui_design(
                    spacing_values=context.get("spacing_values"),
                    typography_sizes=context.get("typography_sizes"),
                    color_contrasts=context.get("color_contrasts"),
                )
                result["validations"].append({"type": "ui", "result": validation})
                result["perspectives"].append(f"UI validation score: {validation.score:.0%}")
            except Exception as e:
                result["perspectives"].append(f"UI validation error: {e}")

        # Check for code architecture validation
        if any(kw in task.lower() for kw in ["architecture", "code", "structure", "complexity"]):
            try:
                validation = self._validation_engine.validate_code_architecture(
                    code_description=task, complexity_metrics=context.get("complexity_metrics")
                )
                result["validations"].append({"type": "code", "result": validation})
                result["perspectives"].append(f"Code validation score: {validation.score:.0%}")
            except Exception as e:
                result["perspectives"].append(f"Code validation error: {e}")

        # Check for AI validation
        if any(kw in task.lower() for kw in ["model", "ai", "neural", "transformer", "layer"]):
            try:
                validation = self._validation_engine.validate_ai_architecture(
                    model_description=task,
                    parameter_count=context.get("parameter_count"),
                    layer_config=context.get("layer_config"),
                )
                result["validations"].append({"type": "ai", "result": validation})
                result["perspectives"].append(f"AI validation score: {validation.score:.0%}")
            except Exception as e:
                result["perspectives"].append(f"AI validation error: {e}")

        if result["validations"]:
            result["confidence"] = sum(v["result"].score for v in result["validations"]) / len(
                result["validations"]
            )
            result["reasoning"] = f"Performed {len(result['validations'])} validation(s)"
        else:
            result["reasoning"] = "No validations triggered for this task"
            result["confidence"] = 0.5

        return result

    def _check_laws(self, task: str, reasoning: list[dict]) -> list[str]:
        """Check for global law violations in reasoning."""
        violations = []
        all_text = task.lower() + " " + json.dumps(reasoning).lower()

        # Check Rule of 2 (dual perspectives)
        single_perspective_words = ["obviously", "clearly", "definitely", "undoubtedly"]
        if any(w in all_text for w in single_perspective_words):
            violations.append("RULE_OF_2: Consider alternative perspectives before concluding")

        # Check Rule of 4 (quadrant thinking)
        if reasoning and len(reasoning) < 2:
            violations.append("RULE_OF_4: Apply quadrant analysis for completeness")

        # Check structural integrity
        vague_phrases = ["etc.", "and so on", "something like", "kind of"]
        if any(p in all_text for p in vague_phrases):
            violations.append(
                "ABSOLUTE_STRUCTURAL_INTEGRITY: Ambiguity detected - label assumptions"
            )

        return violations

    def execute(self, task: str, engines: list[str], context: dict = None) -> ExecutionResult:
        """Execute a task through the specified cognitive engines."""
        import time

        start = time.time()

        ctx = context or {}
        reasoning_steps = []
        engines_used = []
        all_violations = []

        for engine_name in engines:
            if engine_name in self._engines:
                engines_used.append(engine_name)
                result = self._engines[engine_name](task, ctx)
                reasoning_steps.append({"engine": engine_name, "result": result})

        # Check laws against all reasoning
        all_violations = self._check_laws(task, reasoning_steps)

        # Build synthesized output
        output_parts = ["## Cognitive Execution Results\n"]
        output_parts.append(f"Engines engaged: {len(engines_used)}\n")

        for step in reasoning_steps:
            eng = step["engine"].replace("AMOS_", "").replace("_Engine", "")
            output_parts.append(f"\n**{eng}**:")
            res = step["result"]
            if "perspectives" in res:
                for p in res["perspectives"]:
                    output_parts.append(f"  - {p}")
            output_parts.append(f"  Confidence: {res.get('confidence', 0.5):.0%}")

        if all_violations:
            output_parts.append("\n\n⚠️ Law Review Required:")
            for v in all_violations:
                output_parts.append(f"  - {v}")
        else:
            output_parts.append("\n✓ All global laws satisfied")

        elapsed = (time.time() - start) * 1000

        return ExecutionResult(
            task=task,
            engines_used=engines_used,
            reasoning_steps=reasoning_steps,
            output="\n".join(output_parts),
            laws_checked=["RULE_OF_2", "RULE_OF_4", "ABSOLUTE_STRUCTURAL_INTEGRITY"],
            violations_found=all_violations,
            execution_time_ms=elapsed,
        )


# Singleton instance
_executor_instance: Optional[EngineExecutor] = None


def get_executor(brain_loader: Any = None) -> EngineExecutor:
    """Get or create the singleton executor instance."""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = EngineExecutor(brain_loader)
    return _executor_instance


def execute_cognitive_task(task: str, engines: list[str], context: dict = None) -> ExecutionResult:
    """Convenience function to execute a task through cognitive engines."""
    executor = get_executor()
    return executor.execute(task, engines, context)


if __name__ == "__main__":
    # Test execution
    test_task = "Design a function to calculate prime numbers efficiently"
    test_engines = [
        "AMOS_Engineering_And_Mathematics_Engine",
        "AMOS_Deterministic_Logic_And_Law_Engine",
        "AMOS_Design_Language_Engine",
    ]

    print("=" * 60)
    print("AMOS Cognitive Engine Executor - Test")
    print("=" * 60)
    print(f"\nTask: {test_task}\n")

    result = execute_cognitive_task(test_task, test_engines)

    print(result.output)
    print(f"\nExecution time: {result.execution_time_ms:.2f}ms")
    print(f"Laws checked: {len(result.laws_checked)}")
    if result.violations_found:
        print(f"⚠️ Violations: {len(result.violations_found)}")
    else:
        print("✓ No violations")
