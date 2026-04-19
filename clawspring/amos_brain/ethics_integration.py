#!/usr/bin/env python3
"""AMOS Ecosystem v2.3 - Ethics & Validation Integration Layer.

Bridges the cognitive ecosystem with AMOS_ORGANISM_OS ethics validation.
Ensures all cognitive decisions pass ethical validation before execution.
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")


@dataclass
class EthicsValidationResult:
    """Result of ethics validation."""

    passed: bool
    violations: List[str]
    warnings: List[str]
    score: float  # 0.0 to 1.0
    framework: str
    timestamp: datetime


class EthicsValidator:
    """Validates cognitive decisions against ethical frameworks."""

    def __init__(self):
        self.frameworks = {
            "utilitarian": self._validate_utilitarian,
            "deontological": self._validate_deontological,
            "virtue_ethics": self._validate_virtue_ethics,
            "principlism": self._validate_principlism,
        }
        self.violations_log: List[dict] = []

    def validate_action(
        self, action: str, context: Dict[str, Any], framework: str = "principlism"
    ) -> EthicsValidationResult:
        """Validate an action against an ethical framework."""
        if framework not in self.frameworks:
            framework = "principlism"

        violations, warnings, score = self.frameworks[framework](action, context)

        result = EthicsValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            score=score,
            framework=framework,
            timestamp=datetime.now(),
        )

        if not result.passed:
            self._log_violation(action, context, result)

        return result

    def _validate_principlism(self, action: str, context: dict) -> Tuple[list, list, float]:
        """Validate using biomedical ethics principles (Beauchamp & Childress)."""
        violations = []
        warnings = []
        score = 1.0

        # Autonomy - respect for persons
        if any(kw in action.lower() for kw in ["override", "force", "compel"]):
            if not context.get("consent", False):
                violations.append("Autonomy: Action may violate user autonomy")
                score -= 0.3

        # Beneficence - do good
        if context.get("harm_potential", 0) > 0.5:
            warnings.append("Beneficence: High harm potential detected")
            score -= 0.1

        # Non-maleficence - do no harm
        if context.get("harm_probability", 0) > 0.7:
            violations.append("Non-maleficence: High probability of harm")
            score -= 0.4

        # Justice - fairness
        if context.get("discriminatory", False):
            violations.append("Justice: Potential discriminatory impact")
            score -= 0.3

        return violations, warnings, max(0.0, score)

    def _validate_utilitarian(self, action: str, context: dict) -> Tuple[list, list, float]:
        """Validate using utilitarian calculus."""
        violations = []
        warnings = []

        benefit = context.get("benefit_score", 0.5)
        harm = context.get("harm_score", 0.5)
        affected = context.get("affected_count", 1)

        # Net utility calculation
        net_utility = (benefit - harm) * affected
        score = 0.5 + (net_utility / 10)  # Normalize roughly

        if net_utility < 0:
            violations.append(f"Negative utility: net harm to {affected} entities")
            score = 0.0
        elif net_utility < 0.1 * affected:
            warnings.append("Low utility gain for effort required")

        return violations, warnings, max(0.0, min(1.0, score))

    def _validate_deontological(self, action: str, context: dict) -> Tuple[list, list, float]:
        """Validate using duty-based ethics (Kantian)."""
        violations = []
        warnings = []
        score = 1.0

        # Check for treating as means only
        if context.get("instrumentalize", False):
            violations.append("Categorical Imperative: Treating persons as means only")
            score = 0.0

        # Check for universalizability
        if context.get("cannot_universalize", False):
            violations.append("Cannot universalize this maxim")
            score -= 0.5

        # Duty violations
        duty_violations = context.get("duty_violations", [])
        for duty in duty_violations:
            violations.append(f"Duty violation: {duty}")
            score -= 0.2

        return violations, warnings, max(0.0, score)

    def _validate_virtue_ethics(self, action: str, context: dict) -> Tuple[list, list, float]:
        """Validate using virtue ethics (Aristotelian)."""
        violations = []
        warnings = []

        virtues = {
            "wisdom": context.get("wisdom", 0.5),
            "courage": context.get("courage", 0.5),
            "temperance": context.get("temperance", 0.5),
            "justice": context.get("justice", 0.5),
        }

        avg_virtue = sum(virtues.values()) / len(virtues)
        score = avg_virtue

        for virtue, level in virtues.items():
            if level < 0.3:
                warnings.append(f"Lacking {virtue}: {level:.2f}")

        if avg_virtue < 0.5:
            violations.append("Insufficient virtuous character in decision")

        return violations, warnings, score

    def _log_violation(self, action: str, context: dict, result: EthicsValidationResult) -> None:
        """Log ethics violation for audit."""
        self.violations_log.append(
            {
                "timestamp": result.timestamp.isoformat(),
                "action": action,
                "framework": result.framework,
                "violations": result.violations,
                "score": result.score,
                "context_hash": hash(str(context)) & 0xFFFFFF,
            }
        )

    def get_violations_report(self) -> Dict[str, Any]:
        """Get report of all ethics violations."""
        return {
            "total_violations": len(self.violations_log),
            "recent_violations": self.violations_log[-10:],
            "frameworks_used": list(self.frameworks.keys()),
        }


class CognitiveEthicsBridge:
    """Bridge between cognitive routing and ethics validation."""

    def __init__(self):
        self.ethics = EthicsValidator()
        self.enabled = True

    def validate_cognitive_routing(self, task: str, routing_result: Any) -> EthicsValidationResult:
        """Validate a cognitive routing decision."""
        if not self.enabled:
            return EthicsValidationResult(
                passed=True,
                violations=[],
                warnings=[],
                score=1.0,
                framework="disabled",
                timestamp=datetime.now(),
            )

        context = {
            "task": task,
            "suggested_engines": getattr(routing_result, "suggested_engines", []),
            "risk_level": getattr(routing_result, "risk_level", "unknown"),
            "confidence": getattr(routing_result, "confidence", 0.5),
            "harm_potential": 0.3 if getattr(routing_result, "risk_level", "") == "HIGH" else 0.1,
            "consent": True,  # Assume user consent for cognitive routing
        }

        return self.ethics.validate_action(
            f"Cognitive routing for: {task}", context, framework="principlism"
        )

    def validate_orchestration(
        self, task_id: str, task_description: str, priority: str
    ) -> EthicsValidationResult:
        """Validate a master orchestration task."""
        context = {
            "task_id": task_id,
            "priority": priority,
            "harm_potential": 0.5 if priority == "HIGH" else 0.2,
            "affected_count": 1,
            "consent": True,
        }

        return self.ethics.validate_action(
            f"Orchestration: {task_description}", context, framework="utilitarian"
        )

    def get_compliance_status(self) -> Dict[str, Any]:
        """Get ethics compliance status."""
        return {
            "enabled": self.enabled,
            "frameworks_available": list(self.ethics.frameworks.keys()),
            "total_violations_logged": len(self.ethics.violations_log),
            "status": "compliant" if len(self.ethics.violations_log) < 10 else "review_needed",
        }


def main():
    """Demo ethics integration."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.3 - ETHICS INTEGRATION DEMO")
    print("=" * 70)

    # Create bridge
    bridge = CognitiveEthicsBridge()

    # Test 1: Safe task
    print("\nTest 1: Low-risk task")
    result = bridge.ethics.validate_action(
        "Generate documentation",
        {"harm_potential": 0.0, "benefit_score": 0.8, "consent": True},
        "principlism",
    )
    print(f"  Passed: {result.passed}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Violations: {result.violations}")

    # Test 2: High-risk task
    print("\nTest 2: High-risk task")
    result = bridge.ethics.validate_action(
        "Override user preferences",
        {"harm_potential": 0.8, "consent": False, "discriminatory": True},
        "principlism",
    )
    print(f"  Passed: {result.passed}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Violations: {result.violations}")

    # Test 3: Utilitarian analysis
    print("\nTest 3: Utilitarian analysis")
    result = bridge.ethics.validate_action(
        "Deploy resource optimization",
        {"benefit_score": 0.9, "harm_score": 0.1, "affected_count": 100},
        "utilitarian",
    )
    print(f"  Passed: {result.passed}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Net utility positive: {result.score > 0.5}")

    # Compliance status
    print("\nCompliance Status:")
    status = bridge.get_compliance_status()
    for k, v in status.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("Ethics integration layer operational!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
