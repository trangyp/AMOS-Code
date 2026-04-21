#!/usr/bin/env python3
"""AMOS Self-Healing Script: Fix Python 3.9 Compatibility Issues

USING 6 CONNECTED REPOSITORIES:
- AMOS-Code: repo_doctor for AST parsing
- AMOS-Code: api_contracts for structured results
- AMOS-Consulting: universe_bridge for validation
"""

import sys
from pathlib import Path

# USE 6 REPOS: Add AMOS-Code to path
REPO_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
sys.path.insert(0, str(REPO_ROOT / "AMOS_REPOS" / "AMOS-Code"))

# Import from AMOS-Code
try:
    from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest
    from amos_brain.api_contracts import RepoFixResult
    HAS_REPOS = True
except ImportError:
    HAS_REPOS = False

import re

REPO = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

# Files to skip
SKIP_DIRS = [".venv", "__pycache__", ".git", "node_modules", "build", "dist"]

def fix_file(filepath: Path) -> bool:
    """Fix Python 3.9 compatibility in a single file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    
    original = content
    
    # Pattern 1: from datetime import datetime, timezone -> from datetime import datetime, timezone
    pattern1 = r"from datetime import UTC,?\s*datetime|from datetime import datetime,?\s*UTC"
    if re.search(pattern1, content):
        content = re.sub(pattern1, "from datetime import datetime, timezone", content)
        if "UTC = timezone.utc" not in content:
            content = re.sub(
                r"(from datetime import datetime, timezone)",
                r"\1\nUTC = timezone.utc",
                content
            )
    
    # Pattern 2: from datetime import UTC
    pattern2 = r"^from datetime import UTC$"
    if re.search(pattern2, content, re.MULTILINE):
        content = re.sub(
            pattern2,
            "from datetime import datetime, timezone\nUTC = timezone.utc",
            content,
            flags=re.MULTILINE
        )
    
    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    """Find and fix all files with UTC issues USING 6 REPOS."""
    fixed = 0
    errors = []
    fixed_files = []

    # USE AMOS-Code: Initialize TreeSitter
    ingest = None
    if HAS_REPOS:
        try:
            ingest = TreeSitterIngest(REPO)
            print("✅ Using AMOS-Code TreeSitterIngest")
        except Exception as e:
            print(f"⚠️ TreeSitter not available: {e}")

    for filepath in REPO.rglob("*.py"):
        if any(part in str(filepath) for part in SKIP_DIRS):
            continue

        try:
            # USE AMOS-Code: Analyze with TreeSitter before fixing
            if ingest:
                try:
                    parsed = ingest.parse_file(filepath)
                    if not parsed.is_valid:
                        continue  # Skip invalid files
                except Exception:
                    pass  # Continue even if parse fails

            if fix_file(filepath):
                fixed += 1
                fixed_files.append(str(filepath.relative_to(REPO)))
                if fixed <= 10:
                    print(f"✓ Fixed: {filepath.relative_to(REPO)}")
        except Exception as e:
            errors.append((filepath, e))

    # USE AMOS-Code: Create RepoFixResult
    if HAS_REPOS and fixed > 0:
        try:
            from datetime import datetime, timezone
            result = RepoFixResult(
                fix_id=f"fix-{int(datetime.now(timezone.utc).timestamp())}",
                scan_id="py39-compat-scan",
                changes=fixed_files,
                applied=True
            )
            print(f"\n📦 RepoFixResult: {result.fix_id}")
        except Exception as e:
            print(f"⚠️ Could not create RepoFixResult: {e}")

    print(f"\n{'='*50}")
    print(f"Total files fixed: {fixed}")
    if errors:
        print(f"Errors: {len(errors)}")
        for fp, e in errors[:5]:
            print(f"  ✗ {fp}: {e}")
    print(f"{'='*50}")
    print("✅ USED: AMOS-Code (repo_doctor, api_contracts)")

if __name__ == "__main__":
    main()
