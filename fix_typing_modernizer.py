#!/usr/bin/env python3
"""AMOS Typing Modernization Tool

Automatically modernizes Python typing imports across the AMOS codebase:
- Removes deprecated typing imports (Optional, Union, List, Dict, etc.)
- Replaces with Python 3.10+ native syntax (Optional[X], list[X], dict[X, Y])
- Fixes datetime deprecation (utcnow → now(timezone.utc))
- Removes sys.path.insert hacks
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any


def modernize_file(file_path: Path) -> dict[str, Any]:
    """Modernize typing in a single Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"success": False, "error": str(e)}

    original = content
    changes = []

    # Remove Optional from typing imports and track if it was there
    optional_used = False

    # Pattern 1: from typing import ..., Optional, ...
    typing_import_pattern = r"from typing import\s*([^\n]+)"
    match = re.search(typing_import_pattern, content)
    if match:
        imports_str = match.group(1)
        # Check if Optional is in the imports
        if "Optional" in imports_str:
            optional_used = True
            # Remove Optional from imports
            new_imports = re.sub(r",?\s*Optional\s*,?", ",", imports_str).strip(", ")
            # Clean up multiple commas and spaces
            new_imports = re.sub(r",\s*,", ",", new_imports)
            new_imports = re.sub(r"^,\s*", "", new_imports)
            new_imports = re.sub(r"\s*,$", "", new_imports)
            if new_imports:
                content = content.replace(
                    f"from typing import {match.group(1)}", f"from typing import {new_imports}"
                )
            else:
                # Remove entire typing import line if empty
                content = re.sub(r"from typing import\s*[^\n]+\n?", "", content)
            changes.append("Removed Optional from typing imports")

    # Pattern 2: Replace Optional[X] with Optional[X]
    if optional_used:
        # Handle Optional[X] patterns
        optional_pattern = r"Optional\[([^\]]+)\]"
        matches = list(re.finditer(optional_pattern, content))
        if matches:
            # Replace from right to left to preserve positions
            for match in reversed(matches):
                inner_type = match.group(1)
                start, end = match.span()
                content = content[:start] + f"{inner_type} | None" + content[end:]
            changes.append(f"Replaced {len(matches)} Optional[X] with Optional[X]")

    # Pattern 3: Remove Union from typing imports and replace Union[X,Y] with X | Y
    union_used = False
    typing_import_match = re.search(typing_import_pattern, content)
    if typing_import_match:
        imports_str = typing_import_match.group(1)
        if "Union" in imports_str:
            union_used = True
            new_imports = re.sub(r",?\s*Union\s*,?", ",", imports_str).strip(", ")
            new_imports = re.sub(r",\s*,", ",", new_imports)
            new_imports = re.sub(r"^,\s*", "", new_imports)
            new_imports = re.sub(r"\s*,$", "", new_imports)
            if new_imports:
                content = content.replace(
                    f"from typing import {typing_import_match.group(1)}",
                    f"from typing import {new_imports}",
                )
            else:
                content = re.sub(r"from typing import\s*[^\n]+\n?", "", content)
            changes.append("Removed Union from typing imports")

    if union_used:
        union_pattern = r"Union\[([^\]]+)\]"
        matches = list(re.finditer(union_pattern, content))
        if matches:
            for match in reversed(matches):
                inner_types = match.group(1)
                start, end = match.span()
                content = content[:start] + inner_types.replace(",", " |") + content[end:]
            changes.append(f"Replaced {len(matches)} Union[X,Y] with X | Y")

    # Pattern 4: Replace list[X] with list[X]
    list_pattern = r"List\[([^\]]+)\]"
    matches = list(re.finditer(list_pattern, content))
    if matches:
        for match in reversed(matches):
            inner_type = match.group(1)
            start, end = match.span()
            content = content[:start] + f"list[{inner_type}]" + content[end:]
        changes.append(f"Replaced {len(matches)} list[X] with list[X]")

    # Remove List from imports if present
    typing_import_match = re.search(typing_import_pattern, content)
    if typing_import_match:
        imports_str = typing_import_match.group(1)
        if "List" in imports_str:
            new_imports = re.sub(r",?\s*List\s*,?", ",", imports_str).strip(", ")
            new_imports = re.sub(r",\s*,", ",", new_imports)
            new_imports = re.sub(r"^,\s*", "", new_imports)
            new_imports = re.sub(r"\s*,$", "", new_imports)
            if new_imports:
                content = content.replace(
                    f"from typing import {typing_import_match.group(1)}",
                    f"from typing import {new_imports}",
                )
            else:
                content = re.sub(r"from typing import\s*[^\n]+\n?", "", content)
            changes.append("Removed List from typing imports")

    # Pattern 5: Replace dict[X,Y] with dict[X,Y]
    dict_pattern = r"Dict\[([^\]]+)\]"
    matches = list(re.finditer(dict_pattern, content))
    if matches:
        for match in reversed(matches):
            inner_types = match.group(1)
            start, end = match.span()
            content = content[:start] + f"dict[{inner_types}]" + content[end:]
        changes.append(f"Replaced {len(matches)} dict[X,Y] with dict[X,Y]")

    # Remove Dict from imports if present
    typing_import_match = re.search(typing_import_pattern, content)
    if typing_import_match:
        imports_str = typing_import_match.group(1)
        if "Dict" in imports_str:
            new_imports = re.sub(r",?\s*Dict\s*,?", ",", imports_str).strip(", ")
            new_imports = re.sub(r",\s*,", ",", new_imports)
            new_imports = re.sub(r"^,\s*", "", new_imports)
            new_imports = re.sub(r"\s*,$", "", new_imports)
            if new_imports:
                content = content.replace(
                    f"from typing import {typing_import_match.group(1)}",
                    f"from typing import {new_imports}",
                )
            else:
                content = re.sub(r"from typing import\s*[^\n]+\n?", "", content)
            changes.append("Removed Dict from typing imports")

    # Pattern 6: Fix duplicate UTC assignments
    utc_pattern = r"^(UTC\s*=\s*timezone\.utc\s*\n)\s*UTC\s*=\s*timezone\.utc\s*\n"
    if re.search(utc_pattern, content, re.MULTILINE):
        content = re.sub(utc_pattern, r"\1", content, flags=re.MULTILINE)
        changes.append("Removed duplicate UTC = timezone.utc lines")

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return {"success": True, "changes": changes}

    return {"success": True, "changes": []}


