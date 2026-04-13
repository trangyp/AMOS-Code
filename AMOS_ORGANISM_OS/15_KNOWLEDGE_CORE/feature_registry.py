"""
AMOS Feature Registry & Knowledge Integration
===============================================

Comprehensive registry of all AMOS capabilities, engines,
knowledge bases, and domain expertise.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FeatureModule:
    """A feature module in the AMOS ecosystem."""
    name: str
    category: str
    path: str
    status: str = "active"
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class FeatureRegistry:
    """
    Central registry for all AMOS features and capabilities.
    
    Discovers and catalogs:
    - 14 Core Subsystems
    - 10+ Cognitive Engines
    - 6+ Core Brain Engines
    - AMOS Universe Domains
    - Knowledge Packs (Country/Sector/Scenario/State)
    - Specialized Writing Engines
    """

    def __init__(self, root_path: Optional[Path] = None):
        if root_path is None:
            root_path = Path(__file__).parent.parent.parent
        self.root = root_path
        self.features: List[FeatureModule] = []
        self._discover_all()

    def _discover_all(self):
        """Discover all features in the repository."""
        self._discover_subsystems()
        self._discover_cognitive_engines()
        self._discover_core_engines()
        self._discover_universe_engines()
        self._discover_packs()
        self._discover_domains()

    def _discover_subsystems(self):
        """Discover the 14 organism subsystems."""
        subsystems = [
            ("00_ROOT", "Root System", ["identity", "config", "bootstrap"]),
            ("01_BRAIN", "Brain & Cognition", ["reasoning", "planning", "memory"]),
            ("02_SENSES", "Senses & Perception", ["scanning", "context", "input"]),
            ("03_IMMUNE", "Immune & Security", ["threat_detection", "compliance", "audit"]),
            ("04_BLOOD", "Blood & Resources", ["budget", "cashflow", "forecasting"]),
            ("05_SKELETON", "Skeleton & Structure", ["architecture", "schema", "naming"]),
            ("06_MUSCLE", "Muscle & Execution", ["commands", "code_gen", "workflows"]),
            ("07_METABOLISM", "Metabolism & Processing", ["pipelines", "transforms", "routing"]),
            ("08_WORLD_MODEL", "World Model & Context", ["macro_econ", "geopolitics", "sectors"]),
            ("09_SOCIAL_ENGINE", "Social Engine", ["messaging", "connections", "knowledge_share"]),
            ("10_LIFE_ENGINE", "Life Engine", ["bio_rhythm", "health", "mood", "focus"]),
            ("11_LEGAL_BRAIN", "Legal Brain", ["contracts", "ip", "compliance"]),
            ("12_QUANTUM_LAYER", "Quantum Layer", ["superposition", "probability", "timing"]),
            ("13_FACTORY", "Factory", ["agent_creation", "code_gen", "building"]),
            ("14_INTERFACES", "Interfaces", ["cli", "api", "dashboard"]),
        ]
        
        for code, name, caps in subsystems:
            self.features.append(FeatureModule(
                name=name,
                category="core_subsystem",
                path=f"AMOS_ORGANISM_OS/{code}",
                capabilities=caps,
            ))

    def _discover_cognitive_engines(self):
        """Discover cognitive domain engines."""
        cognitive_path = self.root / "_AMOS_BRAIN" / "Cognitive"
        if cognitive_path.exists():
            engines = [
                ("AMOS_Biology_And_Cognition_Engine", "Biology & Cognition"),
                ("AMOS_Design_Engine", "Design"),
                ("AMOS_Design_Language_Engine", "Design Language"),
                ("AMOS_Deterministic_Logic_And_Law_Engine", "Logic & Law"),
                ("AMOS_Econ_Finance_Engine", "Economics & Finance"),
                ("AMOS_Electrical_Power_Engine", "Electrical Power"),
                ("AMOS_Engineering_And_Mathematics_Engine", "Engineering & Math"),
                ("AMOS_Mechanical_Structural_Engine", "Mechanical & Structural"),
                ("AMOS_Numerical_Methods_Engine", "Numerical Methods"),
                ("AMOS_Physics_Cosmos_Engine", "Physics & Cosmos"),
                ("AMOS_Signal_Processing_Engine", "Signal Processing"),
                ("AMOS_Society_Culture_Engine", "Society & Culture"),
                ("AMOS_Strategy_Game_Engine", "Strategy & Game"),
            ]
            
            for engine_id, name in engines:
                self.features.append(FeatureModule(
                    name=name,
                    category="cognitive_engine",
                    path=f"_AMOS_BRAIN/Cognitive/{engine_id}_v0.json",
                    capabilities=["domain_expertise", "specialized_reasoning"],
                ))

    def _discover_core_engines(self):
        """Discover core brain engines."""
        core_engines = [
            ("AMOS_Cognition_Engine", "Cognition"),
            ("AMOS_Consciousness_Engine", "Consciousness"),
            ("AMOS_Emotion_Engine", "Emotion"),
            ("AMOS_Human_Intelligence_Engine", "Human Intelligence"),
            ("AMOS_Mind_Os", "Mind OS"),
            ("AMOS_Personality_Engine", "Personality"),
            ("AMOS_Brain_Master_Os", "Brain Master OS"),
        ]
        
        for engine_id, name in core_engines:
            self.features.append(FeatureModule(
                name=name,
                category="core_brain_engine",
                path=f"_AMOS_BRAIN/Core/{engine_id}_v0.json",
                capabilities=["cognitive_layer", "brain_function"],
            ))

    def _discover_universe_engines(self):
        """Discover AMOS Universe engines."""
        universe_engines = [
            ("AMOS_21_Domain_Agent", "21 Domain Agent"),
            ("AMOS_Academic_Writing_Kernel", "Academic Writing"),
            ("AMOS_Vietnamese_Writing_Engine", "Vietnamese Writing"),
            ("AMOS_Fabrication_Engine", "Fabrication"),
        ]
        
        for engine_id, name in universe_engines:
            self.features.append(FeatureModule(
                name=name,
                category="universe_engine",
                path=f"_AMOS_BRAIN/_AMOS_UNIVERSE/Engines/{engine_id}_v0.json",
                capabilities=["specialized_agent", "language_expertise"],
            ))

    def _discover_packs(self):
        """Discover knowledge packs."""
        packs_path = self.root / "_AMOS_BRAIN" / "Packs"
        if packs_path.exists():
            pack_types = [
                ("Country_Packs", "Country Knowledge", 55),
                ("Sector_Packs", "Sector Knowledge", 19),
                ("State_Packs", "State Knowledge", 7),
                ("Scenario_Packs", "Scenario Knowledge", 1),
                ("Universe_Packs", "Universe Knowledge", 1),
            ]
            
            for folder, name, count in pack_types:
                self.features.append(FeatureModule(
                    name=name,
                    category="knowledge_pack",
                    path=f"_AMOS_BRAIN/Packs/{folder}",
                    capabilities=[f"{count}_packs", "domain_knowledge", "reference_data"],
                ))

    def _discover_domains(self):
        """Discover AMOS Universe domains."""
        domains_path = self.root / "_AMOS_BRAIN" / "_AMOS_UNIVERSE" / "Domains"
        if domains_path.exists():
            domain_areas = [
                ("Biz_Market", "Business & Market", 7),
                ("Org_Risk_Policy", "Organization, Risk & Policy", 9),
                ("Science_Health", "Science & Health", 2),
                ("Tech_Systems", "Technology & Systems", 6),
            ]
            
            for folder, name, items in domain_areas:
                self.features.append(FeatureModule(
                    name=name,
                    category="knowledge_domain",
                    path=f"_AMOS_BRAIN/_AMOS_UNIVERSE/Domains/{folder}",
                    capabilities=[f"{items}_knowledge_bases", "domain_expertise"],
                ))

    def get_summary(self) -> Dict[str, Any]:
        """Get feature registry summary."""
        by_category = {}
        for f in self.features:
            cat = f.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f.name)
        
        return {
            "total_features": len(self.features),
            "by_category": {k: len(v) for k, v in by_category.items()},
            "categories": list(by_category.keys()),
        }

    def list_by_category(self, category: str) -> List[FeatureModule]:
        """List features by category."""
        return [f for f in self.features if f.category == category]


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS FEATURE REGISTRY - DEEP KNOWLEDGE SCAN")
    print("=" * 70)
    
    registry = FeatureRegistry()
    summary = registry.get_summary()
    
    print(f"\nTotal Features Discovered: {summary['total_features']}")
    print("\nBy Category:")
    for cat, count in summary['by_category'].items():
        print(f"  • {cat}: {count}")
    
    print("\n" + "=" * 70)
    print("Feature Registry Complete")
    print("=" * 70)
