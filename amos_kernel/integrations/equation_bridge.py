"""Equation Bridge Integration - Connects kernel to AMOS equation system"""

from typing import Any, Optional

import numpy as np

from ..core.deterministic import DeterministicCore
from ..core.interaction import InteractionOperator
from ..core.law import UniversalLawKernel
from ..core.state import UniversalStateModel
from ..workflows import get_workflow_engine


class KernelEquationBridge:
    """Bridges kernel-first architecture with equation execution system."""

    def __init__(self):
        self.law = UniversalLawKernel()
        self.state = UniversalStateModel()
        self.interaction = InteractionOperator()
        self.deterministic = DeterministicCore()
        self.workflow = get_workflow_engine()

    def execute_equation(
        self,
        equation_name: str,
        domain: str,
        parameters: dict[str, Any],
        validate: bool = True,
    ) -> dict[str, Any]:
        """Execute equation through kernel workflow with validation."""
        # Build state from equation parameters
        raw_state = self._params_to_state(equation_name, domain, parameters)

        # Run through kernel workflow
        result = self.workflow.execute(
            workflow_id=f"equation-{equation_name}",
            raw_input=raw_state,
            validate_laws=validate,
        )

        # Extract mathematical result
        if result.final_state:
            computation_result = self._compute_result(equation_name, parameters)
        else:
            computation_result = None

        return {
            "equation": equation_name,
            "domain": domain,
            "kernel_result": {
                "success": result.success,
                "steps_completed": len([s for s in result.steps if s.status == "completed"]),
                "law_passed": result.law_validation.passed if result.law_validation else False,
                "collapse_risk": result.law_validation.collapse_risk
                if result.law_validation
                else 1.0,
                "drift_detected": result.drift_detected,
                "repairs_proposed": result.repairs_proposed,
            },
            "computation": computation_result,
            "healthy": result.success and not result.drift_detected,
        }

    def _params_to_state(self, equation: str, domain: str, params: dict) -> dict:
        """Convert equation parameters to tensor state."""
        numeric = {k: v for k, v in params.items() if isinstance(v, (int, float))}

        return {
            "biological": {"complexity": len(str(params)) / 100},
            "cognitive": {"equation_depth": self._estimate_depth(equation)},
            "system": {
                "equation": equation,
                "domain": domain,
                **numeric,
            },
            "environment": {"parameters": len(params)},
        }

    def _estimate_depth(self, equation: str) -> float:
        """Estimate equation computational depth."""
        indicators = ["sum", "prod", "integral", "diff", "matrix", "conv"]
        depth = sum(1 for ind in indicators if ind in equation.lower())
        return min(depth / 3, 1.0)

    def _compute_result(self, equation: str, params: dict) -> Optional[dict]:
        """Compute mathematical result for common patterns."""
        try:
            if "softmax" in equation.lower():
                x = params.get("x", [1.0, 2.0, 3.0])
                exp_x = np.exp(np.array(x) - np.max(x))
                result = exp_x / exp_x.sum()
                return {"result": result.tolist(), "shape": len(x)}

            elif "normalize" in equation.lower():
                x = np.array(params.get("x", [1.0, 2.0, 3.0]))
                result = (x - x.mean()) / (x.std() + 1e-8)
                return {"result": result.tolist(), "mean": float(x.mean()), "std": float(x.std())}

            elif "relu" in equation.lower():
                x = np.array(params.get("x", [-1.0, 0.0, 1.0]))
                result = np.maximum(0, x)
                return {"result": result.tolist(), "activated": int((result > 0).sum())}

            else:
                return {"result": "computation not implemented", "params": len(params)}

        except Exception as e:
            return {"error": str(e)}

    def validate_domain_equations(self, domain: str, equations: list[str]) -> dict:
        """Validate all equations for a domain through kernel."""
        results = []
        for eq in equations:
            result = self.execute_equation(eq, domain, {}, validate=True)
            results.append(
                {
                    "equation": eq,
                    "healthy": result["healthy"],
                    "collapse_risk": result["kernel_result"]["collapse_risk"],
                }
            )

        all_healthy = all(r["healthy"] for r in results)
        avg_risk = sum(r["collapse_risk"] for r in results) / len(results) if results else 1.0

        return {
            "domain": domain,
            "total": len(equations),
            "healthy": sum(1 for r in results if r["healthy"]),
            "unhealthy": sum(1 for r in results if not r["healthy"]),
            "average_collapse_risk": avg_risk,
            "domain_healthy": all_healthy and avg_risk < 0.5,
            "equations": results,
        }


def get_equation_bridge() -> KernelEquationBridge:
    """Factory for equation bridge."""
    return KernelEquationBridge()


# Mathematical utilities for equation execution
def softmax(x: list[float]) -> list[float]:
    """Softmax activation through kernel."""
    bridge = get_equation_bridge()
    result = bridge.execute_equation("softmax", "ml", {"x": x})
    return result.get("computation", {}).get("result", x)


def normalize(x: list[float]) -> list[float]:
    """Z-score normalization through kernel."""
    bridge = get_equation_bridge()
    result = bridge.execute_equation("normalize", "statistics", {"x": x})
    return result.get("computation", {}).get("result", x)
