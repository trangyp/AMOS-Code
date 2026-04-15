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
    """18 dimensions of repository state space (Ω∞∞∞∞∞).

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
            StateDimension.SYNTAX,
            StateDimension.IMPORT,
            StateDimension.TYPE,
            StateDimension.API,
            StateDimension.ENTRYPOINT,
            StateDimension.PACKAGING,
            StateDimension.PERSISTENCE,
            StateDimension.STATUS,
            StateDimension.SECURITY,
        ]
