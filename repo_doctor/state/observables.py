"""
Repo Doctor Ω∞ - Observables

Structured measurements, not warnings.

O = {
  o_parse_fatal, o_parse_recoverable,
  o_import_unresolved, o_export_unreachable,
  o_signature_arity_mismatch, o_signature_kwarg_mismatch,
  o_return_shape_mismatch,
  o_entrypoint_missing, o_entrypoint_wrong_target,
  o_packaging_conflict,
  o_roundtrip_failure,
  o_status_false_claim,
  o_runtime_promise_violation,
  o_test_contract_failure,
  o_security_flow_violation,
  o_temporal_breakpoint
}

Subsystem amplitudes:
αk = exp(- Σj wk,j · oj)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .basis import StateDimension


@dataclass
class Observable:
    """A single structured observable measurement.

    Per Ω∞∞∞∞∞: Observables have weights for amplitude calculation:
    α_k = exp(- Σ_j w_{k,j} · o_j)
    """

    name: str
    dimension: StateDimension
    severity: float  # 0-1, higher is worse
    weight: float = 1.0  # Weight for subsystem amplitude calculation
    details: dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    line_number: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "dimension": self.dimension.value,
            "severity": self.severity,
            "details": self.details,
            "source": f"{self.source_file}:{self.line_number}" if self.source_file else "",
        }


@dataclass
class MeasurementResult:
    """Result of measuring an observable."""

    observable: Observable
    measured_value: float
    confidence: float
    timestamp: str = ""


class ObservableSet:
    """
    Collection of observables feeding state amplitudes.
    Ω∞∞∞∞∞: Full observable taxonomy (50+ observable classes)
    """

    # ============================================
    # 4.1 Structural Observables (Syntax/Import/Type)
    # ============================================

    # Parse observables
    O_PARSE_FATAL = Observable(
        name="o_parse_fatal",
        dimension=StateDimension.SYNTAX,
        severity=1.0,
        weight=1.0,
    )
    O_PARSE_RECOVERABLE = Observable(
        name="o_parse_recoverable",
        dimension=StateDimension.SYNTAX,
        severity=0.5,
        weight=0.5,
    )
    O_CRITICAL_FILE_PARSE_FAIL = Observable(
        name="o_critical_file_parse_fail",
        dimension=StateDimension.SYNTAX,
        severity=0.8,
        weight=0.8,
    )

    # Import observables
    O_IMPORT_UNRESOLVED = Observable(
        name="o_import_unresolved",
        dimension=StateDimension.IMPORT,
        severity=1.0,
        weight=1.0,
    )
    O_EXPORT_MISSING = Observable(
        name="o_export_missing",
        dimension=StateDimension.IMPORT,
        severity=0.9,
        weight=0.9,
    )
    O_ENTRYPOINT_IMPORT_FAILURE = Observable(
        name="o_entrypoint_import_failure",
        dimension=StateDimension.IMPORT,
        severity=1.0,
        weight=1.0,
    )
    O_REFLECTION_IMPORT_FAILURE = Observable(
        name="o_reflection_import_failure",
        dimension=StateDimension.IMPORT,
        severity=0.7,
        weight=0.7,
    )

    # Type/signature observables
    O_CALL_ARITY_MISMATCH = Observable(
        name="o_call_arity_mismatch",
        severity=1.0,
        dimension=StateDimension.TYPE,
        weight=1.0,
    )
    O_CALL_KWARG_MISMATCH = Observable(
        name="o_call_kwarg_mismatch",
        severity=1.0,
        dimension=StateDimension.TYPE,
        weight=1.0,
    )
    O_OPTIONAL_ARG_ASSUMPTION_MISMATCH = Observable(
        name="o_optional_arg_assumption_mismatch",
        severity=1.0,
        dimension=StateDimension.TYPE,
        weight=0.8,
    )
    O_RETURN_SHAPE_ASSUMPTION_MISMATCH = Observable(
        name="o_return_shape_assumption_mismatch",
        severity=1.0,
        dimension=StateDimension.TYPE,
        weight=0.8,
    )
    O_SYMBOL_SHADOW_CONFLICT = Observable(
        name="o_symbol_shadow_conflict",
        severity=1.0,
        dimension=StateDimension.TYPE,
        weight=0.6,
    )
    O_NAME_BINDING_AMBIGUITY = Observable(
        name="o_name_binding_ambiguity",
        severity=1.0,
        dimension=StateDimension.TYPE,
        weight=0.5,
    )

    # ============================================
    # 4.2 Packaging/Build Observables
    # ============================================
    O_BUILD_FAILURE = Observable(
        name="o_build_failure",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=1.0,
    )
    O_BUILD_NONDETERMINISM = Observable(
        name="o_build_nondeterminism",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=0.7,
    )
    O_PACKAGE_DISCOVERY_CONFLICT = Observable(
        name="o_package_discovery_conflict",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=0.9,
    )
    O_CONSOLE_SCRIPT_TARGET_MISSING = Observable(
        name="o_console_script_target_missing",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=1.0,
    )
    O_CONSOLE_SCRIPT_TARGET_WRONG = Observable(
        name="o_console_script_target_wrong",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=1.0,
    )
    O_UNSHIPPED_MODULE = Observable(
        name="o_unshipped_module",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=0.8,
    )
    O_DUPLICATE_METADATA_AUTHORITY = Observable(
        name="o_duplicate_metadata_authority",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=0.6,
    )
    O_WHEEL_VS_SOURCE_MISMATCH = Observable(
        name="o_wheel_vs_source_mismatch",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=0.8,
    )
    O_SDIST_VS_WHEEL_MISMATCH = Observable(
        name="o_sdist_vs_wheel_mismatch",
        severity=1.0,
        dimension=StateDimension.PACKAGING,
        weight=0.8,
    )

    # ============================================
    # 4.3 Runtime Observables
    # ============================================
    O_RUNTIME_MODE_MISSING = Observable(
        name="o_runtime_mode_missing",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.9,
    )
    O_FLAG_UNCONSUMED = Observable(
        name="o_flag_unconsumed",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.5,
    )
    O_ENV_UNCONSUMED = Observable(
        name="o_env_unconsumed",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.5,
    )
    O_SHELL_COMMAND_MISSING = Observable(
        name="o_shell_command_missing",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=1.0,
    )
    O_SHELL_HELP_MISMATCH = Observable(
        name="o_shell_help_mismatch",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.8,
    )
    O_SERVER_TRANSPORT_ADVERTISED_NOT_IMPLEMENTED = Observable(
        name="o_server_transport_advertised_not_implemented",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.9,
    )
    O_WRAPPER_RUNTIME_MISMATCH = Observable(
        name="o_wrapper_runtime_mismatch",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.8,
    )
    O_PERMISSION_MODEL_MISMATCH = Observable(
        name="o_permission_model_mismatch",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=0.9,
    )
    O_NATIVE_LIBRARY_LOAD_FAILURE = Observable(
        name="o_native_library_load_failure",
        severity=1.0,
        dimension=StateDimension.RUNTIME,
        weight=1.0,
    )

    # ============================================
    # 4.4 Persistence/Schema Observables
    # ============================================
    O_ROUNDTRIP_FAILURE = Observable(
        name="o_roundtrip_failure",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=1.0,
    )
    O_SCHEMA_FIELD_LOSS = Observable(
        name="o_schema_field_loss",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.9,
    )
    O_SCHEMA_FIELD_RENAME_WITHOUT_ALIAS = Observable(
        name="o_schema_field_rename_without_alias",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.8,
    )
    O_SCHEMA_TYPE_COERCION_BREAK = Observable(
        name="o_schema_type_coercion_break",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.9,
    )
    O_TIMESTAMP_PARSE_FAILURE = Observable(
        name="o_timestamp_parse_failure",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.7,
    )
    O_CACHE_POISON_ACCEPTANCE = Observable(
        name="o_cache_poison_acceptance",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.8,
    )
    O_SAVED_SESSION_UNREPLAYABLE = Observable(
        name="o_saved_session_unreplayable",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.9,
    )
    O_CONFIG_SAVE_LOAD_MISMATCH = Observable(
        name="o_config_save_load_mismatch",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.8,
    )
    O_CODEGEN_SCHEMA_MISMATCH = Observable(
        name="o_codegen_schema_mismatch",
        severity=1.0,
        dimension=StateDimension.PERSISTENCE,
        weight=0.7,
    )

    # ============================================
    # 4.5 Contract-Surface Observables
    # ============================================
    O_DOC_EXAMPLE_FAILURE = Observable(
        name="o_doc_example_failure",
        severity=1.0,
        dimension=StateDimension.DOCS,
        weight=0.8,
    )
    O_TUTORIAL_COMMAND_FAILURE = Observable(
        name="o_tutorial_command_failure",
        severity=1.0,
        dimension=StateDimension.DOCS,
        weight=0.8,
    )
    O_DEMO_INVOCATION_FAILURE = Observable(
        name="o_demo_invocation_failure",
        severity=1.0,
        dimension=StateDimension.DOCS,
        weight=0.9,
    )
    O_CLI_HELP_CONTRACT_MISMATCH = Observable(
        name="o_cli_help_contract_mismatch",
        severity=1.0,
        dimension=StateDimension.DOCS,
        weight=0.7,
    )
    O_SHELL_HELP_CONTRACT_MISMATCH = Observable(
        name="o_shell_help_contract_mismatch",
        severity=1.0,
        dimension=StateDimension.DOCS,
        weight=0.7,
    )
    O_MCP_SCHEMA_CONTRACT_MISMATCH = Observable(
        name="o_mcp_schema_contract_mismatch",
        severity=1.0,
        dimension=StateDimension.API,
        weight=0.9,
    )
    O_LAUNCHER_CLAIM_MISMATCH = Observable(
        name="o_launcher_claim_mismatch",
        severity=1.0,
        dimension=StateDimension.ENTRYPOINT,
        weight=1.0,
    )
    O_EXPORT_SURFACE_MISMATCH = Observable(
        name="o_export_surface_mismatch",
        severity=1.0,
        dimension=StateDimension.API,
        weight=0.8,
    )
    O_STATUS_FALSE_CLAIM = Observable(
        name="o_status_false_claim",
        severity=1.0,
        dimension=StateDimension.STATUS,
        weight=1.0,
    )

    # ============================================
    # 4.6 Temporal Observables
    # ============================================
    O_FIRST_BAD_TRANSITION = Observable(
        name="o_first_bad_transition",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.9,
    )
    O_MERGE_CONTRADICTION = Observable(
        name="o_merge_contradiction",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.8,
    )
    O_HIGH_DRIFT_COMMIT = Observable(
        name="o_high_drift_commit",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.6,
    )
    O_HIGH_DRIFT_MERGE = Observable(
        name="o_high_drift_merge",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.7,
    )
    O_RELEASE_BRANCH_HARD_FAIL = Observable(
        name="o_release_branch_hard_fail",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=1.0,
    )
    O_UNLOCALIZABLE_BREAKPOINT = Observable(
        name="o_unlocalizable_breakpoint",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.8,
    )
    O_REVERT_INCOMPLETE = Observable(
        name="o_revert_incomplete",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.7,
    )
    O_CHERRY_PICK_DIVERGENCE = Observable(
        name="o_cherry_pick_divergence",
        severity=1.0,
        dimension=StateDimension.HISTORY,
        weight=0.6,
    )

    # ============================================
    # 4.7 Security Observables
    # ============================================
    O_SOURCE_SINK_VIOLATION = Observable(
        name="o_source_sink_violation",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=1.0,
    )
    O_SECRET_EXPOSURE_PATH = Observable(
        name="o_secret_exposure_path",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=1.0,
    )
    O_PATH_TRAVERSAL_PATH = Observable(
        name="o_path_traversal_path",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=1.0,
    )
    O_COMMAND_EXECUTION_PATH = Observable(
        name="o_command_execution_path",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=1.0,
    )
    O_UNTRUSTED_DESERIALIZATION_PATH = Observable(
        name="o_untrusted_deserialization_path",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=1.0,
    )
    O_PRIVILEGE_BOUNDARY_BREAK = Observable(
        name="o_privilege_boundary_break",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=1.0,
    )
    O_DEPENDENCY_CRITICAL_FINDING = Observable(
        name="o_dependency_critical_finding",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=0.9,
    )
    O_DEPENDENCY_TRANSITIVE_RISK = Observable(
        name="o_dependency_transitive_risk",
        severity=1.0,
        dimension=StateDimension.SECURITY,
        weight=0.7,
    )

    # ============================================
    # 4.8 Generated Code Observables
    # ============================================
    O_CODEGEN_SCHEMA_MISMATCH = Observable(
        name="o_codegen_schema_mismatch",
        severity=1.0,
        dimension=StateDimension.GENERATED_CODE,
        weight=0.9,
    )
    O_STALE_GENERATED_ARTIFACT = Observable(
        name="o_stale_generated_artifact",
        severity=1.0,
        dimension=StateDimension.GENERATED_CODE,
        weight=0.8,
    )
    O_SOURCE_CODEGEN_CONTRACT_BREAK = Observable(
        name="o_source_codegen_contract_break",
        severity=1.0,
        dimension=StateDimension.GENERATED_CODE,
        weight=0.9,
    )

    # ============================================
    # 4.9 Environment Observables
    # ============================================
    O_PYTHON_VERSION_MISMATCH = Observable(
        name="o_python_version_mismatch",
        severity=1.0,
        dimension=StateDimension.ENVIRONMENT,
        weight=0.7,
    )
    O_OS_SPECIFIC_BREAK = Observable(
        name="o_os_specific_break",
        severity=1.0,
        dimension=StateDimension.ENVIRONMENT,
        weight=0.6,
    )
    O_NATIVE_TOOLCHAIN_BREAK = Observable(
        name="o_native_toolchain_break",
        severity=1.0,
        dimension=StateDimension.ENVIRONMENT,
        weight=0.8,
    )
    O_SECRET_ABSENCE_BREAK = Observable(
        name="o_secret_absence_break",
        severity=1.0,
        dimension=StateDimension.ENVIRONMENT,
        weight=0.7,
    )
    O_NETWORK_DEPENDENCY_BREAK = Observable(
        name="o_network_dependency_break",
        severity=1.0,
        dimension=StateDimension.ENVIRONMENT,
        weight=0.5,
    )

    # ============================================
    # 4.10 Test Observables
    # ============================================
    O_CONTRACT_TEST_FAILURE = Observable(
        name="o_contract_test_failure",
        severity=1.0,
        dimension=StateDimension.TEST,
        weight=0.9,
    )
    O_ORACLE_FLAKINESS = Observable(
        name="o_oracle_flakiness",
        severity=1.0,
        dimension=StateDimension.TEST,
        weight=0.5,
    )
    O_TEST_RUNTIME_MISMATCH = Observable(
        name="o_test_runtime_mismatch",
        severity=1.0,
        dimension=StateDimension.TEST,
        weight=0.7,
    )
    O_TEST_SELECTION_UNSOUNDNESS = Observable(
        name="o_test_selection_unsoundness",
        severity=1.0,
        dimension=StateDimension.TEST,
        weight=0.6,
    )

    # Dimension weights for amplitude calculation
    DIMENSION_WEIGHTS: dict[StateDimension, dict[str, float]] = {
        StateDimension.SYNTAX: {
            "parse_fatal": 10.0,
            "parse_recoverable": 0.5,
        },
        StateDimension.IMPORTS: {
            "unresolved_import": 5.0,
            "export_unreachable": 3.0,
        },
        StateDimension.API: {
            "signature_arity_mismatch": 8.0,
            "signature_kwarg_mismatch": 6.0,
            "return_shape_mismatch": 7.0,
            "doc_example_mismatch": 4.0,
        },
        StateDimension.ENTRYPOINT: {
            "entrypoint_missing": 10.0,
            "entrypoint_wrong_target": 9.0,
            "unconsumed_flag": 3.0,
            "unimplemented_transport": 8.0,
        },
        StateDimension.PACKAGING: {
            "metadata_conflict": 5.0,
            "unshipped_module": 8.0,
            "broken_console_script": 9.0,
        },
        StateDimension.PERSISTENCE: {
            "roundtrip_failure": 7.0,
            "schema_field_loss": 6.0,
            "cache_poison": 10.0,
        },
        StateDimension.STATUS: {
            "false_enabled": 5.0,
            "false_initialized": 7.0,
            "false_healthy": 10.0,
            "false_active": 4.0,
        },
        StateDimension.SECURITY: {
            "security_flow_violation": 10.0,
            "disallowed_dependency": 8.0,
        },
    }

    def __init__(self):
        self.observables: list[Observable] = []

    def add(self, obs: Observable) -> None:
        """Add an observable measurement."""
        self.observables.append(obs)

    def get_for_dimension(self, dim: StateDimension) -> list[Observable]:
        """Get all observables for a dimension."""
        return [o for o in self.observables if o.dimension == dim]

    def calculate_amplitude(self, dim: StateDimension) -> float:
        """
        Calculate amplitude from observables:
        αk = exp(- Σj wk,j · oj)
        """
        import math

        obs_for_dim = self.get_for_dimension(dim)
        if not obs_for_dim:
            return 1.0  # No issues = perfect amplitude

        weights = self.DIMENSION_WEIGHTS.get(dim, {})

        total_penalty = 0.0
        for obs in obs_for_dim:
            w = weights.get(obs.name, 1.0)
            total_penalty += w * obs.severity

        # Exponential decay
        return math.exp(-total_penalty / 10.0)

    def to_amplitude_dict(self) -> dict[StateDimension, float]:
        """Calculate all dimension amplitudes."""
        return {dim: self.calculate_amplitude(dim) for dim in StateDimension}

    def critical_observables(self, threshold: float = 0.5) -> list[Observable]:
        """Get observables above severity threshold."""
        return [o for o in self.observables if o.severity >= threshold]

    def to_dict(self) -> dict[str, Any]:
        """Serialize observable set."""
        return {
            "count": len(self.observables),
            "by_dimension": {
                dim.value: [o.to_dict() for o in self.get_for_dimension(dim)]
                for dim in StateDimension
            },
            "amplitudes": {dim.value: self.calculate_amplitude(dim) for dim in StateDimension},
        }
