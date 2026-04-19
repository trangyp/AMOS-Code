#!/usr/bin/env python3
"""Fix Python 3.10+ union syntax for Python 3.9 compatibility."""

import os
import re
import sys

# Files to fix
FILES = [
    "amos_websocket_manager.py",
    "amos_services.py",
    "amos_structured_logging.py",
    "amos_api_versioning.py",
    "amos_async_jobs.py",
    "amos_distributed_tracing.py",
    "amos_rate_limiting.py",
    "amos_error_handling.py",
]

# Pattern: Type  -> Type
# Handles: str , dict[str, Any] , List[int] , etc.
UNION_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]*\])?)\s*\|\s*None")


def fix_file(filepath):
    """Fix a single file."""
    if not os.path.exists(filepath):
        print(f"⚠️  Not found: {filepath}")
        return False

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content

    # Find all occurrences
    matches = UNION_PATTERN.findall(content)
    if not matches:
        print(f"✅  {filepath}: No issues")
        return True

    # Replace Type  with Type
    content = UNION_PATTERN.sub(r"\1 ", content)

    # Check if Optional import exists
    has_typing_import = "from typing import" in content
    has_optional = "Optional" in original or "Optional" in content

    if has_typing_import and not has_optional:
        # Add Optional to existing typing import
        content = re.sub(
            r"(from typing import)([^\n]+)",
            lambda m: f"{m.group(1)}{m.group(2)}, Optional"
            if "Optional" not in m.group(2)
            else m.group(0),
            content,
        )
    elif not has_typing_import:
        # Add new import line
        content = "from typing import Optional\n" + content

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"🔧  {filepath}: Fixed {len(matches)} occurrences")
        return True

    return True


def main():
    print("Fixing Python 3.9 compatibility issues...")
    print("=" * 60)

    fixed_count = 0
    for filepath in FILES:
        if fix_file(filepath):
            fixed_count += 1

    print("=" * 60)
    print(f"\n✅  Fixed {fixed_count} files")

    # Test imports
    print("\nTesting imports...")
    print("-" * 60)

    for filepath in FILES:
        mod = filepath.replace(".py", "")
        try:
            __import__(mod)
            print(f"✅  {mod}")
        except SyntaxError as e:
            print(f"❌  {mod}: SyntaxError at line {e.lineno}")
        except Exception as e:
            print(f"⚠️  {mod}: {type(e).__name__}: {str(e)[:50]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
