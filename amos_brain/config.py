"""AMOS Brain Configuration System - Layer 11."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LawEnforcementConfig:
    """Configuration for global law enforcement levels."""
    l1_law_of_law: str = "strict"  # strict, standard, lenient
    l2_rule_of_two: str = "strict"
    l3_rule_of_four: str = "standard"
    l4_structural_integrity: str = "strict"
    l5_communication: str = "standard"
    l6_ubi_alignment: str = "lenient"
    
    def get_level(self, law_id: str) -> str:
        """Get enforcement level for a specific law."""
        mapping = {
            "L1": self.l1_law_of_law,
            "L2": self.l2_rule_of_two,
            "L3": self.l3_rule_of_four,
            "L4": self.l4_structural_integrity,
            "L5": self.l5_communication,
            "L6": self.l6_ubi_alignment,
        }
        return mapping.get(law_id, "standard")


@dataclass
class FeatureFlags:
    """Feature flags for cognitive capabilities."""
    enable_rule_of_two: bool = True
    enable_rule_of_four: bool = True
    enable_law_enforcement: bool = True
    enable_state_persistence: bool = True
    enable_monitoring: bool = True
    enable_meta_cognition: bool = True
    enable_audit_logging: bool = True
    enable_anomaly_detection: bool = True


@dataclass
class EnvironmentProfile:
    """Environment-specific configuration."""
    name: str = "development"
    log_level: str = "INFO"
    metrics_retention_hours: int = 24
    max_reasoning_time_ms: int = 30000
    auto_validate_tools: bool = True
    block_high_risk_tools: bool = True
    require_law_compliance: bool = True
    alert_on_violation: bool = True


@dataclass
class CognitiveConfig:
    """
    AMOS Cognitive Configuration Manager - Layer 11.
    
    Provides enterprise configuration for the cognitive OS:
    - Environment profiles (dev/staging/prod)
    - Law enforcement levels
    - Feature flags
    - Custom kernel registration
    """
    
    environment: str = "development"
    law_enforcement: LawEnforcementConfig = field(
        default_factory=LawEnforcementConfig
    )
    features: FeatureFlags = field(default_factory=FeatureFlags)
    
    def __post_init__(self):
        """Initialize with environment profile."""
        self._profiles = {
            "development": EnvironmentProfile(
                name="development",
                log_level="DEBUG",
                metrics_retention_hours=24,
                max_reasoning_time_ms=60000,
                auto_validate_tools=False,
                block_high_risk_tools=False,
                require_law_compliance=False,
                alert_on_violation=False,
            ),
            "staging": EnvironmentProfile(
                name="staging",
                log_level="INFO",
                metrics_retention_hours=72,
                max_reasoning_time_ms=45000,
                auto_validate_tools=True,
                block_high_risk_tools=True,
                require_law_compliance=True,
                alert_on_violation=True,
            ),
            "production": EnvironmentProfile(
                name="production",
                log_level="WARNING",
                metrics_retention_hours=168,  # 7 days
                max_reasoning_time_ms=30000,
                auto_validate_tools=True,
                block_high_risk_tools=True,
                require_law_compliance=True,
                alert_on_violation=True,
            ),
        }
        self._custom_kernels: dict[str, dict] = {}
        self._storage_path = Path.home() / ".amos_brain" / "config"
        self._storage_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def profile(self) -> EnvironmentProfile:
        """Get current environment profile."""
        return self._profiles.get(
            self.environment,
            self._profiles["development"]
        )
    
    def set_environment(self, env: str) -> bool:
        """Switch environment profile."""
        if env in self._profiles:
            self.environment = env
            return True
        return False
    
    def get_law_enforcement_level(self, law_id: str) -> str:
        """Get enforcement level for a law."""
        return self.law_enforcement.get_level(law_id)
    
    def is_law_enforced(self, law_id: str) -> bool:
        """Check if a law should be enforced."""
        if not self.features.enable_law_enforcement:
            return False
        level = self.get_law_enforcement_level(law_id)
        return level in ["strict", "standard"]
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        mapping = {
            "rule_of_two": self.features.enable_rule_of_two,
            "rule_of_four": self.features.enable_rule_of_four,
            "law_enforcement": self.features.enable_law_enforcement,
            "state_persistence": self.features.enable_state_persistence,
            "monitoring": self.features.enable_monitoring,
            "meta_cognition": self.features.enable_meta_cognition,
            "audit_logging": self.features.enable_audit_logging,
            "anomaly_detection": self.features.enable_anomaly_detection,
        }
        return mapping.get(feature, False)
    
    def register_custom_kernel(
        self,
        kernel_id: str,
        name: str,
        description: str,
        domain: str
    ) -> bool:
        """Register a custom cognitive kernel."""
        self._custom_kernels[kernel_id] = {
            "id": kernel_id,
            "name": name,
            "description": description,
            "domain": domain,
            "custom": True,
        }
        return True
    
    def get_custom_kernels(self) -> list[dict]:
        """Get list of registered custom kernels."""
        return list(self._custom_kernels.values())
    
    def to_dict(self) -> dict[str, Any]:
        """Export configuration to dictionary."""
        return {
            "environment": self.environment,
            "law_enforcement": {
                "l1": self.law_enforcement.l1_law_of_law,
                "l2": self.law_enforcement.l2_rule_of_two,
                "l3": self.law_enforcement.l3_rule_of_four,
                "l4": self.law_enforcement.l4_structural_integrity,
                "l5": self.law_enforcement.l5_communication,
                "l6": self.law_enforcement.l6_ubi_alignment,
            },
            "features": {
                "rule_of_two": self.features.enable_rule_of_two,
                "rule_of_four": self.features.enable_rule_of_four,
                "law_enforcement": self.features.enable_law_enforcement,
                "state_persistence": self.features.enable_state_persistence,
                "monitoring": self.features.enable_monitoring,
                "meta_cognition": self.features.enable_meta_cognition,
                "audit_logging": self.features.enable_audit_logging,
                "anomaly_detection": self.features.enable_anomaly_detection,
            },
            "profile": {
                "name": self.profile.name,
                "log_level": self.profile.log_level,
                "max_reasoning_time_ms": self.profile.max_reasoning_time_ms,
            },
            "custom_kernels": len(self._custom_kernels),
        }
    
    def save_to_file(self, filepath: Path | None = None) -> Path:
        """Save configuration to JSON file."""
        if filepath is None:
            filepath = self._storage_path / "brain_config.json"
        
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filepath
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> "CognitiveConfig":
        """Load configuration from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        
        config = cls(environment=data.get("environment", "development"))
        
        # Load law enforcement
        le_data = data.get("law_enforcement", {})
        config.law_enforcement = LawEnforcementConfig(
            l1_law_of_law=le_data.get("l1", "strict"),
            l2_rule_of_two=le_data.get("l2", "strict"),
            l3_rule_of_four=le_data.get("l3", "standard"),
            l4_structural_integrity=le_data.get("l4", "strict"),
            l5_communication=le_data.get("l5", "standard"),
            l6_ubi_alignment=le_data.get("l6", "lenient"),
        )
        
        # Load features
        feat_data = data.get("features", {})
        config.features = FeatureFlags(
            enable_rule_of_two=feat_data.get("rule_of_two", True),
            enable_rule_of_four=feat_data.get("rule_of_four", True),
            enable_law_enforcement=feat_data.get("law_enforcement", True),
            enable_state_persistence=feat_data.get("state_persistence", True),
            enable_monitoring=feat_data.get("monitoring", True),
            enable_meta_cognition=feat_data.get("meta_cognition", True),
            enable_audit_logging=feat_data.get("audit_logging", True),
            enable_anomaly_detection=feat_data.get("anomaly_detection", True),
        )

        # Load custom kernels
        custom_kernels = data.get("custom_kernels", [])
        if isinstance(custom_kernels, list):
            for kernel in custom_kernels:
                kernel_id = kernel.get("id")
                if kernel_id:
                    config._custom_kernels[kernel_id] = kernel

        return config
    
    @classmethod
    def from_env(cls) -> "CognitiveConfig":
        """Create configuration from environment variables."""
        config = cls(
            environment=os.getenv("AMOS_ENV", "development")
        )
        
        # Feature flags from env
        config.features.enable_rule_of_two = (
            os.getenv("AMOS_RULE_OF_TWO", "true").lower() == "true"
        )
        config.features.enable_law_enforcement = (
            os.getenv("AMOS_LAW_ENFORCEMENT", "true").lower() == "true"
        )
        config.features.enable_monitoring = (
            os.getenv("AMOS_MONITORING", "true").lower() == "true"
        )
        config.features.enable_rule_of_four = (
            os.getenv("AMOS_RULE_OF_FOUR", "true").lower() == "true"
        )
        config.features.enable_state_persistence = (
            os.getenv("AMOS_STATE_PERSISTENCE", "true").lower() == "true"
        )
        config.features.enable_meta_cognition = (
            os.getenv("AMOS_META_COGNITION", "true").lower() == "true"
        )
        config.features.enable_audit_logging = (
            os.getenv("AMOS_AUDIT_LOGGING", "true").lower() == "true"
        )
        config.features.enable_anomaly_detection = (
            os.getenv("AMOS_ANOMALY_DETECTION", "true").lower() == "true"
        )

        return config


# Global config instance
_config_instance: CognitiveConfig | None = None


def get_config() -> CognitiveConfig:
    """Get or create global brain configuration."""
    global _config_instance
    if _config_instance is None:
        # Try to load from file, env, or create default
        config_path = Path.home() / ".amos_brain" / "config" / "brain_config.json"
        if config_path.exists():
            _config_instance = CognitiveConfig.load_from_file(config_path)
        else:
            _config_instance = CognitiveConfig.from_env()
    return _config_instance


def reset_config():
    """Reset global configuration (for testing)."""
    global _config_instance
    _config_instance = None
