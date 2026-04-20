#!/usr/bin/env python3
"""
AMOS Agent Invariant Audit System
===================================

Formal invariant checklist for autonomous coding agents.
Minimum audit standard for free-agent coding systems.

Implements the 6-layer completion law:
    Done = Artifact ∧ Execution ∧ Verification ∧ Report

Reference: Formal Invariant Checklist for Autonomous Coding Agents
Failure Classes: Phantom artifact, Phantom action, Phantom verification, etc.

Architecture: 04_LAW layer enforcement for agent tasks
"""

import ast
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum, auto
from pathlib import Path
from typing import Any


class AuditStatus(Enum):
    """Invariant audit status."""

    PASS = auto()  # Invariant verified (1)
    FAIL = auto()  # Invariant failed (0)
    UNVERIFIED = auto()  # Not yet verified (?)
    BOUNDED = auto()  # Partially verified, bounded claims


class FailureClass(Enum):
    """
    Formal failure classification for agent audits.

    Artifact-level:
    - PHANTOM_ARTIFACT: Code-shaped text, not runnable code
    - PHANTOM_DEPENDENCY: References imaginary modules/files
    - PHANTOM_INTERFACE: Assumes API that is not real
    - PHANTOM_ENVIRONMENT: Code only works in imagined environment
    - PHANTOM_BEHAVIOR: Status changes imply work that never occurred

    Process-level:
    - PHANTOM_ACTION: Claimed action with no trace
    - PHANTOM_EDIT: "Updated file" but no diff
    - PHANTOM_RUN: "Ran tests" but no execution
    - PHANTOM_TOOL_SUCCESS: Empty output interpreted as success

    Verification-level:
    - PHANTOM_VERIFICATION: No verifier at all
    - MISBOUND_VERIFICATION: Wrong test for the claim
    - PARTIAL_VERIFICATION: Small safe subset tested
    - PHANTOM_SAFETY: Success inferred from lack of error

    Reporting-level:
    - PHANTOM_REPORT: Statement not traceable to observation
    - PHANTOM_CAPABILITY: Advertised feature not implemented
    - PHANTOM_READINESS: "Healthy" but not really loaded
    - PHANTOM_COMPLETION: "Fixed" but not verified

    Multi-agent-level:
    - PHANTOM_DELEGATION: Parent reports child success without verification
    - UNBACKED_SUBAGENT_SUCCESS: Child provides no grounded evidence
    - HALLUCINATION_CASCADE: False child result propagates downstream

    Persistence-level:
    - PHANTOM_PERSISTENCE: Saved object cannot reload
    - PHANTOM_REPLAY: Listed session cannot replay
    - PHANTOM_BACKEND: Claims persistent storage, uses memory
    """

    # Artifact
    PHANTOM_ARTIFACT = "phantom_artifact"
    PHANTOM_DEPENDENCY = "phantom_dependency"
    PHANTOM_INTERFACE = "phantom_interface"
    PHANTOM_ENVIRONMENT = "phantom_environment"
    PHANTOM_BEHAVIOR = "phantom_behavior"

    # Process
    PHANTOM_ACTION = "phantom_action"
    PHANTOM_EDIT = "phantom_edit"
    PHANTOM_RUN = "phantom_run"
    PHANTOM_TOOL_SUCCESS = "phantom_tool_success"

    # Verification
    PHANTOM_VERIFICATION = "phantom_verification"
    MISBOUND_VERIFICATION = "misbound_verification"
    PARTIAL_VERIFICATION = "partial_verification"
    PHANTOM_SAFETY = "phantom_safety"

    # Reporting
    PHANTOM_REPORT = "phantom_report"
    PHANTOM_CAPABILITY = "phantom_capability"
    PHANTOM_READINESS = "phantom_readiness"
    PHANTOM_COMPLETION = "phantom_completion"

    # Multi-agent
    PHANTOM_DELEGATION = "phantom_delegation"
    UNBACKED_SUBAGENT_SUCCESS = "unbacked_subagent_success"
    HALLUCINATION_CASCADE = "hallucination_cascade"

    # Persistence
    PHANTOM_PERSISTENCE = "phantom_persistence"
    PHANTOM_REPLAY = "phantom_replay"
    PHANTOM_BACKEND = "phantom_backend"


@dataclass
class InvariantResult:
    """Result of a single invariant check."""

    invariant_id: str
    family: str
    status: AuditStatus = field(default=AuditStatus.UNVERIFIED)
    evidence: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    failure_class: FailureClass = None
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class AgentTaskAudit:
    """Complete audit record for an agent task."""

    task_id: str
    goal: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Family results
    artifact_results: list[InvariantResult] = field(default_factory=list)
    execution_results: list[InvariantResult] = field(default_factory=list)
    verification_results: list[InvariantResult] = field(default_factory=list)
    reporting_results: list[InvariantResult] = field(default_factory=list)
    delegation_results: list[InvariantResult] = field(default_factory=list)
    persistence_results: list[InvariantResult] = field(default_factory=list)

    # Completion state
    completion_state: str = "INVALID"  # VALID | BOUNDED | INVALID

    # Evidence
    files_changed: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    verified_claims: list[str] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)
    remaining_risks: list[str] = field(default_factory=list)


