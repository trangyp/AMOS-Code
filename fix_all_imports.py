#!/usr/bin/env python3
"""Comprehensive fix for all import issues in AMOS codebase."""

import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix all import issues in a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content
        lines = content.split("\n")
        new_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip lines that are "from typing import" inside parentheses or after an opening paren import
            if re.match(r"^from typing import", stripped):
                # Check if previous line ends with ( (we're inside a multi-line import)
                if i > 0 and lines[i - 1].strip().endswith("("):
                    i += 1
                    continue

                # Check if we're inside a try block (indented)
                if line.startswith("    ") or line.startswith("\t"):
                    # This is an indented import - likely misplaced
                    i += 1
                    continue

                # Check if next line is indented (function/class body)
                if i + 1 < len(lines) and (
                    lines[i + 1].startswith("    ") or lines[i + 1].startswith("\t")
                ):
                    # Keep it but remove duplicates
                    pass

            new_lines.append(line)
            i += 1

        content = "\n".join(new_lines)

        # Now fix duplicate typing imports on consecutive lines
        content = re.sub(
            r"(from typing import [^\n]+)\nfrom typing import ([^\n]+)",
            lambda m: f'from typing import {m.group(1).replace("from typing import ", "")}, {m.group(2)}',
            content,
        )

        # Remove duplicate items within a single import
        def dedup_import(match):
            prefix = match.group(1)
            items = match.group(2).split(",")
            seen = set()
            unique = []
            for item in items:
                item = item.strip()
                if item and item not in seen:
                    seen.add(item)
                    unique.append(item)
            return f'{prefix}{", ".join(unique)}'

        content = re.sub(r"^(from typing import )(.+)$", dedup_import, content, flags=re.MULTILINE)

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return False


def main():
    root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    fixed = 0
    checked = 0

    for py_file in root.rglob("*.py"):
        if any(part.startswith(".") or part in ["venv", "__pycache__"] for part in py_file.parts):
            continue
        checked += 1
        if fix_file(py_file):
            fixed += 1
            if fixed % 50 == 0:
                print(f"Fixed {fixed} files...")

    print(f"Checked: {checked}, Fixed: {fixed}")


if __name__ == "__main__":
    main()
