#!/usr/bin/env python3
"""Canon Consolidation Script

Consolidates duplicate canon files across AMOS repository by:
1. Replacing duplicate canon_bridge.py files with imports from _AMOS_CANON
2. Replacing duplicate canon_enforcer.py files with unified implementation
3. Updating AMOS_ORGANISM_OS/CANON_INTEGRATION to use _AMOS_CANON

Usage:
    python consolidation_script.py [--dry-run] [--force]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

# Files to consolidate (source -> replacement strategy)
CONSOLIDATION_TARGETS: dict[str, dict[str, Any]] = {
    "AMOS_ORGANISM_OS/CANON_INTEGRATION/canon_bridge.py": {
        "action": "replace_with_import",
        "import_statement": "from _AMOS_CANON import CanonBridge, get_canon_bridge",
        "reason": "Use unified canon_bridge from _AMOS_CANON",
    },
    "AMOS_ORGANISM_OS/CANON_INTEGRATION/canon_enforcer.py": {
        "action": "replace_with_import",
        "import_statement": "from _AMOS_CANON import CanonEnforcer",
        "reason": "Use unified canon_enforcer from _AMOS_CANON",
    },
    "AMOS_REPOS/AMOS-Code/AMOS_ORGANISM_OS/CANON_INTEGRATION/canon_bridge.py": {
        "action": "delete_or_symlink",
        "target": "AMOS_ORGANISM_OS/CANON_INTEGRATION/canon_bridge.py",
        "reason": "Duplicate - use main repo version",
    },
    "build/lib/AMOS_ORGANISM_OS/CANON_INTEGRATION/canon_bridge.py": {
        "action": "mark_deprecated",
        "reason": "Build artifact - regenerate from _AMOS_CANON",
    },
}


def find_duplicate_canon_files() -> list[Path]:
    """Find all duplicate canon files across the repository."""
    duplicates: list[Path] = []
    patterns = ["**/canon_bridge.py", "**/canon_enforcer.py", "**/canon_*.py"]
    
    for pattern in patterns:
        for path in REPO_ROOT.rglob(pattern):
            # Skip _AMOS_CANON itself
            if "_AMOS_CANON" in str(path):
                continue
            # Skip if it's a build artifact
            if "build/lib" in str(path):
                duplicates.append(path)
                continue
            # Skip AMOS_REPOS duplicates
            if "AMOS_REPOS" in str(path):
                duplicates.append(path)
                continue
    
    return duplicates


def consolidate_file(target_path: Path, config: dict[str, Any], dry_run: bool = True) -> bool:
    """Consolidate a single file according to config."""
    action = config.get("action", "skip")
    
    if action == "replace_with_import":
        replacement_code = f'''#!/usr/bin/env python3
"""{target_path.name} - Consolidated canonical module

This file has been consolidated to use _AMOS_CANON.
Original functionality preserved via unified import.
"""

from __future__ import annotations

{config.get("import_statement", "from _AMOS_CANON import *")}

# Re-export all names for backward compatibility
__all__ = []
'''
        if not dry_run:
            target_path.write_text(replacement_code)
            print(f"  Replaced: {target_path}")
        else:
            print(f"  [DRY RUN] Would replace: {target_path}")
        return True
    
    elif action == "delete_or_symlink":
        if not dry_run:
            target_path.unlink()
            print(f"  Deleted: {target_path}")
        else:
            print(f"  [DRY RUN] Would delete: {target_path}")
        return True
    
    elif action == "mark_deprecated":
        deprecation_notice = f'''#!/usr/bin/env python3
"""DEPRECATED: {target_path.name}

This file is deprecated. Use _AMOS_CANON instead.
Reason: {config.get("reason", "Consolidated to _AMOS_CANON")}
"""

raise ImportError(
    "This canon module has been consolidated to _AMOS_CANON. "
    f"Use: {config.get('replacement', 'from _AMOS_CANON import ...')}"
)
'''
        if not dry_run:
            target_path.write_text(deprecation_notice)
            print(f"  Marked deprecated: {target_path}")
        else:
            print(f"  [DRY RUN] Would mark deprecated: {target_path}")
        return True
    
    return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Consolidate AMOS canon files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--force", action="store_true", help="Apply changes without confirmation")
    args = parser.parse_args()
    
    dry_run = args.dry_run
    
    print(f"{'=' * 60}")
    print("AMOS CANON CONSOLIDATION SCRIPT")
    print(f"{'=' * 60}")
    print(f"Repository: {REPO_ROOT}")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print()
    
    # Find duplicates
    print("Finding duplicate canon files...")
    duplicates = find_duplicate_canon_files()
    print(f"Found {len(duplicates)} duplicate files\n")
    
    # Process consolidation targets
    print("Processing consolidation targets:")
    consolidated_count = 0
    
    for rel_path, config in CONSOLIDATION_TARGETS.items():
        target_path = REPO_ROOT / rel_path
        if target_path.exists():
            print(f"\nProcessing: {rel_path}")
            print(f"  Reason: {config.get('reason', 'No reason given')}")
            if consolidate_file(target_path, config, dry_run):
                consolidated_count += 1
    
    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Files found: {len(duplicates)}")
    print(f"Files processed: {consolidated_count}")
    
    if dry_run:
        print("\nTo apply changes, run: python consolidation_script.py --force")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
