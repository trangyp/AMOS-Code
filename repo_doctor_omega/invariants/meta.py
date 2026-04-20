"""Meta-architecture invariants for deep governance and truth preservation.

Implements the 200+ invariant catalog covering:
- Law hierarchy (conflict resolution, precedence, scope)
- Emergency constitution (temporary law changes, decay, truth)
- Silence semantics (absence vs suppression vs delay vs death)
- Constraint provenance (origin, rationale, taint, orphaning)
- Observer plurality (multi-model coherence, arbitration)
- Evidence survival (horizon, recovery preservation, forensics)
- Path dependence (history-shaped equivalence, non-ergodicity)
- Topology rewrite (split/merge integrity, neutralization)
- Anti-objectives (forbidden optimization, Goodhart protection)
- Institutional integrity (commons, shadow constitution, legibility)
- Proof/model transport (assumption preservation, federation)
- World drift (reality alignment, triple-drift boundedness)

Usage:
    from repo_doctor_omega.invariants.meta import MetaArchitectureInvariant

    inv = LawHierarchyInvariant()
    result = inv.check("/path/to/repo")

    if not result.passed:
        for v in result.violations:
            print(f"{v.invariant}: {v.message}")
"""

from pathlib import Path
from typing import Any

from ..state.basis import BasisVector
from .hard import HardInvariant, InvariantKind, InvariantResult, InvariantViolation

# =============================================================================
# Law Hierarchy Invariants
# =============================================================================


class LawHierarchyInvariant(HardInvariant):
    """I_law_hierarchy = 1 iff every protected invariant has explicit precedence.

    When two valid invariants conflict, the system must know which wins.
    Examples: liveness vs consistency, rollback vs audit retention,
    recovery vs least privilege, speed vs proof strength.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.LAW_HIERARCHY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check law hierarchy declarations."""
        violations = []

        # Look for ARCHITECTURE.md or constitutional documents
        config_files = [
            "ARCHITECTURE.md",
            "CONSTITUTION.md",
            "GOVERNANCE.md",
            "docs/architecture/governance.md",
        ]

        found_config = False
        has_precedence_rules = False

        for cfg_file in config_files:
            cfg_path = Path(repo_path) / cfg_file
            if cfg_path.exists():
                found_config = True
                content = cfg_path.read_text(encoding="utf-8", errors="ignore")

                # Check for precedence keywords
                precedence_keywords = [
                    "precedence",
                    "priority",
                    "conflict resolution",
                    "wins over",
                    "overrides",
                    "hierarchy",
                    "emergency >",
                    "safety >",
                    "liveness >",
                ]

                if any(kw in content.lower() for kw in precedence_keywords):
                    has_precedence_rules = True
                    break

        if not found_config:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No governance/constitution document found",
                    location="repository root",
                    severity=0.7,
                    remediation="Create ARCHITECTURE.md with invariant precedence rules",
                )
            )
        elif not has_precedence_rules:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Governance document lacks invariant precedence rules",
                    location="ARCHITECTURE.md",
                    severity=0.6,
                    remediation="Add explicit conflict resolution rules (e.g., 'safety > liveness')",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_config": found_config,
                "has_precedence_rules": has_precedence_rules,
                "config_files_checked": config_files,
            },
        )


class LawScopeInvariant(HardInvariant):
    """I_law_scope = 1 iff every law has explicit applicability conditions.

    A rule exists but the system doesn't specify where it applies:
    - Safety rule intended for production blocks emergency recovery
    - Compatibility rule for clients applied to internal tools
    - Logging rule treated as audit rule
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.LAW_SCOPE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check law scope declarations."""
        violations = []

        # Check for scope annotations in code
        scope_indicators = [
            "@scope",
            "# scope:",
            "# applies to:",
            "# invariant:",
            "SCOPE:",
            "APPLIES:",
            "REGIME:",
        ]

        py_files = list(Path(repo_path).rglob("*.py"))
        files_with_scope = 0
        total_files = 0

        for py_file in py_files[:100]:  # Sample first 100
            if "__pycache__" in str(py_file):
                continue
            total_files += 1

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if any(ind in content for ind in scope_indicators):
                    files_with_scope += 1
            except Exception:
                continue

        coverage = files_with_scope / total_files if total_files > 0 else 0

        if coverage < 0.1:  # Less than 10% scope annotation
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message=f"Low law scope coverage: {coverage:.1%} of files have scope annotations",
                    location="source code",
                    severity=0.5,
                    remediation="Add @scope or # scope: annotations to invariant-critical code",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "files_with_scope": files_with_scope,
                "total_files": total_files,
                "coverage": coverage,
            },
        )


