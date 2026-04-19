#!/usr/bin/env python3
"""AMOS PRIMARY_LOOP Feature Registry Handler - Integrates 1,500+ components into orchestrator."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class FeatureCapability:
    name: str
    category: str
    path: str
    status: str = "available"
    metadata: dict = field(default_factory=dict)


class PrimaryFeatureHandler:
    """Handler for AMOS_MASTER_ORCHESTRATOR PRIMARY_LOOP - discovers and activates 1,500+ features."""

    def __init__(self, organism_root: Optional[Path] = None):
        self.root = organism_root or Path(__file__).parent
        self.features: Dict[str, FeatureCapability] = {}
        self.engines: Dict[str, Any] = {}
        self.knowledge_index: Dict[str, Any] = {}
        self.activated_count = 0

    def scan_ecosystem(self) -> Dict[str, Any]:
        """Scan entire ecosystem for 1,500+ components."""
        print("[FEATURE_HANDLER] Scanning ecosystem...")

        # Scan Python runtime
        for py_file in self.root.rglob("*.py"):
            if py_file.is_file():
                rel_path = str(py_file.relative_to(self.root))
                category = "runtime"
                if "AMOS_ORGANISM_OS" in rel_path:
                    category = "organism_subsystem"
                elif "amos_brain" in rel_path:
                    category = "brain_module"
                elif "amosl" in rel_path:
                    category = "amosl_component"

                self.features[rel_path] = FeatureCapability(
                    name=py_file.stem,
                    category=category,
                    path=rel_path,
                    metadata={"size": py_file.stat().st_size},
                )

        # Scan knowledge base
        brain_root = self.root / "_AMOS_BRAIN"
        if brain_root.exists():
            for json_file in brain_root.rglob("*.json"):
                if json_file.is_file():
                    rel_path = str(json_file.relative_to(self.root))
                    name_lower = json_file.stem.lower()

                    if "engine" in name_lower:
                        self.engines[json_file.stem] = {
                            "path": rel_path,
                            "size": json_file.stat().st_size,
                        }

                    category = "knowledge"
                    if "kernel" in name_lower:
                        category = "kernel"
                    elif "pack" in name_lower:
                        category = "knowledge_pack"

                    self.features[rel_path] = FeatureCapability(
                        name=json_file.stem,
                        category=category,
                        path=rel_path,
                        metadata={"size": json_file.stat().st_size},
                    )

        stats = {
            "total_features": len(self.features),
            "runtime_modules": len([f for f in self.features.values() if f.category == "runtime"]),
            "organism_subsystems": len(
                [f for f in self.features.values() if f.category == "organism_subsystem"]
            ),
            "brain_modules": len(
                [f for f in self.features.values() if f.category == "brain_module"]
            ),
            "amosl_components": len(
                [f for f in self.features.values() if f.category == "amosl_component"]
            ),
            "engines": len(self.engines),
            "knowledge_files": len(
                [f for f in self.features.values() if "knowledge" in f.category]
            ),
            "kernels": len([f for f in self.features.values() if f.category == "kernel"]),
        }

        print(f"[FEATURE_HANDLER] Found {stats['total_features']} features")
        print(f"  - Engines: {stats['engines']}")
        print(f"  - Knowledge: {stats['knowledge_files']}")
        print(f"  - Runtime: {stats['runtime_modules']}")

        return stats

    def activate_for_cycle(self, cycle_context: Dict[str, Any]) -> Dict[str, Any]:
        """Activate relevant features for current cycle."""
        activated = {"engines": [], "knowledge": [], "capabilities": []}

        # Auto-activate based on cycle context
        current_subsystem = cycle_context.get("current_position", "01_BRAIN")

        if current_subsystem == "01_BRAIN":
            # Activate brain engines
            for name, engine in list(self.engines.items())[:5]:
                activated["engines"].append(name)
                self.activated_count += 1

        elif current_subsystem == "12_QUANTUM_LAYER":
            # Activate prediction engines
            pred_engines = [
                e for e in self.engines if "predict" in e.lower() or "quantum" in e.lower()
            ]
            activated["engines"].extend(pred_engines[:3])

        elif current_subsystem == "06_MUSCLE":
            # Activate execution engines
            exec_engines = [
                e for e in self.engines if "code" in e.lower() or "fabrication" in e.lower()
            ]
            activated["engines"].extend(exec_engines[:3])

        return activated

    def get_cycle_recommendation(self, cycle_context: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend features for next cycle based on discovered capabilities."""
        current = cycle_context.get("current_position", "01_BRAIN")

        recommendations = {
            "01_BRAIN": {
                "recommended": ["12_QUANTUM_LAYER", "06_MUSCLE"],
                "reason": "Knowledge + Execution",
            },
            "12_QUANTUM_LAYER": {
                "recommended": ["06_MUSCLE", "07_METABOLISM"],
                "reason": "Execute + Process",
            },
            "06_MUSCLE": {
                "recommended": ["07_METABOLISM", "01_BRAIN"],
                "reason": "Process + Reason",
            },
        }

        return recommendations.get(current, {"recommended": ["01_BRAIN"], "reason": "Default"})

    def export_cycle_state(self, filepath: str) -> bool:
        """Export current feature state for cycle persistence."""
        try:
            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_features": len(self.features),
                "activated_count": self.activated_count,
                "available_engines": list(self.engines.keys())[:20],
                "status": "active",
            }
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False


def demo_handler():
    """Demonstrate feature handler integration."""
    print("\n" + "=" * 60)
    print("AMOS PRIMARY_LOOP FEATURE HANDLER - DEMONSTRATION")
    print("=" * 60)

    handler = PrimaryFeatureHandler()

    print("\n[1] Scanning ecosystem...")
    stats = handler.scan_ecosystem()

    print(f"\n  Total features: {stats['total_features']}")
    print(f"  Runtime modules: {stats['runtime_modules']}")
    print(f"  Organism subsystems: {stats['organism_subsystems']}")
    print(f"  Brain modules: {stats['brain_modules']}")
    print(f"  AMOSL components: {stats['amosl_components']}")
    print(f"  Engines: {stats['engines']}")
    print(f"  Knowledge: {stats['knowledge_files']}")
    print(f"  Kernels: {stats['kernels']}")

    print("\n[2] Simulating PRIMARY_LOOP cycles...")

    cycles = [
        {"current_position": "01_BRAIN", "context": "reasoning"},
        {"current_position": "12_QUANTUM_LAYER", "context": "prediction"},
        {"current_position": "06_MUSCLE", "context": "execution"},
    ]

    for i, cycle in enumerate(cycles, 1):
        print(f"\n  Cycle {i}: {cycle['current_position']}")
        activated = handler.activate_for_cycle(cycle)
        print(f"    Activated engines: {len(activated['engines'])}")

        rec = handler.get_cycle_recommendation(cycle)
        print(f"    Recommended next: {rec['recommended']} ({rec['reason']})")

    print("\n[3] Exporting cycle state...")
    if handler.export_cycle_state("amos_feature_cycle_state.json"):
        print("    ✓ State exported")

    print("\n" + "=" * 60)
    print("✓ FEATURE HANDLER INTEGRATION COMPLETE")
    print("=" * 60)
    print(f"\nImpact: {stats['total_features']} features now accessible to PRIMARY_LOOP")
    print("Status: Ready for AMOS_MASTER_ORCHESTRATOR integration")
    print("=" * 60)


if __name__ == "__main__":
    demo_handler()
