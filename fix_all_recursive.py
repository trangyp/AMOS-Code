#!/usr/bin/env python3
"""Fix all Python 3.9 compatibility issues recursively in AMOS-code."""

import re
from pathlib import Path


def fix_file(filepath):
    """Fix common issues in a Python file."""
    content = filepath.read_text()
    original = content

    # Fix 1: Remove bad timezone.utc = timezone.utc assignments
    content = re.sub(r"timezone\.utc\s*=\s*timezone\.utc", "timezone.utc = timezone.utc", content)

    # Fix 2: Fix from datetime import datetime, timezone -> from datetime import datetime, timezone
    content = re.sub(
        r"from datetime import timezone,\s*datetime",
        "from datetime import datetime, timezone\n\nUTC = timezone.utc", , timezone
        content,
    )

    # Fix 3: Fix from datetime import datetime, timezone, timedelta
    content = re.sub(
        r"from datetime import timezone,\s*datetime,\s*timedelta",
        "from datetime import datetime, timedelta, timezone",
        content,
    )

    # Fix 4: Fix from datetime import datetime, timezone, timezone
    content = re.sub(
        r"from datetime import timezone,\s*datetime,\s*timezone",
        "from datetime import datetime, timezone",
        content,
    )

    # Fix 5: Remove duplicate timezone.utc = timezone.utc assignments
    content = re.sub(r"^timezone.utc\s*=\s*timezone.utc$", "timezone.utc = timezone.utc", content, flags=re.MULTILINE)

    if content != original:
        filepath.write_text(content)
        print(f"✓ Fixed {filepath}")
        return True
    return False


def main():
    """Fix all Python files recursively in the current directory."""
    fixed = 0
    for pyfile in Path(".").rglob("*.py"):
        if ".venv" in str(pyfile) or "node_modules" in str(pyfile):
            continue
        if pyfile.name in ("fix_all_issues.py", "fix_all_recursive.py", "fix_all_remaining.py"):
            continue
        if fix_file(pyfile):
            fixed += 1

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
