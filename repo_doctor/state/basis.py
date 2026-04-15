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
    IMPORTS = "imports"  # |I⟩ import resolution (plural form for compatibility)
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
    GENERATED_CODE = "generated_code"  # |Gc⟩ generated code / codegen integrity
    ENVIRONMENT = "environment"  # |Env⟩ environment compatibility integrity

    # Additional dimensions for future expansion
    CODE_QUALITY = "code_quality"  # |C⟩ code quality
    MAINTAINABILITY = "maintainability"  # |M⟩ maintainability
    LICENSING = "licensing"  # |L⟩ licensing


class StateBasis:
    """
    Basis state management for repository Hilbert space.
    """

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
