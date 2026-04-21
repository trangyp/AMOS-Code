#!/usr/bin/env python3
"""AMOS Legacy Brain Loader - Integrates _LEGACY BRAIN2 cognitive engines."""

import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

LEGACY_BRAIN_PATH = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON/_LEGACY BRAIN2/Core")


@dataclass
class CognitiveEngine:
    """Loaded cognitive engine from legacy JSON."""
    name: str
    version: str
    description: str
    core_laws: dict[str, Any] = field(default_factory=dict)
    layers: dict[str, Any] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)


class LegacyBrainLoader:
    """Loads and integrates legacy AMOS brain components."""
    
    def __init__(self) -> None:
        self.engines: dict[str, CognitiveEngine] = {}
        self.canonical_laws: dict[str, Any] = {}
        self.loaded = False
    
    def load_core_engines(self) -> dict[str, CognitiveEngine]:
        """Load all core cognitive engines."""
        core_files = [
            "AMOS_Cognition_Engine_v0.json",
            "AMOS_Consciousness_Engine_v0.json",
            "AMOS_Emotion_Engine_v0.json",
            "AMOS_Mind_Os_v0.json",
            "AMOS_Personality_Engine_v0.json",
            "AMOS_Quantum_Stack_v0.json",
            "AMOS_Human_Intelligence_Engine_v0.json",
            "AMOS_Os_Agent_v0.json",
        ]
        
        for filename in core_files:
            filepath = LEGACY_BRAIN_PATH / filename
            if filepath.exists():
                engine = self._load_engine(filepath)
                if engine:
                    self.engines[engine.name] = engine
        
        self.loaded = True
        return self.engines
    
    def load_canonical_laws(self) -> dict[str, Any]:
        """Load canonical laws."""
        laws_path = LEGACY_BRAIN_PATH / "Canonical_Laws"
        if laws_path.exists():
            for law_file in laws_path.glob("*.json"):
                with open(law_file, 'r', encoding='utf-8') as f:
                    self.canonical_laws[law_file.stem] = json.load(f)
        return self.canonical_laws
    
    def load_domain_intelligences(self) -> dict[str, CognitiveEngine]:
        """Load domain-specific intelligence engines."""
        intelligences_path = LEGACY_BRAIN_PATH / "7_Intelligents"
        domain_engines = {}
        
        if intelligences_path.exists():
            for intel_file in intelligences_path.glob("*.json"):
                engine = self._load_engine(intel_file)
                if engine:
                    domain_engines[engine.name] = engine
        
        return domain_engines
    
    def _load_engine(self, filepath: Path) -> Optional[CognitiveEngine]:
        """Load a single engine from JSON."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract metadata
            first_key = list(data.keys())[0] if data else None
            if not first_key:
                return None
            
            meta = data[first_key].get("meta", {})
            
            return CognitiveEngine(
                name=meta.get("codename", filepath.stem),
                version=meta.get("version", "0.0.0"),
                description=meta.get("description", ""),
                core_laws=data[first_key].get("layer_1_meta_logic_kernel", {}).get("core_laws", {}),
                layers={k: v for k, v in data[first_key].items() if k.startswith("layer_")},
                raw_data=data
            )
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None
    
    def get_all_laws(self) -> list[str]:
        """Get all available laws across all engines."""
        laws = []
        for engine in self.engines.values():
            laws.extend(engine.core_laws.keys())
        return laws
    
    def apply_law(self, engine_name: str, law_name: str, context: dict) -> dict:
        """Apply a specific law from an engine to context."""
        if engine_name not in self.engines:
            return {"error": f"Engine {engine_name} not found"}
        
        engine = self.engines[engine_name]
        if law_name not in engine.core_laws:
            return {"error": f"Law {law_name} not found in {engine_name}"}
        
        law = engine.core_laws[law_name]
        
        # Apply law logic
        return {
            "engine": engine_name,
            "law": law_name,
            "description": law.get("description", ""),
            "properties": law.get("properties", []),
            "context_applied": context,
            "result": "law_evaluated"
        }


# Singleton instance
_legacy_loader: Optional[LegacyBrainLoader] = None


def get_legacy_brain_loader() -> LegacyBrainLoader:
    """Get the singleton legacy brain loader."""
    global _legacy_loader
    if _legacy_loader is None:
        _legacy_loader = LegacyBrainLoader()
    return _legacy_loader


def activate_legacy_brain() -> dict[str, Any]:
    """Activate all legacy brain components."""
    loader = get_legacy_brain_loader()
    
    engines = loader.load_core_engines()
    laws = loader.load_canonical_laws()
    domain_engines = loader.load_domain_intelligences()
    
    return {
        "status": "activated",
        "core_engines": list(engines.keys()),
        "canonical_laws": list(laws.keys()),
        "domain_intelligences": list(domain_engines.keys()),
        "total_laws": len(loader.get_all_laws())
    }


if __name__ == "__main__":
    result = activate_legacy_brain()
    print(f"Legacy Brain Activation: {result}")