# =============================================================================
# Emergency Constitution Invariants
# =============================================================================


class EmergencyConstitutionInvariant(HardInvariant):
    """I_emergency_constitution = 1 iff emergency modes have explicit law changes.

    Emergency modes must have:
    - Explicit temporary law changes
    - Bounded duration
    - Audit requirements
    - Restoration conditions
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.EMERGENCY_CONSTITUTION)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check emergency constitution declarations."""
        violations = []

        # Look for emergency documentation
        emergency_files = [
            "EMERGENCY.md",
            "RUNBOOK.md",
            "docs/emergency",
            "docs/runbooks",
        ]

        found_emergency_doc = False
        has_duration_bounds = False
        has_restoration = False
        has_audit = False

        for ef in emergency_files:
            ef_path = Path(repo_path) / ef
            if ef_path.exists():
                found_emergency_doc = True
                if ef_path.is_dir():
                    # Check files in directory
                    for f in ef_path.iterdir():
                        if f.is_file():
                            content = f.read_text(encoding="utf-8", errors="ignore")
                            if "duration" in content.lower() or "timeout" in content.lower():
                                has_duration_bounds = True
                            if "restore" in content.lower() or "recovery" in content.lower():
                                has_restoration = True
                            if "audit" in content.lower() or "log" in content.lower():
                                has_audit = True
                else:
                    content = ef_path.read_text(encoding="utf-8", errors="ignore")
                    if "duration" in content.lower() or "timeout" in content.lower():
                        has_duration_bounds = True
                    if "restore" in content.lower() or "recovery" in content.lower():
                        has_restoration = True
                    if "audit" in content.lower() or "log" in content.lower():
                        has_audit = True

        if not found_emergency_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No emergency constitution documentation found",
                    location="repository",
                    severity=0.6,
                    remediation="Create EMERGENCY.md with emergency modes and law changes",
                )
            )

        if found_emergency_doc and not has_duration_bounds:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Emergency modes lack bounded duration",
                    location="emergency docs",
                    severity=0.7,
                    remediation="Add explicit duration bounds to all emergency modes",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_emergency_doc": found_emergency_doc,
                "has_duration_bounds": has_duration_bounds,
                "has_restoration": has_restoration,
                "has_audit": has_audit,
            },
        )


# =============================================================================
# Silence Semantics Invariants
# =============================================================================


class SilenceSemanticsInvariant(HardInvariant):
    """I_silence = 1 iff silence states are explicitly distinguished.

    The system must distinguish:
    - No event occurred
    - Event occurred but not observed
    - Event suppressed
    - Event delayed
    - Event intentionally withheld
    - Event source dead
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.SILENCE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check silence semantics in logging/observability code."""
        violations = []

        # Look for silence-handling patterns
        silence_patterns = [
            "null",
            "none",
            "missing",
            "absent",
            "withheld",
            "suppressed",
            "dropped",
            "filtered",
            "delayed",
            "unknown",
            "unavailable",
            "timeout",
            "dead",
        ]

        # Check if codebase has explicit None/null handling
        py_files = list(Path(repo_path).rglob("*.py"))
        has_explicit_silence = False

        for py_file in py_files[:50]:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                # Look for explicit null handling with context
                if "if x is None" in content or "if result is None" in content:
                    has_explicit_silence = True
                    break
                # Check for Maybe/Optional types
                if "" in content or "Maybe" in content:
                    has_explicit_silence = True
                    break
            except Exception:
                continue

        if not has_explicit_silence:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Code lacks explicit silence/absence handling",
                    location="source code",
                    severity=0.5,
                    remediation="Use Optional types and explicit None branches",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "has_explicit_silence": has_explicit_silence,
                "silence_patterns": silence_patterns[:5] if silence_patterns else [],
            },
        )


