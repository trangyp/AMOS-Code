"""
Repo Doctor Ω∞∞∞∞∞ - State Basis

The 15 basis states for repository state space per Ω∞∞∞∞∞ specification:
H_repo = H_S ⊗ H_I ⊗ H_Ty ⊗ H_A ⊗ H_E ⊗ H_Pk ⊗ H_Rt ⊗ H_Ps ⊗ H_St ⊗ H_T ⊗ H_D ⊗ H_Sec ⊗ H_H ⊗ H_Gc ⊗ H_Env

|S⟩   syntax            |I⟩   imports        |Ty⟩  types/signatures
|A⟩   API contracts      |E⟩   entrypoints    |Pk⟩  packaging
|Rt⟩  runtime            |Ps⟩  persistence    |St⟩  status
|T⟩   tests              |D⟩   docs           |Sec⟩ security
|H⟩   history            |Gc⟩  generated code |Env⟩ environment
"""

from __future__ import annotations

from enum import Enum


class StateDimension(Enum):
    """
    18 dimensions of repository state space (Ω∞∞∞∞∞).

    Original 12 + 6 Phase 1-2 additions.
    """

    # Original 12 dimensions
    SYNTAX = "syntax"  # |S⟩ parse integrity
    IMPORT = "import"  # |I⟩ import resolution (singular form for observables)
    IMPORTS = "imports"  # |I⟩ import resolution (plural compat)
    TYPE = "type"  # |T⟩ type/signature integrity (singular)
    TYPES = "types"  # |T⟩ type/signature integrity (plural)
    API = "api"  # |A⟩ public API contract integrity
    ENTRYPOINT = "entrypoint"  # |E⟩ entrypoint / launcher integrity
    PACKAGING = "packaging"  # |Pk⟩ packaging / build / distribution integrity
    RUNTIME = "runtime"  # |Rt⟩ runtime behavior integrity
    PERSISTENCE = "persistence"  # |Ps⟩ persistence / schema / state integrity
    STATUS = "status"  # |St⟩ status-truth integrity
    TEST = "test"  # |T⟩ test / oracle integrity
    DOCS = "docs"  # |D⟩ docs / demos / tutorials integrity
    SECURITY = "security"  # |Sec⟩ security integrity

    # Temporal and environment surfaces (3)
    HISTORY = "history"  # |H⟩ history / temporal / drift integrity
    GENERATED_CODE = "generated_code"  # |Gc⟩ codegen integrity
    ENVIRONMENT = "environment"  # |Env⟩ environment compatibility integrity

    # Legacy compatibility dimensions
    BUILD = "build"  # |B⟩ build integrity (legacy compat)
    CONFIG = "config"  # |Cfg⟩ config integrity (legacy compat)

    # Architectural invariants dimensions
    ARCHITECTURE = "architecture"  # |Arch⟩ architectural integrity
    HIDDEN_STATE = "hidden_state"  # |Hs⟩ hidden state integrity

    # Phase 3: Control System Dimensions (18 new dimensions)
    # Time and temporal semantics
    CLOCK_SEMANTICS = "clock_semantics"  # |Clk⟩ clock/temporal semantics
    TEMPORAL_ORDER = "temporal_order"  # |Ord⟩ event ordering integrity

    # State and consistency
    CONSISTENCY_MODEL = "consistency_model"  # |Cons⟩ consistency semantics
    CACHE_COHERENCE = "cache_coherence"  # |Cache⟩ cache architecture
    PROVENANCE = "provenance"  # |Prov⟩ data lineage/provenance

    # Identity and security
    IDENTITY_LIFECYCLE = "identity_lifecycle"  # |Id⟩ identity/credential lifecycle
    CAPABILITY_DISCIPLINE = "capability_discipline"  # |Cap⟩ capability discipline

    # Flow control and resilience
    QUEUE_BACKPRESSURE = "queue_backpressure"  # |Queue⟩ queue/retry/backpressure
    FALLBACK_TOPOLOGY = "fallback_topology"  # |Fallback⟩ fallback paths
    IDEMPOTENCY_BOUNDARY = "idempotency_boundary"  # |Idem⟩ idempotency semantics
    CONTROL_LOOP_STABILITY = "control_loop_stability"  # |Ctrl⟩ control loop stability

    # Data lifecycle
    DATA_LINEAGE = "data_lineage"  # |Lineage⟩ data lineage/deletion
    DEPRECATION_LIFECYCLE = "deprecation_lifecycle"  # |Dep⟩ deprecation lifecycle

    # Governance and operations
    FORENSIC_AUDITABILITY = "forensic_auditability"  # |Audit⟩ auditability
    ESCALATION_GRAPH = "escalation_graph"  # |Esc⟩ escalation paths
    FAILURE_DOMAINS = "failure_domains"  # |Iso⟩ failure domain isolation
    NEGATIVE_CAPABILITY = "negative_capability"  # |Neg⟩ forbidden states/transitions
    ARCHITECTURAL_DEBT = "architectural_debt"  # |Debt⟩ architectural debt

    # Additional dimensions for future expansion
    CODE_QUALITY = "code_quality"  # |C⟩ code quality
    MAINTAINABILITY = "maintainability"  # |M⟩ maintainability
    LICENSING = "licensing"  # |L⟩ licensing
    MIGRATION = "migration"  # |Mg⟩ migration integrity
    PERFORMANCE = "performance"  # |Perf⟩ performance
    OBSERVABILITY = "observability"  # |Obs⟩ observability
    SEMANTIC_INTEGRITY = "semantic_integrity"  # |Sem⟩ semantic integrity
    RECOVERY = "recovery"  # |Rec⟩ recovery integrity

    # Phase 4: State Machine and Coexistence Dimensions (25+ new dimensions)
    # State machine architecture
    STATE_MACHINE_INTEGRITY = "state_machine_integrity"  # |SM⟩ state machine correctness
    FORBIDDEN_STATE_REACHABILITY = "forbidden_state_reachability"  # |Fbd⟩ forbidden states
    TRANSITION_LEGALITY = "transition_legality"  # |Trans⟩ transition validity

    # Multi-version coexistence
    MULTIVERSION_COEXISTENCE = "multiversion_coexistence"  # |MV⟩ multi-version safety
    COMPATIBILITY_WINDOW = "compatibility_window"  # |Compat⟩ version window truth
    SPLIT_BRAIN_RESISTANCE = "split_brain_resistance"  # |SB⟩ authority divergence

    # Cutover and coordination
    CUTOVER_INTEGRITY = "cutover_integrity"  # |Cut⟩ dual-read/write safety
    CANARY_SAFETY = "canary_safety"  # |Canary⟩ canary/shadow integrity
    CHANGE_COORDINATION = "change_coordination"  # |Coord⟩ multi-surface coordination

    # Data lifecycle and quality
    DATA_QUALITY = "data_quality"  # |DQ⟩ data quality architecture
    BACKFILL_INTEGRITY = "backfill_integrity"  # |BF⟩ backfill/replay safety
    GARBAGE_COLLECTION = "garbage_collection"  # |GC⟩ GC and tombstone integrity

    # External contracts
    EXTERNAL_CONTRACT = "external_contract"  # |Ext⟩ external dependency contracts
    QUOTA_ARCHITECTURE = "quota_architecture"  # |Quota⟩ rate limit/quota modeling
    VENDOR_SUBSTITUTABILITY = "vendor_substitutability"  # |Vend⟩ vendor exit paths

    # Experimentation and flags
    EXPERIMENT_SAFETY = "experiment_safety"  # |Exp⟩ A/B test safety
    FLAG_LATTICE = "flag_lattice"  # |Flag⟩ feature flag bounds
    MODE_ACTIVATION = "mode_activation"  # |Mode⟩ runtime mode semantics

    # Economic and resources
    ECONOMIC_ENVELOPE = "economic_envelope"  # |Cost⟩ cost/resource budgets
    RESOURCE_COUPLING = "resource_coupling"  # |ResCoup⟩ bottleneck sharing

    # Team and knowledge
    TEAM_TOPOLOGY_FIT = "team_topology_fit"  # |Team⟩ Conway alignment
    KNOWLEDGE_DISTRIBUTION = "knowledge_distribution"  # |KnowDist⟩ knowledge spread
    INCENTIVE_ALIGNMENT = "incentive_alignment"  # |Incent⟩ incentive geometry

    # Exception and override governance
    EXCEPTION_GOVERNANCE = "exception_governance"  # |Exc⟩ emergency bypasses
    OVERRIDE_DECAY = "override_decay"  # |Over⟩ temporary override limits
    HOTFIX_TOPOLOGY = "hotfix_topology"  # |Hot⟩ hotfix safety

    # Compliance and legal
    COMPLIANCE_LIFECYCLE = "compliance_lifecycle"  # |Comp⟩ retention/deletion compliance

    # Epistemic integrity
    EPISTEMIC_INTEGRITY = "epistemic_integrity"  # |Know⟩ evidence/decision quality
    EVIDENCE_FRESHNESS = "evidence_freshness"  # |Fresh⟩ evidence staleness
    EVIDENCE_SCOPE = "evidence_scope"  # |Scope⟩ evidence generalization
    DECISION_RIGHTS = "decision_rights"  # |Rights⟩ decision authority alignment

    # Constitutional and ownership
    CONSTITUTIONAL_INTEGRITY = "constitutional_integrity"  # |Const⟩ constitution adherence
    STATE_OWNERSHIP = "state_ownership"  # |Own⟩ state authority clarity
    ABSENCE_SEMANTICS = "absence_semantics"  # |Abs⟩ "not present" meaning

    # Disaster and resilience
    DISASTER_RECOVERY = "disaster_recovery"  # |DR⟩ DR architecture
    GRACEFUL_DEGRADATION = "graceful_degradation"  # |Grace⟩ degradation paths
    BLAST_CONTAINMENT = "blast_containment"  # |Blast⟩ blast radius limits
    ISOLATION = "isolation"  # |Iso⟩ isolation boundaries

    # Interoperability
    INTEROPERABILITY = "interoperability"  # |Port⟩ cross-system compatibility

    # Phase 5: Lease, Transaction, and Meta-Stability Dimensions (30+ new)
    # Lease and revocation
    LEASE_INTEGRITY = "lease_integrity"  # |Lease⟩ lease semantics
    ZOMBIE_LEASE = "zombie_lease"  # |Zombie⟩ expired lease action
    LEASE_CLOCK_COUPLING = "lease_clock_coupling"  # |LeaseClk⟩ lease/clock skew

    # Transaction boundaries
    TRANSACTION_SCOPE = "transaction_scope"  # |Txn⟩ transaction boundary
    CROSS_PLANE_COMMIT = "cross_plane_commit"  # |XPlane⟩ multi-plane atomicity
    COMPENSATION_CLOSURE = "compensation_closure"  # |Compensate⟩ compensation completeness

    # Saturation and overload
    SATURATION_SAFETY = "saturation_safety"  # |Sat⟩ saturation correctness
    OVERLOAD_POLICY = "overload_policy"  # |Overload⟩ shedding order
    SATURATION_AUTHORITY_DRIFT = "saturation_authority_drift"  # |SatAuth⟩ overload authority shift

    # Hysteresis and state memory
    HYSTERESIS_SAFETY = "hysteresis_safety"  # |Hyst⟩ threshold oscillation
    STATE_MEMORY = "state_memory"  # |StateMem⟩ prior state dependence

    # Symmetry and symmetry breaking
    FALSE_SYMMETRY = "false_symmetry"  # |FalseSym⟩ incorrect interchangeability
    SYMMETRY_BREAKING = "symmetry_breaking"  # |SymBreak⟩ hidden asymmetry

    # Trust domains
    TRUST_DOMAIN_INTEGRITY = "trust_domain_integrity"  # |Trust⟩ trust boundary
    TRUST_TRANSITIVITY = "trust_transitivity"  # |TrustTrans⟩ trust chain validity
    TRUST_CACHE_BLEED = "trust_cache_bleed"  # |TrustCache⟩ cross-domain cache

    # Hermeticity
    BUILD_HERMETICITY = "build_hermeticity"  # |HermBuild⟩ build reproducibility
    TEST_HERMETICITY = "test_hermeticity"  # |HermTest⟩ test isolation
    DOCTOR_HERMETICITY = "doctor_hermeticity"  # |HermDoc⟩ diagnostic purity

    # Impossibility boundaries
    IMPOSSIBILITY_AWARENESS = "impossibility_awareness"  # |Imposs⟩ guarantee feasibility
    IMPOSSIBILITY_HONESTY = "impossibility_honesty"  # |ImpossHonest⟩ tradeoff explicitness

    # Dark-state and nullspace
    DARK_STATE_DETECTABILITY = "dark_state_detectability"  # |Dark⟩ unobserved states
    NULLSPACE_BEHAVIOR = "nullspace_behavior"  # |Null⟩ observational collapse

    # Non-local and global invariants
    NONLOCAL_INVARIANT = "nonlocal_invariant"  # |NonLocal⟩ global safety
    GLOBAL_CONSERVATION = "global_conservation"  # |Conserv⟩ quantity preservation

    # Truth and distributed systems
    TRUTH_ARBITRATION = "truth_arbitration"  # |Truth⟩ authority resolution
    IRREVERSIBILITY_MANAGEMENT = "irreversibility_management"  # |Irrev⟩ irreversible action
    QUIESCENCE_INTEGRITY = "quiescence_integrity"  # |Quiesce⟩ safe stopping

    # Liveness and fairness
    LIVENESS = "liveness"  # |Live⟩ progress guarantee
    FAIRNESS = "fairness"  # |Fair⟩ equitable scheduling
    SCHEDULER_ROBUSTNESS = "scheduler_robustness"  # |Sched⟩ scheduler safety

    # Partition and convergence
    PARTITION_BEHAVIOR = "partition_behavior"  # |Part⟩ partition handling
    CONVERGENCE = "convergence"  # |Conv⟩ eventual consistency
    CAUSAL_ATTRIBUTION = "causal_attribution"  # |Cause⟩ causality tracking

    # Compositional and observer effects
    COMPOSITIONAL_VALIDITY = "compositional_validity"  # |Compose⟩ component composition
    OBSERVER_EFFECT_BOUND = "observer_effect_bound"  # |ObsFx⟩ measurement impact
    ARCHITECTURAL_ENTROPY = "architectural_entropy"  # |Entropy⟩ disorder growth

    # Loss and boundedness
    LOSS_BOUNDEDNESS = "loss_boundedness"  # |Loss⟩ acceptable loss
    SEMANTIC_LOSS = "semantic_loss"  # |SemLoss⟩ meaning preservation

    # Policy and adaptation
    POLICY_PRECEDENCE = "policy_precedence"  # |Policy⟩ rule ordering
    ADAPTIVE_STABILITY = "adaptive_stability"  # |Adapt"> self-regulation


