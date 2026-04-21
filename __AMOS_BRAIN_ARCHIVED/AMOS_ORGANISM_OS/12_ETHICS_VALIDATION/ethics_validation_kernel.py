#!/usr/bin/env python3
"""AMOS Ethics Validation Kernel - 12_ETHICS_VALIDATION Subsystem

Responsible for:
- Ethical constraint enforcement
- Moral reasoning and evaluation
- Value alignment checking
- Harm prevention and safety validation
- Ethical approval for actions
- Bias detection and mitigation
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum, auto
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.ethics")


class EthicalPrinciple(Enum):
    """Core ethical principles for evaluation."""

    NON_MALEFICENCE = auto()  # Do no harm
    BENEFICENCE = auto()  # Do good
    AUTONOMY = auto()  # Respect self-determination
    JUSTICE = auto()  # Fairness and equality
    TRANSPARENCY = auto()  # Openness and honesty
    ACCOUNTABILITY = auto()  # Responsibility for actions


class ValidationResult(Enum):
    """Result of ethical validation."""

    APPROVED = auto()
    CONDITIONAL = auto()
    REJECTED = auto()
    UNCLEAR = auto()


class HarmCategory(Enum):
    """Categories of potential harm."""

    PHYSICAL = auto()
    PSYCHOLOGICAL = auto()
    FINANCIAL = auto()
    PRIVACY = auto()
    REPUTATIONAL = auto()
    ENVIRONMENTAL = auto()
    SOCIAL = auto()


@dataclass
class EthicalConstraint:
    """An ethical constraint rule."""

    constraint_id: str
    principle: EthicalPrinciple
    description: str
    condition: str
    severity: int = 5  # 1-10
    exceptions: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


@dataclass
class HarmAssessment:
    """Assessment of potential harm."""

    category: HarmCategory
    severity: float  # 0.0 - 1.0
    probability: float  # 0.0 - 1.0
    affected_parties: list[str] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class EthicalEvaluation:
    """Complete ethical evaluation of an action."""

    evaluation_id: str
    action_type: str
    result: ValidationResult
    overall_score: float  # -1.0 to 1.0
    principle_scores: dict[EthicalPrinciple, float] = field(default_factory=dict)
    harm_assessments: list[HarmAssessment] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


class EthicsValidationKernel:
    """The Ethics Validation Kernel ensures all actions align with ethical
    principles, preventing harm and ensuring value alignment.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.ethics_path = organism_root / "12_ETHICS_VALIDATION"
        self.constraints_path = self.ethics_path / "constraints"
        self.evaluations_path = self.ethics_path / "evaluations"
        self.values_path = self.ethics_path / "values"

        # Ensure directories
        self.constraints_path.mkdir(parents=True, exist_ok=True)
        self.evaluations_path.mkdir(parents=True, exist_ok=True)
        self.values_path.mkdir(parents=True, exist_ok=True)

        # Core values
        self.core_values = [
            "human_welfare",
            "autonomy",
            "fairness",
            "transparency",
            "accountability",
            "safety",
        ]

        # Ethical constraints
        self.constraints: dict[str, EthicalConstraint] = {}

        # Evaluation history
        self.evaluations: list[EthicalEvaluation] = []

        # Harm prevention rules
        self.harm_rules: dict[HarmCategory, list[dict[str, Any]]] = defaultdict(list)

        # Statistics
        self.stats = {
            "evaluations_performed": 0,
            "actions_approved": 0,
            "actions_rejected": 0,
            "actions_conditional": 0,
            "harm_prevented": 0,
        }

        # Initialize default constraints
        self._init_default_constraints()

        logger.info(f"EthicsValidationKernel initialized at {self.ethics_path}")

    def _init_default_constraints(self):
        """Initialize default ethical constraints."""
        defaults = [
            EthicalConstraint(
                constraint_id="no_physical_harm",
                principle=EthicalPrinciple.NON_MALEFICENCE,
                description="Never cause physical harm to humans",
                condition="action.type == 'physical' AND action.target == 'human'",
                severity=10,
            ),
            EthicalConstraint(
                constraint_id="respect_privacy",
                principle=EthicalPrinciple.AUTONOMY,
                description="Respect individual privacy and data rights",
                condition="action.involves == 'personal_data'",
                severity=8,
            ),
            EthicalConstraint(
                constraint_id="no_financial_exploitation",
                principle=EthicalPrinciple.JUSTICE,
                description="Do not exploit users financially",
                condition="action.type == 'financial' AND action.benefit == 'self'",
                severity=9,
            ),
            EthicalConstraint(
                constraint_id="be_truthful",
                principle=EthicalPrinciple.TRANSPARENCY,
                description="Be honest and transparent in communications",
                condition="action.type == 'communication'",
                severity=7,
            ),
            EthicalConstraint(
                constraint_id="promote_welfare",
                principle=EthicalPrinciple.BENEFICENCE,
                description="Act to promote human welfare when possible",
                condition="action.can_help == True",
                severity=6,
            ),
            EthicalConstraint(
                constraint_id="accept_accountability",
                principle=EthicalPrinciple.ACCOUNTABILITY,
                description="Accept responsibility for actions and their consequences",
                condition="action.has_consequences == True",
                severity=7,
            ),
        ]

        for constraint in defaults:
            self.constraints[constraint.constraint_id] = constraint

        logger.info(f"Initialized {len(defaults)} default ethical constraints")

    def add_constraint(
        self,
        constraint_id: str,
        principle: EthicalPrinciple,
        description: str,
        condition: str,
        severity: int = 5,
        exceptions: list[str] = None,
    ) -> EthicalConstraint:
        """Add a new ethical constraint."""
        constraint = EthicalConstraint(
            constraint_id=constraint_id,
            principle=principle,
            description=description,
            condition=condition,
            severity=severity,
            exceptions=exceptions or [],
        )

        self.constraints[constraint_id] = constraint
        logger.info(f"Added ethical constraint: {constraint_id}")
        return constraint

    def evaluate_action(
        self,
        action_type: str,
        action_details: dict[str, Any],
        context: dict[str, Any] = None,
    ) -> EthicalEvaluation:
        """Perform comprehensive ethical evaluation of an action."""
        context = context or {}

        # Initialize evaluation
        eval_id = f"eval_{len(self.evaluations)}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        principle_scores = dict.fromkeys(EthicalPrinciple, 0.0)
        harm_assessments = []
        concerns = []
        recommendations = []

        # Check each constraint
        for constraint in self.constraints.values():
            match_score = self._check_constraint(constraint, action_details, context)

            if match_score > 0.5:  # Constraint applies
                principle_scores[constraint.principle] += match_score * (constraint.severity / 10)

                if match_score * constraint.severity > 5:
                    concerns.append(f"{constraint.principle.name}: {constraint.description}")
                    recommendations.append(f"Review {constraint.constraint_id} compliance")

        # Assess potential harm
        harm_assessments = self._assess_harm(action_type, action_details, context)

        # Calculate overall score
        if harm_assessments:
            harm_score = sum(h.severity * h.probability for h in harm_assessments) / len(
                harm_assessments
            )
            principle_scores[EthicalPrinciple.NON_MALEFICENCE] -= harm_score

        # Determine result
        overall_score = sum(principle_scores.values()) / len(principle_scores)

        if overall_score < -0.3 or any(h.severity > 0.7 for h in harm_assessments):
            result = ValidationResult.REJECTED
            self.stats["actions_rejected"] += 1
            self.stats["harm_prevented"] += len(harm_assessments)
        elif overall_score < 0.3 or any(h.severity > 0.4 for h in harm_assessments):
            result = ValidationResult.CONDITIONAL
            self.stats["actions_conditional"] += 1
            recommendations.append("Implement suggested mitigations before proceeding")
        else:
            result = ValidationResult.APPROVED
            self.stats["actions_approved"] += 1

        # Create evaluation record
        evaluation = EthicalEvaluation(
            evaluation_id=eval_id,
            action_type=action_type,
            result=result,
            overall_score=overall_score,
            principle_scores=principle_scores,
            harm_assessments=harm_assessments,
            concerns=concerns,
            recommendations=recommendations,
        )

        self.evaluations.append(evaluation)
        self.stats["evaluations_performed"] += 1

        logger.info(f"Ethical evaluation {eval_id}: {result.name} (score: {overall_score:+.2f})")
        return evaluation

    def _check_constraint(
        self, constraint: EthicalConstraint, action_details: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Check if a constraint applies to an action. Returns match score 0.0-1.0."""
        score = 0.0

        # Simple keyword matching (in production, use more sophisticated logic)
        condition_lower = constraint.condition.lower()

        # Check action type match
        if f"action.type == '{action_details.get('type', '')}'" in condition_lower:
            score += 0.5

        # Check action properties
        for key, value in action_details.items():
            if f"action.{key}" in condition_lower and str(value).lower() in condition_lower:
                score += 0.25

        # Check context
        for key, value in context.items():
            if f"context.{key}" in condition_lower and str(value).lower() in condition_lower:
                score += 0.25

        return min(1.0, score)

    def _assess_harm(
        self, action_type: str, action_details: dict[str, Any], context: dict[str, Any]
    ) -> list[HarmAssessment]:
        """Assess potential harm from an action."""
        assessments = []

        # Check for different harm categories
        harm_checks = [
            (HarmCategory.PHYSICAL, ["physical", "injury", "dangerous", "unsafe"]),
            (HarmCategory.PSYCHOLOGICAL, ["psychological", "emotional", "distress", "mental"]),
            (HarmCategory.FINANCIAL, ["financial", "money", "payment", "cost", "loss"]),
            (HarmCategory.PRIVACY, ["privacy", "personal_data", "confidential", "private"]),
            (HarmCategory.REPUTATIONAL, ["reputation", "public", "embarrassing", "defamation"]),
            (HarmCategory.ENVIRONMENTAL, ["environment", "pollution", "waste", "ecosystem"]),
            (HarmCategory.SOCIAL, ["social", "community", "discrimination", "bias"]),
        ]

        # Combine action details and context for analysis
        combined_text = json.dumps({**action_details, **context}).lower()

        for category, keywords in harm_checks:
            severity = 0.0
            probability = 0.0

            for keyword in keywords:
                if keyword in combined_text:
                    severity += 0.2
                    probability += 0.15

            if severity > 0:
                assessment = HarmAssessment(
                    category=category,
                    severity=min(1.0, severity),
                    probability=min(1.0, probability),
                    description=f"Potential {category.name.lower()} harm detected",
                )
                assessments.append(assessment)

        return assessments

    def check_value_alignment(self, proposed_values: list[str]) -> dict[str, Any]:
        """Check alignment of proposed values with core values."""
        aligned = []
        misaligned = []

        for value in proposed_values:
            value_lower = value.lower()
            if any(core in value_lower for core in self.core_values):
                aligned.append(value)
            else:
                misaligned.append(value)

        alignment_score = len(aligned) / len(proposed_values) if proposed_values else 0.0

        return {
            "alignment_score": alignment_score,
            "aligned_values": aligned,
            "misaligned_values": misaligned,
            "core_values": self.core_values,
        }

    def detect_bias(self, data: dict[str, Any]) -> dict[str, Any]:
        """Detect potential biases in data or decisions."""
        bias_indicators = []

        # Check for demographic indicators
        demographic_keywords = ["gender", "race", "age", "religion", "nationality", "disability"]
        data_text = json.dumps(data).lower()

        for keyword in demographic_keywords:
            if keyword in data_text:
                bias_indicators.append(f"Contains {keyword} - ensure fair treatment")

        # Check for stereotypical language
        stereotype_keywords = ["always", "never", "all", "none", "every"]
        for keyword in stereotype_keywords:
            if f'"{keyword}"' in data_text or f"'{keyword}'" in data_text:
                bias_indicators.append(f"Absolute language '{keyword}' detected - review for bias")

        return {
            "bias_detected": len(bias_indicators) > 0,
            "indicators": bias_indicators,
            "recommendation": "Review for fairness"
            if bias_indicators
            else "No obvious bias detected",
        }

    def validate_with_consent(
        self, action: dict[str, Any], consent_data: dict[str, Any]
    ) -> ValidationResult:
        """Validate an action requires consent."""
        if not consent_data.get("consent_obtained", False):
            logger.warning("Action requires consent but none provided")
            return ValidationResult.REJECTED

        if consent_data.get("consent_revoked", False):
            logger.warning("Consent has been revoked")
            return ValidationResult.REJECTED

        if datetime.now(UTC).isoformat() > consent_data.get("expires_at", "9999-12-31"):
            logger.warning("Consent has expired")
            return ValidationResult.REJECTED

        return ValidationResult.APPROVED

    def get_ethical_report(self) -> dict[str, Any]:
        """Generate comprehensive ethical report."""
        recent_evals = self.evaluations[-100:] if len(self.evaluations) > 100 else self.evaluations

        # Calculate statistics
        results = defaultdict(int)
        for e in recent_evals:
            results[e.result.name] += 1

        # Most common concerns
        all_concerns = [c for e in recent_evals for c in e.concerns]
        concern_counts = defaultdict(int)
        for c in all_concerns:
            concern_counts[c] += 1

        top_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_evaluations": self.stats["evaluations_performed"],
            "recent_results": dict(results),
            "approval_rate": self.stats["actions_approved"]
            / max(1, self.stats["evaluations_performed"]),
            "harm_prevented": self.stats["harm_prevented"],
            "active_constraints": len(self.constraints),
            "core_values": self.core_values,
            "top_concerns": top_concerns,
            "average_score": sum(e.overall_score for e in recent_evals) / max(1, len(recent_evals)),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def get_state(self) -> dict[str, Any]:
        """Get current ethics validation state."""
        return {
            "evaluations_performed": self.stats["evaluations_performed"],
            "actions_approved": self.stats["actions_approved"],
            "actions_rejected": self.stats["actions_rejected"],
            "actions_conditional": self.stats["actions_conditional"],
            "harm_prevented": self.stats["harm_prevented"],
            "active_constraints": len(self.constraints),
            "core_values": self.core_values,
            "recent_evaluation": self.evaluations[-1].result.name if self.evaluations else None,
            "timestamp": datetime.now(UTC).isoformat(),
        }


if __name__ == "__main__":
    # Test the ethics validation kernel
    root = Path(__file__).parent.parent
    ethics = EthicsValidationKernel(root)

    print("Ethics State (initial):")
    print(json.dumps(ethics.get_state(), indent=2))

    print("\n=== Test 1: Evaluate Safe Action ===")

    eval1 = ethics.evaluate_action(
        action_type="read_file",
        action_details={"type": "read", "target": "data.txt", "readonly": True},
        context={"user": "researcher", "purpose": "analysis"},
    )
    print(f"Action: read_file -> {eval1.result.name}")
    print(f"Score: {eval1.overall_score:+.2f}")
    print(f"Concerns: {eval1.concerns}")

    print("\n=== Test 2: Evaluate Risky Action ===")

    eval2 = ethics.evaluate_action(
        action_type="delete_user_data",
        action_details={"type": "delete", "target": "user_data", "irreversible": True},
        context={"user": "admin", "purpose": "cleanup"},
    )
    print(f"Action: delete_user_data -> {eval2.result.name}")
    print(f"Score: {eval2.overall_score:+.2f}")
    print(f"Concerns: {eval2.concerns}")
    print(f"Harm assessments: {[(h.category.name, h.severity) for h in eval2.harm_assessments]}")

    print("\n=== Test 3: Evaluate Financial Action ===")

    eval3 = ethics.evaluate_action(
        action_type="process_payment",
        action_details={"type": "financial", "amount": 1000, "target": "external"},
        context={"user": "customer", "authorized": True},
    )
    print(f"Action: process_payment -> {eval3.result.name}")
    print(f"Score: {eval3.overall_score:+.2f}")

    print("\n=== Test 4: Check Value Alignment ===")

    alignment = ethics.check_value_alignment(
        ["user_safety", "data_protection", "profit_maximization", "efficiency"]
    )
    print(f"Alignment score: {alignment['alignment_score']:.2f}")
    print(f"Aligned: {alignment['aligned_values']}")
    print(f"Misaligned: {alignment['misaligned_values']}")

    print("\n=== Test 5: Detect Bias ===")

    bias_check = ethics.detect_bias(
        {
            "description": "All users of this category always behave this way",
            "demographics": {"gender": "male", "age": "25-35"},
        }
    )
    print(f"Bias detected: {bias_check['bias_detected']}")
    print(f"Indicators: {bias_check['indicators']}")

    print("\n=== Test 6: Add Custom Constraint ===")

    ethics.add_constraint(
        constraint_id="environmental_protection",
        principle=EthicalPrinciple.NON_MALEFICENCE,
        description="Minimize environmental impact",
        condition="action.affects == 'environment'",
        severity=8,
    )
    print(f"Added constraint. Total constraints: {len(ethics.constraints)}")

    print("\n=== Test 7: Generate Ethical Report ===")

    report = ethics.get_ethical_report()
    print(f"Total evaluations: {report['total_evaluations']}")
    print(f"Approval rate: {report['approval_rate']:.1%}")
    print(f"Average score: {report['average_score']:+.2f}")

    print("\nFinal State:")
    print(json.dumps(ethics.get_state(), indent=2))
