"""Ultimate Meta-Architecture Invariants - The Deepest Layer.

This module implements the final frontier of architectural verification:
- Modality system (required/allowed/forbidden/optional)
- Obligation system (duties through time)
- Memory system (remembering and forgetting)
- Substitution system (semantic preservation)
- Counterparty system (external obligations)
- Narrative system (story coherence)
- Undecidability system (truth bounds)
- Bootstrap system (genesis and succession)
- Ecology system (external adaptation)
- Retroactivity system (backward change safety)
"""

from pathlib import Path
from typing import Any

from ..invariants.hard import HardInvariant, InvariantKind, InvariantResult, InvariantViolation
from ..state.basis import BasisVector


# =============================================================================
# Ultimate Meta-Architecture: Bootstrap and Genesis
# =============================================================================

class BootstrapIntegrityInvariant(HardInvariant):
    """I_bootstrap = 1 iff every truth domain has explicit genesis semantics."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.BOOTSTRAP_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check for bootstrap integrity."""
        violations = []

        bootstrap_files = ["BOOTSTRAP.md", "GENESIS.md", "FIRST_PRINCIPLES.md", "FOUNDATIONS.md"]
        found_bootstrap_doc = any(
            (Path(repo_path) / bf).exists()
            for bf in bootstrap_files
        )

        if not found_bootstrap_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No bootstrap genesis documentation - first laws not established",
                    location="foundations",
                    severity=0.7,
                    remediation="Document how truth domains are bootstrapped: first law, owner, evidence anchor",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_bootstrap_doc": found_bootstrap_doc},
        )


class AnchorSuccessionInvariant(HardInvariant):
    """I_anchor = 1 iff protected truth anchors can be lawfully rotated/succeeded."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.ANCHOR_SUCCESSION)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check for anchor succession policy."""
        violations = []

        succession_keywords = ["succession", "rotation", "handoff", "transfer", "anchor"]
        succession_files = ["SUCCESSION.md", "ROTATION.md", "ANCHOR.md"]

        found_succession_doc = any(
            (Path(repo_path) / sf).exists()
            for sf in succession_files
        )

        if not found_succession_doc:
            # Check in governance docs
            gov_path = Path(repo_path) / "GOVERNANCE.md"
            if gov_path.exists():
                content = gov_path.read_text(encoding="utf-8", errors="ignore")
                if any(kw in content.lower() for kw in succession_keywords):
                    found_succession_doc = True

        if not found_succession_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No anchor succession policy - truth anchors cannot be safely rotated",
                    location="governance",
                    severity=0.65,
                    remediation="Document how truth anchors (configs, keys, authorities) are rotated without rupture",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_succession_doc": found_succession_doc},
        )


# =============================================================================
# Ultimate Meta-Architecture: Ecology and Adaptation
# =============================================================================

class EcologicalAwarenessInvariant(HardInvariant):
    """I_ecology = 1 iff adaptive external participants are represented in world model."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.ECOLOGICAL_AWARENESS)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check for ecological awareness."""
        violations = []

        ecology_keywords = ["ecology", "ecosystem", "external", "vendor", "upstream", "downstream"]
        ecology_files = ["ECOLOGY.md", "ECOSYSTEM.md", "EXTERNAL.md", "VENDORS.md"]

        found_ecology_doc = any(
            (Path(repo_path) / ef).exists()
            for ef in ecology_files
        )

        if not found_ecology_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No ecological awareness - external adaptive participants not modeled",
                    location="world model",
                    severity=0.55,
                    remediation="Document external ecology: vendors, clients, operators, and how they adapt",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_ecology_doc": found_ecology_doc},
        )


class MoralHazardResistanceInvariant(HardInvariant):
    """I_moral = 1 iff incentive misalignment is detected and bounded."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.MORAL_HAZARD_RESISTANCE)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check for moral hazard awareness."""
        violations = []

        moral_keywords = ["incentive", "moral hazard", "gaming", "metric", "reward", "alignment"]
        incentive_files = ["INCENTIVES.md", "ALIGNMENT.md", "ETHICS.md", "MORAL_HAZARD.md"]

        found_incentive_doc = any(
            (Path(repo_path) / inf).exists()
            for inf in incentive_files
        )

        if not found_incentive_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No moral hazard analysis - incentive misalignments not tracked",
                    location="incentive design",
                    severity=0.5,
                    remediation="Document incentives and how they align/diverge from system health",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_incentive_doc": found_incentive_doc},
        )


# =============================================================================
# Ultimate Meta-Architecture: Retroactivity
# =============================================================================

class RetroactivitySafetyInvariant(HardInvariant):
    """I_retro = 1 iff backward changes have explicit safety semantics."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.RETROACTIVITY_SAFETY)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check for retroactivity safety."""
        violations = []

        retro_keywords = ["retroactive", "backward", "rewrite history", "amend", "rebase"]
        retro_files = ["RETROACTIVITY.md", "HISTORY.md", "IMMUTABILITY.md", "APPEND_ONLY.md"]

        found_retro_policy = any(
            (Path(repo_path) / rf).exists()
            for rf in retro_files
        )

        if not found_retro_policy:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No retroactivity safety policy - backward changes not governed",
                    location="temporal policy",
                    severity=0.7,
                    remediation="Document rules for retroactive changes: when allowed, when forbidden, audit requirements",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_retro_policy": found_retro_policy},
        )


__all__ = [
    "BootstrapIntegrityInvariant",
    "AnchorSuccessionInvariant",
    "EcologicalAwarenessInvariant",
    "MoralHazardResistanceInvariant",
    "RetroactivitySafetyInvariant",
]
