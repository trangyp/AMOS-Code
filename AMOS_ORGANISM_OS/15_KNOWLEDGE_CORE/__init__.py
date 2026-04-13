"""
15_KNOWLEDGE_CORE — Deep Knowledge Integration & Feature Discovery

The knowledge integration layer of AMOS.
Discovers, catalogs, and integrates all features, engines,
and knowledge bases from the entire AMOS ecosystem.

Role: Feature registry, knowledge integration, capability discovery
Kernel refs: KNOWLEDGE_KERNEL, FEATURE_REGISTRY

Owner: Trang
Version: 1.0.0
"""

from .feature_registry import FeatureRegistry, FeatureModule

__all__ = [
    "FeatureRegistry",
    "FeatureModule",
]