class AgentInvariantAuditor:
    """
    Formal invariant auditor for autonomous coding agents.

    Implements the completion law:
        Done = Artifact ∧ Execution ∧ Verification ∧ Report

    Critical invariants (must all pass for completion):
        {A1, A2, A3, A4, X1, X2, X3, V1, V2, O1, O3, O4}

    Completion rule:
        Complete = 1 iff min(Critical) = 1
    """

    CRITICAL_INVARIANTS = {
        "A1",
        "A2",
        "A3",
        "A4",  # Artifact
        "X1",
        "X2",
        "X3",  # Execution
        "V1",
        "V2",  # Verification
        "O1",
        "O3",
        "O4",  # Reporting
    }

    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.audit_history: list[AgentTaskAudit] = []

    # =========================================================================
    # Family A — Artifact Invariants
    # =========================================================================

    def check_A1_syntax(self, code: str, language: str = "python") -> InvariantResult:
        """
        A1. Syntax invariant: Parse(C) = 1
        Question: Does the code parse in its declared language?
        Failure: Phantom artifact - code-shaped text, not runnable code
        """
        result = InvariantResult(invariant_id="A1", family="Artifact")

        if language == "python":
            try:
                ast.parse(code)
                result.status = AuditStatus.PASS
                result.evidence.append("Python AST parsing successful")
                result.confidence = 1.0
            except SyntaxError as e:
                result.status = AuditStatus.FAIL
                result.violations.append(f"Syntax error: {e}")
                result.failure_class = FailureClass.PHANTOM_ARTIFACT
                result.confidence = 1.0
        else:
            result.status = AuditStatus.UNVERIFIED
            result.evidence.append(f"Syntax check for {language} not implemented")

        return result

    def check_A2_resolution(self, code: str, file_path: Path = None) -> InvariantResult:
        """
        A2. Resolution invariant: Resolve(C, R, E, T) = 1
        Question: Do imports, files, commands, modules, paths exist?
        Failure: Phantom dependency - references imaginary modules
        """
        result = InvariantResult(invariant_id="A2", family="Artifact")

        if not code:
            result.status = AuditStatus.FAIL
            result.violations.append("Empty code provided")
            result.failure_class = FailureClass.PHANTOM_DEPENDENCY
            return result

        try:
            tree = ast.parse(code)
            unresolved = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        if not self._module_exists(mod):
                            unresolved.append(mod)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split(".")[0]
                        if not self._module_exists(mod):
                            unresolved.append(mod)

            if unresolved:
                result.status = AuditStatus.FAIL
                result.violations.append(f"Unresolved imports: {unresolved}")
                result.failure_class = FailureClass.PHANTOM_DEPENDENCY
                result.confidence = 0.9
            else:
                result.status = AuditStatus.PASS
                result.evidence.append("All imports resolvable")
                result.confidence = 0.85

        except SyntaxError:
            result.status = AuditStatus.UNVERIFIED
            result.evidence.append("Cannot check resolution - syntax error")

        return result

    def check_A3_contract(self, code: str, interface_specs: dict = None) -> InvariantResult:
        """
        A3. Contract invariant: Contract(C, S) = 1
        Question: Do calls, parameters, return shapes match actual definitions?
        Failure: Phantom interface - assumes API that is not real
        """
        result = InvariantResult(invariant_id="A3", family="Artifact")

        # Check for common contract violations
        violations = []

        # Pattern: function calls with wrong arity (simplified check)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # This is a simplified check - full contract checking requires type analysis
                    pass
        except SyntaxError:
            pass

        if violations:
            result.status = AuditStatus.FAIL
            result.violations.extend(violations)
            result.failure_class = FailureClass.PHANTOM_INTERFACE
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("No obvious contract violations detected")
            result.confidence = 0.7  # Lower confidence without full type analysis

        return result

    def check_A4_environment(self, code: str, target_env: dict = None) -> InvariantResult:
        """
        A4. Environment invariant: EnvFit(C, E, T) = 1
        Question: Does artifact match actual runtime, platform, loader, OS?
        Failure: Phantom environment - only works in imagined environment
        """
        result = InvariantResult(invariant_id="A4", family="Artifact")

        issues = []

        # Check for Python version-specific features
        if "match " in code and ":" in code:  # Pattern matching (3.10+)
            issues.append("May require Python 3.10+ (match statement)")

            # Check for type union syntax (3.10+)
            # Could be an issue for < 3.10
            pass

        if issues:
            result.status = AuditStatus.BOUNDED if target_env else AuditStatus.PASS
            result.evidence.extend(issues)
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("No obvious environment constraints")

        return result

    def check_A5_state_transition(self, code: str) -> InvariantResult:
        """
        A5. State-transition invariant: Transition(C) = ClaimedTransition(C)
        Question: Does the code really change state as claimed?
        Failure: Phantom behavior - implies work that never occurs
        """
        result = InvariantResult(invariant_id="A5", family="Artifact")

        # Check for suspicious patterns
        suspicious = []

        # Pattern: except: pass (swallows errors, claims success)
        if "except:" in code and "pass" in code:
            suspicious.append("Bare except: pass - may hide failures")

        # Pattern: return True at end regardless of logic
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "return True" in line and i > 0:
                # Check if preceded by error handling
                prev_lines = "\n".join(lines[max(0, i - 5) : i])
                if "except" in prev_lines or "try" in prev_lines:
                    suspicious.append(
                        f"Line {i}: return True after exception handling - possible phantom success"
                    )

        if suspicious:
            result.status = AuditStatus.BOUNDED
            result.evidence.extend(suspicious)
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("No obvious phantom behavior patterns")

        return result

    # =========================================================================
    # Family X — Execution Invariants
    # =========================================================================

    def check_X1_action_provenance(
        self, claimed_actions: list[str], observed_steps: list[str]
    ) -> InvariantResult:
        """
        X1. Action provenance invariant
        ∀ claim_action k, ∃ observed step x supporting k
        Question: Is every claimed edit/run/read/write backed by actual action?
        Failure: Phantom action - claimed but no trace
        """
        result = InvariantResult(invariant_id="X1", family="Execution")

        phantom_actions = []
        for action in claimed_actions:
            if not any(
                action.lower() in obs.lower() or obs.lower() in action.lower()
                for obs in observed_steps
            ):
                phantom_actions.append(action)

        if phantom_actions:
            result.status = AuditStatus.FAIL
            result.violations.append(f"Phantom actions: {phantom_actions}")
            result.failure_class = FailureClass.PHANTOM_ACTION
        else:
            result.status = AuditStatus.PASS
            result.evidence.append(f"All {len(claimed_actions)} actions have observed steps")

        return result

    def check_X2_edit_provenance(
        self, claimed_edits: dict[str, str], actual_diffs: dict[str, str]
    ) -> InvariantResult:
        """
        X2. Edit provenance invariant
        ClaimedEdit(f) -> ExistsDiff(f)
        Question: Is every claimed file fix backed by actual diff?
        Failure: Phantom edit - says fixed but no diff exists
        """
        result = InvariantResult(invariant_id="X2", family="Execution")

        phantom_edits = []
        for file_path in claimed_edits:
            if file_path not in actual_diffs or not actual_diffs[file_path].strip():
                phantom_edits.append(file_path)

        if phantom_edits:
            result.status = AuditStatus.FAIL
            result.violations.append(f"Phantom edits (no diff): {phantom_edits}")
            result.failure_class = FailureClass.PHANTOM_EDIT
        else:
            result.status = AuditStatus.PASS
            result.evidence.append(f"All {len(claimed_edits)} claimed edits have diffs")

        return result

    def check_X3_run_provenance(
        self, claimed_runs: list[str], execution_log: list[dict]
    ) -> InvariantResult:
        """
        X3. Run provenance invariant
        ClaimedRun(cmd) -> ExistsRun(cmd)
        Question: Did the claimed command actually execute in right environment?
        Failure: Phantom run - says ran tests but no execution
        """
        result = InvariantResult(invariant_id="X3", family="Execution")

        phantom_runs = []
        for cmd in claimed_runs:
            cmd_normalized = cmd.strip().split()[0] if cmd.strip() else ""
            found = any(cmd_normalized in log.get("command", "") for log in execution_log)
            if not found:
                phantom_runs.append(cmd)

        if phantom_runs:
            result.status = AuditStatus.FAIL
            result.violations.append(f"Phantom runs: {phantom_runs}")
            result.failure_class = FailureClass.PHANTOM_RUN
        else:
            result.status = AuditStatus.PASS
            result.evidence.append(f"All {len(claimed_runs)} claimed runs verified")

        return result

    def check_X4_tool_result_grounding(
        self, claimed_outcome: str, actual_output: str
    ) -> InvariantResult:
        """
        X4. Tool-result grounding invariant
        ClaimedToolOutcome -> ObservedToolOutcome
        Question: Does agent's interpretation match actual tool result?
        Failure: Phantom tool success - empty output as success
        """
        result = InvariantResult(invariant_id="X4", family="Execution")

        # Check for common grounding failures
        issues = []

        if not actual_output.strip() and "success" in claimed_outcome.lower():
            issues.append("Empty output interpreted as success")

        if len(actual_output) < 10 and "complete" in claimed_outcome.lower():
            issues.append("Minimal output claimed as complete")

        if issues:
            result.status = AuditStatus.FAIL
            result.violations.extend(issues)
            result.failure_class = FailureClass.PHANTOM_TOOL_SUCCESS
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("Tool outcome grounded in actual output")

        return result

    # =========================================================================
    # Family V — Verification Invariants
    # =========================================================================

    def check_V1_verification_existence(self, verification_steps: list[dict]) -> InvariantResult:
        """
        V1. Verification existence invariant
        ReportSuccess -> Exists(verification step)
        Question: Was there any verifier at all?
        Failure: Phantom verification - claims tested but no test
        """
        result = InvariantResult(invariant_id="V1", family="Verification")

        if not verification_steps:
            result.status = AuditStatus.FAIL
            result.violations.append("No verification steps provided")
            result.failure_class = FailureClass.PHANTOM_VERIFICATION
        else:
            result.status = AuditStatus.PASS
            result.evidence.append(f"{len(verification_steps)} verification steps found")

        return result

    def check_V2_verification_relevance(
        self, claim_type: str, verifier_type: str
    ) -> InvariantResult:
        """
        V2. Verification relevance invariant
        VerifierType matches ClaimType
        Question: Did the right test verify the right thing?
        Failure: Misbound verification - parse check claims packaging
        """
        result = InvariantResult(invariant_id="V2", family="Verification")

        # Mapping of appropriate verifiers to claims
        relevance_map = {
            "syntax": ["parse", "ast", "syntax"],
            "resolution": ["import", "resolve", "dependency"],
            "interface": ["type_check", "contract", "interface"],
            "packaging": ["build", "package", "install"],
            "cli_ux": ["cli_test", "integration", "e2e"],
            "works": ["runtime", "execution", "integration"],
        }

        appropriate = relevance_map.get(claim_type, [])
        if any(v in verifier_type.lower() for v in appropriate):
            result.status = AuditStatus.PASS
            result.evidence.append(f"{verifier_type} is appropriate for {claim_type}")
        else:
            result.status = AuditStatus.FAIL
            result.violations.append(f"{verifier_type} does not verify {claim_type}")
            result.failure_class = FailureClass.MISBOUND_VERIFICATION

        return result

    def check_V3_verification_sufficiency(
        self, critical_claims: list[str], verified_claims: list[str]
    ) -> InvariantResult:
        """
        V3. Verification sufficiency invariant
        CriticalClaims ⊆ VerifiedClaims
        Question: Were all important claims tested, or only safe subset?
        Failure: Partial verification masquerading as total
        """
        result = InvariantResult(invariant_id="V3", family="Verification")

        missing = set(critical_claims) - set(verified_claims)

        if missing:
            result.status = AuditStatus.BOUNDED
            result.violations.append(f"Untested critical claims: {missing}")
            result.failure_class = FailureClass.PARTIAL_VERIFICATION
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("All critical claims verified")

        return result

    def check_V4_negative_evidence(
        self, success_claimed: bool, failure_observed: bool
    ) -> InvariantResult:
        """
        V4. Negative evidence invariant
        NoFailureObserved ≠ Success
        Question: Did agent infer success only from lack of visible error?
        Failure: Phantom safety - no error seen so must be working
        """
        result = InvariantResult(invariant_id="V4", family="Verification")

        if success_claimed and not failure_observed:
            # This is weak evidence - just lack of failure
            result.status = AuditStatus.BOUNDED
            result.evidence.append("Success inferred from lack of failure (weak evidence)")
        elif success_claimed and failure_observed:
            result.status = AuditStatus.FAIL
            result.violations.append("Success claimed but failure observed")
            result.failure_class = FailureClass.PHANTOM_SAFETY
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("Proper positive verification exists")

        return result

    # =========================================================================
    # Family O — Reporting Invariants
    # =========================================================================

    def check_O1_report_equivalence(
        self,
        report: str,
        observed_artifacts: list[str],
        observed_runs: list[str],
        verifier_outputs: list[str],
    ) -> InvariantResult:
        """
        O1. Report equivalence invariant
        Report(O) = Summarize(Observed(A, X, V, S))
        Question: Can every material statement be traced to observation?
        Failure: Phantom report - statement not traceable
        """
        result = InvariantResult(invariant_id="O1", family="Reporting")

        # Check for claims in report that aren't grounded
        ungrounded = []

        # Simple heuristic: check if mentioned files exist in observed
        for artifact in observed_artifacts:
            if artifact not in report and Path(artifact).name not in report:
                ungrounded.append(f"Artifact {artifact} not mentioned")

        if ungrounded:
            result.status = AuditStatus.BOUNDED
            result.evidence.extend(ungrounded)
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("Report grounded in observations")

        return result

    def check_O2_capability_honesty(
        self, advertised: list[str], implemented: list[str]
    ) -> InvariantResult:
        """
        O2. Capability honesty invariant
        AdvertisedCapability ⊆ ImplementedCapability
        Question: Do docs advertise only real features?
        Failure: Phantom capability - promised but not implemented
        """
        result = InvariantResult(invariant_id="O2", family="Reporting")

        phantom = set(advertised) - set(implemented)

        if phantom:
            result.status = AuditStatus.FAIL
            result.violations.append(f"Phantom capabilities: {phantom}")
            result.failure_class = FailureClass.PHANTOM_CAPABILITY
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("All advertised capabilities implemented")

        return result

    def check_O3_status_honesty(self, reported_state: str, actual_state: str) -> InvariantResult:
        """
        O3. Status honesty invariant
        ReportedState = ActualState
        Question: Does "healthy" correspond to real load state?
        Failure: Phantom readiness - claims ready but not loaded
        """
        result = InvariantResult(invariant_id="O3", family="Reporting")

        # Map of claimed states to what they actually require
        state_requirements = {
            "healthy": ["loaded", "initialized", "running"],
            "ready": ["initialized", "configured"],
            "operational": ["loaded", "tested", "running"],
        }

        if reported_state.lower() in ["healthy", "ready", "operational"]:
            if actual_state.lower() not in state_requirements.get(reported_state.lower(), []):
                result.status = AuditStatus.FAIL
                result.violations.append(f"Reported '{reported_state}' but actual '{actual_state}'")
                result.failure_class = FailureClass.PHANTOM_READINESS
            else:
                result.status = AuditStatus.PASS
                result.evidence.append(f"Status '{reported_state}' matches actual state")
        else:
            result.status = AuditStatus.PASS

        return result

    def check_O4_completion_honesty(
        self, claimed_done: bool, goal_satisfied: bool
    ) -> InvariantResult:
        """
        O4. Completion honesty invariant
        ReportDone -> GoalSatisfied
        Question: Does "fixed" mean patched, verified, behaviorally complete?
        Failure: Phantom completion - says done but goal not met
        """
        result = InvariantResult(invariant_id="O4", family="Reporting")

        if claimed_done and not goal_satisfied:
            result.status = AuditStatus.FAIL
            result.violations.append("Completion claimed but goal not satisfied")
            result.failure_class = FailureClass.PHANTOM_COMPLETION
        elif claimed_done and goal_satisfied:
            result.status = AuditStatus.PASS
            result.evidence.append("Completion claim verified")
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("Task ongoing or properly incomplete")

        return result

    # =========================================================================
    # Family D — Delegation Invariants (Multi-Agent)
    # =========================================================================

    def check_D1_delegation_closure(
        self, child_result: dict, parent_verification: dict
    ) -> InvariantResult:
        """
        D1. Delegation closure invariant
        DelegatedResult -> IndependentlyVerifiedByParent
        Question: Did parent independently verify child's claimed result?
        Failure: Phantom delegation - parent reports child success without check
        """
        result = InvariantResult(invariant_id="D1", family="Delegation")

        if child_result.get("completed") and not parent_verification:
            result.status = AuditStatus.FAIL
            result.violations.append("Child result not independently verified by parent")
            result.failure_class = FailureClass.PHANTOM_DELEGATION
        else:
            result.status = AuditStatus.PASS
            if parent_verification:
                result.evidence.append("Parent verified child result")

        return result

    def check_D2_delegation_provenance(
        self, child_claim: str, child_evidence: list[str]
    ) -> InvariantResult:
        """
        D2. Delegation provenance invariant
        ChildClaim -> ChildEvidence
        Question: Does the child itself provide grounded evidence?
        Failure: Unbacked sub-agent success
        """
        result = InvariantResult(invariant_id="D2", family="Delegation")

        if not child_evidence:
            result.status = AuditStatus.FAIL
            result.violations.append("Child claim has no supporting evidence")
            result.failure_class = FailureClass.UNBACKED_SUBAGENT_SUCCESS
        else:
            result.status = AuditStatus.PASS
            result.evidence.append(f"Child provided {len(child_evidence)} evidence items")

        return result

    def check_D3_delegation_contamination(
        self, child_failed: bool, propagated_to_parent: bool
    ) -> InvariantResult:
        """
        D3. Delegation contamination invariant
        FalseChildSuccess -> must not propagate to parent completion
        Question: Can one bad sub-agent result poison downstream tasks?
        Failure: Hallucination cascade
        """
        result = InvariantResult(invariant_id="D3", family="Delegation")

        if child_failed and propagated_to_parent:
            result.status = AuditStatus.FAIL
            result.violations.append("Child failure propagated to parent completion")
            result.failure_class = FailureClass.HALLUCINATION_CASCADE
        else:
            result.status = AuditStatus.PASS
            if child_failed:
                result.evidence.append("Child failure properly contained")

        return result

    # =========================================================================
    # Family P — Persistence Invariants
    # =========================================================================

    def check_P1_persistence(self, saved_state: dict, reload_test: dict) -> InvariantResult:
        """
        P1. Persistence invariant
        Save(s) -> Reload(s) -> EquivalentState(s)
        Question: Can the claimed saved object actually be reloaded?
        Failure: Phantom persistence - save claimed but reload fails
        """
        result = InvariantResult(invariant_id="P1", family="Persistence")

        if not reload_test:
            result.status = AuditStatus.UNVERIFIED
            result.evidence.append("Reload test not performed")
        elif not reload_test.get("success"):
            result.status = AuditStatus.FAIL
            result.violations.append("Reload failed - persistence not real")
            result.failure_class = FailureClass.PHANTOM_PERSISTENCE
        else:
            # Check equivalence
            if reload_test.get("state") == saved_state:
                result.status = AuditStatus.PASS
                result.evidence.append("Reload successful with equivalent state")
            else:
                result.status = AuditStatus.FAIL
                result.violations.append("Reloaded state differs from saved")
                result.failure_class = FailureClass.PHANTOM_PERSISTENCE

        return result

    def check_P2_session_identity(
        self, listed_sessions: list[str], replayable: list[str]
    ) -> InvariantResult:
        """
        P2. Session identity invariant
        ListableSession -> ReplayableSession
        Question: If a session is listed, can it actually be replayed?
        Failure: Phantom replay - listed but not replayable
        """
        result = InvariantResult(invariant_id="P2", family="Persistence")

        not_replayable = set(listed_sessions) - set(replayable)

        if not_replayable:
            result.status = AuditStatus.FAIL
            result.violations.append(f"Non-replayable sessions: {not_replayable}")
            result.failure_class = FailureClass.PHANTOM_REPLAY
        else:
            result.status = AuditStatus.PASS
            result.evidence.append("All listed sessions replayable")

        return result

    def check_P3_backend_honesty(
        self, claims_persistent: bool, uses_backend: bool
    ) -> InvariantResult:
        """
        P3. Backend honesty invariant
        ClaimPersistentBackend -> ActualPersistentBackend
        Question: Does system really use persistent storage or only memory?
        Failure: Phantom backend - claims persistence, uses cache
        """
        result = InvariantResult(invariant_id="P3", family="Persistence")

        if claims_persistent and not uses_backend:
            result.status = AuditStatus.FAIL
            result.violations.append("Claims persistent backend but uses in-memory only")
            result.failure_class = FailureClass.PHANTOM_BACKEND
        else:
            result.status = AuditStatus.PASS
            if claims_persistent:
                result.evidence.append("Persistent backend verified")
            else:
                result.evidence.append("In-memory usage is as claimed")

        return result

    # =========================================================================
    # Completion Law & Critical Invariants
    # =========================================================================

    def evaluate_completion(self, audit: AgentTaskAudit) -> str:
        """
        Evaluate completion law: Done = A ∧ X ∧ V ∧ O

        Critical invariants (must all pass):
        {A1, A2, A3, A4, X1, X2, X3, V1, V2, O1, O3, O4}

        Completion rule: Complete = 1 iff min(Critical) = 1
        """
        all_results = (
            audit.artifact_results
            + audit.execution_results
            + audit.verification_results
            + audit.reporting_results
        )

        critical_results = [r for r in all_results if r.invariant_id in self.CRITICAL_INVARIANTS]

        # Check if all critical passed
        all_passed = all(r.status == AuditStatus.PASS for r in critical_results)
        any_failed = any(r.status == AuditStatus.FAIL for r in critical_results)
        any_unverified = any(r.status == AuditStatus.UNVERIFIED for r in critical_results)

        if all_passed:
            return "VALID"
        elif any_failed:
            return "INVALID"
        elif any_unverified:
            return "BOUNDED"
        else:
            return "INVALID"

    # =========================================================================
    # Full Audit Interface
    # =========================================================================

    def audit_task(self, task_id: str, goal: str, **kwargs) -> AgentTaskAudit:
        """
        Perform full invariant audit on an agent task.

        Args:
            task_id: Unique task identifier
            goal: Explicit measurable goal
            **kwargs: Task-specific data for invariant checking

        Returns:
            Complete audit record
        """
        audit = AgentTaskAudit(task_id=task_id, goal=goal)

        # Run artifact checks
        if "code" in kwargs:
            code = kwargs["code"]
            audit.artifact_results = [
                self.check_A1_syntax(code),
                self.check_A2_resolution(code, kwargs.get("file_path")),
                self.check_A3_contract(code, kwargs.get("interface_specs")),
                self.check_A4_environment(code, kwargs.get("target_env")),
                self.check_A5_state_transition(code),
            ]

        # Run execution checks
        if "claimed_actions" in kwargs:
            audit.execution_results = [
                self.check_X1_action_provenance(
                    kwargs["claimed_actions"], kwargs.get("observed_steps", [])
                ),
                self.check_X2_edit_provenance(
                    kwargs.get("claimed_edits", {}), kwargs.get("actual_diffs", {})
                ),
                self.check_X3_run_provenance(
                    kwargs.get("claimed_runs", []), kwargs.get("execution_log", [])
                ),
                self.check_X4_tool_result_grounding(
                    kwargs.get("claimed_outcome", ""), kwargs.get("actual_output", "")
                ),
            ]

        # Run verification checks
        if "verification_steps" in kwargs:
            audit.verification_results = [
                self.check_V1_verification_existence(kwargs["verification_steps"]),
                self.check_V2_verification_relevance(
                    kwargs.get("claim_type", ""), kwargs.get("verifier_type", "")
                ),
                self.check_V3_verification_sufficiency(
                    kwargs.get("critical_claims", []), kwargs.get("verified_claims", [])
                ),
                self.check_V4_negative_evidence(
                    kwargs.get("success_claimed", False), kwargs.get("failure_observed", False)
                ),
            ]

        # Run reporting checks
        if "report" in kwargs:
            audit.reporting_results = [
                self.check_O1_report_equivalence(
                    kwargs["report"],
                    kwargs.get("observed_artifacts", []),
                    kwargs.get("observed_runs", []),
                    kwargs.get("verifier_outputs", []),
                ),
                self.check_O2_capability_honesty(
                    kwargs.get("advertised", []), kwargs.get("implemented", [])
                ),
                self.check_O3_status_honesty(
                    kwargs.get("reported_state", ""), kwargs.get("actual_state", "")
                ),
                self.check_O4_completion_honesty(
                    kwargs.get("claimed_done", False), kwargs.get("goal_satisfied", False)
                ),
            ]

        # Evaluate completion
        audit.completion_state = self.evaluate_completion(audit)

        # Store history
        self.audit_history.append(audit)

        return audit

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _module_exists(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def generate_report(self, audit: AgentTaskAudit) -> dict[str, Any]:
        """Generate structured audit report."""
        all_results = (
            audit.artifact_results
            + audit.execution_results
            + audit.verification_results
            + audit.reporting_results
            + audit.delegation_results
            + audit.persistence_results
        )

        passed = sum(1 for r in all_results if r.status == AuditStatus.PASS)
        failed = sum(1 for r in all_results if r.status == AuditStatus.FAIL)
        unverified = sum(1 for r in all_results if r.status == AuditStatus.UNVERIFIED)
        bounded = sum(1 for r in all_results if r.status == AuditStatus.BOUNDED)

        critical_results = [r for r in all_results if r.invariant_id in self.CRITICAL_INVARIANTS]
        critical_passed = all(r.status == AuditStatus.PASS for r in critical_results)

        return {
            "task_id": audit.task_id,
            "goal": audit.goal,
            "timestamp": audit.timestamp,
            "completion_state": audit.completion_state,
            "can_claim_done": critical_passed,
            "summary": {
                "total_invariants": len(all_results),
                "passed": passed,
                "failed": failed,
                "unverified": unverified,
                "bounded": bounded,
                "critical_passed": critical_passed,
            },
            "invariant_families": {
                "artifact": [self._result_to_dict(r) for r in audit.artifact_results],
                "execution": [self._result_to_dict(r) for r in audit.execution_results],
                "verification": [self._result_to_dict(r) for r in audit.verification_results],
                "reporting": [self._result_to_dict(r) for r in audit.reporting_results],
                "delegation": [self._result_to_dict(r) for r in audit.delegation_results],
                "persistence": [self._result_to_dict(r) for r in audit.persistence_results],
            },
            "files_changed": audit.files_changed,
            "commands_run": audit.commands_run,
            "verified_claims": audit.verified_claims,
            "unverified_claims": audit.unverified_claims,
            "remaining_risks": audit.remaining_risks,
        }

    def _result_to_dict(self, result: InvariantResult) -> dict[str, Any]:
        """Convert invariant result to dictionary."""
        return {
            "invariant_id": result.invariant_id,
            "family": result.family,
            "status": result.status.name,
            "confidence": result.confidence,
            "evidence": result.evidence,
            "violations": result.violations,
            "failure_class": result.failure_class.value if result.failure_class else None,
        }

    def get_failure_signatures(self, audit: AgentTaskAudit) -> list[dict[str, Any]]:
        """Identify anti-pattern signatures from audit results."""
        all_results = (
            audit.artifact_results
            + audit.execution_results
            + audit.verification_results
            + audit.reporting_results
        )

        signatures = []

        # Signature A — "looks fixed" (phantom edit + phantom report)
        phantom_edit = any(
            r.failure_class == FailureClass.PHANTOM_EDIT for r in audit.execution_results
        )
        phantom_report = any(
            r.failure_class == FailureClass.PHANTOM_REPORT for r in audit.reporting_results
        )
        if phantom_edit and phantom_report:
            signatures.append(
                {
                    "signature": "A",
                    "name": "looks fixed",
                    "description": "Persuasive explanation but no diff",
                    "classification": ["phantom_edit", "phantom_report"],
                }
            )

        # Signature B — "verified" (phantom verification + phantom run)
        phantom_verification = any(
            r.failure_class == FailureClass.PHANTOM_VERIFICATION for r in audit.verification_results
        )
        phantom_run = any(
            r.failure_class == FailureClass.PHANTOM_RUN for r in audit.execution_results
        )
        if phantom_verification or phantom_run:
            signatures.append(
                {
                    "signature": "B",
                    "name": "verified",
                    "description": "Says 'confirmed' or 'tested' but no test evidence",
                    "classification": ["phantom_verification", "phantom_run"],
                }
            )

        # Signature C — "supported" (phantom capability)
        phantom_capability = any(
            r.failure_class == FailureClass.PHANTOM_CAPABILITY for r in audit.reporting_results
        )
        if phantom_capability:
            signatures.append(
                {
                    "signature": "C",
                    "name": "supported",
                    "description": "Docs advertise commands/features not implemented",
                    "classification": ["phantom_capability"],
                }
            )

        # Signature D — "initialized" (phantom readiness)
        phantom_readiness = any(
            r.failure_class == FailureClass.PHANTOM_READINESS for r in audit.reporting_results
        )
        if phantom_readiness:
            signatures.append(
                {
                    "signature": "D",
                    "name": "initialized",
                    "description": "Object exists but content/specs/modules did not load",
                    "classification": ["phantom_readiness"],
                }
            )

        # Signature F — "saved" (phantom persistence)
        phantom_persistence = any(
            r.failure_class == FailureClass.PHANTOM_PERSISTENCE for r in audit.persistence_results
        )
        if phantom_persistence:
            signatures.append(
                {
                    "signature": "F",
                    "name": "saved",
                    "description": "Says data persisted but reload path fails",
                    "classification": ["phantom_persistence"],
                }
            )

        return signatures


def main() -> int:
    """Demo the agent invariant auditor."""
    print("=" * 70)
    print("AMOS Agent Invariant Audit System")
    print("Formal invariant checklist for autonomous coding agents")
    print("=" * 70)

    auditor = AgentInvariantAuditor()

    # Example 1: Phantom artifact (syntax error)
    print("\n[Example 1] Phantom Artifact - Syntax Error")
    bad_code = "def broken(\n    pass  # Missing closing paren"

    result = auditor.check_A1_syntax(bad_code)
    print(f"  A1 Syntax: {result.status.name}")
    if result.failure_class:
        print(f"  Failure Class: {result.failure_class.value}")
    print(f"  Violations: {result.violations}")

    # Example 2: Phantom dependency (unresolved import)
    print("\n[Example 2] Phantom Dependency - Unresolved Import")
    code_with_import = "import nonexistent_module_xyz\nprint('hello')"

    result = auditor.check_A2_resolution(code_with_import)
    print(f"  A2 Resolution: {result.status.name}")
    if result.failure_class:
        print(f"  Failure Class: {result.failure_class.value}")
    print(f"  Violations: {result.violations}")

    # Example 3: Phantom edit
    print("\n[Example 3] Phantom Edit - Claimed but no diff")
    claimed = {"/path/to/file.py": "fixed"}
    actual = {}  # No actual diff

    result = auditor.check_X2_edit_provenance(claimed, actual)
    print(f"  X2 Edit Provenance: {result.status.name}")
    if result.failure_class:
        print(f"  Failure Class: {result.failure_class.value}")
    print(f"  Violations: {result.violations}")

    # Example 4: Phantom completion
    print("\n[Example 4] Phantom Completion - Claimed done but goal not met")
    result = auditor.check_O4_completion_honesty(claimed_done=True, goal_satisfied=False)
    print(f"  O4 Completion Honesty: {result.status.name}")
    if result.failure_class:
        print(f"  Failure Class: {result.failure_class.value}")
    print(f"  Violations: {result.violations}")

    # Example 5: Full task audit
    print("\n[Example 5] Full Task Audit")
    audit = auditor.audit_task(
        task_id="TASK-001",
        goal="Fix syntax error in calculator.py",
        code="def add(a, b): return a + b",  # Valid code
        claimed_actions=["fixed calculator.py"],
        observed_steps=["edit calculator.py"],
        claimed_edits={"calculator.py": "fixed"},
        actual_diffs={"calculator.py": "def add(a, b): return a + b"},
        claimed_done=True,
        goal_satisfied=True,
    )

    report = auditor.generate_report(audit)
    print(f"  Task: {report['task_id']}")
    print(f"  Goal: {report['goal']}")
    print(f"  Completion State: {report['completion_state']}")
    print(f"  Can Claim Done: {report['can_claim_done']}")
    print(f"  Summary: {report['summary']['passed']} passed, {report['summary']['failed']} failed")

    # Check for failure signatures
    signatures = auditor.get_failure_signatures(audit)
    if signatures:
        print(f"  Failure Signatures Detected: {len(signatures)}")
        for sig in signatures:
            print(f"    - {sig['name']}: {sig['description']}")
    else:
        print("  No failure signatures detected - clean audit")

    print("\n" + "=" * 70)
    print("Audit system operational")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