class StateBasis:
    """Basis state management for repository Hilbert space."""

    # Severity weights for Hamiltonian (λk) per Ω∞∞∞∞∞
    WEIGHTS: dict[StateDimension, float] = {
        StateDimension.SYNTAX: 100.0,
        StateDimension.IMPORT: 90.0,
        StateDimension.TYPE: 70.0,
        StateDimension.API: 95.0,
        StateDimension.ENTRYPOINT: 90.0,
        StateDimension.PACKAGING: 90.0,
        StateDimension.RUNTIME: 80.0,
        StateDimension.PERSISTENCE: 70.0,
        StateDimension.STATUS: 65.0,
        StateDimension.TEST: 50.0,
        StateDimension.SECURITY: 100.0,
        StateDimension.DOCS: 35.0,
        StateDimension.HISTORY: 55.0,
        StateDimension.GENERATED_CODE: 60.0,
        StateDimension.ENVIRONMENT: 45.0,
        StateDimension.BUILD: 85.0,
        StateDimension.CONFIG: 70.0,
        StateDimension.ARCHITECTURE: 85.0,
        StateDimension.HIDDEN_STATE: 75.0,
        # Phase 3: Control system dimensions
        StateDimension.CLOCK_SEMANTICS: 90.0,
        StateDimension.TEMPORAL_ORDER: 85.0,
        StateDimension.CONSISTENCY_MODEL: 95.0,
        StateDimension.CACHE_COHERENCE: 80.0,
        StateDimension.PROVENANCE: 75.0,
        StateDimension.IDENTITY_LIFECYCLE: 100.0,
        StateDimension.CAPABILITY_DISCIPLINE: 95.0,
        StateDimension.QUEUE_BACKPRESSURE: 85.0,
        StateDimension.FALLBACK_TOPOLOGY: 90.0,
        StateDimension.IDEMPOTENCY_BOUNDARY: 95.0,
        StateDimension.CONTROL_LOOP_STABILITY: 100.0,
        StateDimension.DATA_LINEAGE: 80.0,
        StateDimension.DEPRECATION_LIFECYCLE: 70.0,
        StateDimension.FORENSIC_AUDITABILITY: 75.0,
        StateDimension.ESCALATION_GRAPH: 85.0,
        StateDimension.FAILURE_DOMAINS: 90.0,
        StateDimension.NEGATIVE_CAPABILITY: 95.0,
        StateDimension.ARCHITECTURAL_DEBT: 60.0,
        # Expansion dimensions
        StateDimension.MIGRATION: 80.0,
        StateDimension.PERFORMANCE: 50.0,
        StateDimension.OBSERVABILITY: 65.0,
        StateDimension.SEMANTIC_INTEGRITY: 90.0,
        StateDimension.RECOVERY: 85.0,
        # Phase 4: State machine and coexistence dimensions
        StateDimension.STATE_MACHINE_INTEGRITY: 95.0,
        StateDimension.FORBIDDEN_STATE_REACHABILITY: 100.0,
        StateDimension.TRANSITION_LEGALITY: 90.0,
        StateDimension.MULTIVERSION_COEXISTENCE: 90.0,
        StateDimension.COMPATIBILITY_WINDOW: 95.0,
        StateDimension.SPLIT_BRAIN_RESISTANCE: 95.0,
        StateDimension.CUTOVER_INTEGRITY: 95.0,
        StateDimension.CANARY_SAFETY: 85.0,
        StateDimension.CHANGE_COORDINATION: 90.0,
        StateDimension.DATA_QUALITY: 85.0,
        StateDimension.BACKFILL_INTEGRITY: 80.0,
        StateDimension.GARBAGE_COLLECTION: 75.0,
        StateDimension.EXTERNAL_CONTRACT: 90.0,
        StateDimension.QUOTA_ARCHITECTURE: 85.0,
        StateDimension.VENDOR_SUBSTITUTABILITY: 70.0,
        StateDimension.EXPERIMENT_SAFETY: 85.0,
        StateDimension.FLAG_LATTICE: 80.0,
        StateDimension.MODE_ACTIVATION: 90.0,
        StateDimension.ECONOMIC_ENVELOPE: 60.0,
        StateDimension.RESOURCE_COUPLING: 85.0,
        StateDimension.TEAM_TOPOLOGY_FIT: 75.0,
        StateDimension.KNOWLEDGE_DISTRIBUTION: 80.0,
        StateDimension.INCENTIVE_ALIGNMENT: 70.0,
        StateDimension.EXCEPTION_GOVERNANCE: 90.0,
        StateDimension.OVERRIDE_DECAY: 85.0,
        StateDimension.HOTFIX_TOPOLOGY: 95.0,
        StateDimension.COMPLIANCE_LIFECYCLE: 80.0,
        StateDimension.EPISTEMIC_INTEGRITY: 85.0,
        StateDimension.EVIDENCE_FRESHNESS: 80.0,
        StateDimension.EVIDENCE_SCOPE: 85.0,
        StateDimension.DECISION_RIGHTS: 90.0,
        StateDimension.CONSTITUTIONAL_INTEGRITY: 95.0,
        StateDimension.STATE_OWNERSHIP: 90.0,
        StateDimension.ABSENCE_SEMANTICS: 85.0,
        StateDimension.DISASTER_RECOVERY: 90.0,
        StateDimension.GRACEFUL_DEGRADATION: 85.0,
        StateDimension.BLAST_CONTAINMENT: 90.0,
        StateDimension.ISOLATION: 90.0,
        StateDimension.INTEROPERABILITY: 80.0,
    }

    # Collapse thresholds (θk) per Ω∞∞∞∞∞
    THRESHOLDS: dict[StateDimension, float] = {
        StateDimension.SYNTAX: 0.95,
        StateDimension.IMPORT: 0.90,
        StateDimension.TYPE: 0.80,
        StateDimension.API: 0.95,
        StateDimension.ENTRYPOINT: 0.90,
        StateDimension.PACKAGING: 0.90,
        StateDimension.RUNTIME: 0.80,
        StateDimension.PERSISTENCE: 0.80,
        StateDimension.STATUS: 0.85,
        StateDimension.TEST: 0.75,
        StateDimension.SECURITY: 0.95,
        StateDimension.DOCS: 0.50,
        StateDimension.HISTORY: 0.60,
        StateDimension.GENERATED_CODE: 0.70,
        StateDimension.ENVIRONMENT: 0.65,
        StateDimension.BUILD: 0.85,
        StateDimension.CONFIG: 0.80,
        StateDimension.ARCHITECTURE: 0.85,
        StateDimension.HIDDEN_STATE: 0.80,
        # Phase 3: Control system thresholds
        StateDimension.CLOCK_SEMANTICS: 0.90,
        StateDimension.TEMPORAL_ORDER: 0.85,
        StateDimension.CONSISTENCY_MODEL: 0.95,
        StateDimension.CACHE_COHERENCE: 0.85,
        StateDimension.PROVENANCE: 0.75,
        StateDimension.IDENTITY_LIFECYCLE: 0.95,
        StateDimension.CAPABILITY_DISCIPLINE: 0.95,
        StateDimension.QUEUE_BACKPRESSURE: 0.85,
        StateDimension.FALLBACK_TOPOLOGY: 0.90,
        StateDimension.IDEMPOTENCY_BOUNDARY: 0.95,
        StateDimension.CONTROL_LOOP_STABILITY: 0.95,
        StateDimension.DATA_LINEAGE: 0.80,
        StateDimension.DEPRECATION_LIFECYCLE: 0.70,
        StateDimension.FORENSIC_AUDITABILITY: 0.75,
        StateDimension.ESCALATION_GRAPH: 0.85,
        StateDimension.FAILURE_DOMAINS: 0.90,
        StateDimension.NEGATIVE_CAPABILITY: 0.90,
        StateDimension.ARCHITECTURAL_DEBT: 0.60,
        # Expansion thresholds
        StateDimension.MIGRATION: 0.85,
        StateDimension.PERFORMANCE: 0.50,
        StateDimension.OBSERVABILITY: 0.70,
        StateDimension.SEMANTIC_INTEGRITY: 0.90,
        StateDimension.RECOVERY: 0.85,
        # Phase 4: State machine and coexistence thresholds
        StateDimension.STATE_MACHINE_INTEGRITY: 0.95,
        StateDimension.FORBIDDEN_STATE_REACHABILITY: 0.99,
        StateDimension.TRANSITION_LEGALITY: 0.90,
        StateDimension.MULTIVERSION_COEXISTENCE: 0.90,
        StateDimension.COMPATIBILITY_WINDOW: 0.95,
        StateDimension.SPLIT_BRAIN_RESISTANCE: 0.95,
        StateDimension.CUTOVER_INTEGRITY: 0.95,
        StateDimension.CANARY_SAFETY: 0.85,
        StateDimension.CHANGE_COORDINATION: 0.90,
        StateDimension.DATA_QUALITY: 0.85,
        StateDimension.BACKFILL_INTEGRITY: 0.80,
        StateDimension.GARBAGE_COLLECTION: 0.75,
        StateDimension.EXTERNAL_CONTRACT: 0.90,
        StateDimension.QUOTA_ARCHITECTURE: 0.85,
        StateDimension.VENDOR_SUBSTITUTABILITY: 0.70,
        StateDimension.EXPERIMENT_SAFETY: 0.85,
        StateDimension.FLAG_LATTICE: 0.80,
        StateDimension.MODE_ACTIVATION: 0.90,
        StateDimension.ECONOMIC_ENVELOPE: 0.60,
        StateDimension.RESOURCE_COUPLING: 0.85,
        StateDimension.TEAM_TOPOLOGY_FIT: 0.75,
        StateDimension.KNOWLEDGE_DISTRIBUTION: 0.80,
        StateDimension.INCENTIVE_ALIGNMENT: 0.70,
        StateDimension.EXCEPTION_GOVERNANCE: 0.90,
        StateDimension.OVERRIDE_DECAY: 0.85,
        StateDimension.HOTFIX_TOPOLOGY: 0.95,
        StateDimension.COMPLIANCE_LIFECYCLE: 0.80,
        StateDimension.EPISTEMIC_INTEGRITY: 0.85,
        StateDimension.EVIDENCE_FRESHNESS: 0.80,
        StateDimension.EVIDENCE_SCOPE: 0.85,
        StateDimension.DECISION_RIGHTS: 0.90,
        StateDimension.CONSTITUTIONAL_INTEGRITY: 0.95,
        StateDimension.STATE_OWNERSHIP: 0.90,
        StateDimension.ABSENCE_SEMANTICS: 0.85,
        StateDimension.DISASTER_RECOVERY: 0.90,
        StateDimension.GRACEFUL_DEGRADATION: 0.85,
        StateDimension.BLAST_CONTAINMENT: 0.90,
        StateDimension.ISOLATION: 0.90,
        StateDimension.INTEROPERABILITY: 0.80,
    }

    @classmethod
    def get_weight(cls, dim: StateDimension) -> float:
        """Get Hamiltonian weight for dimension."""
        return cls.WEIGHTS.get(dim, 50.0)

    @classmethod
    def get_threshold(cls, dim: StateDimension) -> float:
        """Get collapse threshold for dimension."""
        return cls.THRESHOLDS.get(dim, 0.80)

    @classmethod
    def all_dimensions(cls) -> list[StateDimension]:
        """Return all basis dimensions."""
        return list(StateDimension)

    @classmethod
    def hard_fail_dimensions(cls) -> list[StateDimension]:
        """Dimensions that cause hard failure when collapsed."""
        return [
            # Core dimensions (Phase 1-2)
            StateDimension.SYNTAX,
            StateDimension.IMPORT,
            StateDimension.TYPE,
            StateDimension.API,
            StateDimension.ENTRYPOINT,
            StateDimension.PACKAGING,
            StateDimension.PERSISTENCE,
            StateDimension.STATUS,
            StateDimension.SECURITY,
            # Control system dimensions (Phase 3)
            StateDimension.IDENTITY_LIFECYCLE,
            StateDimension.CAPABILITY_DISCIPLINE,
            StateDimension.CONTROL_LOOP_STABILITY,
            StateDimension.NEGATIVE_CAPABILITY,
            # State machine & coexistence dimensions (Phase 4)
            StateDimension.FORBIDDEN_STATE_REACHABILITY,
            StateDimension.SPLIT_BRAIN_RESISTANCE,
            StateDimension.CUTOVER_INTEGRITY,
            StateDimension.CONSTITUTIONAL_INTEGRITY,
            StateDimension.HOTFIX_TOPOLOGY,
        ]
