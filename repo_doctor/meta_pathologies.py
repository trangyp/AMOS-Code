"""Meta-Architecture Pathologies - The Missing Layer.

Detects failures that live above ordinary architecture:
- Failures of meaning (semantic integrity)
- Failures of time ordering (temporal architecture)
- Failures of trust and provenance
- Failures of recovery and containment
- Failures of multi-actor operation
- Failures of compositionality
- Failures of the doctor itself (diagnostic self-integrity)

The true state is:
R** = (
  implementation_state,
  architecture_state,
  temporal_order_state,
  trust_state,
  containment_state,
  recovery_state,
  semantic_state,
  governance_state,
  operator_state,
  diagnostic_self_state
)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class MetaPathologyType(Enum):
    """Meta-architectural failure classes."""

    # Semantic integrity
    ONTOLOGY_DRIFT = auto()  # Same word means different things
    SEMANTIC_ALIAS_EXPLOSION = auto()  # Uncontrolled synonyms
    FALSE_SEMANTIC_EQUIVALENCE = auto()  # Treated as equal when not

    # Temporal-order
    PARTIAL_ORDER_FAILURE = auto()  # Missing causal ordering
    TEMPORAL_PLANE_SKEW = auto()  # Planes lag each other
    EVENTUAL_VALIDITY_TRAP = auto()  # Unbounded "eventually"

    # Provenance and trust
    PROVENANCE_GAP = auto()  # Unknown artifact origin
    SUPPLY_CHAIN_SEMANTIC_TRUST_FAILURE = auto()  # Untrusted deps
    REPRODUCIBILITY_FAILURE = auto()  # Non-deterministic builds

    # Recovery and containment
    RECOVERY_PATH_INCOMPLETENESS = auto()  # No path back to safety
    NON_IDEMPOTENT_RECOVERY = auto()  # Recovery changes state each run
    BLAST_CONTAINMENT_FAILURE = auto()  # Failure propagates too wide

    # Isolation
    ISOLATION_FAILURE = auto()  # State leaks across boundaries
    NAMESPACE_COLLISION = auto()  # Insufficient namespace separation

    # Operator-path
    OPERATOR_WORKFLOW_INVALIDITY = auto()  # Unrealistic human sequences
    REVIEW_PATH_MISMATCH = auto()  # Authority/review misalignment

    # Diagnostic self-integrity
    MEASUREMENT_BLIND_SPOT = auto()  # No observable for failure class
    FALSE_PROOF_SURFACE = auto()  # Weak property treated as strong
    ORACLE_UNSOUNDNESS = auto()  # Incomplete test oracle
    REPAIR_RECOMMENDATION_UNSOUNDNESS = auto()  # Fix increases debt


@dataclass
class MetaPathology:
    """A meta-architectural pathology."""

    pathology_type: MetaPathologyType
    location: str
    message: str
    severity: str  # "critical", "high", "medium", "low"
    details: dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    invariant_violated: str = ""


class SemanticIntegrityDetector:
    """
    Detects failures of meaning.

    The repo may execute correctly while the meanings of its terms drift.
    """

    # Critical terms that must have consistent meanings
    CRITICAL_TERMS = {
        "status": ["runtime_liveness", "structural_validity", "health_check"],
        "healthy": ["service_up", "invariants_pass", "all_checks_ok"],
        "mode": ["cli_flag", "feature_set", "operation_mode"],
        "ready": ["initialized", "built", "connected", "admissible"],
        "valid": ["parses", "type_checks", "invariants_hold"],
        "active": ["running", "enabled", "configured"],
    }

    # Known semantic aliases that should be controlled
    SEMANTIC_ALIASES = {
        "workflow": ["recipe", "flow", "job", "task", "session", "pipeline"],
        "package": ["module", "distribution", "artifact", "bundle"],
        "status": ["health", "readiness", "validity", "enabled"],
        "config": ["settings", "options", "parameters", "preferences"],
        "handler": ["processor", "consumer", "listener", "callback"],
    }

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> list[MetaPathology]:
        """Detect semantic integrity problems."""
        pathologies = []
        pathologies.extend(self._detect_ontology_drift())
        pathologies.extend(self._detect_semantic_alias_explosion())
        pathologies.extend(self._detect_false_equivalence())
        return pathologies

    def _detect_ontology_drift(self) -> list[MetaPathology]:
        """
        Detect when the same word means different things in different layers.

        Examples:
        - "status" means runtime liveness in one place and structural validity elsewhere
        - "healthy" means "service up" in ops, but "all hard invariants pass" in code
        """
        pathologies = []

        # Scan for term definitions in code and docs
        term_usages: dict[str, list[tuple[str, str]]] = {term: [] for term in self.CRITICAL_TERMS}

        # Check Python files for docstrings and comments
        for py_file in self.repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for term in self.CRITICAL_TERMS:
                    # Look for term in docstrings, comments, and variable names
                    patterns = [
                        rf'"""[^"]*\b{term}\b[^"]*"""',  # Docstring
                        rf"'''[^']*\b{term}\b[^']*'''",  # Docstring
                        rf'#.*\b{term}\b',  # Comment
                        rf'{term}_\w+',  # Variable name
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches[:3]:  # Limit to first 3
                            term_usages[term].append((str(py_file), match[:50]))
            except Exception:
                continue

        # Check markdown docs
        for md_file in self.repo_path.rglob("*.md"):
            try:
                content = md_file.read_text()
                for term in self.CRITICAL_TERMS:
                    if re.search(rf'\b{term}\b', content, re.IGNORECASE):
                        context = re.search(rf'.{{0,30}}\b{term}\b.{{0,30}}', content, re.IGNORECASE)
                        if context:
                            term_usages[term].append((str(md_file), context.group()))
            except Exception:
                continue

        # Detect drift: same term used in multiple files with potentially different meanings
        for term, usages in term_usages.items():
            if len(usages) >= 3:
                # Check if contexts suggest different meanings
                contexts = [usage[1].lower() for usage in usages]
                # Check for divergent contexts
                has_runtime_context = any(kw in ctx for ctx in contexts for kw in ["runtime", "server", "service", "up", "down"])
                has_structural_context = any(kw in ctx for ctx in contexts for kw in ["structural", "validity", "invariant", "check"])

                if has_runtime_context and has_structural_context:
                    pathologies.append(
                        MetaPathology(
                            pathology_type=MetaPathologyType.ONTOLOGY_DRIFT,
                            location=term,
                            message=f"Term '{term}' appears to have divergent meanings: "
                                    f"runtime context ({has_runtime_context}) vs "
                                    f"structural context ({has_structural_context})",
                            severity="high",
                            details={"usages": usages[:5], "possible_meanings": self.CRITICAL_TERMS.get(term, [])},
                            remediation=f"Define '{term}' explicitly in architecture glossary or split into disambiguated terms",
                            invariant_violated="I_ontology",
                        )
                    )

        return pathologies

    def _detect_semantic_alias_explosion(self) -> list[MetaPathology]:
        """
        Detect uncontrolled synonyms for architecture-critical concepts.

        Examples:
        - workflow / recipe / flow / job / task / session (uncontrolled)
        - package / module / distribution / artifact (unmapped)
        """
        pathologies = []

        # Count occurrences of each alias group
        for concept, aliases in self.SEMANTIC_ALIASES.items():
            alias_counts: dict[str, int] = {}

            # Scan Python files
            for py_file in self.repo_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    for alias in aliases:
                        count = len(re.findall(rf'\b{alias}\b', content, re.IGNORECASE))
                        if count > 0:
                            alias_counts[alias] = alias_counts.get(alias, 0) + count
                except Exception:
                    continue

            # Check for uncontrolled explosion
            if len(alias_counts) >= 3:
                # Check if there's a controlled mapping
                has_registry = self._has_semantic_registry(concept, aliases)

                if not has_registry:
                    pathologies.append(
                        MetaPathology(
                            pathology_type=MetaPathologyType.SEMANTIC_ALIAS_EXPLOSION,
                            location=f"concept:{concept}",
                            message=f"Concept '{concept}' has {len(alias_counts)} uncontrolled aliases: "
                                    f"{list(alias_counts.keys())[:5]}",
                            severity="medium",
                            details={"alias_counts": alias_counts, "concept": concept},
                            remediation=f"Create semantic registry mapping all '{concept}' aliases to canonical terms",
                            invariant_violated="I_semantic_alias",
                        )
                    )

        return pathologies

    def _detect_false_equivalence(self) -> list[MetaPathology]:
        """
        Detect when two things are treated as equivalent when they are not.

        Examples:
        - "initialized" treated as equivalent to "loaded"
        - "build succeeds" treated as equivalent to "artifact valid"
        - "documented" treated as equivalent to "enforced"
        """
        pathologies = []

        # Known false equivalence patterns
        equivalence_patterns = [
            ("initialized", "loaded", "Initialization does not imply full load"),
            ("exported", "publicly_supported", "Export ≠ public API contract"),
            ("documented", "enforced", "Documentation does not enforce behavior"),
            ("build_succeeds", "artifact_valid", "Build success ≠ artifact validity"),
            ("parses", "type_checks", "Parsing does not imply type safety"),
        ]

        for term_a, term_b, explanation in equivalence_patterns:
            # Look for patterns suggesting equivalence
            for py_file in self.repo_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    # Check for compound conditions or assignments suggesting equivalence
                    patterns = [
                        rf'{term_a}.*{term_b}',  # Sequential usage
                        rf'{term_b}.*{term_a}',  # Reverse order
                        rf'{term_a}\s*=\s*{term_b}',  # Assignment
                        rf'{term_b}\s*=\s*{term_a}',  # Reverse assignment
                    ]

                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            pathologies.append(
                                MetaPathology(
                                    pathology_type=MetaPathologyType.FALSE_SEMANTIC_EQUIVALENCE,
                                    location=str(py_file),
                                    message=f"Potential false equivalence: '{term_a}' and '{term_b}' "
                                            f"used in ways suggesting equivalence. {explanation}",
                                    severity="high",
                                    details={"term_a": term_a, "term_b": term_b, "pattern": pattern},
                                    remediation="Explicitly distinguish states or add intermediate validation",
                                    invariant_violated="I_false_equivalence",
                                )
                            )
                            break  # One per file is enough
                except Exception:
                    continue

        return pathologies

    def _has_semantic_registry(self, concept: str, aliases: list[str]) -> bool:
        """Check if a semantic registry exists for this concept."""
        # Look for registry files
        registry_patterns = [
            "semantic_registry*",
            "glossary*",
            "terminology*",
            "concepts*",
        ]
        for pattern in registry_patterns:
            for file in self.repo_path.glob(pattern):
                try:
                    content = file.read_text()
                    if concept in content and any(alias in content for alias in aliases[:2]):
                        return True
                except Exception:
                    continue
        return False


class TemporalOrderDetector:
    """
    Detects failures of causal ordering.

    Operations are only valid in a strict partial order, but the architecture
    models them as independent.
    """

    # Required operation orderings (a must precede b)
    REQUIRED_ORDERINGS = [
        ("migrate", "deploy", "Database migrations must precede deployment"),
        ("build", "codegen_publish", "Build must precede codegen publish"),
        ("schema_sync", "server_start", "Schema sync must precede server start"),
        ("policy_load", "mode_enable", "Policy load must precede mode enable"),
        ("protocol_support", "client_rollout", "Server protocol support must precede client rollout"),
    ]

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> list[MetaPathology]:
        """Detect temporal-order architecture failures."""
        pathologies = []
        pathologies.extend(self._detect_partial_order_failure())
        pathologies.extend(self._detect_temporal_plane_skew())
        pathologies.extend(self._detect_eventuality_traps())
        return pathologies

    def _detect_partial_order_failure(self) -> list[MetaPathology]:
        """
        Detect missing explicit causal ordering.

        Examples:
        - migrate before deploy (not enforced)
        - build before codegen publish (not represented)
        - start server after schema sync (not checked)
        """
        pathologies = []

        # Check CI/CD pipelines for ordering
        ci_files = list(self.repo_path.glob(".github/workflows/*.yml"))
        ci_files.extend(self.repo_path.glob(".gitlab-ci.yml"))
        ci_files.extend(self.repo_path.glob("Jenkinsfile"))

        for ci_file in ci_files:
            try:
                content = ci_file.read_text()

                # Check for required orderings
                for op_a, op_b, explanation in self.REQUIRED_ORDERINGS:
                    has_a = op_a.replace("_", "") in content.lower() or op_a in content
                    has_b = op_b.replace("_", "") in content.lower() or op_b in content

                    if has_a and has_b:
                        # Check if there's explicit ordering
                        has_ordering = self._check_explicit_ordering(content, op_a, op_b)

                        if not has_ordering:
                            pathologies.append(
                                MetaPathology(
                                    pathology_type=MetaPathologyType.PARTIAL_ORDER_FAILURE,
                                    location=str(ci_file),
                                    message=f"Operations '{op_a}' and '{op_b}' present but "
                                            f"no explicit ordering enforced. {explanation}",
                                    severity="high",
                                    details={"operation_a": op_a, "operation_b": op_b},
                                    remediation=f"Add explicit dependency: {op_a} must precede {op_b}",
                                    invariant_violated="I_partial_order",
                                )
                            )
            except Exception:
                continue

        return pathologies

    def _detect_temporal_plane_skew(self) -> list[MetaPathology]:
        """
        Detect when control, data, execution, and observation planes lag.

        Examples:
        - deployment updated, docs not updated
        - runtime updated, observability not updated
        - migration completed, status plane reports old state
        """
        pathologies = []

        # Check for plane synchronization mechanisms
        planes = {
            "control": ["deployment", "config", "policy"],
            "data": ["schema", "migration", "state"],
            "execution": ["runtime", "server", "worker"],
            "observation": ["metrics", "logs", "status", "health"],
        }

        # Look for skew indicators
        for plane_name, plane_keywords in planes.items():
            # Check if plane has update mechanisms
            has_update_mechanism = self._check_plane_update_mechanism(plane_keywords)

            if not has_update_mechanism:
                pathologies.append(
                    MetaPathology(
                        pathology_type=MetaPathologyType.TEMPORAL_PLANE_SKEW,
                        location=f"plane:{plane_name}",
                        message=f"{plane_name.capitalize()} plane lacks explicit update/sync mechanism. "
                                f"May lag other planes causing skew.",
                        severity="medium",
                        details={"plane": plane_name, "keywords": plane_keywords},
                        remediation=f"Add bounded skew constraints and sync mechanisms for {plane_name} plane",
                        invariant_violated="I_plane_skew",
                    )
                )

        return pathologies

    def _detect_eventuality_traps(self) -> list[MetaPathology]:
        """
        Detect unbounded "eventually" consistency.

        Examples:
        - "rollout eventually converges" (no bound)
        - "caches eventually refresh" (no timeout)
        - "metrics eventually appear" (no SLA)
        """
        pathologies = []

        # Look for "eventually" without bounds
        for py_file in self.repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Find eventually patterns without bounds
                eventually_patterns = [
                    r'eventually.*?converge',
                    r'eventually.*?refresh',
                    r'eventually.*?appear',
                    r'eventually.*?catch',
                    r'eventually.*?align',
                ]

                for pattern in eventually_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Check if there's a bound nearby
                        context_start = max(0, match.start() - 200)
                        context_end = min(len(content), match.end() + 200)
                        context = content[context_start:context_end]

                        has_bound = any(
                            kw in context.lower()
                            for kw in ["timeout", "deadline", "bound", "limit", "seconds", "ms"]
                        )

                        if not has_bound:
                            pathologies.append(
                                MetaPathology(
                                    pathology_type=MetaPathologyType.EVENTUAL_VALIDITY_TRAP,
                                    location=str(py_file),
                                    message=f"Unbounded 'eventually' pattern found: '{match.group()}'. "
                                            f"No convergence bound specified.",
                                    severity="high",
                                    details={"pattern": match.group(), "context": context[:100]},
                                    remediation="Add explicit bounded convergence: timeout or max attempts",
                                    invariant_violated="I_eventuality",
                                )
                            )
            except Exception:
                continue

        return pathologies

    def _check_explicit_ordering(self, content: str, op_a: str, op_b: str) -> bool:
        """Check if explicit ordering exists between two operations."""
        # Look for dependency keywords
        dep_patterns = [
            rf'needs.*{op_a}',
            rf'depends.*{op_a}',
            rf'requires.*{op_a}',
            rf'after.*{op_a}',
            rf'{op_a}.*before',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in dep_patterns)

    def _check_plane_update_mechanism(self, keywords: list[str]) -> bool:
        """Check if a plane has update/sync mechanisms."""
        # Look for sync/update mechanisms in common files
        mechanism_files = [
            "sync.py", "update.py", "refresh.py", "watch.py",
            "reconcile.py", "poll.py", "subscribe.py",
        ]

        for filename in mechanism_files:
            for file in self.repo_path.rglob(filename):
                try:
                    content = file.read_text()
                    if any(kw in content for kw in keywords):
                        return True
                except Exception:
                    continue

        return False


class ProvenanceTrustDetector:
    """
    Detects failures of trust and provenance.

    A repo can be correct in structure and still invalid because
    you cannot trust what produced it.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> list[MetaPathology]:
        """Detect provenance and trust failures."""
        pathologies = []
        pathologies.extend(self._detect_provenance_gap())
        pathologies.extend(self._detect_supply_chain_trust_failure())
        pathologies.extend(self._detect_reproducibility_failure())
        return pathologies

    def _detect_provenance_gap(self) -> list[MetaPathology]:
        """
        Detect unknown artifact origins.

        Examples:
        - Generated file with unknown generator version
        - Build artifact without reproducible source mapping
        - Copied config templates with no authority
        """
        pathologies = []

        # Check for generated files without provenance markers
        for gen_file in self.repo_path.rglob("*.py"):
            try:
                content = gen_file.read_text()

                # Check if it looks generated
                is_generated = any(
                    marker in content[:500]
                    for marker in ["generated", "auto-generated", "@generated", "# GENERATED"]
                )

                if is_generated:
                    # Check for provenance info
                    has_provenance = any(
                        marker in content[:1000]
                        for marker in [
                            "generator:", "tool:", "version:", "source:",
                            "provenance", "derived from", "created by",
                        ]
                    )

                    if not has_provenance:
                        pathologies.append(
                            MetaPathology(
                                pathology_type=MetaPathologyType.PROVENANCE_GAP,
                                location=str(gen_file),
                                message=f"Generated file lacks provenance information. "
                                        f"Cannot trace origin or verify authority.",
                                severity="medium",
                                details={"file": str(gen_file)},
                                remediation="Add provenance header: generator, version, source mapping",
                                invariant_violated="I_provenance",
                            )
                        )
            except Exception:
                continue

        return pathologies

    def _detect_supply_chain_trust_failure(self) -> list[MetaPathology]:
        """
        Detect semantically untrusted dependencies.

        Examples:
        - Hidden plugin source
        - Transitive dependency introduces runtime path
        - Build tool version changes emitted artifacts
        """
        pathologies = []

        # Check requirements files for version pinning
        req_files = list(self.repo_path.glob("requirements*.txt"))
        req_files.extend(self.repo_path.glob("pyproject.toml"))

        for req_file in req_files:
            try:
                content = req_file.read_text()

                # Check for unpinned dependencies (trust issue)
                unpinned = re.findall(r'^[a-zA-Z][a-zA-Z0-9_-]+$', content, re.MULTILINE)

                if len(unpinned) > 5:
                    pathologies.append(
                        MetaPathology(
                            pathology_type=MetaPathologyType.SUPPLY_CHAIN_SEMANTIC_TRUST_FAILURE,
                            location=str(req_file),
                            message=f"{len(unpinned)} unpinned dependencies found. "
                                    f"Semantic behavior may change with version updates.",
                            severity="medium",
                            details={"unpinned_count": len(unpinned), "examples": unpinned[:5]},
                            remediation="Pin dependency versions and add hash verification",
                            invariant_violated="I_supply_semantic",
                        )
                    )
            except Exception:
                continue

        return pathologies

    def _detect_reproducibility_failure(self) -> list[MetaPathology]:
        """
        Detect non-deterministic builds.

        Examples:
        - Timestamps in generated artifacts
        - Random seeds not fixed
        - Environment-dependent outputs
        """
        pathologies = []

        # Check for reproducibility indicators
        indicators = [
            ("datetime.now()", "Non-deterministic timestamp in output"),
            ("random.randint", "Unseeded random usage"),
            ("os.environ", "Environment-dependent behavior"),
            ("uuid.uuid4()", "Non-deterministic UUID generation"),
        ]

        for pattern, explanation in indicators:
            for py_file in self.repo_path.rglob("*.py"):
                try:
                    content = py_file.read_text()

                    if pattern in content:
                        # Check if it's in a build/codegen context
                        is_build_context = any(
                            ctx in content[:2000]
                            for ctx in ["build", "generate", "codegen", "compile", "package"]
                        )

                        if is_build_context:
                            pathologies.append(
                                MetaPathology(
                                    pathology_type=MetaPathologyType.REPRODUCIBILITY_FAILURE,
                                    location=str(py_file),
                                    message=f"Potential reproducibility issue: {explanation}. "
                                            f"Found '{pattern}' in build context.",
                                    severity="medium",
                                    details={"pattern": pattern, "explanation": explanation},
                                    remediation=f"Make {pattern} deterministic or add to reproducibility exceptions",
                                    invariant_violated="I_reproducible",
                                )
                            )
                            break  # One per file
                except Exception:
                    continue

        return pathologies


