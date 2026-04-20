"""
AMOS Compiler: Intent Intermediate Representation
Converts natural language into structured, repo-grounded intent.

This implements the Intent -> Meaning stage of the AMOS pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto
from typing import Any, Optional


class ActionType(Enum):
    """Classification of code transformation actions."""

    INSPECT = auto()  # Read/analyze without modification
    EXPLAIN = auto()  # Generate explanation
    FIND = auto()  # Locate symbols or patterns
    FIX = auto()  # Correct bugs or issues
    REFACTOR = auto()  # Restructure without behavior change
    RENAME = auto()  # Change symbol names
    ADD = auto()  # Add new code
    REMOVE = auto()  # Delete code
    MODIFY = auto()  # Change behavior
    MIGRATE = auto()  # Move between patterns/apis
    ENFORCE = auto()  # Apply architectural constraints


class RiskLevel(Enum):
    """Risk classification for changes."""

    LOW = "low"  # Safe, auto-apply
    MEDIUM = "medium"  # Review recommended
    HIGH = "high"  # Approval required
    CRITICAL = "critical"  # Multiple approvals + verification


class EditLevel(Enum):
    """Level of code transformation sophistication."""

    TEXT = 1  # Simple text replacement
    AST = 2  # AST-aware edits
    SYMBOL = 3  # Symbol-aware (renames, moves)
    SEMANTIC = 4  # Behavior-changing across modules


@dataclass
class Constraint:
    """A constraint on the transformation."""

    type: str  # e.g., "preserve_behavior", "local_only", "no_db_change"
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckRequirement:
    """A verification check that must pass."""

    check_type: str  # e.g., "test", "lint", "typecheck", "architecture"
    scope: list[str] = field(default_factory=list)
    must_pass: bool = True
    command: Optional[str] = None


@dataclass
class ArtifactExpectation:
    """Expected output artifacts from the transformation."""

    type: str  # "code", "test", "doc", "config"
    path_pattern: Optional[str] = None
    description: str = ""


@dataclass
class TargetDomain:
    """The conceptual domain being targeted."""

    name: str  # e.g., "self_hosted_provider_auth"
    glossary_terms: list[str] = field(default_factory=list)
    symbol_patterns: list[str] = field(default_factory=list)
    file_patterns: list[str] = field(default_factory=list)


@dataclass
class IntentIR:
    """
    Intermediate Representation of a natural language instruction.

    This is the structured output of the Intent Parser stage,
    ready for grounding to actual repo symbols.
    """

    # Original input
    raw_instruction: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Core action classification
    action: ActionType = ActionType.INSPECT
    edit_level: EditLevel = EditLevel.TEXT

    # Target domain (conceptual)
    target_domain: TargetDomain = field(default_factory=lambda: TargetDomain(""))

    # Constraints and requirements
    constraints: list[Constraint] = field(default_factory=list)
    required_checks: list[CheckRequirement] = field(default_factory=list)

    # Risk assessment
    risk_level: RiskLevel = RiskLevel.LOW
    risk_reason: str = ""

    # Expected outcomes
    expected_artifacts: list[ArtifactExpectation] = field(default_factory=list)

    # Uncertainty tracking
    ambiguities: list[str] = field(default_factory=list)
    clarifying_questions: list[str] = field(default_factory=list)

    # Metadata
    inferred: bool = False  # True if any fields were inferred
    confidence: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "raw_instruction": self.raw_instruction,
            "timestamp": self.timestamp,
            "action": self.action.name,
            "edit_level": self.edit_level.value,
            "target_domain": {
                "name": self.target_domain.name,
                "glossary_terms": self.target_domain.glossary_terms,
                "symbol_patterns": self.target_domain.symbol_patterns,
                "file_patterns": self.target_domain.file_patterns,
            },
            "constraints": [
                {"type": c.type, "description": c.description, "parameters": c.parameters}
                for c in self.constraints
            ],
            "required_checks": [
                {
                    "check_type": c.check_type,
                    "scope": c.scope,
                    "must_pass": c.must_pass,
                    "command": c.command,
                }
                for c in self.required_checks
            ],
            "risk_level": self.risk_level.value,
            "risk_reason": self.risk_reason,
            "expected_artifacts": [
                {"type": a.type, "path_pattern": a.path_pattern, "description": a.description}
                for a in self.expected_artifacts
            ],
            "ambiguities": self.ambiguities,
            "clarifying_questions": self.clarifying_questions,
            "confidence": self.confidence,
        }


class IntentParser:
    """
    Parses natural language instructions into IntentIR.

    This is the first stage of the AMOS compiler pipeline.
    """

    # Keywords that map to action types
    ACTION_KEYWORDS: dict[ActionType, list[str]] = {
        ActionType.INSPECT: ["show", "find", "locate", "list", "display", "what is", "where is"],
        ActionType.EXPLAIN: ["explain", "describe", "how does", "why", "document"],
        ActionType.FIX: ["fix", "repair", "correct", "resolve", "bug", "issue"],
        ActionType.REFACTOR: ["refactor", "restructure", "clean up", "simplify", "organize"],
        ActionType.RENAME: ["rename", "call it", "change name"],
        ActionType.ADD: ["add", "create", "implement", "build", "new"],
        ActionType.REMOVE: ["remove", "delete", "drop", "eliminate"],
        ActionType.MODIFY: [
            "modify",
            "change",
            "update",
            "make",
            "set",
            "enable",
            "disable",
            "optional",
        ],
        ActionType.MIGRATE: ["migrate", "move to", "upgrade", "convert"],
        ActionType.ENFORCE: ["enforce", "ensure", "require", "validate"],
    }

    # Risk indicators
    RISK_INDICATORS: dict[RiskLevel, list[str]] = {
        RiskLevel.CRITICAL: [
            "auth",
            "authentication",
            "password",
            "secret",
            "kernel",
            "law",
            "payment",
            "billing",
            "security",
            "encryption",
        ],
        RiskLevel.HIGH: [
            "database",
            "schema",
            "migration",
            "api",
            "endpoint",
            "contract",
            "public",
            "external",
            "customer",
        ],
        RiskLevel.MEDIUM: ["behavior", "logic", "flow", "config", "provider", "model"],
    }

    def parse(self, instruction: str) -> IntentIR:
        """
        Parse a natural language instruction into IntentIR.

        This is a rule-based parser. In production, this would use
        an LLM with structured output to Pydantic models.
        """
        instruction_lower = instruction.lower()

        # Determine action type
        action = self._detect_action(instruction_lower)

        # Determine edit level based on action
        edit_level = self._determine_edit_level(action, instruction_lower)

        # Detect target domain
        target_domain = self._detect_target_domain(instruction_lower)

        # Assess risk
        risk_level, risk_reason = self._assess_risk(instruction_lower, action)

        # Extract constraints
        constraints = self._extract_constraints(instruction_lower)

        # Determine required checks
        required_checks = self._determine_checks(action, risk_level)

        # Identify ambiguities
        ambiguities = self._identify_ambiguities(instruction)

        return IntentIR(
            raw_instruction=instruction,
            action=action,
            edit_level=edit_level,
            target_domain=target_domain,
            constraints=constraints,
            required_checks=required_checks,
            risk_level=risk_level,
            risk_reason=risk_reason,
            ambiguities=ambiguities,
            confidence=0.8 if not ambiguities else 0.5,
        )

    def _detect_action(self, instruction: str) -> ActionType:
        """Detect the action type from keywords."""
        for action_type, keywords in self.ACTION_KEYWORDS.items():
            if any(kw in instruction for kw in keywords):
                return action_type
        return ActionType.INSPECT  # Default

    def _determine_edit_level(self, action: ActionType, instruction: str) -> EditLevel:
        """Determine the required edit sophistication."""
        # Check for semantic-level indicators
        semantic_indicators = [
            "everywhere",
            "all",
            "across",
            "throughout",
            "except",
            "only",
            "preserve",
            "maintain",
        ]
        if any(si in instruction for si in semantic_indicators):
            return EditLevel.SEMANTIC

        # Check for symbol-level indicators
        symbol_indicators = ["rename", "move", "extract", "interface"]
        if action == ActionType.RENAME or any(si in instruction for si in symbol_indicators):
            return EditLevel.SYMBOL

        # Check for AST-level indicators
        ast_indicators = ["refactor", "restructure", "clean up"]
        if any(si in instruction for si in ast_indicators):
            return EditLevel.AST

        return EditLevel.TEXT

    def _detect_target_domain(self, instruction: str) -> TargetDomain:
        """Detect the conceptual domain being targeted."""
        # This would integrate with glossary in production
        domain = TargetDomain(name="unknown")

        # Detect glossary terms
        if "localhost" in instruction or "local" in instruction:
            domain.name = "localhost_config"
            domain.glossary_terms.append("self_hosted")
            domain.symbol_patterns.extend(["localhost", "local", "127.0.0.1"])

        if "api key" in instruction or "auth" in instruction:
            domain.name = "authentication"
            domain.glossary_terms.append("api_key")
            domain.symbol_patterns.extend(["APIKey", "api_key", "auth"])

        if "customer" in instruction:
            domain.name = "customer_domain"
            domain.glossary_terms.append("customer")
            domain.symbol_patterns.extend(["Customer", "customer"])

        return domain

    def _assess_risk(self, instruction: str, action: ActionType) -> tuple[RiskLevel, str]:
        """Assess the risk level of the change."""
        for level, indicators in self.RISK_INDICATORS.items():
            if any(ind in instruction for ind in indicators):
                return level, f"Detected keywords indicating {level.value} risk"

        # Higher risk for behavior changes
        if action in (ActionType.MODIFY, ActionType.REMOVE):
            return RiskLevel.MEDIUM, "Behavior modification requires caution"

        return RiskLevel.LOW, "Standard operation"

    def _extract_constraints(self, instruction: str) -> list[Constraint]:
        """Extract constraints from the instruction."""
        constraints = []

        # Scope constraints
        if "only" in instruction and "localhost" in instruction:
            constraints.append(
                Constraint(
                    type="local_only",
                    description="Changes must only affect localhost/self-hosted paths",
                    parameters={"scope": "localhost"},
                )
            )

        if "except" in instruction or "not" in instruction:
            # Extract exception patterns
            constraints.append(
                Constraint(
                    type="preserve_scope",
                    description="Preserve behavior in excluded scopes",
                    parameters={},
                )
            )

        # Behavioral constraints
        if "preserve" in instruction or "keep" in instruction:
            constraints.append(
                Constraint(
                    type="preserve_behavior",
                    description="Existing behavior must be preserved",
                    parameters={},
                )
            )

        return constraints

    def _determine_checks(self, action: ActionType, risk: RiskLevel) -> list[CheckRequirement]:
        """Determine what checks must pass."""
        checks = []

        # All modifications need tests
        if action in (ActionType.MODIFY, ActionType.FIX, ActionType.REFACTOR):
            checks.append(
                CheckRequirement(check_type="test", scope=["unit", "integration"], must_pass=True)
            )

        # Type checking for code changes
        if action != ActionType.INSPECT:
            checks.append(CheckRequirement(check_type="typecheck", must_pass=True))

        # Architecture validation for structural changes
        if action in (ActionType.REFACTOR, ActionType.MIGRATE):
            checks.append(CheckRequirement(check_type="architecture", must_pass=True))

        # High risk requires more checks
        if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            checks.append(CheckRequirement(check_type="security", must_pass=True))

        return checks

    def _identify_ambiguities(self, instruction: str) -> list[str]:
        """Identify potential ambiguities in the instruction."""
        ambiguities = []

        # Check for vague quantifiers
        vague_terms = ["this", "that", "it", "some", "many"]
        if any(term in instruction.lower().split() for term in vague_terms):
            ambiguities.append("Contains vague references (this/that/it)")

        # Check for missing scope
        if "everywhere" in instruction.lower() and "except" not in instruction.lower():
            if "only" not in instruction.lower():
                ambiguities.append("Broad scope without explicit boundaries")

        return ambiguities


def parse_intent(instruction: str) -> IntentIR:
    """Convenience function to parse an instruction."""
    parser = IntentParser()
    return parser.parse(instruction)