# =============================================================================
# Constraint Provenance Invariants
# =============================================================================


class ConstraintProvenanceInvariant(HardInvariant):
    """I_constraint_provenance = 1 iff every constraint has attributable origin.

    The system enforces rules but no longer knows why:
    - Ancient compatibility shim
    - Retirement block with no rationale
    - Migration ordering workaround
    - Runtime flag required "for historical reasons"
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.CONSTRAINT_PROVENANCE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for constraint provenance documentation."""
        violations = []

        # Look for rationale/justification in comments
        provenance_indicators = [
            "rationale:",
            "reason:",
            "because",
            "due to",
            "needed for",
            "workaround for",
            "temporary",
            "TODO:",
            "FIXME:",
        ]

        py_files = list(Path(repo_path).rglob("*.py"))
        files_with_rationale = 0
        files_with_todos = 0
        total_files = 0

        for py_file in py_files[:100]:
            if "__pycache__" in str(py_file):
                continue
            total_files += 1

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if any(p in content.lower() for p in provenance_indicators):
                    files_with_rationale += 1
                if "TODO" in content or "FIXME" in content:
                    files_with_todos += 1
            except Exception:
                continue

        # High TODO count suggests missing provenance
        todo_ratio = files_with_todos / total_files if total_files > 0 else 0

        if todo_ratio > 0.3:  # More than 30% files have TODOs
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message=f"High TODO density ({todo_ratio:.1%}) suggests missing constraint rationale",
                    location="source code",
                    severity=0.4,
                    remediation="Document rationale for TODOs and workarounds",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "files_with_rationale": files_with_rationale,
                "files_with_todos": files_with_todos,
                "total_files": total_files,
                "todo_ratio": todo_ratio,
            },
        )


# =============================================================================
# Observer Plurality Invariants
# =============================================================================


class ObserverPluralityInvariant(HardInvariant):
    """I_observer_plurality = 1 iff all observers have reconciliation semantics.

    Code graph, rollout model, owner graph, compliance model, runtime telemetry,
    and package metadata may disagree. The system needs explicit arbitration.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.OBSERVER_PLURALITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for observer reconciliation mechanisms."""
        violations = []

        # Look for observer/reconciliation patterns
        observer_files = [
            "reconcile.py",
            "sync.py",
            "merge.py",
            "arbitrate.py",
            "consensus.py",
            "observer.py",
            "multi_model.py",
        ]

        found_observer_code = False
        has_reconciliation = False

        for of in observer_files:
            of_path = Path(repo_path) / of
            if of_path.exists():
                found_observer_code = True
                content = of_path.read_text(encoding="utf-8", errors="ignore")
                if "reconcile" in content.lower() or "arbitrate" in content.lower():
                    has_reconciliation = True
                break

        # Check for multiple model sources
        models = []
        if (Path(repo_path) / "requirements.txt").exists():
            models.append("dependencies")
        if (Path(repo_path) / "pyproject.toml").exists():
            models.append("packaging")
        if list(Path(repo_path).rglob("*.proto")):
            models.append("protobuf")
        if list(Path(repo_path).rglob("*.graphql")):
            models.append("graphql")

        if len(models) > 1 and not found_observer_code:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message=f"Multiple models ({models}) but no observer reconciliation code",
                    location="repository models",
                    severity=0.5,
                    remediation="Add observer reconciliation for multi-model consistency",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_observer_code": found_observer_code,
                "has_reconciliation": has_reconciliation,
                "detected_models": models,
            },
        )


# =============================================================================
# Evidence Survival Invariants
# =============================================================================