class RecoveryContainmentDetector:
    """
    Detects failures of recovery and containment.

    The architecture can fail, but there may be no declared valid path back to safety.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> list[MetaPathology]:
        """Detect recovery and containment failures."""
        pathologies = []
        pathologies.extend(self._detect_recovery_path_incompleteness())
        pathologies.extend(self._detect_non_idempotent_recovery())
        pathologies.extend(self._detect_blast_containment_failure())
        return pathologies

    def _detect_recovery_path_incompleteness(self) -> list[MetaPathology]:
        """
        Detect missing recovery paths.

        Examples:
        - Rollback restores code but not schema
        - Disable flag restores mode but not cache state
        - Revert commit restores source but not artifact pipeline
        """
        pathologies = []

        # Check for recovery documentation
        recovery_docs = ["RECOVERY.md", "ROLLBACK.md", "INCIDENT.md", "RUNBOOK.md"]
        has_recovery_doc = any((self.repo_path / doc).exists() for doc in recovery_docs)

        if not has_recovery_doc:
            # Check if there are failure-prone components
            failure_prone = self._has_failure_prone_components()

            if failure_prone:
                pathologies.append(
                    MetaPathology(
                        pathology_type=MetaPathologyType.RECOVERY_PATH_INCOMPLETENESS,
                        location=str(self.repo_path),
                        message="No recovery documentation found, but failure-prone components detected. "
                                "No declared path back to safety.",
                        severity="high",
                        details={"failure_prone": failure_prone},
                        remediation="Create RECOVERY.md with rollback procedures for each failure class",
                        invariant_violated="I_recovery",
                    )
                )

        return pathologies

    def _detect_non_idempotent_recovery(self) -> list[MetaPathology]:
        """
        Detect recovery actions that change state each time run.

        Examples:
        - Rerunning migration mutates state incorrectly
        - Rerunning bootstrap duplicates artifacts
        - Rerunning rollback leaves partial state
        """
        pathologies = []

        # Check migration scripts for idempotency markers
        for mig_file in self.repo_path.rglob("migrations/*.py"):
            try:
                content = mig_file.read_text()

                # Check for idempotency indicators
                has_idempotency = any(
                    marker in content
                    for marker in ["IF NOT EXISTS", "idempotent", "skip if", "check if"]
                )

                if not has_idempotency:
                    # Check if it has destructive operations
                    destructive = ["DROP", "DELETE", "ALTER", "UPDATE"]
                    has_destructive = any(op in content.upper() for op in destructive)

                    if has_destructive:
                        pathologies.append(
                            MetaPathology(
                                pathology_type=MetaPathologyType.NON_IDEMPOTENT_RECOVERY,
                                location=str(mig_file),
                                message="Migration lacks idempotency markers but has destructive operations. "
                                        "Rerunning may corrupt state.",
                                severity="high",
                                details={"file": str(mig_file)},
                                remediation="Add idempotency checks: skip if already applied",
                                invariant_violated="I_recovery_idempotent",
                            )
                        )
            except Exception:
                continue

        return pathologies

    def _detect_blast_containment_failure(self) -> list[MetaPathology]:
        """
        Detect failures that propagate too widely.

        Examples:
        - One status bug affects rollout gating across repos
        - One shared schema drift breaks multiple services
        - One package version bump invalidates whole fleet
        """
        pathologies = []

        # Check for shared state without containment
        shared_files = [
            "config.py", "settings.py", "constants.py",
            "shared.py", "common.py", "utils.py",
        ]

        for shared_file in shared_files:
            for file in self.repo_path.rglob(shared_file):
                try:
                    content = file.read_text()

                    # Count dependents (imports)
                    import_count = 0
                    for py_file in self.repo_path.rglob("*.py"):
                        try:
                            py_content = py_file.read_text()
                            module_name = str(file.relative_to(self.repo_path)).replace("/", ".").replace(".py", "")
                            if f"from {module_name}" in py_content or f"import {module_name.split('.')[-1]}" in py_content:
                                import_count += 1
                                if import_count > 20:
                                    break
                        except Exception:
                            continue

                    if import_count > 10:
                        # Check for containment mechanisms
                        has_containment = any(
                            marker in content
                            for marker in ["version", "scope", "boundary", "isolation"]
                        )

                        if not has_containment:
                            pathologies.append(
                                MetaPathology(
                                    pathology_type=MetaPathologyType.BLAST_CONTAINMENT_FAILURE,
                                    location=str(file),
                                    message=f"Shared file has {import_count} dependents but no blast containment. "
                                            f"Changes may propagate too widely.",
                                    severity="medium",
                                    details={"dependents": import_count, "file": str(file)},
                                    remediation="Add versioning, scoping, or circuit breakers for blast containment",
                                    invariant_violated="I_blast",
                                )
                            )
                            break
                except Exception:
                    continue

        return pathologies

    def _has_failure_prone_components(self) -> bool:
        """Check if repo has components prone to failure."""
        indicators = [
            "server", "api", "worker", "daemon", "service",
            "database", "migration", "deployment", "rollout",
        ]

        for indicator in indicators:
            for py_file in self.repo_path.rglob("*.py"):
                if indicator in py_file.name.lower():
                    return True

        return False


class DiagnosticSelfIntegrityDetector:
    """
    Detects failures of the diagnostic system itself.

    The doctor can be wrong - this validates the diagnostic architecture.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.detected_pathologies: list[MetaPathology] = []

    def detect(self) -> list[MetaPathology]:
        """Detect diagnostic self-integrity failures."""
        pathologies = []
        pathologies.extend(self._detect_measurement_blind_spots())
        pathologies.extend(self._detect_false_proof_surface())
        pathologies.extend(self._detect_oracle_unsoundness())
        pathologies.extend(self._detect_repair_unsoundness())
        return pathologies

    def _detect_measurement_blind_spots(self) -> list[MetaPathology]:
        """
        Detect failure classes with no observables.

        The doctor has no observable for a failure class.
        """
        pathologies = []

        # Check what failure classes we should detect but might miss
        # This is a self-check: do we have detectors for all critical invariants?

        critical_invariants = [
            ("I_authority_order", "AuthorityOrderDetector"),
            ("I_boundary", "BoundaryDetector"),
            ("I_layer_separation", "LayerLeakageDetector"),
            ("I_bootstrap", "BootstrapPathDetector"),
            ("I_provenance", "ProvenanceTrustDetector"),
        ]

        for invariant, expected_detector in critical_invariants:
            # Check if detector exists
            detector_exists = self._check_detector_exists(expected_detector)

            if not detector_exists:
                pathologies.append(
                    MetaPathology(
                        pathology_type=MetaPathologyType.MEASUREMENT_BLIND_SPOT,
                        location=f"invariant:{invariant}",
                        message=f"Critical invariant {invariant} may lack sufficient detector. "
                                f"Expected {expected_detector} not found.",
                        severity="critical",
                        details={"invariant": invariant, "expected_detector": expected_detector},
                        remediation=f"Add or verify detector for {invariant}",
                        invariant_violated="I_measurement_complete",
                    )
                )

        return pathologies

    def _detect_false_proof_surface(self) -> list[MetaPathology]:
        """
        Detect weak properties treated as strong.

        Examples:
        - build passes ⇒ artifact valid (weak proof)
        - initialized ⇒ ready (false implication)
        - docs compile ⇒ docs accurate (unrelated)
        """
        pathologies = []

        # Check for weak proofs in CI/CD
        ci_files = list(self.repo_path.glob(".github/workflows/*.yml"))

        for ci_file in ci_files:
            try:
                content = ci_file.read_text()

                # Check for common false proof patterns
                false_proofs = [
                    ("build passes", "artifact valid", "Build success does not imply validity"),
                    ("tests pass", "system correct", "Test coverage may be incomplete"),
                    ("lint clean", "no bugs", "Linting does not catch logic errors"),
                    ("docs built", "docs accurate", "Build does not verify content"),
                ]

                for weak, claimed_strong, explanation in false_proofs:
                    if weak.replace(" ", "_") in content or weak in content:
                        if claimed_strong.replace(" ", "_") in content or claimed_strong in content:
                            pathologies.append(
                                MetaPathology(
                                    pathology_type=MetaPathologyType.FALSE_PROOF_SURFACE,
                                    location=str(ci_file),
                                    message=f"Potential false proof: '{weak}' used to prove '{claimed_strong}'. "
                                            f"{explanation}.",
                                    severity="high",
                                    details={"weak": weak, "claimed_strong": claimed_strong},
                                    remediation=f"Strengthen proof or weaken claim. Add explicit verification for {claimed_strong}",
                                    invariant_violated="I_proof_strength",
                                )
                            )
            except Exception:
                continue

        return pathologies

    def _detect_oracle_unsoundness(self) -> list[MetaPathology]:
        """
        Detect incomplete test oracles.

        The doctor's test oracle is incomplete or mode-blind.
        """
        pathologies = []

        # Check test coverage of critical modes
        test_files = list(self.repo_path.rglob("test*.py"))
        test_files.extend(self.repo_path.rglob("*_test.py"))

        if test_files:
            # Check for mode coverage
            modes = ["dev", "prod", "test", "staging", "ci"]
            mode_coverage = {mode: False for mode in modes}

            for test_file in test_files:
                try:
                    content = test_file.read_text()
                    for mode in modes:
                        if mode in content.lower():
                            mode_coverage[mode] = True
                except Exception:
                    continue

            uncovered_modes = [m for m, covered in mode_coverage.items() if not covered]

            if len(uncovered_modes) >= 2:
                pathologies.append(
                    MetaPathology(
                        pathology_type=MetaPathologyType.ORACLE_UNSOUNDNESS,
                        location="test_suite",
                        message=f"Test oracle may be mode-blind. Uncovered modes: {uncovered_modes}. "
                                f"Behavior in these modes may differ.",
                        severity="medium",
                        details={"uncovered_modes": uncovered_modes, "mode_coverage": mode_coverage},
                        remediation="Add tests covering all critical modes: dev, prod, ci, etc.",
                        invariant_violated="I_oracle_sound",
                    )
                )

        return pathologies

    def _detect_repair_unsoundness(self) -> list[MetaPathology]:
        """
        Detect repairs that increase architecture debt.

        Recommended repairs are not monotone with respect to protected invariants.
        """
        pathologies = []

        # This is a self-check: do our repair suggestions respect invariants?
        # We need to check if repair_bridge.py exists and validate its logic

        repair_bridge_path = self.repo_path / "amos_brain" / "repair_bridge.py"
        if repair_bridge_path.exists():
            try:
                content = repair_bridge_path.read_text()

                # Check if repairs validate invariants
                checks_invariants = "invariant" in content.lower() and "check" in content.lower()
                monotone = "monotone" in content.lower() or "preserves" in content.lower()

                if not checks_invariants or not monotone:
                    pathologies.append(
                        MetaPathology(
                            pathology_type=MetaPathologyType.REPAIR_RECOMMENDATION_UNSOUNDNESS,
                            location=str(repair_bridge_path),
                            message="Repair synthesis may not verify invariant preservation. "
                                    "Repairs could increase architecture debt.",
                            severity="high",
                            details={"checks_invariants": checks_invariants, "monotone": monotone},
                            remediation="Add explicit invariant checks before and after repair suggestions",
                            invariant_violated="I_repair_sound",
                        )
                    )
            except Exception:
                pass

        return pathologies

    def _check_detector_exists(self, detector_name: str) -> bool:
        """Check if a detector class exists in the codebase."""
        # Check in arch_pathologies.py
        arch_path = self.repo_path / "repo_doctor" / "arch_pathologies.py"
        if arch_path.exists():
            try:
                content = arch_path.read_text()
                return f"class {detector_name}" in content
            except Exception:
                pass

        # Check in meta_pathologies.py (this file)
        meta_path = self.repo_path / "repo_doctor" / "meta_pathologies.py"
        if meta_path.exists():
            try:
                content = meta_path.read_text()
                return f"class {detector_name}" in content
            except Exception:
                pass

        return False


