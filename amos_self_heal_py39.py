#!/usr/bin/env python3
"""AMOS Self-Healing Script: Fix Python 3.9 Compatibility Issues"""

import re
from pathlib import Path

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
    # with UTC = timezone.utc added after imports
    pattern1 = r"from datetime import UTC,?\s*datetime|from datetime import datetime,?\s*UTC"
    if re.search(pattern1, content):
        # Replace the import line
        content = re.sub(
            pattern1,
            "from datetime import datetime, timezone",
            content
        )
        # Add UTC = timezone.utc after the import line if not present
        if "UTC = timezone.utc" not in content and "UTC=timezone.utc" not in content:
            content = re.sub(
                r"(from datetime import datetime, timezone)",
                r"\1\nUTC = timezone.utc",
                content
            )
    
    # Pattern 2: from datetime import UTC (without datetime)
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
    """Find and fix all files with datetime.UTC issues."""
    fixed = 0
    errors = []
    
    for filepath in REPO.rglob("*.py"):
        # Skip directories
        if any(part in str(filepath) for part in SKIP_DIRS):
            continue
        
        try:
            if fix_file(filepath):
                fixed += 1
                if fixed <= 10:  # Print first 10 for verification
                    print(f"✓ Fixed: {filepath.relative_to(REPO)}")
        except Exception as e:
            errors.append((filepath, e))
    
    print(f"\n{'='*50}")
    print(f"Total files fixed: {fixed}")
    if errors:
        print(f"Errors: {len(errors)}")
        for fp, e in errors[:5]:
            print(f"  ✗ {fp}: {e}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
