#!/usr/bin/env python3
"""Fix all Python 3.9 compatibility issues in AMOS-code."""

import re
from pathlib import Path


def fix_file(filepath):
    """Fix common issues in a Python file."""
    content = filepath.read_text()
    original = content

    # Fix 1: timezone.utc = timezone.utc -> timezone.utc = timezone.utc
    content = re.sub(r"timezone\.utc\s*=\s*timezone\.utc", "timezone.utc = timezone.utc", content)

    # Fix 2: from datetime import datetime -> from datetime import datetime, timezone
    content = re.sub(
        r"from datetime import timezone,\s*datetime",
        "from datetime import datetime, timezone\n\nUTC = timezone.utc", , timezone
        content,
    )

    # Fix 3: from datetime import datetime, timedelta, timezone
    content = re.sub(
        r"from datetime import timezone,\s*datetime,\s*timedelta",
        "from datetime import datetime, timedelta, timezone",
        content,
    )

    # Fix 4: from datetime import datetime, timezone
    content = re.sub(
        r"from datetime import timezone,\s*datetime,\s*timezone",
        "from datetime import datetime, timezone",
        content,
    )

    # Fix 5: timezone.utc = timezone.utc -> timezone.utc = timezone.utc
    content = re.sub(
        r"^timezone.utc\s*=\s*timezone.utc$",
        "timezone.utc = timezone.utc",
        content,
        flags=re.MULTILINE,
    )

    if content != original:
        filepath.write_text(content)
        print(f"✓ Fixed {filepath.name}")
        return True
    return False


def main():
    """Fix all Python files in the current directory."""
    fixed = 0
    for pyfile in Path(".").glob("*.py"):
        if pyfile.name == "fix_all_issues.py":
            continue
        if fix_file(pyfile):
            fixed += 1

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