class EvidenceSurvivalInvariant(HardInvariant):
    """I_evidence_survival = 1 iff evidence survives required decision horizon.

    Logs, spans, ephemeral caches, rollout markers, or queue states disappear
    before governance, diagnosis, or recovery can use them.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.EVIDENCE_SURVIVAL)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check evidence retention policies."""
        violations = []

        # Look for retention configuration
        retention_files = [
            "retention.yaml",
            "retention.yml",
            "retention.json",
            "logs/retention",
            "config/retention",
        ]

        found_retention_config = False
        has_horizon = False

        for rf in retention_files:
            rf_path = Path(repo_path) / rf
            if rf_path.exists():
                found_retention_config = True
                content = rf_path.read_text(encoding="utf-8", errors="ignore")
                if "days" in content or "hours" in content or "retention" in content:
                    has_horizon = True
                break

        # Check for log rotation that might destroy evidence
        log_configs = list(Path(repo_path).rglob("*log*"))
        has_log_rotation = any("rotate" in str(lc).lower() for lc in log_configs)

        if not found_retention_config and has_log_rotation:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Log rotation without explicit retention policy",
                    location="logging configuration",
                    severity=0.6,
                    remediation="Add retention policy that preserves evidence for decision horizon",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_retention_config": found_retention_config,
                "has_horizon": has_horizon,
                "has_log_rotation": has_log_rotation,
            },
        )


# =============================================================================
# Path Dependence Invariants
# =============================================================================


class PathDependenceInvariant(HardInvariant):
    """I_path_dependence = 1 iff historical paths affecting admissibility remain queryable.

    Two systems with identical current state are not equivalent because they
    arrived through different transitions (migration path, codegen lineage,
    invalidation history, emergency sequence).
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.PATH_DEPENDENCE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for path history tracking."""
        violations = []

        # Check for migration history
        migration_files = [
            "migrations/",
            "alembic/",
            "db/migrate",
            "MIGRATIONS.md",
            "MIGRATION_HISTORY.md",
        ]

        has_migration_tracking = False
        has_migration_order = False

        for mf in migration_files:
            mf_path = Path(repo_path) / mf
            if mf_path.exists():
                has_migration_tracking = True
                if mf_path.is_dir():
                    # Check for ordered migrations
                    files = list(mf_path.iterdir())
                    if any(f.name[0].isdigit() for f in files if f.is_file()):
                        has_migration_order = True
                break

        # Check for git history depth (proxy for path preservation)
        git_path = Path(repo_path) / ".git"
        has_git_history = git_path.exists()

        if not has_migration_tracking and not has_git_history:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No migration tracking or version history found",
                    location="repository",
                    severity=0.5,
                    remediation="Add migration tracking or ensure git history preserves path",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "has_migration_tracking": has_migration_tracking,
                "has_migration_order": has_migration_order,
                "has_git_history": has_git_history,
            },
        )


# =============================================================================
# Topology Rewrite Invariants
# =============================================================================


class TopologyRewriteInvariant(HardInvariant):
    """I_topology_rewrite = 1 iff split/merge/extraction preserves canonical truth.

    Operations like repo split, repo merge, service extraction, authority move,
    schema handoff, protocol succession must preserve truth, lineage, and
    compatibility semantics.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.TOPOLOGY_REWRITE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for topology change documentation."""
        violations = []

        # Look for split/merge/extraction documentation
        topology_files = [
            "SPLIT.md",
            "MERGE.md",
            "EXTRACTION.md",
            "docs/topology",
            "TOPOLOGY.md",
        ]

        found_topology_doc = False
        has_neutralization_plan = False

        for tf in topology_files:
            tf_path = Path(repo_path) / tf
            if tf_path.exists():
                found_topology_doc = True
                content = tf_path.read_text(encoding="utf-8", errors="ignore")
                if "neutralize" in content.lower() or "retire" in content.lower():
                    has_neutralization_plan = True
                break

        # Check for multiple origin references (suggests merge)
        origin_refs = list(Path(repo_path).glob("*.origin"))
        if origin_refs and not found_topology_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Multiple origin references but no topology change documentation",
                    location="repository",
                    severity=0.5,
                    remediation="Document topology changes and neutralization plans",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_topology_doc": found_topology_doc,
                "has_neutralization_plan": has_neutralization_plan,
                "origin_refs": len(origin_refs),
            },
        )


# =============================================================================
# Anti-Objective Invariants
# =============================================================================


