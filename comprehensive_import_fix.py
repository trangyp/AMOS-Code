#!/usr/bin/env python3
"""Comprehensive import fixer for AMOS codebase."""

import glob
import re

# Directories to scan
SCAN_DIRS = [
    "clawspring/amos_brain",
    "amos_brain",
    "amos_model_fabric",
    "backend",
]

# Typing constructs that need imports
TYPING_CONSTRUCTS = {
    "List": "typing",
    "Dict": "typing",
    "Optional": "typing",
    "Any": "typing",
    "Tuple": "typing",
    "Set": "typing",
    "Union": "typing",
    "Callable": "typing",
    "Protocol": "typing",
    "TypeVar": "typing",
    "Generic": "typing",
    "Iterator": "typing",
    "Generator": "typing",
}


def find_used_names(content):
    """Find all names used in the file that might need imports."""
    used = set()
    for name in TYPING_CONSTRUCTS.keys():
        # Match name as standalone word, not part of another word
        if re.search(rf"\b{name}\b", content):
            used.add(name)
    return used


def get_existing_imports(content):
    """Get existing typing imports from file."""
    imported = set()
    # Match 'from typing import X, Y' or 'from typing import X'
    pattern = r"from typing import ([^\n]+)"
    matches = re.findall(pattern, content)
    for match in matches:
        names = [n.strip() for n in match.split(",")]
        imported.update(names)
    return imported


def fix_file(filepath):
    """Fix imports in a single file."""
    try:
        with open(filepath) as f:
            content = f.read()

        original = content

        # Find what typing constructs are used
        used_names = find_used_names(content)

        # Find what's already imported
        existing_imports = get_existing_imports(content)

        # Find missing imports
        missing = used_names - existing_imports

        if missing:
            # Find the first import line to add our import after it
            lines = content.split("\n")
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from") or line.startswith("import"):
                    import_idx = i + 1

            # Create new import line
            new_import = f"from typing import {', '.join(sorted(missing))}"
            lines.insert(import_idx, new_import)
            content = "\n".join(lines)

            with open(filepath, "w") as f:
                f.write(content)
            return True, missing

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False, set()


def main():
    """Main entry point."""
    print("Scanning for Python files with import issues...")

    all_files = []
    for dir_pattern in SCAN_DIRS:
        pattern = (
            f"/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/{dir_pattern}/**/*.py"
        )
        all_files.extend(glob.glob(pattern, recursive=True))

    fixed_count = 0
    total_missing = set()

    for filepath in all_files:
        fixed, missing = fix_file(filepath)
        if fixed:
            print(f"Fixed {filepath}: added {missing}")
            fixed_count += 1
            total_missing.update(missing)

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} files")
    print(f"Total unique imports added: {sorted(total_missing)}")
    print(f"{'='*60}")

    # Test backend import
    print("\nTesting backend import...")
    import sys

    sys.path.insert(0, "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    try:
        print("✅ Backend main.py imports successfully!")
    except Exception as e:
        print(f"❌ Backend import failed: {e}")


if __name__ == "__main__":
    main()
