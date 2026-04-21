#!/usr/bin/env python3
"""Fix all UTC import issues for Python 3.9 compatibility."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent


def fix_utc_imports(filepath: Path):
    """Fix UTC imports in a file."""
    content = filepath.read_text()
    original = content

    # Pattern: from datetime import datetime, timezone, timezone
    # -> from datetime import datetime, timezone\nUTC = timezone.utc

    # Handle various patterns
    patterns = [
        (r'from datetime import datetime, timezone, timezone',
         'from datetime import datetime, timezone\nUTC = timezone.utc'),
        (r'from datetime import datetime, timezone, timedelta, timezone',
         'from datetime import datetime, timedelta, timezone\nUTC = timezone.utc'),
        (r'from datetime import datetime, timezone',
         'from datetime import datetime, timezone\nUTC = timezone.utc'),
        (r'from datetime import datetime, timezone\nUTC = timezone\.utc, timezone',
         'from datetime import timezone\nUTC = timezone.utc'),
        (r'from datetime import datetime, timezone\nUTC = timezone\.utc\n',
         'from datetime import timezone\nUTC = timezone.utc\n'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Remove duplicate UTC = UTC lines
    content = re.sub(r'\nUTC = UTC\n', '\n', content)

    if content != original:
        filepath.write_text(content)
        return True
    return False


def main():
    """Fix all files."""
    fixed = 0

    # Fix amos_brain directory
    for f in (REPO_ROOT / "amos_brain").rglob("*.py"):
        try:
            if fix_utc_imports(f):
                fixed += 1
                print(f"Fixed: {f.name}")
        except Exception as e:
            print(f"Error fixing {f}: {e}")

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