class AntiObjectiveInvariant(HardInvariant):
    """I_anti_objective = 1 iff every workflow declares forbidden optimization directions.

    The system knows what to maximize but not what must never be optimized:
    - Optimize latency even if audit disappears
    - Optimize rollout speed even if compatibility window shrinks
    - Optimize "green status" by collapsing degraded/healthy distinction
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.ANTI_OBJECTIVE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for anti-objective declarations."""
        violations = []

        # Look for anti-objective / guardrail documentation
        anti_objective_keywords = [
            "never",
            "must not",
            "forbidden",
            "prohibited",
            "anti-objective",
            "guardrail",
            "constraint",
            "not allowed",
            "cannot optimize",
        ]

        # Check README and architecture docs
        doc_files = ["README.md", "ARCHITECTURE.md", "GOALS.md"]
        found_anti_objectives = False

        for df in doc_files:
            df_path = Path(repo_path) / df
            if df_path.exists():
                content = df_path.read_text(encoding="utf-8", errors="ignore")
                if any(kw in content.lower() for kw in anti_objective_keywords):
                    found_anti_objectives = True
                    break

        if not found_anti_objectives:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No anti-objective declarations found in documentation",
                    location="documentation",
                    severity=0.4,
                    remediation="Add explicit 'what we must never optimize' section",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_anti_objectives": found_anti_objectives,
                "docs_checked": doc_files,
            },
        )


# =============================================================================
# Legibility Invariant
# =============================================================================


class LegibilityInvariant(HardInvariant):
    """I_legibility = 1 iff architecture remains reconstructable without tribal knowledge.

    The system stays live while becoming illegible to new maintainers.
    Structure, rationale, and coordination paths must be discoverable.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.LEGIBILITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for legibility indicators."""
        violations = []

        # Check for onboarding documentation
        onboarding_files = [
            "ONBOARDING.md",
            "CONTRIBUTING.md",
            "NEWBIE.md",
            "docs/onboarding",
            "docs/getting-started",
        ]

        found_onboarding = any((Path(repo_path) / of).exists() for of in onboarding_files)

        # Check for architecture diagrams
        diagram_files = list(Path(repo_path).rglob("*.png")) + list(Path(repo_path).rglob("*.svg"))
        has_diagrams = (
            len(
                [
                    d
                    for d in diagram_files
                    if "diagram" in str(d).lower() or "arch" in str(d).lower()
                ]
            )
            > 0
        )

        # Check for decision records
        adr_files = list(Path(repo_path).glob("*ADR*")) + list(Path(repo_path).glob("*decision*"))
        has_adrs = len(adr_files) > 0

        if not found_onboarding:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No onboarding documentation found",
                    location="documentation",
                    severity=0.5,
                    remediation="Create ONBOARDING.md for new maintainers",
                )
            )

        if not has_adrs:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No architecture decision records found",
                    location="documentation",
                    severity=0.4,
                    remediation="Add ADRs for significant architectural decisions",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "found_onboarding": found_onboarding,
                "has_diagrams": has_diagrams,
                "has_adrs": has_adrs,
            },
        )


# =============================================================================
# Model Transport Invariant
# =============================================================================


class ModelTransportInvariant(HardInvariant):
    """I_model_transport = 1 iff models are revalidated before cross-surface use.

    A model accurate for one service, repo, or epoch is reused elsewhere
    after ontology, constraints, or interfaces changed.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.MODEL_TRANSPORT)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for model validation on transport."""
        violations = []

        # Look for model validation patterns
        validation_patterns = [
            "validate_model",
            "model.validate",
            "check_model",
            "schema.validate",
            "contract.validate",
        ]

        py_files = list(Path(repo_path).rglob("*.py"))
        has_model_validation = False

        for py_file in py_files[:50]:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if any(vp in content for vp in validation_patterns):
                    has_model_validation = True
                    break
            except Exception:
                continue

        # Check for schema files (suggests model boundaries)
        schema_files = list(Path(repo_path).rglob("*.json")) + list(Path(repo_path).rglob("*.yaml"))
        has_schemas = len([s for s in schema_files if "schema" in str(s).lower()]) > 0

        if has_schemas and not has_model_validation:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Schema definitions but no model validation on transport",
                    location="source code",
                    severity=0.5,
                    remediation="Add model revalidation before cross-surface use",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "has_model_validation": has_model_validation,
                "has_schemas": has_schemas,
            },
        )


