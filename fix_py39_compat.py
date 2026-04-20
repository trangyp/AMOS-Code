#!/usr/bin/env python3
"""Fix Python 3.9 compatibility - UTC import issues."""

import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix UTC imports in a single file."""
    content = filepath.read_text()
    original = content

    # Pattern 1: from datetime import datetime, timezone, timezone
    # Replace with: from datetime import datetime, timezone\nUTC = timezone.utc
    pattern1 = r'from datetime import UTC,\s*datetime,\s*timezone'
    replacement1 = 'from datetime import datetime, timezone\nUTC = timezone.utc'
    content = re.sub(pattern1, replacement1, content)

    # Pattern 2: from datetime import UTC, timezone
    pattern2 = r'from datetime import UTC,\s*timezone'
    content = re.sub(pattern2, replacement1, content)

    # Pattern 3: from datetime import UTC
    pattern3 = r'from datetime import UTC'
    content = re.sub(pattern3, 'from datetime import timezone\nUTC = timezone.utc', content)

    # Pattern 4: from datetime import ..., UTC, ...
    # Handle cases where UTC is in the middle of imports
    pattern4 = r'from datetime import\s+([^,]+,\s*)*UTC\s*,\s*([^\n]+)'
    def replacer4(m):
        imports = m.group(0).replace('UTC,', '').replace(', UTC', '').replace('UTC', '')
        imports = imports.replace('from datetime import ,', 'from datetime import ')
        imports = re.sub(r',\s*,', ',', imports)
        imports = imports.strip()
        return f"{imports}\nUTC = timezone.utc"
    content = re.sub(pattern4, replacer4, content)

    if content != original:
        filepath.write_text(content)
        return True
    return False


def main():
    """Fix all Python files in the repository."""
    repo_root = Path(__file__).parent
    fixed_count = 0

    # Only fix files in amos_brain first (critical path)
    for pyfile in (repo_root / "amos_brain").rglob("*.py"):
        if fix_file(pyfile):
            fixed_count += 1
            print(f"Fixed: {pyfile.relative_to(repo_root)}")

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
