#!/usr/bin/env python3
"""Fix timezone.utc to timezone.utc for Python 3.9 compatibility."""

from pathlib import Path


def fix_file(filepath):
    """Fix timezone.utc usage in a single file."""
    content = filepath.read_text()
    original = content

    # Check if file uses timezone.utc
    if "timezone.utc" not in content:
        return False

    # Fix 1: Replace timezone.utc with timezone.utc
    content = content.replace("timezone.utc", "timezone.utc")

    # Fix 2: Add timezone import if missing
    if "timezone" not in content or "from datetime import" not in content:
        # Check if datetime is imported
        if "from datetime import datetime" in content and "timezone" not in content:
            content = content.replace(
                "from datetime import datetime", "from datetime import datetime, timezone"
            )
        elif "import datetime" in content and "from datetime import timezone" not in content:
            # Add timezone import after datetime import
            content = content.replace(
                "import datetime", "import datetime\nfrom datetime import timezone"
            )

    if content != original:
        filepath.write_text(content)
        return True
    return False


def main():
    """Find and fix all files with timezone.utc."""
    repo = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    fixed = 0
    errors = []

    # Find all Python files
    for filepath in repo.rglob("*.py"):
        # Skip .venv and other cache dirs
        if any(part in str(filepath) for part in [".venv", "__pycache__", ".git", "node_modules"]):
            continue

        try:
            if fix_file(filepath):
                fixed += 1
                print(f"Fixed: {filepath.relative_to(repo)}")
        except Exception as e:
            errors.append(f"{filepath}: {e}")

    print(f"\nFixed {fixed} files")
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors[:10]:
            print(f"  {err}")


if __name__ == "__main__":
    main()