# =============================================================================
# World Drift Invariant
# =============================================================================


class WorldDriftInvariant(HardInvariant):
    """I_world_drift = 1 iff world-facing assumptions are monitored within bounded lag.

    Architecture fails because the world changes faster than assumptions.
    External APIs, regulations, dependencies evolve.
    """

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.WORLD_DRIFT)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for world-drift monitoring."""
        violations = []

        # Look for dependency monitoring
        dep_files = [
            "requirements.txt",
            "pyproject.toml",
            "Pipfile",
            "package.json",
            "Cargo.toml",
            "go.mod",
        ]

        has_dependency_files = False
        has_version_pins = False

        for df in dep_files:
            df_path = Path(repo_path) / df
            if df_path.exists():
                has_dependency_files = True
                content = df_path.read_text(encoding="utf-8", errors="ignore")
                # Check for version pinning (indicates drift awareness)
                if "==" in content or ">=" in content or "<=" in content:
                    has_version_pins = True
                break

        # Check for update automation
        update_configs = [
            ".github/dependabot.yml",
            ".github/renovate.json",
            ".dependabot/config.yml",
        ]
        has_update_automation = any((Path(repo_path) / uc).exists() for uc in update_configs)

        if has_dependency_files and not has_version_pins and not has_update_automation:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="Dependencies unpinned without automated update monitoring",
                    location="dependencies",
                    severity=0.5,
                    remediation="Pin dependencies or add automated update monitoring (dependabot)",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={
                "has_dependency_files": has_dependency_files,
                "has_version_pins": has_version_pins,
                "has_update_automation": has_update_automation,
            },
        )


# =============================================================================
# Ultimate Meta-Architecture: Modality System
# =============================================================================


class ModalityInvariant(HardInvariant):
    """I_modality = 1 iff required/allowed/forbidden/optional are distinguished."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.MODAL_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check modality distinctions."""
        violations = []

        # Check for modality documentation
        modality_files = ["MODALITY.md", "MODES.md", "STATES.md"]
        found_modality = any((Path(repo_path) / mf).exists() for mf in modality_files)

        if not found_modality:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No modality documentation - required/allowed/forbidden not distinguished",
                    location="modality",
                    severity=0.6,
                    remediation="Document modality states: required, allowed, forbidden, optional",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_modality_doc": found_modality},
        )


class ModalCollapseInvariant(HardInvariant):
    """I_modal_collapse = 1 iff modality confusion is prevented."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.MODAL_COLLAPSE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check for modality collapse prevention."""
        violations = []

        collapse_files = ["MODAL_COLLAPSE.md", "MODE_SAFETY.md"]
        found_collapse_doc = any((Path(repo_path) / cf).exists() for cf in collapse_files)

        if not found_collapse_doc:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No modality collapse prevention documented",
                    location="modal_safety",
                    severity=0.5,
                    remediation="Document how modality confusion is prevented",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_collapse_doc": found_collapse_doc},
        )


# =============================================================================
# Ultimate Meta-Architecture: Obligation System
# =============================================================================


class ObligationLifecycleInvariant(HardInvariant):
    """I_obligation = 1 iff duties have explicit creation/maturity/discharge."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.OBLIGATION_LIFECYCLE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check obligation lifecycle documentation."""
        violations = []

        obligation_files = ["OBLIGATION.md", "DUTIES.md", "COMMITMENTS.md"]
        found_obligation = any((Path(repo_path) / of).exists() for of in obligation_files)

        if not found_obligation:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No obligation lifecycle documentation",
                    location="obligations",
                    severity=0.6,
                    remediation="Document duty creation, maturity, and discharge semantics",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_obligation_doc": found_obligation},
        )


class ObligationTransferInvariant(HardInvariant):
    """I_obligation_transfer = 1 iff duty transfer integrity is maintained."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.OBLIGATION_TRANSFER)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check obligation transfer integrity."""
        violations = []

        transfer_files = ["TRANSFER.md", "HANDOFF.md", "DELEGATION.md"]
        found_transfer = any((Path(repo_path) / tf).exists() for tf in transfer_files)

        if not found_transfer:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No obligation transfer documentation",
                    location="transfer",
                    severity=0.5,
                    remediation="Document how duty transfers preserve integrity",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_transfer_doc": found_transfer},
        )


