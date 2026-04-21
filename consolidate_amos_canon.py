#!/usr/bin/env python3
"""AMOS CANON Consolidation Tool

Consolidates duplicate _AMOS_CANON directories across all 6 repos.
Creates canonical master in root _00_AMOS_CANON/ and manages symlinks.

Usage:
    python consolidate_amos_canon.py --analyze
    python consolidate_amos_canon.py --consolidate
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
from pathlib import Path
from typing import dict, list, tuple

REPO_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

# All _AMOS_CANON locations
CANON_LOCATIONS = [
    "_00_AMOS_CANON",
    "_AMOS_BRAIN",
    "AMOS_REPOS/AMOS-Code/_00_AMOS_CANON",
    "AMOS_REPOS/AMOS-Consulting/_AMOS_CANON",
    "AMOS_REPOS/AMOS-Claws/_AMOS_CANON",
    "AMOS_REPOS/AMOS-Invest/_AMOS_CANON",
    "AMOS_REPOS/AMOS-Invest/_AMOS-SYSTEM-main/_AMOS_CANON",
    "AMOS_REPOS/Mailinhconect/_AMOS_CANON",
    "AMOS_REPOS/Mailinhconect/_AMOS-SYSTEM-main/_AMOS_CANON",
    "AMOS_REPOS/Mailinhconect/_AMOS-SYSTEM-main/_00_AMOS_CANON",
    "AMOS_REPOS/AMOS-UNIVERSE/MAIN/SYSTEMS/CORE/AMOS_CORE_SYSTEMS/FOUNDATION/00_AMOS_CANON_",
]


class CanonConsolidator:
    """Consolidate _AMOS_CANON directories."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.root = REPO_ROOT
        self.master = self.root / "_00_AMOS_CANON"
        self.found: list[Path] = []
        self.duplicates: list[tuple[Path, Path]] = []
        
    def scan(self) -> None:
        """Scan for all _AMOS_CANON directories."""
        print("=" * 70)
        print("AMOS CANON CONSOLIDATION - SCAN")
        print("=" * 70)
        
        for loc in CANON_LOCATIONS:
            path = self.root / loc
            if path.exists():
                self.found.append(path)
                size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                files = len(list(path.rglob("*")))
                print(f"  ✓ {loc}")
                print(f"    Files: {files}, Size: {size / 1024:.1f} KB")
            else:
                print(f"  ✗ {loc} (not found)")
                
        print(f"\nTotal found: {len(self.found)} locations")
        
    def analyze_duplicates(self) -> None:
        """Analyze duplicate files."""
        print("\n" + "=" * 70)
        print("ANALYZING DUPLICATES")
        print("=" * 70)
        
        # Check AMOS.brain files
        brain_files = []
        for loc in self.found:
            brain = loc / "AMOS_DESIGNER_OS" / "AMOS.brain"
            if brain.exists():
                brain_files.append(brain)
                
        print(f"\nAMOS.brain files found: {len(brain_files)}")
        
        for i, f1 in enumerate(brain_files):
            for f2 in brain_files[i+1:]:
                if filecmp.cmp(f1, f2, shallow=False):
                    print(f"  ✓ Identical: {f1.name}")
                else:
                    print(f"  ✗ Different: {f1.parent.parent.name}")
                    size1 = f1.stat().st_size
                    size2 = f2.stat().st_size
                    print(f"    {f1.parent.parent.name}: {size1} bytes")
                    print(f"    {f2.parent.parent.name}: {size2} bytes")
                    
    def consolidate(self) -> None:
        """Consolidate to master location."""
        print("\n" + "=" * 70)
        print("CONSOLIDATION")
        print("=" * 70)
        
        if self.dry_run:
            print("[DRY RUN - No changes made]")
            
        # Ensure master exists
        if not self.master.exists():
            print(f"❌ Master not found: {self.master}")
            return
            
        # Create symlink script for repos
        script_lines = ["#!/bin/bash", "# AMOS CANON Symlink Setup", ""]
        
        for loc in CANON_LOCATIONS[2:]:  # Skip master and _AMOS_BRAIN
            path = self.root / loc
            if path.exists() and path != self.master:
                script_lines.append(f"# {loc}")
                script_lines.append(f"rm -rf \"{path}\"")
                rel_path = os.path.relpath(self.master, path.parent)
                script_lines.append(f"ln -s \"{rel_path}\" \"{path}\"")
                script_lines.append("")
                
        script_path = self.root / "setup_canon_symlinks.sh"
        if not self.dry_run:
            script_path.write_text("\n".join(script_lines))
            script_path.chmod(0o755)
            
        print(f"\n✓ Created: {script_path}")
        print("Run with: ./setup_canon_symlinks.sh")
        
    def report(self) -> None:
        """Generate consolidation report."""
        print("\n" + "=" * 70)
        print("CONSOLIDATION REPORT")
        print("=" * 70)
        print(f"Master location: {self.master}")
        print(f"Duplicate locations: {len(self.found) - 1}")
        print(f"\nRecommended action:")
        print(f"  1. Keep: {self.master}")
        print(f"  2. Replace others with symlinks to master")
        print(f"  3. Run: ./setup_canon_symlinks.sh")


def main():
    parser = argparse.ArgumentParser(description="AMOS CANON Consolidation")
    parser.add_argument("--analyze", action="store_true", help="Analyze duplicates")
    parser.add_argument("--consolidate", action="store_true", help="Consolidate")
    parser.add_argument("--execute", action="store_true", help="Actually make changes")
    args = parser.parse_args()
    
    dry_run = not args.execute
    consolidator = CanonConsolidator(dry_run=dry_run)
    
    consolidator.scan()
    
    if args.analyze or args.consolidate:
        consolidator.analyze_duplicates()
        
    if args.consolidate:
        consolidator.consolidate()
        
    consolidator.report()


if __name__ == "__main__":
    main()
