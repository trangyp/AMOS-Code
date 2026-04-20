"""Canonical runtime contract for AMOS kernel"""

from datetime import datetime, timezone
UTC = timezone.utc

RUNTIME_CONTRACT = {
    "contract_version": "1.0.0",
    "canonical_runtime": "amos-brain",
    "canonical_module": "amos_kernel.runtime.main",
    "package": {
        "name": "amos-brain",
        "version": "7.0.0",
        "python_requires": ">=3.10",
    },
    "public_entrypoints": [
        "amos-brain",
        "amos-brain doctor",
    ],
    "health_check_module": "amos_kernel.runtime.doctor",
    "health_check_function": "check",
    "forbidden_patterns": [
        "sys.path.insert",
        "repo_root_script_execution",
        "silent_required_ci_failures",
        "bare_except",
        "import *",
    ],
    "required_modules": [
        "core.law",
        "core.state",
        "core.interaction",
        "core.deterministic",
        "core.observe",
        "core.repair",
    ],
    "dependency_order": [
        "law",  # L0
        "state",  # L1
        "interaction",  # L2
        "deterministic",  # L3
        "observe",  # L4
        "repair",  # L5
    ],
    "kernel_layers": {
        "L0": {"name": "law", "purpose": "invariant validation"},
        "L1": {"name": "state", "purpose": "tensor normalization"},
        "L2": {"name": "interaction", "purpose": "internal/external coupling"},
        "L3": {"name": "deterministic", "purpose": "prediction/transitions"},
        "L4": {"name": "observe", "purpose": "drift detection"},
        "L5": {"name": "repair", "purpose": "planning/verification"},
    },
}