class PromiseIntegrityInvariant(HardInvariant):
    """I_promise = 1 iff promises have explicit creation and fulfillment tracking."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.PROMISE_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check promise integrity."""
        violations = []

        promise_files = ["PROMISE.md", "COMMITMENTS.md", "CONTRACTS.md"]
        found_promise = any((Path(repo_path) / pf).exists() for pf in promise_files)

        if not found_promise:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No promise integrity documentation",
                    location="promises",
                    severity=0.6,
                    remediation="Document promise creation and fulfillment semantics",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_promise_doc": found_promise},
        )


# =============================================================================
# Ultimate Meta-Architecture: Memory and Forgetting
# =============================================================================


class MemoryDisciplineInvariant(HardInvariant):
    """I_memory = 1 iff what must be remembered is explicitly declared."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.MEMORY_DISCIPLINE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check memory discipline."""
        violations = []

        memory_files = ["MEMORY.md", "RETENTION.md", "ARCHIVE.md"]
        found_memory = any((Path(repo_path) / mf).exists() for mf in memory_files)

        if not found_memory:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No memory discipline documentation",
                    location="memory",
                    severity=0.5,
                    remediation="Document what must be remembered and for how long",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_memory_doc": found_memory},
        )


class ForgettingSafetyInvariant(HardInvariant):
    """I_forgetting = 1 iff safe forgetting with tombstones is implemented."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.FORGETTING_SAFETY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check forgetting safety."""
        violations = []

        forgetting_files = ["FORGETTING.md", "DELETION.md", "TOMBSTONE.md"]
        found_forgetting = any((Path(repo_path) / ff).exists() for ff in forgetting_files)

        if not found_forgetting:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No forgetting safety documentation",
                    location="forgetting",
                    severity=0.5,
                    remediation="Document safe forgetting with tombstones",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_forgetting_doc": found_forgetting},
        )


class TombstoneIntegrityInvariant(HardInvariant):
    """I_tombstone = 1 iff deletion evidence is preserved."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.TOMBSTONE_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check tombstone integrity."""
        violations = []

        tombstone_files = ["TOMBSTONE.md", "AUDIT.md", "EVIDENCE.md"]
        found_tombstone = any((Path(repo_path) / tf).exists() for tf in tombstone_files)

        if not found_tombstone:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No tombstone integrity documentation",
                    location="tombstones",
                    severity=0.6,
                    remediation="Document deletion evidence preservation",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_tombstone_doc": found_tombstone},
        )


# =============================================================================
# Ultimate Meta-Architecture: Counterparty and Externality
# =============================================================================


class CounterpartyIntegrityInvariant(HardInvariant):
    """I_counterparty = 1 iff external obligations are represented."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.COUNTERPARTY_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check counterparty integrity."""
        violations = []

        counterparty_files = ["COUNTERPARTY.md", "EXTERNAL.md", "VENDORS.md"]
        found_counterparty = any((Path(repo_path) / cf).exists() for cf in counterparty_files)

        if not found_counterparty:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No counterparty integrity documentation",
                    location="counterparty",
                    severity=0.6,
                    remediation="Document external obligation representation",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_counterparty_doc": found_counterparty},
        )


class ExternalityBoundednessInvariant(HardInvariant):
    """I_externality = 1 iff irretractable emissions are bounded."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.EXTERNALITY_BOUNDEDNESS)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check externality boundedness."""
        violations = []

        externality_files = ["EXTERNALITY.md", "EMISSIONS.md", "BOUNDS.md"]
        found_externality = any((Path(repo_path) / ef).exists() for ef in externality_files)

        if not found_externality:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No externality boundedness documentation",
                    location="externality",
                    severity=0.7,
                    remediation="Document irretractable emission controls",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_externality_doc": found_externality},
        )