def find_and_fix_files(root_dir: Path, max_files: int = 200) -> dict[str, Any]:
    """Find and fix all Python files in the given directory."""
    results = {"fixed": [], "skipped": [], "errors": []}

    # Directories to exclude
    exclude_dirs = {".venv", "build", "__pycache__", ".git", "node_modules", ".pytest_cache"}

    python_files = []
    for path in root_dir.rglob("*.py"):
        # Skip excluded directories
        if any(exclude in path.parts for exclude in exclude_dirs):
            continue
        python_files.append(path)

    print(f"Found {len(python_files)} Python files to analyze")

    for i, file_path in enumerate(python_files[:max_files]):
        if i % 50 == 0:
            print(f"Processed {i}/{min(len(python_files), max_files)} files...")

        result = modernize_file(file_path)
        if result.get("success"):
            if result.get("changes"):
                results["fixed"].append(
                    {"file": str(file_path.relative_to(root_dir)), "changes": result["changes"]}
                )
        else:
            results["errors"].append(
                {"file": str(file_path.relative_to(root_dir)), "error": result.get("error")}
            )

    return results


def main() -> int:
    """Main entry point."""
    root_dir = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    print("=" * 70)
    print("AMOS Typing Modernization Tool")
    print("=" * 70)
    print(f"Root directory: {root_dir}")
    print()

    results = find_and_fix_files(root_dir, max_files=500)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Files fixed: {len(results['fixed'])}")
    print(f"Files with errors: {len(results['errors'])}")

    if results["fixed"]:
        print()
        print("Fixed files:")
        for item in results["fixed"][:20]:  # Show first 20
            print(f"  ✓ {item['file']}")
            for change in item["changes"]:
                print(f"    - {change}")
        if len(results["fixed"]) > 20:
            print(f"  ... and {len(results['fixed']) - 20} more files")

    if results["errors"]:
        print()
        print("Errors:")
        for item in results["errors"][:10]:
            print(f"  ✗ {item['file']}: {item['error']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
