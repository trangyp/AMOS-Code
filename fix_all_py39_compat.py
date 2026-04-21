#!/usr/bin/env python3
"""Fix all Python 3.9 compatibility issues in the AMOS codebase."""

import re
from pathlib import Path


def fix_file(filepath):
    """Fix Python 3.9 compatibility issues in a file."""
    content = filepath.read_text()
    original = content

    # Pattern 1: from datetime import datetime, timezone
    content = re.sub(
        r"from datetime import datetime, timezone
UTC = timezone.utc,\s*datetime,\s*timezone",
        "from datetime import datetime, timezone",
        content,
    )

    # Pattern 2: from datetime import datetime, timezone
    content = re.sub(
        r"from datetime import datetime,\s*timezone\s*=\s*UTC",
        "from datetime import datetime, timezone\nUTC = timezone.utc",
        content,
    )

    # Pattern 3: from datetime import timezone
    content = re.sub(
        r"from datetime import datetime, timezone
UTC = timezone.utc\s*$",
        "from datetime import timezone\nUTC = timezone.utc",
        content,
        flags=re.MULTILINE,
    )

    # Pattern 4: UTC = UTC (standalone line after import)
    content = re.sub(r"^UTC\s*=\s*UTC\s*$", "UTC = timezone.utc", content, flags=re.MULTILINE)

    if content != original:
        filepath.write_text(content)
        return True
    return False


def main():
    repo = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    fixed = 0

    for filepath in repo.rglob("*.py"):
        if any(part in str(filepath) for part in [".venv", "__pycache__", ".git", "node_modules"]):
            continue

        try:
            if fix_file(filepath):
                fixed += 1
                print(f"Fixed: {filepath.relative_to(repo)}")
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
