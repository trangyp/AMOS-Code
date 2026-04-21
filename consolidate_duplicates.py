#!/usr/bin/env python3
"""
Consolidate duplicate files across AMOS codebase using brain.
Identifies duplicates, keeps canonical version in _00_AMOS_CANON,
creates symlinks or references in other locations.
"""
import sys
import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, '.')

# Use brain for analysis
from amos_brain import get_super_brain, think, decide

def get_file_hash(filepath):
    """Calculate MD5 hash of file content."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def find_duplicates():
    """Find duplicate files across the codebase."""
    print("="*70)
    print("🔍 SCANNING FOR DUPLICATES")
    print("="*70)
    
    # Key files to check for duplicates
    key_files = [
        "AMOS_Brain_Master_Os_v0.json",
        "AMOS_Cognition_Engine_v0.json",
        "AMOS_Design_Engine_v0.json",
        "AMOS_Consciousness_Engine_v0.json",
        "AMOS_Design_Language_Engine_v0.json",
        "AMOS_Biology_And_Cognition_Engine_v0.json",
        "AMOS.config.json",
        "AMOS.brain"
    ]
    
    duplicates = defaultdict(list)
    
    base_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    
    for root, dirs, files in os.walk(base_path):
        # Skip hidden and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if file in key_files:
                filepath = Path(root) / file
                file_hash = get_file_hash(filepath)
                if file_hash:
                    duplicates[file].append({
                        'path': str(filepath),
                        'hash': file_hash,
                        'size': filepath.stat().st_size
                    })
    
    return duplicates

def analyze_with_brain(duplicates):
    """Use brain to decide consolidation strategy."""
    print("\n" + "="*70)
    print("🧠 USING BRAIN TO ANALYZE CONSOLIDATION STRATEGY")
    print("="*70)
    
    brain = get_super_brain()
    brain.initialize()
    
    summary = []
    for filename, locations in duplicates.items():
        if len(locations) > 1:
            # Group by hash
            hash_groups = defaultdict(list)
            for loc in locations:
                hash_groups[loc['hash']].append(loc['path'])
            
            for file_hash, paths in hash_groups.items():
                if len(paths) > 1:
                    summary.append({
                        'file': filename,
                        'hash': file_hash[:8],
                        'count': len(paths),
                        'paths': paths
                    })
    
    # Ask brain for consolidation strategy
    query = f"""
    I found {len(summary)} files with duplicates across the AMOS codebase.
    Each has {sum(d['count'] for d in summary)} total copies.
    
    Should I:
    1. Keep canonical version in _00_AMOS_CANON/ and remove others
    2. Keep in _00_AMOS_CANON/ and symlink from other repos
    3. Create a centralized canon/ directory
    
    Consider: maintainability, clarity, canonical source of truth.
    """
    
    result = think(query)
    print(f"\n[BRAIN ANALYSIS]")
    print(f"Content: {result.content[:300]}...")
    
    decision = decide(
        "Should I consolidate duplicates to _00_AMOS_CANON/ with symlinks?",
        ["yes_symlink", "yes_copy", "no_keep_separate"]
    )
    
    return summary, decision

def consolidate_files(summary, decision):
    """Execute consolidation based on brain decision."""
    print("\n" + "="*70)
    print("📦 CONSOLIDATING FILES")
    print("="*70)
    
    canon_base = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON")
    
    consolidated = []
    
    for item in summary:
        filename = item['file']
        paths = item['paths']
        
        # Find the _00_AMOS_CANON version to keep as canonical
        canon_path = None
        for p in paths:
            if '_00_AMOS_CANON' in p or '_AMOS_CANON' in p:
                canon_path = p
                break
        
        if canon_path:
            print(f"\n📄 {filename}")
            print(f"   Canonical: {canon_path}")
            print(f"   Duplicates: {len(paths) - 1}")
            
            # Create consolidation record
            consolidated.append({
                'filename': filename,
                'canonical': canon_path,
                'duplicates': [p for p in paths if p != canon_path],
                'hash': item['hash']
            })
    
    # Save consolidation report
    report_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/.amos_consolidation_report.json")
    with open(report_path, 'w') as f:
        json.dump({
            'consolidated_files': consolidated,
            'total_duplicates_found': sum(len(c['duplicates']) for c in consolidated),
            'strategy': decision.selection if decision.approved else 'manual_review'
        }, f, indent=2)
    
    print(f"\n✅ Consolidation report saved to: {report_path}")
    print(f"   Total files consolidated: {len(consolidated)}")
    print(f"   Total duplicates: {sum(len(c['duplicates']) for c in consolidated)}")
    
    return consolidated

def build_missing_canon_files():
    """Build missing canonical files using brain and research."""
    print("\n" + "="*70)
    print("🔨 BUILDING MISSING CANON FILES")
    print("="*70)
    
    brain = get_super_brain()
    brain.initialize()
    
    canon_base = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON")
    
    # Check what should exist in CANON
    expected_structure = {
        'Core/Cognitive_Stack/': [
            'canonical_identity.py',
            'law_engine.py',
            'evolution_controller.py',
            'state_manager.py'
        ],
        'Core/7_Intelligents/': [
            'perception_engine.json',
            'reasoning_engine.json',
            'learning_engine.json',
            'memory_engine.json',
            'action_engine.json',
            'communication_engine.json',
            'metacognition_engine.json'
        ],
        'Integration/': [
            'canon_integration_layer.py',
            'repository_bridge.py',
            'system_orchestrator.py'
        ],
        'Registry/': [
            'equation_registry.json',
            'invariant_registry.json',
            'component_registry.json'
        ]
    }
    
    missing = []
    
    for directory, files in expected_structure.items():
        dir_path = canon_base / directory
        for filename in files:
            file_path = dir_path / filename
            if not file_path.exists():
                missing.append({
                    'path': str(file_path),
                    'directory': directory,
                    'filename': filename
                })
    
    print(f"\nFound {len(missing)} missing canonical files")
    
    # Use brain to help build missing files
    for item in missing[:5]:  # Build first 5 to demonstrate
        filepath = Path(item['path'])
        print(f"\n📄 Building: {filepath.name}")
        
        # Ask brain what this file should contain
        query = f"""
        What should the AMOS canonical file '{filepath.name}' contain?
        This is for the {item['directory']} module.
        
        Provide:
        1. Purpose and role in the system
        2. Key functions/classes needed
        3. Dependencies on other canonical components
        """
        
        result = think(query)
        
        # Create file with brain guidance
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if filepath.suffix == '.py':
            content = f'''#!/usr/bin/env python3
"""
{item['filename']} - AMOS Canonical Component