class MetaPathologyEngine:
    """
    Master engine for meta-architectural pathologies.

    Coordinates all meta-level detectors.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.detectors = {
            "semantic_integrity": SemanticIntegrityDetector(repo_path),
            "temporal_order": TemporalOrderDetector(repo_path),
            "provenance_trust": ProvenanceTrustDetector(repo_path),
            "recovery_containment": RecoveryContainmentDetector(repo_path),
            "diagnostic_self": DiagnosticSelfIntegrityDetector(repo_path),
        }

    def detect_all(self) -> dict[str, list[MetaPathology]]:
        """Run all meta-pathology detectors."""
        results = {}
        for name, detector in self.detectors.items():
            try:
                results[name] = detector.detect()
            except Exception as e:
                results[name] = [
                    MetaPathology(
                        pathology_type=MetaPathologyType.MEASUREMENT_BLIND_SPOT,
                        location=f"detector:{name}",
                        message=f"Detector failed: {e}",
                        severity="medium",
                    )
                ]
        return results

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all meta-pathologies."""
        results = self.detect_all()

        total = sum(len(p) for p in results.values())
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_type: dict[str, int] = {}

        for detector_results in results.values():
            for pathology in detector_results:
                by_severity[pathology.severity] = by_severity.get(pathology.severity, 0) + 1
                ptype = pathology.pathology_type.name
                by_type[ptype] = by_type.get(ptype, 0) + 1

        return {
            "total": total,
            "by_detector": {k: len(v) for k, v in results.items()},
            "by_severity": by_severity,
            "by_type": by_type,
        }


def get_meta_pathology_engine(repo_path: str | Path | None = None) -> MetaPathologyEngine:
    """Factory function to get meta-pathology engine instance."""
    return MetaPathologyEngine(repo_path or ".")
