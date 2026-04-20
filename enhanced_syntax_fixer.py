#!/usr/bin/env python3
"""Enhanced Syntax Fixer - State of Art Python Repository Repair."""

import ast
import re
from pathlib import Path


def scan_syntax_errors(repo_path: str) -> list[tuple[Path, str]]:
    """Scan all Python files for syntax errors."""
    errors = []
    root = Path(repo_path).resolve()
    skip_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".ruff_cache",
        ".pytest_cache",
    }

    for path in root.rglob("*.py"):
        if any(part in skip_dirs for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            ast.parse(content)
        except SyntaxError as e:
            errors.append((path, f"Line {e.lineno}: {e.msg}"))
        except Exception as e:
            errors.append((path, str(e)))

    return sorted(errors)


def fix_file(filepath: Path) -> tuple[bool, str]:
    """Attempt to fix a file with syntax errors."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content
        lines = content.split("\n")

        # Common fixes for malformed imports
        fixes_applied = []

        # Pattern 1: Remove duplicate imports on same line
        content = re.sub(r"from typing import (\w+), \1", r"from typing import \1", content)

        # Pattern 2: Fix imports inside function bodies (move to top)
        # Find import statements that are indented
        new_lines = []
        import_lines = []
        body_lines = []
        in_import_section = True

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if this is an import inside a function/class (indented but not in a string)
            if line.startswith("    ") or line.startswith("\t"):
                if stripped.startswith(("import ", "from ")) and not in_import_section:
                    # This is an indented import - move to top later
                    import_lines.append(stripped)
                    continue

            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith('"""')
                and not stripped.startswith("from ")
                and not stripped.startswith("import ")
            ):
                in_import_section = False

            body_lines.append(line)

        # Reconstruct: add dedented imports, then body
        if import_lines:
            # Find insertion point (after other imports, before first non-import)
            insert_idx = 0
            for i, line in enumerate(body_lines):
                stripped = line.strip()
                if (
                    stripped
                    and not stripped.startswith("#")
                    and not stripped.startswith('"""')
                    and not stripped.startswith("from ")
                    and not stripped.startswith("import ")
                ):
                    insert_idx = i
                    break

            new_content = "\n".join(
                body_lines[:insert_idx] + import_lines + body_lines[insert_idx:]
            )
        else:
            new_content = "\n".join(body_lines)

        # Pattern 3: Fix "from typing import Optional, Optional" -> "from typing import Optional"
        new_content = re.sub(
            r"from typing import ([\w, ]+),\s*\1", r"from typing import \1", new_content
        )

        # Pattern 4: Fix multiple blank lines between imports
        new_content = re.sub(r"(from .+ import .+\n)\n+(from .+ import)", r"\1\n\2", new_content)
        new_content = re.sub(r"(import .+\n)\n+(import .+)", r"\1\n\2", new_content)

        if new_content != original:
            filepath.write_text(new_content, encoding="utf-8")
            return True, "Fixed import placement issues"

        return False, "No fixable patterns found"

    except Exception as e:
        return False, str(e)


def main():
    repo_path = "."
    print(f"Scanning {repo_path} for syntax errors...")

    errors = scan_syntax_errors(repo_path)
    print(f"Found {len(errors)} files with syntax errors")

    fixed_count = 0
    for filepath, error in errors[:20]:  # Fix first 20
        print(f"\nFixing: {filepath}")
        print(f"  Error: {error}")

        success, msg = fix_file(filepath)
        if success:
            print(f"  ✓ {msg}")
            fixed_count += 1

            # Verify fix
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                ast.parse(content)
                print("  ✓ Syntax now valid")
            except SyntaxError as e:
                print(f"  ✗ Still has syntax error: Line {e.lineno}: {e.msg}")
        else:
            print(f"  ✗ {msg}")

    print(f"\nFixed {fixed_count}/{len(errors)} files")


if __name__ == "__main__":
    main()
