"""Repo Doctor Ω∞∞∞ - Configuration System.

Manages all configuration for the repository verification system:
- Basis vector weights customization
- Invariant enablement/disablement
- Threshold settings
- CI/CD integration settings
- Autonomous governance parameters
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .state.basis import BasisVector


@dataclass
class InvariantConfig:
    """Configuration for a single invariant."""

    enabled: bool = True
    severity_threshold: float = 0.5
    auto_repair: bool = False
    blocking: bool = False


@dataclass
class BasisVectorConfig:
    """Configuration for a basis vector."""

    enabled: bool = True
    weight: float = None  # None = use default
    threshold: float = 0.5  # Amplitude threshold


@dataclass
class RepoDoctorConfig:
    """Master configuration for Repo Doctor Ω∞∞∞."""

    # General settings
    version: str = "2.8.0"
    energy_threshold: float = 10.0
    releasable_threshold: float = 10.0

    # Invariant layers
    hard_invariants_enabled: bool = True
    soft_invariants_enabled: bool = True
    meta_invariants_enabled: bool = True
    ultimate_invariants_enabled: bool = True

    # Basis vector configs (overrides defaults)
    basis_configs: Dict[str, BasisVectorConfig] = field(default_factory=dict)

    # Invariant configs (per-invariant settings)
    invariant_configs: Dict[str, InvariantConfig] = field(default_factory=dict)

    # CI/CD settings
    ci_mode: bool = False
    fail_on_violation: bool = True
    report_format: str = "json"  # json, markdown, text

    # Autonomous governance
    autonomous_mode: bool = False
    governance_interval: int = 3600  # seconds
    max_autonomous_cycles: int = None

    # Brain integration
    brain_enabled: bool = True
    repair_synthesis_enabled: bool = True

    # Evolution settings
    self_evolution_enabled: bool = False
    rollback_on_failure: bool = True
    regression_guard_enabled: bool = True

    # Reporting
    save_history: bool = True
    history_file: str = ".amos_governance_history.json"
    verbose: bool = False

    @classmethod
    def from_file(cls, path: str) -> RepoDoctorConfig:
        """Load configuration from JSON file."""
        config_path = Path(path)
        if not config_path.exists():
            return cls.create_default()

        with open(config_path) as f:
            data = json.load(f)

        # Convert dict configs to dataclasses
        if "basis_configs" in data:
            data["basis_configs"] = {
                k: BasisVectorConfig(**v) if isinstance(v, dict) else v
                for k, v in data["basis_configs"].items()
            }

        if "invariant_configs" in data:
            data["invariant_configs"] = {
                k: InvariantConfig(**v) if isinstance(v, dict) else v
                for k, v in data["invariant_configs"].items()
            }

        return cls(**data)

    @classmethod
    def create_default(cls) -> RepoDoctorConfig:
        """Create default configuration."""
        config = cls()

        # Initialize all basis vectors with default configs
        for bv in BasisVector:
            config.basis_configs[bv.name] = BasisVectorConfig()

        # Initialize invariant configs for key invariants
        key_invariants = [
            "ParseInvariant",
            "ImportInvariant",
            "SecurityInvariant",
            "TestInvariant",
            "LawHierarchyInvariant",
            "LegibilityInvariant",
            "ModalityInvariant",
            "ObligationLifecycleInvariant",
            "BootstrapIntegrityInvariant",
        ]

        for inv_name in key_invariants:
            config.invariant_configs[inv_name] = InvariantConfig(
                enabled=True,
                severity_threshold=0.5,
                auto_repair=False,
                blocking=("Security" in inv_name or "Parse" in inv_name),
            )

        return config

    @classmethod
    def create_ci_config(cls) -> RepoDoctorConfig:
        """Create configuration optimized for CI/CD."""
        config = cls.create_default()
        config.ci_mode = True
        config.fail_on_violation = True
        config.report_format = "json"
        self_evolution_enabled = False
        autonomous_mode = False
        verbose = False
        return config

    @classmethod
    def create_autonomous_config(cls) -> RepoDoctorConfig:
        """Create configuration for autonomous governance."""
        config = cls.create_default()
        config.autonomous_mode = True
        config.governance_interval = 3600
        config.self_evolution_enabled = True
        config.repair_synthesis_enabled = True
        config.brain_enabled = True
        config.save_history = True
        return config

    def to_file(self, path: str) -> None:
        """Save configuration to JSON file."""
        config_path = Path(path)

        # Convert dataclasses to dicts for serialization
        data = asdict(self)

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_basis_weight(self, basis: BasisVector) -> float:
        """Get weight for a basis vector (config or default)."""
        if basis.name in self.basis_configs:
            cfg = self.basis_configs[basis.name]
            if cfg.weight is not None:
                return cfg.weight

        # Return default weight
        from .state.basis import RepositoryState

        defaults = RepositoryState._default_weights()
        return defaults.get(basis, 50.0)

    def is_invariant_enabled(self, invariant_name: str) -> bool:
        """Check if an invariant is enabled."""
        if invariant_name in self.invariant_configs:
            return self.invariant_configs[invariant_name].enabled
        return True  # Default: enabled

    def is_basis_enabled(self, basis: BasisVector) -> bool:
        """Check if a basis vector is enabled."""
        if basis.name in self.basis_configs:
            return self.basis_configs[basis.name].enabled
        return True  # Default: enabled


def load_config(repo_path: str = ".") -> RepoDoctorConfig:
    """Load configuration from repo or create default."""
    # Look for config files in order of precedence
    config_files = [
        ".repo-doctor.json",
        ".repo-doctor.config.json",
        "repo-doctor.config.json",
    ]

    repo_path = Path(repo_path)

    for config_file in config_files:
        config_path = repo_path / config_file
        if config_path.exists():
            return RepoDoctorConfig.from_file(str(config_path))

    # Return default config
    return RepoDoctorConfig.create_default()


def create_sample_config(path: str = "repo-doctor.config.json") -> None:
    """Create a sample configuration file."""
    config = RepoDoctorConfig.create_default()

    # Customize some settings as examples
    config.energy_threshold = 15.0
    config.verbose = True

    # Disable some basis vectors for demo
    config.basis_configs["STYLE_READABILITY"].enabled = False
    config.basis_configs["REFACTOR_OPPORTUNITY"].enabled = False

    # Configure specific invariants
    config.invariant_configs["SecurityInvariant"] = InvariantConfig(
        enabled=True,
        severity_threshold=0.3,  # Lower threshold for security
        auto_repair=False,
        blocking=True,  # Security issues block releases
    )

    config.to_file(path)
    print(f"Sample configuration created: {path}")


if __name__ == "__main__":
    # Create sample config when run directly
    create_sample_config()
