#!/usr/bin/env python3
"""Consolidate AMOS engines and remove duplicates."""

import json
import shutil
from pathlib import Path

REPO = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_AMOS_CANON")

# Engine paths that are duplicates
COGNITIVE_DIR = REPO / "Cognitive"
INTELLIGENTS_DIR = REPO / "Core" / "7_Intelligents"


def consolidate_engines():
    """Remove duplicate engines between Cognitive/ and Core/7_Intelligents/."""
    print("="*60)
    print("AMOS ENGINE CONSOLIDATION")
    print("="*60)
    
    # Check directories
    if not COGNITIVE_DIR.exists():
        print(f"❌ Missing: {COGNITIVE_DIR}")
        return
    if not INTELLIGENTS_DIR.exists():
        print(f"❌ Missing: {INTELLIGENTS_DIR}")
        return
    
    # Find duplicate engines
    cognitive_engines = {f.name for f in COGNITIVE_DIR.glob("*.json")}
    intelligents_engines = {f.name for f in INTELLIGENTS_DIR.glob("*.json")}
    
    duplicates = cognitive_engines & intelligents_engines
    
    print(f"\n[1] Found {len(cognitive_engines)} in Cognitive/")
    print(f"[2] Found {len(intelligents_engines)} in Core/7_Intelligents/")
    print(f"[3] Duplicates: {len(duplicates)}")
    
    # Remove duplicates from Cognitive/ (keep Core/7_Intelligents/)
    if duplicates:
        print(f"\n[4] Removing duplicates from Cognitive/...")
        for dup in sorted(duplicates):
            dup_path = COGNITIVE_DIR / dup
            try:
                dup_path.unlink()
                print(f"   ✅ Removed: {dup}")
            except Exception as e:
                print(f"   ❌ Error removing {dup}: {e}")
    
    # Remove empty Cognitive/ directory
    remaining = list(COGNITIVE_DIR.glob("*.json"))
    if not remaining:
        print(f"\n[5] Removing empty Cognitive/ directory...")
        shutil.rmtree(COGNITIVE_DIR)
        print(f"   ✅ Removed: {COGNITIVE_DIR.name}/")
    else:
        print(f"\n[5] Keeping {len(remaining)} unique engines in Cognitive/")
    
    # Create master engine manifest
    print(f"\n[6] Creating master engine manifest...")
    
    # Collect all engines
    all_engines = []
    
    # Core engines
    core_dir = REPO / "Core"
    for engine in sorted(core_dir.glob("AMOS_*_Engine_v0.json")):
        all_engines.append({
            "name": engine.stem,
            "category": "Core",
            "path": str(engine.relative_to(REPO)),
            "type": "cognitive"
        })
    
    # 7_Intelligents engines
    for engine in sorted(INTELLIGENTS_DIR.glob("*.json")):
        all_engines.append({
            "name": engine.stem,
            "category": "7_Intelligents",
            "path": str(engine.relative_to(REPO)),
            "type": "intelligent"
        })
    
    # Speed engine
    speed_engine = REPO / "AMOS_Speed_Engine_v0.json"
    if speed_engine.exists():
        all_engines.append({
            "name": "AMOS_Speed_Engine_v0",
            "category": "Speed",
            "path": "AMOS_Speed_Engine_v0.json",
            "type": "optimization"
        })
    
    # Save manifest
    manifest = {
        "version": "1.0",
        "total_engines": len(all_engines),
        "engines": all_engines,
        "categories": list(set(e["category"] for e in all_engines))
    }
    
    manifest_path = REPO / "_MASTER_ENGINE_MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"   ✅ Created: {manifest_path.name}")
    print(f"   📊 Total engines: {len(all_engines)}")
    
    # Print summary
    print("\n" + "="*60)
    print("ENGINE CONSOLIDATION COMPLETE")
    print("="*60)
    for cat in sorted(set(e["category"] for e in all_engines)):
        count = sum(1 for e in all_engines if e["category"] == cat)
        print(f"   📁 {cat}: {count} engines")


if __name__ == "__main__":
    consolidate_engines()