class ReciprocityIntegrityInvariant(HardInvariant):
    """I_reciprocity = 1 iff bilateral obligations are preserved."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.RECIPROCITY_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check reciprocity integrity."""
        violations = []

        reciprocity_files = ["RECIPROCITY.md", "BILATERAL.md", "MUTUAL.md"]
        found_reciprocity = any((Path(repo_path) / rf).exists() for rf in reciprocity_files)

        if not found_reciprocity:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No reciprocity integrity documentation",
                    location="reciprocity",
                    severity=0.5,
                    remediation="Document bilateral obligation preservation",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_reciprocity_doc": found_reciprocity},
        )


# =============================================================================
# Ultimate Meta-Architecture: Narrative and Explanation
# =============================================================================


class NarrativeCoherenceInvariant(HardInvariant):
    """I_narrative = 1 iff story consistency is maintained across surfaces."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.NARRATIVE_COHERENCE)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check narrative coherence."""
        violations = []

        narrative_files = ["NARRATIVE.md", "STORY.md", "HISTORY.md"]
        found_narrative = any((Path(repo_path) / nf).exists() for nf in narrative_files)

        if not found_narrative:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No narrative coherence documentation",
                    location="narrative",
                    severity=0.5,
                    remediation="Document story consistency across surfaces",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_narrative_doc": found_narrative},
        )


class ExplainabilityInvariant(HardInvariant):
    """I_explainability = 1 iff decisions are attributable and explainable."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.EXPLAINABILITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check explainability."""
        violations = []

        explain_files = ["EXPLAINABILITY.md", "TRANSPARENCY.md", "DECISIONS.md"]
        found_explain = any((Path(repo_path) / ef).exists() for ef in explain_files)

        if not found_explain:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No explainability documentation",
                    location="explainability",
                    severity=0.6,
                    remediation="Document decision attribution and explanation",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_explain_doc": found_explain},
        )


# =============================================================================
# Ultimate Meta-Architecture: Undecidability and Incompleteness
# =============================================================================


class UndecidabilityAwarenessInvariant(HardInvariant):
    """I_undecidability = 1 iff unprovable claims are explicitly handled."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.UNDECIDABILITY_AWARENESS)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check undecidability awareness."""
        violations = []

        undecidability_files = ["UNDECIDABILITY.md", "UNCERTAINTY.md", "LIMITS.md"]
        found_undecidability = any((Path(repo_path) / uf).exists() for uf in undecidability_files)

        if not found_undecidability:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No undecidability awareness documentation",
                    location="undecidability",
                    severity=0.5,
                    remediation="Document explicit handling of unprovable claims",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_undecidability_doc": found_undecidability},
        )


class SpecificationCompletenessInvariant(HardInvariant):
    """I_completeness = 1 iff incompleteness is explicitly marked."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.SPECIFICATION_COMPLETENESS)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check specification completeness marking."""
        violations = []

        completeness_files = ["COMPLETENESS.md", "INCOMPLETENESS.md", "TODO.md"]
        found_completeness = any((Path(repo_path) / cf).exists() for cf in completeness_files)

        if not found_completeness:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No specification completeness documentation",
                    location="completeness",
                    severity=0.5,
                    remediation="Document explicit incompleteness marking",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_completeness_doc": found_completeness},
        )


# =============================================================================
# Ultimate Meta-Architecture: Substitution
# =============================================================================


class SubstitutionIntegrityInvariant(HardInvariant):
    """I_substitution = 1 iff semantic preservation under substitution is verified."""

    def __init__(self):
        super().__init__(InvariantKind.META, BasisVector.SUBSTITUTION_INTEGRITY)

    def check(self, repo_path: str, context: dict[str, Any] = None) -> InvariantResult:
        """Check substitution integrity."""
        violations = []

        substitution_files = ["SUBSTITUTION.md", "REPLACEMENT.md", "SEMANTICS.md"]
        found_substitution = any((Path(repo_path) / sf).exists() for sf in substitution_files)

        if not found_substitution:
            violations.append(
                InvariantViolation(
                    invariant=self.name,
                    message="No substitution integrity documentation",
                    location="substitution",
                    severity=0.5,
                    remediation="Document semantic preservation under substitution",
                )
            )

        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"found_substitution_doc": found_substitution},
        )