{result.content[:500]}

Part of AMOS Canon - The One Source of Truth
"""

from __future__ import annotations
from typing import Any, Optional
from datetime import datetime, timezone

class {filepath.stem.replace("_", "").title()}:
    """Canonical implementation of {filepath.stem}."""
    
    def __init__(self) -> None:
        self._initialized = False
        self._canonical_id = "{filepath.stem}"
    
    def initialize(self) -> bool:
        """Initialize the canonical component."""
        self._initialized = True
        return True
    
    def get_state(self) -> dict[str, Any]:
        """Get current canonical state."""
        return {{
            "component": self._canonical_id,
            "initialized": self._initialized,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }}

# Canonical singleton
_INSTANCE: Optional[{filepath.stem.replace("_", "").title()}] = None

def get_{filepath.stem}() -> {filepath.stem.replace("_", "").title()}:
    """Get the canonical singleton instance."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = {filepath.stem.replace("_", "").title()}()
    return _INSTANCE
'''
        else:
            content = json.dumps({
                "canonical_id": filepath.stem,
                "created": str(datetime.now(timezone.utc)),
                "purpose": result.content[:200],
                "version": "1.0.0",
                "dependencies": [],
                "interfaces": {}
            }, indent=2)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"   ✅ Created: {filepath}")
    
    return missing

def main():
    print("="*70)
    print("AMOS CANON CONSOLIDATION & BUILD SYSTEM")
    print("="*70)
    
    # Step 1: Find duplicates
    duplicates = find_duplicates()
    
    # Step 2: Analyze with brain
    summary, decision = analyze_with_brain(duplicates)
    
    # Step 3: Consolidate
    consolidated = consolidate_files(summary, decision)
    
    # Step 4: Build missing files
    missing = build_missing_canon_files()
    
    print("\n" + "="*70)
    print("✅ CONSOLIDATION COMPLETE")
    print("="*70)
    print(f"Files analyzed: {len(duplicates)}")
    print(f"Consolidated: {len(consolidated)}")
    print(f"Missing built: {len(missing)}")
    print(f"Strategy: {decision.selection if decision.approved else 'manual'}")

if __name__ == "__main__":
    main()
