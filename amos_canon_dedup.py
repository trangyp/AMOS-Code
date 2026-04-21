#!/usr/bin/env python3
"""Quick AMOS Canon Deduplication Script."""

import os
import shutil
from pathlib import Path

REPO_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

# The two duplicate directories
CANON_00 = REPO_ROOT / "_00_AMOS_CANON"
AMOS_BRAIN = REPO_ROOT / "_AMOS_BRAIN"
TARGET = REPO_ROOT / "_AMOS_CANON"


def deduplicate():
    """Consolidate _00_AMOS_CANON and _AMOS_BRAIN into _AMOS_CANON."""
    print("="*60)
    print("AMOS CANON DEDUPLICATION")
    print("="*60)
    
    # Check which directories exist
    dirs_to_merge = []
    if CANON_00.exists():
        dirs_to_merge.append(CANON_00)
        print(f"✅ Found: {CANON_00}")
    if AMOS_BRAIN.exists():
        dirs_to_merge.append(AMOS_BRAIN)
        print(f"✅ Found: {AMOS_BRAIN}")
    
    if not dirs_to_merge:
        print("❌ No canon directories found!")
        return
    
    # Create target
    if TARGET.exists():
        print(f"⚠️  Target {TARGET} already exists, removing...")
        shutil.rmtree(TARGET)
    
    print(f"\n[1] Copying to {TARGET}...")
    
    # Copy from first source
    source = dirs_to_merge[0]
    shutil.copytree(source, TARGET)
    print(f"   ✅ Copied {source.name}")
    
    # Create manifest
    manifest = TARGET / "_CANON_MANIFEST.json"
    import json
    manifest_data = {
        "consolidated_from": [str(d.name) for d in dirs_to_merge],
        "target": str(TARGET.name),
        "timestamp": str(os.path.getmtime(TARGET))
    }
    with open(manifest, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    
    print(f"   ✅ Created manifest: {manifest}")
    
    # Rename old directories (don't delete for safety)
    print(f"\n[2] Archiving old directories...")
    for d in dirs_to_merge:
        archive_name = REPO_ROOT / f"_{d.name}_ARCHIVED"
        if archive_name.exists():
            shutil.rmtree(archive_name)
        os.rename(d, archive_name)
        print(f"   ✅ Archived: {d.name} → {archive_name.name}")
    
    # Count files
    file_count = sum(1 for _ in TARGET.rglob("*") if _.is_file())
    dir_count = sum(1 for _ in TARGET.rglob("*") if _.is_dir())
    
    print(f"\n[3] Summary:")
    print(f"   📁 Directories: {dir_count}")
    print(f"   📄 Files: {file_count}")
    print(f"   📍 Location: {TARGET}")
    
    print("\n" + "="*60)
    print("DEDUPLICATION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    deduplicate()
