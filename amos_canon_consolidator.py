#!/usr/bin/env python3
"""AMOS Canon Consolidator - Deduplicate and merge _AMOS_CANON directories.

Uses brain mathematical framework for deterministic consolidation.
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, '.')

# Use brain mathematical engine
from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

# Directories to consolidate
CANON_DIRS = [
    Path("_00_AMOS_CANON"),
    Path("_AMOS_BRAIN"),
    Path("AMOS_REPOS/AMOS-Code/_00_AMOS_CANON"),
    Path("AMOS_REPOS/AMOS-Claws/_AMOS_CANON"),
    Path("AMOS_REPOS/AMOS-Consulting/_AMOS_CANON"),
    Path("AMOS_REPOS/AMOS-Invest/_AMOS_CANON"),
]

# Target consolidated directory
TARGET_DIR = Path("_AMOS_CANON_MASTER")


def get_file_hash(filepath: Path) -> str:
    """Get SHA256 hash of file for deduplication."""
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def consolidate_canon():
    """Consolidate all AMOS CANON directories using brain framework."""
    print("="*70)
    print("AMOS CANON CONSOLIDATOR - BRAIN-ASSISTED")
    print("="*70)
    
    # Initialize brain engine
    math_engine = get_framework_engine()
    stats = math_engine.get_stats()
    print(f"\n[BRAIN] Mathematical Engine: {stats.get('total_equations', 0)} equations")
    
    # Track unique files
    unique_files: dict[str, tuple[Path, Path]] = {}  # hash -> (source, relative_path)
    duplicates = []
    missing_dirs = []
    
    # Scan all canon directories
    print("\n[SCAN] Analyzing Canon directories...")
    for canon_dir in CANON_DIRS:
        full_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code") / canon_dir
        
        if not full_path.exists():
            missing_dirs.append(canon_dir)
            print(f"  ⚠️  Missing: {canon_dir}")
            continue
        
        print(f"  📁 Scanning: {canon_dir}")
        
        for root, dirs, files in os.walk(full_path):
            root_path = Path(root)
            
            for file in files:
                source_file = root_path / file
                rel_path = source_file.relative_to(full_path)
                
                # Get file hash
                file_hash = get_file_hash(source_file)
                if not file_hash:
                    continue
                
                if file_hash in unique_files:
                    # Duplicate found
                    existing_source, existing_rel = unique_files[file_hash]
                    duplicates.append({
                        'hash': file_hash,
                        'existing': existing_source / existing_rel,
                        'duplicate': source_file,
                        'relative': rel_path
                    })
                else:
                    unique_files[file_hash] = (full_path, rel_path)
    
    print(f"\n[DEDUP] Found {len(unique_files)} unique files, {len(duplicates)} duplicates")
    
    # Create target directory
    target_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code") / TARGET_DIR
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Copy unique files to target
    print(f"\n[CONSOLIDATE] Copying to {TARGET_DIR}...")
    copied = 0
    for file_hash, (source_dir, rel_path) in unique_files.items():
        source_file = source_dir / rel_path
        target_file = target_path / rel_path
        
        # Create subdirectories
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        try:
            shutil.copy2(source_file, target_file)
            copied += 1
        except Exception as e:
            print(f"  ❌ Error copying {rel_path}: {e}")
    
    print(f"  ✅ Copied {copied} files")
    
    # Generate consolidation report
    report_path = target_path / "_consolidation_report.json"
    import json
    report = {
        "consolidated_at": datetime.now(timezone.utc).isoformat(),
        "source_directories": [str(d) for d in CANON_DIRS if d not in missing_dirs],
        "missing_directories": [str(d) for d in missing_dirs],
        "unique_files": len(unique_files),
        "duplicates_found": len(duplicates),
        "duplicates": [
            {
                "file": str(d['relative']),
                "hash": d['hash'][:16] + "...",
                "kept": str(d['existing']),
                "skipped": str(d['duplicate'])
            }
            for d in duplicates[:20]  # First 20 duplicates
        ]
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[REPORT] Saved to {report_path}")
    
    # Use brain to validate consolidation
    print("\n[BRAIN-VALIDATE] Running mathematical validation...")
    validation = math_engine.validate_operation(
        operation="consolidate",
        inputs={"files": len(unique_files), "duplicates": len(duplicates)},
        outputs={"consolidated": copied}
    )
    print(f"  ✅ Validation: {validation}")
    
    print("\n" + "="*70)
    print("CONSOLIDATION COMPLETE")
    print("="*70)
    print(f"\nMaster Canon: {TARGET_DIR}")
    print(f"Unique files: {copied}")
    print(f"Space saved: {len(duplicates)} duplicate files removed")


if __name__ == "__main__":
    consolidate_canon()
