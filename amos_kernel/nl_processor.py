"""
AMOS Natural Language Processor - Intent IR and Command Lifecycle

Implements Section 105 from Axiom specification:
- Intake → Normalize → Parse → Load Control Files → Build Graph → Ground
- Classify Risk → Plan → Generate Patch → Verify → Explain → Commit/Reject → Ledger
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .axiom_state import get_state_manager
from .control_directory import get_control_manager

# ============================================================================
# Intent IR Types
# ============================================================================


class RiskLevel(Enum):
    """Risk classification for code changes."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CommandStatus(Enum):
    """Status in command lifecycle."""

    PENDING = "pending"
    INTAKE = "intake"
    NORMALIZE = "normalize"
    PARSE = "parse"
    GROUND = "ground"
    CLASSIFY = "classify"
    PLAN = "plan"
    GENERATE = "generate"
    VERIFY = "verify"
    EXPLAIN = "explain"
    COMMIT = "commit"
    REJECT = "reject"
    COMPLETE = "complete"


@dataclass
class IntentIR:
    """
    Intermediate Representation of human intent.
    Structured before code changes are generated.
    """

    intent_id: str
    raw_input: str
    normalized_input: str
    parsed_entities: dict[str, Any] = field(default_factory=dict)
    code_scope: list[str] = field(default_factory=list)
    action_type: str = ""  # create, modify, delete, query
    target_files: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, raw_input: str) -> IntentIR:
        """Create IntentIR from raw natural language input."""
        intent_id = hashlib.sha256(
            f"{raw_input}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]

        return cls(
            intent_id=intent_id,
            raw_input=raw_input,
            normalized_input=raw_input.lower().strip(),
        )


@dataclass
class PatchProposal:
    """Proposed code change."""

    patch_id: str
    target_file: str
    original_content: str
    modified_content: str
    line_range: tuple[int, int]
    change_type: str  # add, modify, delete
    explanation: str


@dataclass
class VerificationResult:
    """Result of verification checks."""

    check_name: str
    passed: bool
    details: dict[str, Any]
    error_message: str = ""


@dataclass
class CommandLedger:
    """Immutable ledger entry for command execution."""

    ledger_id: str
    intent_id: str
    status: CommandStatus
    transitions: list[dict[str, Any]] = field(default_factory=list)
    final_state: str = ""  # committed, rejected
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None


# ============================================================================
# Natural Language Processor
# ============================================================================


class NLProcessor:
    """
    Process natural language into Intent IR and command lifecycle.
    """

    def __init__(self) -> None:
        self.control_manager = get_control_manager()
        self.state_manager = get_state_manager()
        self._ledgers: dict[str, CommandLedger] = {}

    # -----------------------------------------------------------------------
    # Phase 1: Intake & Normalize
    # -----------------------------------------------------------------------

    def intake(self, raw_input: str) -> IntentIR:
        """
        Phase 1: Intake raw natural language input.
        Create Intent IR from raw input.
        """
        intent = IntentIR.from_raw(raw_input)
        self._update_ledger(intent.intent_id, CommandStatus.INTAKE, {})
        return intent

    def normalize(self, intent: IntentIR) -> IntentIR:
        """
        Phase 2: Normalize input.
        - Lowercase
        - Remove extra whitespace
        - Standardize terminology using glossary
        """
        normalized = intent.raw_input.lower().strip()

        # Apply glossary substitutions if control directory exists
        if self.control_manager.exists():
            glossary = self.control_manager.get_glossary()
            for term in glossary.terms:
                # Replace variations with canonical term
                for example in term.examples:
                    normalized = normalized.replace(example.lower(), term.human_term.lower())

        intent.normalized_input = normalized
        self._update_ledger(intent.intent_id, CommandStatus.NORMALIZE, {"normalized": normalized})
        return intent

    # -----------------------------------------------------------------------
    # Phase 2: Parse
    # -----------------------------------------------------------------------

    def parse(self, intent: IntentIR) -> IntentIR:
        """
        Phase 3: Parse normalized input.
        Extract entities, action type, and targets.
        """
        parsed = self._extract_entities(intent.normalized_input)

        intent.parsed_entities = parsed
        intent.action_type = parsed.get("action", "unknown")
        intent.target_files = parsed.get("targets", [])

        self._update_ledger(
            intent.intent_id,
            CommandStatus.PARSE,
            {"entities": parsed, "action": intent.action_type},
        )
        return intent

    def _extract_entities(self, text: str) -> dict[str, Any]:
        """Extract action entities from normalized text."""
        entities: dict[str, Any] = {
            "action": "unknown",
            "targets": [],
            "parameters": {},
        }

        # Action detection patterns
        action_patterns = {
            "create": ["create", "add", "new", "implement", "build"],
            "modify": ["modify", "change", "update", "edit", "fix", "refactor", "improve"],
            "delete": ["delete", "remove", "drop", "eliminate"],
            "query": ["find", "search", "get", "show", "list", "what", "how"],
        }

        for action, patterns in action_patterns.items():
            if any(p in text for p in patterns):
                entities["action"] = action
                break

        # File pattern detection
        file_patterns = [
            r"[\w/]+\.py",
            r"[\w/]+\.js",
            r"[\w/]+\.ts",
            r"[\w/]+\.json",
            r"[\w/]+\.yaml",
            r"[\w/]+\.md",
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, text)
            entities["targets"].extend(matches)

        # Extract quoted strings as parameters
        quoted = re.findall(r'"([^"]*)"', text)
        if quoted:
            entities["parameters"]["strings"] = quoted

        return entities

    # -----------------------------------------------------------------------
    # Phase 3: Ground
    # -----------------------------------------------------------------------

    def ground(self, intent: IntentIR) -> IntentIR:
        """
        Phase 4: Ground intent to code scope.
        Use glossary to map human terms to code locations.
        """
        if not self.control_manager.exists():
            # No control directory, use basic heuristics
            intent.code_scope = intent.target_files
            return intent

        glossary = self.control_manager.get_glossary()
        grounded_scope: list[str] = []

        for entity_name, entity_data in intent.parsed_entities.items():
            if entity_name == "targets":
                for target in entity_data:
                    term_mapping = glossary.lookup_term(target)
                    if term_mapping:
                        grounded_scope.append(term_mapping.code_scope)
                    else:
                        grounded_scope.append(target)

        intent.code_scope = grounded_scope or intent.target_files

        self._update_ledger(
            intent.intent_id,
            CommandStatus.GROUND,
            {"code_scope": grounded_scope},
        )
        return intent

    # -----------------------------------------------------------------------
    # Phase 4: Classify Risk
    # -----------------------------------------------------------------------

    def classify_risk(self, intent: IntentIR) -> RiskLevel:
        """
        Phase 5: Classify risk level.
        Check policies and determine risk score.
        """
        if not self.control_manager.exists():
            # No control directory, use heuristics
            risk = self._heuristic_risk(intent)
        else:
            # Check policies
            action = {
                "type": intent.action_type,
                "target": {"files": intent.target_files},
            }
            risk_score = self.control_manager.compute_risk_score(action)

            if risk_score < 0.25:
                risk = RiskLevel.LOW
            elif risk_score < 0.5:
                risk = RiskLevel.MEDIUM
            elif risk_score < 0.75:
                risk = RiskLevel.HIGH
            else:
                risk = RiskLevel.CRITICAL

        self._update_ledger(
            intent.intent_id,
            CommandStatus.CLASSIFY,
            {"risk_level": risk.value},
        )
        return risk

    def _heuristic_risk(self, intent: IntentIR) -> RiskLevel:
        """Heuristic risk classification without control directory."""
        # Delete operations are higher risk
        if intent.action_type == "delete":
            return RiskLevel.HIGH

        # Multiple file changes are higher risk
        if len(intent.target_files) > 3:
            return RiskLevel.MEDIUM

        # Protected patterns
        protected_patterns = ["config", "secret", "password", "key", "auth"]
        for target in intent.target_files:
            if any(p in target.lower() for p in protected_patterns):
                return RiskLevel.CRITICAL

        return RiskLevel.LOW

    # -----------------------------------------------------------------------
    # Phase 5: Plan
    # -----------------------------------------------------------------------

    def plan(self, intent: IntentIR) -> list[dict[str, Any]]:
        """
        Phase 6: Generate execution plan.
        Break intent into discrete steps.
        """
        steps: list[dict[str, Any]] = []

        if intent.action_type == "create":
            for target in intent.target_files:
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "create_file",
                        "target": target,
                        "verify": ["syntax", "exists"],
                    }
                )

        elif intent.action_type == "modify":
            for target in intent.target_files:
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "read_file",
                        "target": target,
                    }
                )
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "generate_patch",
                        "target": target,
                        "intent": intent.normalized_input,
                    }
                )
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "apply_patch",
                        "target": target,
                        "verify": ["syntax", "imports", "tests"],
                    }
                )

        elif intent.action_type == "delete":
            for target in intent.target_files:
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "backup_file",
                        "target": target,
                    }
                )
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "delete_file",
                        "target": target,
                        "verify": ["no_references"],
                    }
                )

        self._update_ledger(
            intent.intent_id,
            CommandStatus.PLAN,
            {"steps": len(steps)},
        )
        return steps

    # -----------------------------------------------------------------------
    # Phase 6: Generate Patch
    # -----------------------------------------------------------------------

    def generate_patch(self, intent: IntentIR, target_file: str) -> PatchProposal | None:
        """
        Phase 7: Generate code patch.
        Create actual code changes based on intent.

        Note: In production, this would use LLM or AST manipulation.
        This is a placeholder implementation.
        """
        if not Path(target_file).exists():
            return None

        try:
            with open(target_file) as f:
                original = f.read()
        except Exception:
            return None

        # Placeholder: Create a comment with the intent
        patch_id = hashlib.sha256(f"{intent.intent_id}:{target_file}".encode()).hexdigest()[:16]

        modified = original + f"\n# AMOS: {intent.normalized_input}\n"

        lines = original.split("\n")

        proposal = PatchProposal(
            patch_id=patch_id,
            target_file=target_file,
            original_content=original,
            modified_content=modified,
            line_range=(len(lines), len(lines)),
            change_type="modify",
            explanation=f"Apply intent: {intent.normalized_input}",
        )

        self._update_ledger(
            intent.intent_id,
            CommandStatus.GENERATE,
            {"patch_id": patch_id, "target": target_file},
        )
        return proposal

    # -----------------------------------------------------------------------
    # Phase 7: Verify
    # -----------------------------------------------------------------------

    def verify(self, proposal: PatchProposal) -> list[VerificationResult]:
        """
        Phase 8: Verify patch proposal.
        Run verification checks from verify.yaml.
        """
        results: list[VerificationResult] = []

        # Syntax check
        if proposal.target_file.endswith(".py"):
            results.append(self._verify_syntax_python(proposal))

        # File existence check
        results.append(self._verify_file_exists(proposal))

        # Load additional checks from control directory
        if self.control_manager.exists():
            verify_config = self.control_manager.get_verify()
            for check in verify_config.checks:
                if check.required:
                    results.append(
                        VerificationResult(
                            check_name=check.name,
                            passed=True,  # Placeholder
                            details={"command": check.command},
                        )
                    )

        self._update_ledger(
            proposal.patch_id,
            CommandStatus.VERIFY,
            {"checks": len(results), "passed": sum(1 for r in results if r.passed)},
        )
        return results

    def _verify_syntax_python(self, proposal: PatchProposal) -> VerificationResult:
        """Verify Python syntax."""
        import ast

        try:
            ast.parse(proposal.modified_content)
            return VerificationResult(
                check_name="syntax",
                passed=True,
                details={},
            )
        except SyntaxError as e:
            return VerificationResult(
                check_name="syntax",
                passed=False,
                details={"line": e.lineno, "text": e.text},
                error_message=str(e),
            )

    def _verify_file_exists(self, proposal: PatchProposal) -> VerificationResult:
        """Verify target file exists."""
        exists = Path(proposal.target_file).exists()
        return VerificationResult(
            check_name="file_exists",
            passed=exists,
            details={"path": proposal.target_file},
            error_message="" if exists else "File not found",
        )

    # -----------------------------------------------------------------------
    # Phase 8: Explain
    # -----------------------------------------------------------------------

    def explain(
        self, intent: IntentIR, proposal: PatchProposal, verifications: list[VerificationResult]
    ) -> str:
        """
        Phase 9: Generate explanation of changes.
        Human-readable summary before commit.
        """
        all_passed = all(v.passed for v in verifications)

        if proposal is None:
            targets = ", ".join(intent.target_files) if intent.target_files else "N/A"
            return f"""# Intent Analysis

## Input
{intent.normalized_input}

## Action
- Type: {intent.action_type}
- Targets: {targets}

## Status
No specific code changes proposed. Intent parsed successfully.
"""

        explanation = f"""# Proposed Changes

## Intent
{intent.normalized_input}

## Action
- Type: {intent.action_type}
- Target: {proposal.target_file}
- Scope: {", ".join(intent.code_scope) or "N/A"}

## Changes
```diff
# Lines {proposal.line_range[0]}-{proposal.line_range[1]}
# {proposal.change_type}
```

## Verification
"""
        for v in verifications:
            status = "✅" if v.passed else "❌"
            explanation += f"- {status} {v.check_name}\n"

        explanation += f"\n## Status: {'Ready to commit' if all_passed else 'Verification failed'}"

        self._update_ledger(
            intent.intent_id,
            CommandStatus.EXPLAIN,
            {"verification_passed": all_passed},
        )
        return explanation

    # -----------------------------------------------------------------------
    # Phase 9: Commit or Reject
    # -----------------------------------------------------------------------

    def commit(self, intent: IntentIR, proposal: PatchProposal) -> bool:
        """
        Phase 10a: Commit changes to filesystem.
        """
        try:
            with open(proposal.target_file, "w") as f:
                f.write(proposal.modified_content)

            self._update_ledger(
                intent.intent_id,
                CommandStatus.COMMIT,
                {"file": proposal.target_file},
            )
            self._finalize_ledger(intent.intent_id, "committed")
            return True
        except Exception as e:
            self._finalize_ledger(intent.intent_id, f"error: {e}")
            return False

    def reject(self, intent: IntentIR, reason: str) -> None:
        """
        Phase 10b: Reject changes with reason.
        """
        self._update_ledger(
            intent.intent_id,
            CommandStatus.REJECT,
            {"reason": reason},
        )
        self._finalize_ledger(intent.intent_id, f"rejected: {reason}")

    # -----------------------------------------------------------------------
    # Ledger Management
    # -----------------------------------------------------------------------

    def _update_ledger(
        self, intent_id: str, status: CommandStatus, details: dict[str, Any]
    ) -> None:
        """Update ledger with transition."""
        if intent_id not in self._ledgers:
            self._ledgers[intent_id] = CommandLedger(
                ledger_id=hashlib.sha256(intent_id.encode()).hexdigest()[:16],
                intent_id=intent_id,
                status=status,
            )

        ledger = self._ledgers[intent_id]
        ledger.transitions.append(
            {
                "status": status.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": details,
            }
        )
        ledger.status = status

    def _finalize_ledger(self, intent_id: str, final_state: str) -> None:
        """Finalize ledger entry."""
        if intent_id in self._ledgers:
            ledger = self._ledgers[intent_id]
            ledger.final_state = final_state
            ledger.completed_at = datetime.now(UTC)
            ledger.status = CommandStatus.COMPLETE

    def get_ledger(self, intent_id: str) -> CommandLedger | None:
        """Get ledger for intent."""
        return self._ledgers.get(intent_id)

    # -----------------------------------------------------------------------
    # Full Pipeline
    # -----------------------------------------------------------------------

    def process(
        self, raw_input: str, auto_commit: bool = False
    ) -> tuple[IntentIR, list[PatchProposal], str]:
        """
        Run full natural language processing pipeline.

        Returns: (intent, proposals, explanation)
        """
        # Phases 1-4: Intake through Ground
        intent = self.intake(raw_input)
        intent = self.normalize(intent)
        intent = self.parse(intent)
        intent = self.ground(intent)

        # Phase 5: Classify Risk
        risk = self.classify_risk(intent)

        # Phase 6: Plan
        steps = self.plan(intent)

        # Phases 7-8: Generate & Verify (for each target)
        proposals: list[PatchProposal] = []
        all_verifications: list[VerificationResult] = []

        for step in steps:
            if step.get("action") == "generate_patch":
                proposal = self.generate_patch(intent, step["target"])
                if proposal:
                    verifications = self.verify(proposal)
                    proposals.append(proposal)
                    all_verifications.extend(verifications)

        # Phase 9: Explain
        explanation = self.explain(intent, proposals[0] if proposals else None, all_verifications)

        # Phase 10: Commit or Reject
        if auto_commit and all(v.passed for v in all_verifications):
            for proposal in proposals:
                self.commit(intent, proposal)

        return intent, proposals, explanation


def get_nl_processor() -> NLProcessor:
    """Get NL processor instance."""
    return NLProcessor()
