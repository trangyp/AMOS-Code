"""AMOS Unified Cognitive Gateway - Master Integration Layer"""


import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from amos_api_gateway import AMOSAPIGateway
    GATEWAY_AVAILABLE = True
except ImportError:
    GATEWAY_AVAILABLE = False

try:
    from amos_unified_orchestrator import AMOSUnifiedOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from .governance_integration import GovernanceIntegration
    GOVERNANCE_AVAILABLE = True
except ImportError:
    GOVERNANCE_AVAILABLE = False

try:
    from .math_framework_integration import MathFrameworkIntegration
    MATH_AVAILABLE = True
except ImportError:
    MATH_AVAILABLE = False

try:
    from .equation_validation_engine import EquationValidationEngine
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


class RequestType(Enum):
    COGNITIVE = "cognitive"
    GOVERNANCE = "governance"
    MATHEMATICAL = "mathematical"
    ORCHESTRATION = "orchestration"


@dataclass
class GatewayResponse:
    status: str
    data: dict = field(default_factory=dict)
    processing_time_ms: float = 0.0


class UnifiedCognitiveGateway:
    """Master gateway integrating all AMOS cognitive components."""

    def __init__(self, port: int = 9999):
        self.port = port
        self._api_gateway: AMOSAPIGateway | None = None
        self._orchestrator: AMOSUnifiedOrchestrator | None = None
        self._governance: GovernanceIntegration | None = None
        self._math_framework: MathFrameworkIntegration | None = None
        self._validation: EquationValidationEngine | None = None
        self._initialized = False
        self._request_count = 0

    def initialize(self) -> dict[str, Any]:
        """Initialize all gateway components."""
        print("\n" + "=" * 70)
        print("AMOS UNIFIED COGNITIVE GATEWAY - INITIALIZATION")
        print("=" * 70)

        results = {}

        if GATEWAY_AVAILABLE:
            self._api_gateway = AMOSAPIGateway(port=self.port)
            results["api_gateway"] = True
            print("[1/4] ✓ API Gateway")

        if ORCHESTRATOR_AVAILABLE:
            self._orchestrator = AMOSUnifiedOrchestrator()
            orch_result = self._orchestrator.initialize()
            results["orchestrator"] = orch_result.get("initialized", False)
            print(f"[2/4] ✓ Orchestrator: {orch_result.get('subsystems_online', 0)}/14 subsystems")

        if GOVERNANCE_AVAILABLE:
            self._governance = GovernanceIntegration()
            self._governance.initialize()
            results["governance"] = True
            print("[3/4] ✓ Governance")

        if MATH_AVAILABLE:
            self._math_framework = MathFrameworkIntegration()
            results["math_framework"] = True
            print("[4/4] ✓ Math Framework")

        if VALIDATION_AVAILABLE:
            self._validation = EquationValidationEngine()
            results["validation"] = True
            print("[5/5] ✓ Equation Validation")

        self._initialized = any(results.values())
        print("=" * 70)
        return results

    def process_request(self, request_type: str, data: dict) -> GatewayResponse:
        """Process a request through the unified gateway."""
        start_time = time.time()
        self._request_count += 1

        try:
            if request_type == "math" and self._math_framework:
                equation = data.get("equation")
                inputs = data.get("inputs", {})
                result = self._math_framework.execute(equation, inputs)
                return GatewayResponse("success", result, (time.time() - start_time) * 1000)

            elif request_type == "orchestrate" and self._orchestrator:
                task = data.get("task", "")
                result = self._orchestrator.orchestrate_task(task, data)
                return GatewayResponse("success", result, (time.time() - start_time) * 1000)

            elif request_type == "governance" and self._governance:
                health = self._governance.get_health()
                return GatewayResponse("success", health, (time.time() - start_time) * 1000)

            elif request_type == "validate" and self._validation:
                equation = data.get("equation")
                if equation:
                    result = self._validation.validate_equation(equation)
                    result_dict = {
                        "equation": result.equation_name,
                        "domain": result.domain,
                        "status": result.status.name,
                        "time_ms": result.execution_time_ms,
                        "invariants_valid": result.invariants_valid,
                    }
                    if result.error_message:
                        result_dict["error"] = result.error_message
                    return GatewayResponse("success", result_dict, (time.time() - start_time) * 1000)
                else:
                    report = self._validation.validate_all()
                    return GatewayResponse("success", {"report": "Validation complete"}, (time.time() - start_time) * 1000)

            else:
                return GatewayResponse("error", {"message": "Unknown request type or component unavailable"}, 0)

        except Exception as e:
            return GatewayResponse("error", {"error": str(e)}, (time.time() - start_time) * 1000)

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive gateway status."""
        return {
            "initialized": self._initialized,
            "request_count": self._request_count,
            "components": {
                "api_gateway": self._api_gateway is not None,
                "orchestrator": self._orchestrator is not None,
                "governance": self._governance is not None,
                "math_framework": self._math_framework is not None,
                "validation": self._validation is not None,
            }
        }


# Global instance
_gateway: UnifiedCognitiveGateway | None = None


def get_unified_gateway() -> UnifiedCognitiveGateway:
    """Get global UnifiedCognitiveGateway instance."""
from __future__ import annotations

    global _gateway
    if _gateway is None:
        _gateway = UnifiedCognitiveGateway()
        _gateway.initialize()
    return _gateway


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Unified Cognitive Gateway - Test")
    print("=" * 70)

    gateway = UnifiedCognitiveGateway()
    status = gateway.initialize()

    print("\n[Test 1] Math Execution")
    print("-" * 50)
    if status.get("math_framework"):
        result = gateway.process_request("math", {"equation": "sigmoid", "inputs": {"x": 2.0}})
        print(f"Sigmoid(2.0): {result.data.get('result')}")

    print("\n[Test 2] Gateway Status")
    print("-" * 50)
    print(json.dumps(gateway.get_status(), indent=2))

    print("\n" + "=" * 70)
    print("Unified Cognitive Gateway operational!")
    print("=" * 70)
