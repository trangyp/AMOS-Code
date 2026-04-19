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

from dataclasses import dataclass, field
from typing import Any

from .basis import StateDimension


@dataclass
class Observable:
    """
    A single structured observable measurement.

    Per Ω∞∞∞∞∞: Observables have weights for amplitude calculation:
    α_k = exp(- Σ_j w_{k,j} · o_j)
    """

    name: str
    dimension: StateDimension
    severity: float  # 0-1, higher is worse
    weight: float = 1.0  # Weight for subsystem amplitude calculation
    details: Dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    line_number: int = 0

    def to_dict(self) -> Dict[str, Any]:
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

    # ============================================
    # Phase 3: Control System Observables
    # ============================================

    # 5.1 Clock and Temporal Semantics
    O_CLOCK_SKEW_DETECTED = Observable(
        name="o_clock_skew_detected",
        severity=1.0,
        dimension=StateDimension.CLOCK_SEMANTICS,
        weight=0.9,
    )
    O_TIMESTAMP_AMBIGUITY = Observable(
        name="o_timestamp_ambiguity",
        severity=0.9,
        dimension=StateDimension.CLOCK_SEMANTICS,
        weight=0.8,
    )
    O_EXPIRY_LOGIC_INCONSISTENT = Observable(
        name="o_expiry_logic_inconsistent",
        severity=1.0,
        dimension=StateDimension.CLOCK_SEMANTICS,
        weight=0.9,
    )
    O_TEMPORAL_ORDER_VIOLATION = Observable(
        name="o_temporal_order_violation",
        severity=1.0,
        dimension=StateDimension.TEMPORAL_ORDER,
        weight=0.9,
    )

    # 5.2 Cache Coherence
    O_CACHE_INVALIDATION_MISSING = Observable(
        name="o_cache_invalidation_missing",
        severity=0.9,
        dimension=StateDimension.CACHE_COHERENCE,
        weight=0.9,
    )
    O_CACHE_STALE_OVERRIDE = Observable(
        name="o_cache_stale_override",
        severity=1.0,
        dimension=StateDimension.CACHE_COHERENCE,
        weight=1.0,
    )
    O_CACHE_KEY_SEMANTICS_DRIFT = Observable(
        name="o_cache_key_semantics_drift",
        severity=0.8,
        dimension=StateDimension.CACHE_COHERENCE,
        weight=0.8,
    )

    # 5.3 Consistency Model
    O_CONSISTENCY_MODEL_UNDECLARED = Observable(
        name="o_consistency_model_undeclared",
        severity=0.9,
        dimension=StateDimension.CONSISTENCY_MODEL,
        weight=0.9,
    )
    O_STRONG_CONSISTENCY_ASSUMPTION_INVALID = Observable(
        name="o_strong_consistency_assumption_invalid",
        severity=1.0,
        dimension=StateDimension.CONSISTENCY_MODEL,
        weight=1.0,
    )
    O_READ_AFTER_WRITE_FAILURE = Observable(
        name="o_read_after_write_failure",
        severity=1.0,
        dimension=StateDimension.CONSISTENCY_MODEL,
        weight=0.9,
    )

    # 5.4 Identity and Capability
    O_CREDENTIAL_ROTATION_FAILURE = Observable(
        name="o_credential_rotation_failure",
        severity=1.0,
        dimension=StateDimension.IDENTITY_LIFECYCLE,
        weight=1.0,
    )
    O_AMBIENT_AUTHORITY_DETECTED = Observable(
        name="o_ambient_authority_detected",
        severity=0.9,
        dimension=StateDimension.CAPABILITY_DISCIPLINE,
        weight=0.9,
    )
    O_CAPABILITY_LEAKAGE_PATH = Observable(
        name="o_capability_leakage_path",
        severity=1.0,
        dimension=StateDimension.CAPABILITY_DISCIPLINE,
        weight=1.0,
    )

    # 5.5 Queue and Backpressure
    O_RETRY_AMPLIFICATION_LOOP = Observable(
        name="o_retry_amplification_loop",
        severity=1.0,
        dimension=StateDimension.QUEUE_BACKPRESSURE,
        weight=1.0,
    )
    O_UNBOUNDED_QUEUE_GROWTH = Observable(
        name="o_unbounded_queue_growth",
        severity=0.9,
        dimension=StateDimension.QUEUE_BACKPRESSURE,
        weight=0.9,
    )
    O_BACKPRESSURE_MISSING = Observable(
        name="o_backpressure_missing",
        severity=0.9,
        dimension=StateDimension.QUEUE_BACKPRESSURE,
        weight=0.9,
    )

    # 5.6 Fallback and Idempotency
    O_FALLBACK_BYPASSES_AUTH = Observable(
        name="o_fallback_bypasses_auth",
        severity=1.0,
        dimension=StateDimension.FALLBACK_TOPOLOGY,
        weight=1.0,
    )
    O_IDEMPOTENCY_BOUNDARY_VIOLATION = Observable(
        name="o_idempotency_boundary_violation",
        severity=1.0,
        dimension=StateDimension.IDEMPOTENCY_BOUNDARY,
        weight=1.0,
    )

    # 5.7 Lineage and Deprecation
    O_DERIVED_ARTIFACT_OUTLIVES_SOURCE = Observable(
        name="o_derived_artifact_outlives_source",
        severity=0.8,
        dimension=StateDimension.DATA_LINEAGE,
        weight=0.8,
    )
    O_DEPRECATION_WITHOUT_SUNSET = Observable(
        name="o_deprecation_without_sunset",
        severity=0.7,
        dimension=StateDimension.DEPRECATION_LIFECYCLE,
        weight=0.7,
    )

    # 5.8 Audit and Escalation
    O_FORENSIC_GAP_DETECTED = Observable(
        name="o_forensic_gap_detected",
        severity=0.8,
        dimension=StateDimension.FORENSIC_AUDITABILITY,
        weight=0.8,
    )
    O_ESCALATION_PATH_UNDEFINED = Observable(
        name="o_escalation_path_undefined",
        severity=0.9,
        dimension=StateDimension.ESCALATION_GRAPH,
        weight=0.9,
    )

    # 5.9 Control Loop and Failure Domains
    O_CONTROL_LOOP_OSCILLATION = Observable(
        name="o_control_loop_oscillation",
        severity=1.0,
        dimension=StateDimension.CONTROL_LOOP_STABILITY,
        weight=1.0,
    )
    O_FAILURE_DOMAIN_OVERLAP = Observable(
        name="o_failure_domain_overlap",
        severity=0.9,
        dimension=StateDimension.FAILURE_DOMAINS,
        weight=0.9,
    )

    # 5.10 Negative Capability and Debt
    O_FORBIDDEN_STATE_NOT_BLOCKED = Observable(
        name="o_forbidden_state_not_blocked",
        severity=1.0,
        dimension=StateDimension.NEGATIVE_CAPABILITY,
        weight=1.0,
    )
    O_ARCHITECTURAL_DEBT_UNBOUNDED = Observable(
        name="o_architectural_debt_unbounded",
        severity=0.6,
        dimension=StateDimension.ARCHITECTURAL_DEBT,
        weight=0.6,
    )

    # ============================================
    # Phase 4: State Machine and Coexistence Observables
    # ============================================

    # 6.1 State Machine Integrity
    O_UNDECLARED_REACHABLE_STATE = Observable(
        name="o_undeclared_reachable_state",
        severity=1.0,
        dimension=StateDimension.STATE_MACHINE_INTEGRITY,
        weight=1.0,
    )
    O_PARTIAL_INITIALIZATION_HEALTHY = Observable(
        name="o_partial_initialization_healthy",
        severity=0.95,
        dimension=StateDimension.STATE_MACHINE_INTEGRITY,
        weight=0.95,
    )
    O_HALF_MIGRATED_ROUTABLE = Observable(
        name="o_half_migrated_routable",
        severity=1.0,
        dimension=StateDimension.STATE_MACHINE_INTEGRITY,
        weight=1.0,
    )
    O_ROLLBACK_INVARIANT_VIOLATION = Observable(
        name="o_rollback_invariant_violation",
        severity=1.0,
        dimension=StateDimension.STATE_MACHINE_INTEGRITY,
        weight=1.0,
    )

    # 6.2 Forbidden State Reachability
    O_FORBIDDEN_STATE_REACHABLE = Observable(
        name="o_forbidden_state_reachable",
        severity=1.0,
        dimension=StateDimension.FORBIDDEN_STATE_REACHABILITY,
        weight=1.0,
    )

    # 6.3 Transition Legality
    O_UNDECLARED_TRANSITION_PATH = Observable(
        name="o_undeclared_transition_path",
        severity=0.9,
        dimension=StateDimension.TRANSITION_LEGALITY,
        weight=0.9,
    )
    O_TRANSITION_WITHOUT_PRECONDITION = Observable(
        name="o_transition_without_precondition",
        severity=0.85,
        dimension=StateDimension.TRANSITION_LEGALITY,
        weight=0.85,
    )

    # 6.4 Multi-Version Coexistence
    O_VERSION_WINDOW_UNDEFINED = Observable(
        name="o_version_window_undefined",
        severity=0.9,
        dimension=StateDimension.MULTIVERSION_COEXISTENCE,
        weight=0.9,
    )
    O_SHELL_LAUNCHER_MISMATCH = Observable(
        name="o_shell_launcher_mismatch",
        severity=0.9,
        dimension=StateDimension.MULTIVERSION_COEXISTENCE,
        weight=0.9,
    )
    O_GENERATED_CLIENT_LAG = Observable(
        name="o_generated_client_lag",
        severity=0.85,
        dimension=StateDimension.MULTIVERSION_COEXISTENCE,
        weight=0.85,
    )
    O_MIXED_ARTIFACT_INCOMPATIBLE = Observable(
        name="o_mixed_artifact_incompatible",
        severity=1.0,
        dimension=StateDimension.MULTIVERSION_COEXISTENCE,
        weight=1.0,
    )

    # 6.5 Compatibility Window
    O_COMPATIBILITY_WINDOW_VIOLATED = Observable(
        name="o_compatibility_window_violated",
        severity=1.0,
        dimension=StateDimension.COMPATIBILITY_WINDOW,
        weight=1.0,
    )

    # 6.6 Split-Brain Resistance
    O_SPLIT_BRAIN_POSSIBLE = Observable(
        name="o_split_brain_possible",
        severity=1.0,
        dimension=StateDimension.SPLIT_BRAIN_RESISTANCE,
        weight=1.0,
    )
    O_DIVERGENT_AUTHORITY_NO_RECONCILIATION = Observable(
        name="o_divergent_authority_no_reconciliation",
        severity=1.0,
        dimension=StateDimension.SPLIT_BRAIN_RESISTANCE,
        weight=1.0,
    )

    # 6.7 Cutover Integrity
    O_DUAL_WRITE_NO_IDEMPOTENCY = Observable(
        name="o_dual_write_no_idempotency",
        severity=1.0,
        dimension=StateDimension.CUTOVER_INTEGRITY,
        weight=1.0,
    )
    O_DUAL_READ_INCONSISTENT_PRECEDENCE = Observable(
        name="o_dual_read_inconsistent_precedence",
        severity=0.95,
        dimension=StateDimension.CUTOVER_INTEGRITY,
        weight=0.95,
    )
    O_WRITE_OLD_READ_NEW_ASYMMETRY = Observable(
        name="o_write_old_read_new_asymmetry",
        severity=0.9,
        dimension=StateDimension.CUTOVER_INTEGRITY,
        weight=0.9,
    )
    O_ONE_WAY_CUTOVER_HIDDEN = Observable(
        name="o_one_way_cutover_hidden",
        severity=0.85,
        dimension=StateDimension.CUTOVER_INTEGRITY,
        weight=0.85,
    )

    # 6.8 Canary Safety
    O_CANARY_CORRUPTS_STATE = Observable(
        name="o_canary_corrupts_state",
        severity=1.0,
        dimension=StateDimension.CANARY_SAFETY,
        weight=1.0,
    )
    O_CANARY_FALSE_CONFIDENCE = Observable(
        name="o_canary_false_confidence",
        severity=0.9,
        dimension=StateDimension.CANARY_SAFETY,
        weight=0.9,
    )

    # 6.9 Change Coordination
    O_UNCOORDINATED_MULTI_SURFACE = Observable(
        name="o_uncoordinated_multi_surface",
        severity=0.9,
        dimension=StateDimension.CHANGE_COORDINATION,
        weight=0.9,
    )

    # 6.10 Data Quality
    O_CONFIG_PARSEABLE_BUT_INVALID = Observable(
        name="o_config_parseable_but_invalid",
        severity=0.85,
        dimension=StateDimension.DATA_QUALITY,
        weight=0.85,
    )
    O_CACHE_OLDER_THAN_POLICY = Observable(
        name="o_cache_older_than_policy",
        severity=0.9,
        dimension=StateDimension.DATA_QUALITY,
        weight=0.9,
    )
    O_MIGRATION_COMPLETE_BUT_INVALID = Observable(
        name="o_migration_complete_but_invalid",
        severity=1.0,
        dimension=StateDimension.DATA_QUALITY,
        weight=1.0,
    )
    O_GENERATED_ARTIFACT_SEMANTICALLY_STALE = Observable(
        name="o_generated_artifact_semantically_stale",
        severity=0.85,
        dimension=StateDimension.DATA_QUALITY,
        weight=0.85,
    )

    # 6.11 Backfill Integrity
    O_BACKFILL_NON_MONOTONIC = Observable(
        name="o_backfill_non_monotonic",
        severity=0.9,
        dimension=StateDimension.BACKFILL_INTEGRITY,
        weight=0.9,
    )
    O_BACKFILL_NON_IDEMPOTENT = Observable(
        name="o_backfill_non_idempotent",
        severity=0.9,
        dimension=StateDimension.BACKFILL_INTEGRITY,
        weight=0.9,
    )
    O_BACKFILL_LINEAGE_VIOLATION = Observable(
        name="o_backfill_lineage_violation",
        severity=0.85,
        dimension=StateDimension.BACKFILL_INTEGRITY,
        weight=0.85,
    )

    # 6.12 Garbage Collection
    O_DELETED_SOURCE_LIVE_DERIVED = Observable(
        name="o_deleted_source_live_derived",
        severity=0.8,
        dimension=StateDimension.GARBAGE_COLLECTION,
        weight=0.8,
    )
    O_PURGED_DATA_CACHED_REFERENCES = Observable(
        name="o_purged_data_cached_references",
        severity=1.0,
        dimension=StateDimension.GARBAGE_COLLECTION,
        weight=1.0,
    )
    O_RETENTION_POLICY_AUDIT_CONFLICT = Observable(
        name="o_retention_policy_audit_conflict",
        severity=0.9,
        dimension=StateDimension.GARBAGE_COLLECTION,
        weight=0.9,
    )

    # 6.13 External Contract
    O_EXTERNAL_CONTRACT_UNVERSIONED = Observable(
        name="o_external_contract_unversioned",
        severity=0.9,
        dimension=StateDimension.EXTERNAL_CONTRACT,
        weight=0.9,
    )
    O_EXTERNAL_FAILURE_SEMANTICS_UNDECLARED = Observable(
        name="o_external_failure_semantics_undeclared",
        severity=0.9,
        dimension=StateDimension.EXTERNAL_CONTRACT,
        weight=0.9,
    )

    # 6.14 Quota Architecture
    O_QUOTA_UNMODELED = Observable(
        name="o_quota_unmodeled",
        severity=0.85,
        dimension=StateDimension.QUOTA_ARCHITECTURE,
        weight=0.85,
    )
    O_RATE_LIMIT_RETRY_INCOMPATIBLE = Observable(
        name="o_rate_limit_retry_incompatible",
        severity=0.9,
        dimension=StateDimension.QUOTA_ARCHITECTURE,
        weight=0.9,
    )

    # 6.15 Vendor Substitutability
    O_CRITICAL_VENDOR_NO_EXIT_PATH = Observable(
        name="o_critical_vendor_no_exit_path",
        severity=0.7,
        dimension=StateDimension.VENDOR_SUBSTITUTABILITY,
        weight=0.7,
    )

    # 6.16 Experiment Safety
    O_EXPERIMENT_AUTHORITY_VIOLATION = Observable(
        name="o_experiment_authority_violation",
        severity=1.0,
        dimension=StateDimension.EXPERIMENT_SAFETY,
        weight=1.0,
    )
    O_EXPERIMENT_OBSERVABILITY_GAP = Observable(
        name="o_experiment_observability_gap",
        severity=0.85,
        dimension=StateDimension.EXPERIMENT_SAFETY,
        weight=0.85,
    )
    O_EXPERIMENT_ROLLBACK_IMPOSSIBLE = Observable(
        name="o_experiment_rollback_impossible",
        severity=0.9,
        dimension=StateDimension.EXPERIMENT_SAFETY,
        weight=0.9,
    )

    # 6.17 Flag Lattice
    O_FLAG_COMBINATIONS_UNBOUNDED = Observable(
        name="o_flag_combinations_unbounded",
        severity=0.8,
        dimension=StateDimension.FLAG_LATTICE,
        weight=0.8,
    )
    O_FLAG_INTERACTION_UNDECLARED = Observable(
        name="o_flag_interaction_undeclared",
        severity=0.85,
        dimension=StateDimension.FLAG_LATTICE,
        weight=0.85,
    )

    # 6.18 Mode Activation
    O_HIDDEN_MODE_ACTIVATION = Observable(
        name="o_hidden_mode_activation",
        severity=0.9,
        dimension=StateDimension.MODE_ACTIVATION,
        weight=0.9,
    )
    O_UNDOCUMENTED_MODE_SIDE_EFFECT = Observable(
        name="o_undocumented_mode_side_effect",
        severity=0.85,
        dimension=StateDimension.MODE_ACTIVATION,
        weight=0.85,
    )

    # 6.19 Economic Envelope
    O_OBSERVABILITY_TOO_EXPENSIVE = Observable(
        name="o_observability_too_expensive",
        severity=0.6,
        dimension=StateDimension.ECONOMIC_ENVELOPE,
        weight=0.6,
    )
    O_RETRY_EXPLODES_COST = Observable(
        name="o_retry_explodes_cost",
        severity=0.9,
        dimension=StateDimension.ECONOMIC_ENVELOPE,
        weight=0.9,
    )
    O_SAFE_PATH_TOO_EXPENSIVE = Observable(
        name="o_safe_path_too_expensive",
        severity=0.85,
        dimension=StateDimension.ECONOMIC_ENVELOPE,
        weight=0.85,
    )

    # 6.20 Resource Coupling
    O_UNDECLARED_BOTTLENECK_SHARING = Observable(
        name="o_undeclared_bottleneck_sharing",
        severity=0.9,
        dimension=StateDimension.RESOURCE_COUPLING,
        weight=0.9,
    )

    # 6.21 Team Topology
    O_CONWAY_MISFIT = Observable(
        name="o_conway_misfit",
        severity=0.75,
        dimension=StateDimension.TEAM_TOPOLOGY_FIT,
        weight=0.75,
    )
    O_TEAM_BOUNDARY_ARCHITECTURE_MISMATCH = Observable(
        name="o_team_boundary_architecture_mismatch",
        severity=0.8,
        dimension=StateDimension.TEAM_TOPOLOGY_FIT,
        weight=0.8,
    )

    # 6.22 Knowledge Distribution
    O_SINGLE_PERSON_CRITICAL_PATH = Observable(
        name="o_single_person_critical_path",
        severity=0.8,
        dimension=StateDimension.KNOWLEDGE_DISTRIBUTION,
        weight=0.8,
    )
    O_OPAQUE_RECOVERY_KNOWLEDGE = Observable(
        name="o_opaque_recovery_knowledge",
        severity=0.85,
        dimension=StateDimension.KNOWLEDGE_DISTRIBUTION,
        weight=0.85,
    )

    # 6.23 Incentive Alignment
    O_LOCAL_WIN_GLOBAL_DAMAGE = Observable(
        name="o_local_win_global_damage",
        severity=0.7,
        dimension=StateDimension.INCENTIVE_ALIGNMENT,
        weight=0.7,
    )
    O_SPEED_VS_Safety_INCENTIVE_CONFLICT = Observable(
        name="o_speed_vs_safety_incentive_conflict",
        severity=0.75,
        dimension=StateDimension.INCENTIVE_ALIGNMENT,
        weight=0.75,
    )

    # 6.24 Exception Governance
    O_EMERGENCY_BYPASS_UNBOUNDED = Observable(
        name="o_emergency_bypass_unbounded",
        severity=1.0,
        dimension=StateDimension.EXCEPTION_GOVERNANCE,
        weight=1.0,
    )
    O_EXCEPTION_UNREVIEWED = Observable(
        name="o_exception_unreviewed",
        severity=0.9,
        dimension=StateDimension.EXCEPTION_GOVERNANCE,
        weight=0.9,
    )
    O_EXCEPTION_UNLOGGED = Observable(
        name="o_exception_unlogged",
        severity=0.9,
        dimension=StateDimension.EXCEPTION_GOVERNANCE,
        weight=0.9,
    )

    # 6.25 Override Decay
    O_OVERRIDE_WITHOUT_EXPIRY = Observable(
        name="o_override_without_expiry",
        severity=0.85,
        dimension=StateDimension.OVERRIDE_DECAY,
        weight=0.85,
    )
    O_TEMPORARY_BECOMES_PERMANENT = Observable(
        name="o_temporary_becomes_permanent",
        severity=0.8,
        dimension=StateDimension.OVERRIDE_DECAY,
        weight=0.8,
    )

    # 6.26 Hotfix Topology
    O_HOTFIX_VIOLATES_ARCHITECTURE = Observable(
        name="o_hotfix_violates_architecture",
        severity=0.95,
        dimension=StateDimension.HOTFIX_TOPOLOGY,
        weight=0.95,
    )
    O_HOTFIX_ROLLBACK_UNSAFE = Observable(
        name="o_hotfix_rollback_unsafe",
        severity=1.0,
        dimension=StateDimension.HOTFIX_TOPOLOGY,
        weight=1.0,
    )

    # 6.27 Compliance Lifecycle
    O_ROLLBACK_REQUIRES_DELETED_DATA = Observable(
        name="o_rollback_requires_deleted_data",
        severity=0.9,
        dimension=StateDimension.COMPLIANCE_LIFECYCLE,
        weight=0.9,
    )
    O_CACHE_DELETION_LAG_VIOLATION = Observable(
        name="o_cache_deletion_lag_violation",
        severity=0.9,
        dimension=StateDimension.COMPLIANCE_LIFECYCLE,
        weight=0.9,
    )
    O_GENERATED_ARTIFACT_RETENTION_VIOLATION = Observable(
        name="o_generated_artifact_retention_violation",
        severity=0.85,
        dimension=StateDimension.COMPLIANCE_LIFECYCLE,
        weight=0.85,
    )

    # 6.28 Epistemic Integrity
    O_EVIDENCE_STALE_FOR_DECISION = Observable(
        name="o_evidence_stale_for_decision",
        severity=0.85,
        dimension=StateDimension.EPISTEMIC_INTEGRITY,
        weight=0.85,
    )
    O_EVIDENCE_GENERALIZED_INCORRECTLY = Observable(
        name="o_evidence_generalized_incorrectly",
        severity=0.9,
        dimension=StateDimension.EPISTEMIC_INTEGRITY,
        weight=0.9,
    )
    O_DECISION_WITHOUT_EVIDENCE_ACCESS = Observable(
        name="o_decision_without_evidence_access",
        severity=0.9,
        dimension=StateDimension.EPISTEMIC_INTEGRITY,
        weight=0.9,
    )

    # 6.29 Constitutional and Ownership
    O_CONSTITUTION_VIOLATION = Observable(
        name="o_constitution_violation",
        severity=1.0,
        dimension=StateDimension.CONSTITUTIONAL_INTEGRITY,
        weight=1.0,
    )
    O_STATE_AUTHORITY_AMBIGUOUS = Observable(
        name="o_state_authority_ambiguous",
        severity=0.9,
        dimension=StateDimension.STATE_OWNERSHIP,
        weight=0.9,
    )
    O_ABSENCE_SEMANTICS_UNDECLARED = Observable(
        name="o_absence_semantics_undeclared",
        severity=0.85,
        dimension=StateDimension.ABSENCE_SEMANTICS,
        weight=0.85,
    )

    # 6.30 Disaster Recovery
    O_DR_UNTESTED_PATH = Observable(
        name="o_dr_untested_path",
        severity=0.9,
        dimension=StateDimension.DISASTER_RECOVERY,
        weight=0.9,
    )
    O_DR_INCOMPLETE_COVERAGE = Observable(
        name="o_dr_incomplete_coverage",
        severity=0.85,
        dimension=StateDimension.DISASTER_RECOVERY,
        weight=0.85,
    )

    # 6.31 Graceful Degradation
    O_DEGRADATION_PATH_UNDEFINED = Observable(
        name="o_degradation_path_undefined",
        severity=0.9,
        dimension=StateDimension.GRACEFUL_DEGRADATION,
        weight=0.9,
    )
    O_DEGRADATION_CASCADES_UNCONTROLLABLY = Observable(
        name="o_degradation_cascades_uncontrollably",
        severity=1.0,
        dimension=StateDimension.GRACEFUL_DEGRADATION,
        weight=1.0,
    )

    # 6.32 Interoperability
    O_CROSS_SYSTEM_CONTRACT_VIOLATION = Observable(
        name="o_cross_system_contract_violation",
        severity=0.85,
        dimension=StateDimension.INTEROPERABILITY,
        weight=0.85,
    )

    # =========================================================================
    # PHASE 5: LEASE, TRANSACTION, AND META-STABILITY (40+ new)
    # =========================================================================

    # 7.1 Lease and Revocation
    O_LEASE_SEMANTICS_UNDEFINED = Observable(
        name="o_lease_semantics_undefined",
        severity=0.9,
        dimension=StateDimension.LEASE_INTEGRITY,
        weight=0.9,
    )
    O_ZOMBIE_LEASE_ACTIVE = Observable(
        name="o_zombie_lease_active",
        severity=1.0,
        dimension=StateDimension.ZOMBIE_LEASE,
        weight=1.0,
    )
    O_LEASE_CLOCK_SKEW_UNBOUNDED = Observable(
        name="o_lease_clock_skew_unbounded",
        severity=0.85,
        dimension=StateDimension.LEASE_CLOCK_COUPLING,
        weight=0.85,
    )

    # 7.2 Transaction Boundaries
    O_TRANSACTION_SCOPE_AMBIGUOUS = Observable(
        name="o_transaction_scope_ambiguous",
        severity=0.85,
        dimension=StateDimension.TRANSACTION_SCOPE,
        weight=0.85,
    )
    O_CROSS_PLANE_COMMIT_FAILURE = Observable(
        name="o_cross_plane_commit_failure",
        severity=0.9,
        dimension=StateDimension.CROSS_PLANE_COMMIT,
        weight=0.9,
    )
    O_COMPENSATION_INCOMPLETE = Observable(
        name="o_compensation_incomplete",
        severity=0.85,
        dimension=StateDimension.COMPENSATION_CLOSURE,
        weight=0.85,
    )

    # 7.3 Saturation and Overload
    O_CORRECTNESS_UNDER_SATURATION_VIOLATED = Observable(
        name="o_correctness_under_saturation_violated",
        severity=0.8,
        dimension=StateDimension.SATURATION_SAFETY,
        weight=0.8,
    )
    O_OVERLOAD_SHEDDING_ORDER_IMPLICIT = Observable(
        name="o_overload_shedding_order_implicit",
        severity=0.75,
        dimension=StateDimension.OVERLOAD_POLICY,
        weight=0.75,
    )
    O_SATURATION_AUTHORITY_DRIFT_DETECTED = Observable(
        name="o_saturation_authority_drift_detected",
        severity=0.9,
        dimension=StateDimension.SATURATION_AUTHORITY_DRIFT,
        weight=0.9,
    )

    # 7.4 Hysteresis and State Memory
    O_HYSTERESIS_ABSENT_CAUSES_OSCILLATION = Observable(
        name="o_hysteresis_absent_causes_oscillation",
        severity=0.7,
        dimension=StateDimension.HYSTERESIS_SAFETY,
        weight=0.7,
    )
    O_STATE_MEMORY_DEPENDENCE_HIDDEN = Observable(
        name="o_state_memory_dependence_hidden",
        severity=0.75,
        dimension=StateDimension.STATE_MEMORY,
        weight=0.75,
    )

    # 7.5 Symmetry and Symmetry Breaking
    O_FALSE_SYMMETRY_ASSUMED = Observable(
        name="o_false_symmetry_assumed",
        severity=0.8,
        dimension=StateDimension.FALSE_SYMMETRY,
        weight=0.8,
    )
    O_HIDDEN_SYMMETRY_BREAKING = Observable(
        name="o_hidden_symmetry_breaking",
        severity=0.75,
        dimension=StateDimension.SYMMETRY_BREAKING,
        weight=0.75,
    )

    # 7.6 Trust Domains
    O_TRUST_DOMAIN_COLLAPSE = Observable(
        name="o_trust_domain_collapse",
        severity=0.95,
        dimension=StateDimension.TRUST_DOMAIN_INTEGRITY,
        weight=0.95,
    )
    O_TRUST_TRANSITIVITY_ILLUSION = Observable(
        name="o_trust_transitivity_illusion",
        severity=0.85,
        dimension=StateDimension.TRUST_TRANSITIVITY,
        weight=0.85,
    )
    O_CROSS_DOMAIN_CACHE_BLEED = Observable(
        name="o_cross_domain_cache_bleed",
        severity=0.9,
        dimension=StateDimension.TRUST_CACHE_BLEED,
        weight=0.9,
    )

    # 7.7 Hermeticity
    O_BUILD_NONHERMETIC = Observable(
        name="o_build_nonhermetic",
        severity=0.8,
        dimension=StateDimension.BUILD_HERMETICITY,
        weight=0.8,
    )
    O_TEST_NONHERMETIC = Observable(
        name="o_test_nonhermetic",
        severity=0.75,
        dimension=StateDimension.TEST_HERMETICITY,
        weight=0.75,
    )
    O_DOCTOR_NONHERMETIC = Observable(
        name="o_doctor_nonhermetic",
        severity=0.85,
        dimension=StateDimension.DOCTOR_HERMETICITY,
        weight=0.85,
    )

    # 7.8 Impossibility Boundaries
    O_IMPOSSIBLE_GUARANTEE_BUNDLE = Observable(
        name="o_impossible_guarantee_bundle",
        severity=0.9,
        dimension=StateDimension.IMPOSSIBILITY_AWARENESS,
        weight=0.9,
    )
    O_SILENT_IMPOSSIBILITY_COMPENSATION = Observable(
        name="o_silent_impossibility_compensation",
        severity=0.85,
        dimension=StateDimension.IMPOSSIBILITY_HONESTY,
        weight=0.85,
    )

    # 7.9 Dark-State and Nullspace
    O_DARK_STATE_UNOBSERVED = Observable(
        name="o_dark_state_unobserved",
        severity=0.8,
        dimension=StateDimension.DARK_STATE_DETECTABILITY,
        weight=0.8,
    )
    O_NULLSPACE_COLLAPSE = Observable(
        name="o_nullspace_collapse",
        severity=0.75,
        dimension=StateDimension.NULLSPACE_BEHAVIOR,
        weight=0.75,
    )

    # 7.10 Non-Local and Global Invariants
    O_NONLOCAL_INVARIANT_VIOLATED = Observable(
        name="o_nonlocal_invariant_violated",
        severity=0.9,
        dimension=StateDimension.NONLOCAL_INVARIANT,
        weight=0.9,
    )
    O_GLOBAL_CONSERVATION_FAILURE = Observable(
        name="o_global_conservation_failure",
        severity=0.85,
        dimension=StateDimension.GLOBAL_CONSERVATION,
        weight=0.85,
    )

    # 7.11 Truth and Distributed Systems
    O_TRUTH_ARBITRATION_UNRESOLVED = Observable(
        name="o_truth_arbitration_unresolved",
        severity=0.95,
        dimension=StateDimension.TRUTH_ARBITRATION,
        weight=0.95,
    )
    O_IRREVERSIBLE_ACTION_UNBOUNDED = Observable(
        name="o_irreversible_action_unbounded",
        severity=0.9,
        dimension=StateDimension.IRREVERSIBILITY_MANAGEMENT,
        weight=0.9,
    )
    O_QUIESCENCE_UNSAFE = Observable(
        name="o_quiescence_unsafe",
        severity=0.85,
        dimension=StateDimension.QUIESCENCE_INTEGRITY,
        weight=0.85,
    )

    # 7.12 Liveness and Fairness
    O_LIVENESS_GUARANTEE_ABSENT = Observable(
        name="o_liveness_guarantee_absent",
        severity=0.8,
        dimension=StateDimension.LIVENESS,
        weight=0.8,
    )
    O_FAIRNESS_VIOLATION = Observable(
        name="o_fairness_violation",
        severity=0.75,
        dimension=StateDimension.FAIRNESS,
        weight=0.75,
    )
    O_SCHEDULER_UNSAFE = Observable(
        name="o_scheduler_unsafe",
        severity=0.8,
        dimension=StateDimension.SCHEDULER_ROBUSTNESS,
        weight=0.8,
    )

    # 7.13 Partition and Convergence
    O_PARTITION_HANDLING_INCORRECT = Observable(
        name="o_partition_handling_incorrect",
        severity=0.85,
        dimension=StateDimension.PARTITION_BEHAVIOR,
        weight=0.85,
    )
    O_CONVERGENCE_FAILURE = Observable(
        name="o_convergence_failure",
        severity=0.8,
        dimension=StateDimension.CONVERGENCE,
        weight=0.8,
    )
    O_CAUSAL_ATTRIBUTION_LOST = Observable(
        name="o_causal_attribution_lost",
        severity=0.85,
        dimension=StateDimension.CAUSAL_ATTRIBUTION,
        weight=0.85,
    )

    # 7.14 Compositional and Observer Effects
    O_COMPOSITIONAL_INVALIDITY = Observable(
        name="o_compositional_invalidity",
        severity=0.9,
        dimension=StateDimension.COMPOSITIONAL_VALIDITY,
        weight=0.9,
    )
    O_OBSERVER_EFFECT_UNBOUNDED = Observable(
        name="o_observer_effect_unbounded",
        severity=0.75,
        dimension=StateDimension.OBSERVER_EFFECT_BOUND,
        weight=0.75,
    )
    O_ARCHITECTURAL_ENTROPY_UNCHECKED = Observable(
        name="o_architectural_entropy_unchecked",
        severity=0.7,
        dimension=StateDimension.ARCHITECTURAL_ENTROPY,
        weight=0.7,
    )

    # 7.15 Loss and Boundedness
    O_LOSS_UNBOUNDED = Observable(
        name="o_loss_unbounded",
        severity=0.85,
        dimension=StateDimension.LOSS_BOUNDEDNESS,
        weight=0.85,
    )
    O_SEMANTIC_LOSS_UNDETECTED = Observable(
        name="o_semantic_loss_undetected",
        severity=0.8,
        dimension=StateDimension.SEMANTIC_LOSS,
        weight=0.8,
    )

    # 7.16 Policy and Adaptation
    O_POLICY_PRECEDENCE_AMBIGUOUS = Observable(
        name="o_policy_precedence_ambiguous",
        severity=0.85,
        dimension=StateDimension.POLICY_PRECEDENCE,
        weight=0.85,
    )
    O_ADAPTIVE_INSTABILITY = Observable(
        name="o_adaptive_instability",
        severity=0.8,
        dimension=StateDimension.ADAPTIVE_STABILITY,
        weight=0.8,
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
        # Phase 3: Control system dimensions
        StateDimension.CLOCK_SEMANTICS: {
            "clock_skew": 9.0,
            "timestamp_ambiguity": 8.0,
            "expiry_inconsistent": 9.0,
        },
        StateDimension.TEMPORAL_ORDER: {
            "order_violation": 9.0,
        },
        StateDimension.CACHE_COHERENCE: {
            "invalidation_missing": 9.0,
            "stale_override": 10.0,
            "key_semantics_drift": 8.0,
        },
        StateDimension.CONSISTENCY_MODEL: {
            "model_undeclared": 9.0,
            "strong_assumption_invalid": 10.0,
            "read_after_write_failure": 9.0,
        },
        StateDimension.IDENTITY_LIFECYCLE: {
            "rotation_failure": 10.0,
        },
        StateDimension.CAPABILITY_DISCIPLINE: {
            "ambient_authority": 9.0,
            "capability_leak": 10.0,
        },
        StateDimension.QUEUE_BACKPRESSURE: {
            "retry_amplification": 10.0,
            "unbounded_growth": 9.0,
            "backpressure_missing": 9.0,
        },
        StateDimension.FALLBACK_TOPOLOGY: {
            "fallback_bypasses_auth": 10.0,
        },
        StateDimension.IDEMPOTENCY_BOUNDARY: {
            "boundary_violation": 10.0,
        },
        StateDimension.DATA_LINEAGE: {
            "artifact_outlives_source": 8.0,
        },
        StateDimension.DEPRECATION_LIFECYCLE: {
            "deprecation_without_sunset": 7.0,
        },
        StateDimension.FORENSIC_AUDITABILITY: {
            "forensic_gap": 8.0,
        },
        StateDimension.ESCALATION_GRAPH: {
            "escalation_undefined": 9.0,
        },
        StateDimension.CONTROL_LOOP_STABILITY: {
            "control_oscillation": 10.0,
        },
        StateDimension.FAILURE_DOMAINS: {
            "domain_overlap": 9.0,
        },
        StateDimension.NEGATIVE_CAPABILITY: {
            "forbidden_state_unblocked": 10.0,
        },
        StateDimension.ARCHITECTURAL_DEBT: {
            "debt_unbounded": 6.0,
        },
        # Phase 4: State machine and coexistence dimensions
        StateDimension.STATE_MACHINE_INTEGRITY: {
            "undeclared_state": 10.0,
            "partial_init_healthy": 9.5,
            "half_migrated": 10.0,
            "rollback_violation": 10.0,
        },
        StateDimension.FORBIDDEN_STATE_REACHABILITY: {
            "forbidden_reachable": 10.0,
        },
        StateDimension.TRANSITION_LEGALITY: {
            "undeclared_path": 9.0,
            "no_precondition": 8.5,
        },
        StateDimension.MULTIVERSION_COEXISTENCE: {
            "window_undefined": 9.0,
            "shell_mismatch": 9.0,
            "client_lag": 8.5,
            "mixed_incompatible": 10.0,
        },
        StateDimension.COMPATIBILITY_WINDOW: {
            "window_violated": 10.0,
        },
        StateDimension.SPLIT_BRAIN_RESISTANCE: {
            "split_brain_possible": 10.0,
            "no_reconciliation": 10.0,
        },
        StateDimension.CUTOVER_INTEGRITY: {
            "dual_write_no_idempotency": 10.0,
            "dual_read_inconsistent": 9.5,
            "write_read_asymmetry": 9.0,
            "hidden_cutover": 8.5,
        },
        StateDimension.CANARY_SAFETY: {
            "canary_corrupts": 10.0,
            "false_confidence": 9.0,
        },
        StateDimension.CHANGE_COORDINATION: {
            "uncoordinated_multi": 9.0,
        },
        StateDimension.DATA_QUALITY: {
            "parseable_invalid": 8.5,
            "cache_older_policy": 9.0,
            "migration_invalid": 10.0,
            "artifact_stale": 8.5,
        },
        StateDimension.BACKFILL_INTEGRITY: {
            "non_monotonic": 9.0,
            "non_idempotent": 9.0,
            "lineage_violation": 8.5,
        },
        StateDimension.GARBAGE_COLLECTION: {
            "deleted_source_live": 8.0,
            "purged_cached": 10.0,
            "retention_audit_conflict": 9.0,
        },
        StateDimension.EXTERNAL_CONTRACT: {
            "unversioned": 9.0,
            "failure_undeclared": 9.0,
        },
        StateDimension.QUOTA_ARCHITECTURE: {
            "quota_unmodeled": 8.5,
            "rate_retry_incompatible": 9.0,
        },
        StateDimension.VENDOR_SUBSTITUTABILITY: {
            "no_exit_path": 7.0,
        },
        StateDimension.EXPERIMENT_SAFETY: {
            "authority_violation": 10.0,
            "observability_gap": 8.5,
            "rollback_impossible": 9.0,
        },
        StateDimension.FLAG_LATTICE: {
            "combinations_unbounded": 8.0,
            "interaction_undeclared": 8.5,
        },
        StateDimension.MODE_ACTIVATION: {
            "hidden_activation": 9.0,
            "undocumented_side_effect": 8.5,
        },
        StateDimension.ECONOMIC_ENVELOPE: {
            "observability_expensive": 6.0,
            "retry_explodes": 9.0,
            "safe_path_expensive": 8.5,
        },
        StateDimension.RESOURCE_COUPLING: {
            "bottleneck_sharing": 9.0,
        },
        StateDimension.TEAM_TOPOLOGY_FIT: {
            "conway_misfit": 7.5,
            "boundary_mismatch": 8.0,
        },
        StateDimension.KNOWLEDGE_DISTRIBUTION: {
            "single_person": 8.0,
            "opaque_recovery": 8.5,
        },
        StateDimension.INCENTIVE_ALIGNMENT: {
            "local_global_damage": 7.0,
            "speed_safety_conflict": 7.5,
        },
        StateDimension.EXCEPTION_GOVERNANCE: {
            "bypass_unbounded": 10.0,
            "unreviewed": 9.0,
            "unlogged": 9.0,
        },
        StateDimension.OVERRIDE_DECAY: {
            "no_expiry": 8.5,
            "temporary_permanent": 8.0,
        },
        StateDimension.HOTFIX_TOPOLOGY: {
            "violates_architecture": 9.5,
            "rollback_unsafe": 10.0,
        },
        StateDimension.COMPLIANCE_LIFECYCLE: {
            "rollback_requires_deleted": 9.0,
            "cache_deletion_lag": 9.0,
            "artifact_retention": 8.5,
        },
        StateDimension.EPISTEMIC_INTEGRITY: {
            "evidence_stale": 8.5,
            "generalized_incorrectly": 9.0,
            "no_evidence_access": 9.0,
        },
        StateDimension.CONSTITUTIONAL_INTEGRITY: {
            "constitution_violation": 10.0,
        },
        StateDimension.STATE_OWNERSHIP: {
            "authority_ambiguous": 9.0,
        },
        StateDimension.ABSENCE_SEMANTICS: {
            "undeclared": 8.5,
        },
        StateDimension.DISASTER_RECOVERY: {
            "untested_path": 9.0,
            "incomplete_coverage": 8.5,
        },
        StateDimension.GRACEFUL_DEGRADATION: {
            "path_undefined": 9.0,
            "cascades_uncontrollably": 10.0,
        },
        StateDimension.INTEROPERABILITY: {
            "cross_system_violation": 8.5,
        },
        # Phase 5: Lease, Transaction, and Meta-Stability weights
        StateDimension.LEASE_INTEGRITY: {
            "semantics_undefined": 9.0,
        },
        StateDimension.ZOMBIE_LEASE: {
            "zombie_active": 10.0,
        },
        StateDimension.LEASE_CLOCK_COUPLING: {
            "clock_skew_unbounded": 8.5,
        },
        StateDimension.TRANSACTION_SCOPE: {
            "scope_ambiguous": 8.5,
        },
        StateDimension.CROSS_PLANE_COMMIT: {
            "cross_plane_failure": 9.0,
        },
        StateDimension.COMPENSATION_CLOSURE: {
            "compensation_incomplete": 8.5,
        },
        StateDimension.SATURATION_SAFETY: {
            "correctness_violated": 8.0,
        },
        StateDimension.OVERLOAD_POLICY: {
            "shedding_implicit": 7.5,
        },
        StateDimension.SATURATION_AUTHORITY_DRIFT: {
            "authority_drift": 9.0,
        },
        StateDimension.HYSTERESIS_SAFETY: {
            "absent_oscillation": 7.0,
        },
        StateDimension.STATE_MEMORY: {
            "dependence_hidden": 7.5,
        },
        StateDimension.FALSE_SYMMETRY: {
            "symmetry_assumed": 8.0,
        },
        StateDimension.SYMMETRY_BREAKING: {
            "breaking_hidden": 7.5,
        },
        StateDimension.TRUST_DOMAIN_INTEGRITY: {
            "domain_collapse": 9.5,
        },
        StateDimension.TRUST_TRANSITIVITY: {
            "transitivity_illusion": 8.5,
        },
        StateDimension.TRUST_CACHE_BLEED: {
            "cache_bleed": 9.0,
        },
        StateDimension.BUILD_HERMETICITY: {
            "build_nonhermetic": 8.0,
        },
        StateDimension.TEST_HERMETICITY: {
            "test_nonhermetic": 7.5,
        },
        StateDimension.DOCTOR_HERMETICITY: {
            "doctor_nonhermetic": 8.5,
        },
        StateDimension.IMPOSSIBILITY_AWARENESS: {
            "impossible_bundle": 9.0,
        },
        StateDimension.IMPOSSIBILITY_HONESTY: {
            "silent_compensation": 8.5,
        },
        StateDimension.DARK_STATE_DETECTABILITY: {
            "dark_state_unobserved": 8.0,
        },
        StateDimension.NULLSPACE_BEHAVIOR: {
            "nullspace_collapse": 7.5,
        },
        StateDimension.NONLOCAL_INVARIANT: {
            "nonlocal_violated": 9.0,
        },
        StateDimension.GLOBAL_CONSERVATION: {
            "conservation_failure": 8.5,
        },
        StateDimension.TRUTH_ARBITRATION: {
            "arbitration_unresolved": 9.5,
        },
        StateDimension.IRREVERSIBILITY_MANAGEMENT: {
            "action_unbounded": 9.0,
        },
        StateDimension.QUIESCENCE_INTEGRITY: {
            "quiescence_unsafe": 8.5,
        },
        StateDimension.LIVENESS: {
            "guarantee_absent": 8.0,
        },
        StateDimension.FAIRNESS: {
            "fairness_violation": 7.5,
        },
        StateDimension.SCHEDULER_ROBUSTNESS: {
            "scheduler_unsafe": 8.0,
        },
        StateDimension.PARTITION_BEHAVIOR: {
            "handling_incorrect": 8.5,
        },
        StateDimension.CONVERGENCE: {
            "convergence_failure": 8.0,
        },
        StateDimension.CAUSAL_ATTRIBUTION: {
            "attribution_lost": 8.5,
        },
        StateDimension.COMPOSITIONAL_VALIDITY: {
            "compositional_invalidity": 9.0,
        },
        StateDimension.OBSERVER_EFFECT_BOUND: {
            "observer_effect_unbounded": 7.5,
        },
        StateDimension.ARCHITECTURAL_ENTROPY: {
            "entropy_unchecked": 7.0,
        },
        StateDimension.LOSS_BOUNDEDNESS: {
            "loss_unbounded": 8.5,
        },
        StateDimension.SEMANTIC_LOSS: {
            "semantic_loss_undetected": 8.0,
        },
        StateDimension.POLICY_PRECEDENCE: {
            "precedence_ambiguous": 8.5,
        },
        StateDimension.ADAPTIVE_STABILITY: {
            "adaptive_instability": 8.0,
        },
    }

    def __init__(self):
        self.observables: List[Observable] = []

    def add(self, obs: Observable) -> None:
        """Add an observable measurement."""
        self.observables.append(obs)

    def get_for_dimension(self, dim: StateDimension) -> List[Observable]:
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

    def critical_observables(self, threshold: float = 0.5) -> List[Observable]:
        """Get observables above severity threshold."""
        return [o for o in self.observables if o.severity >= threshold]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize observable set."""
        return {
            "count": len(self.observables),
            "by_dimension": {
                dim.value: [o.to_dict() for o in self.get_for_dimension(dim)]
                for dim in StateDimension
            },
            "amplitudes": {dim.value: self.calculate_amplitude(dim) for dim in StateDimension},
        }
