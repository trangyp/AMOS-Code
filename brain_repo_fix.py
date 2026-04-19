#!/usr/bin/env python3

"""AMOS Brain - Repository Fix System

Uses actual AMOS brain infrastructure to analyze and fix repository.
"""

import ast
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Use actual AMOS brain
sys.path.insert(0, str(Path(__file__).parent))

from typing import Any

from amos_brain import GlobalLaws, get_brain


def scan_repository(repo_path: str) -> list[Path]:
    """Scan all Python files in repository."""
    files = []
    root = Path(repo_path).resolve()

    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ruff_cache"}

    for path in root.rglob("*.py"):
        # Check if any parent is a skip dir
        if any(part in skip_dirs for part in path.parts):
            continue
        files.append(path)

    return sorted(files)


def check_syntax(filepath: Path) -> tuple[bool, str]:
    """Check if file has valid syntax."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def fix_broken_imports(filepath: Path) -> bool:
    """Fix common broken import patterns."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content
        lines = content.split("\n")

        # Pattern 1: Fix imports split across lines incorrectly
        # from x import (
        # from typing import Optional, Optional  # Wrong - should be before, Any
        #     y,
        # )

        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a from/import inside a parenthesized import block
            stripped = line.strip()
            if stripped.startswith("from typing import Optional,") and i > 0:
                # Check if we're inside an import block
                prev_line = lines[i - 1].strip() if i > 0 else ""
                if prev_line.endswith("(") and "import" in prev_line:
                    # This is wrong - move typing import before the block
                    # Find the start of the block
                    block_start = i - 1
                    while block_start > 0 and not lines[block_start].strip().startswith("from "):
                        block_start -= 1

                    # Extract the typing import line (remove leading whitespace if any)
                    typing_line = line.lstrip()

                    # Remove from current position and insert at block_start
                    # Actually just insert before block
                    new_lines.append(typing_line)
                    # Don't add the original line
                    i += 1
                    continue

            new_lines.append(line)
            i += 1

        content = "\n".join(new_lines)

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception:
        return False


def run_ruff_on_file(filepath: Path) -> bool:
    """Run ruff check --fix on a single file."""
    try:
        result = subprocess.run(
            ["ruff", "check", str(filepath), "--fix", "--exit-non-zero-on-fix"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def process_file(filepath: Path, brain: Any) -> dict[str, Any]:
    """Process a single file with brain guidance."""
    result = {
        "path": str(filepath),
        "syntax_ok": False,
        "syntax_error": "",
        "fixed": False,
        "fix_type": "",
    }

    # Check syntax
    ok, error = check_syntax(filepath)
    result["syntax_ok"] = ok
    result["syntax_error"] = error

    if not ok:
        # Try to fix broken imports
        if fix_broken_imports(filepath):
            # Re-check
            ok, error = check_syntax(filepath)
            result["syntax_ok"] = ok
            result["syntax_error"] = error
            if ok:
                result["fixed"] = True
                result["fix_type"] = "broken_import"

        if not ok:
            return result

    # Run ruff
    if run_ruff_on_file(filepath):
        result["fixed"] = True
        result["fix_type"] = result["fix_type"] + ",ruff" if result["fix_type"] else "ruff"

    return result


def main() -> None:
    """Main brain-driven repository fix."""
    # Initialize brain
    brain = get_brain()
    GlobalLaws()

    print(f"{'=' * 70}")
    print("AMOS BRAIN: Repository Fix System")
    print(f"Brain ID: {brain.brain_id if hasattr(brain, 'brain_id') else 'active'}")
    print(f"Timestamp: {datetime.now(UTC).isoformat()}")
    print(f"{'=' * 70}")

    # Scan repository
    print("\n[1/4] Scanning repository...")
    files = scan_repository(".")
    print(f"      Found {len(files)} Python files")

    # Check syntax on all files
    print("\n[2/4] Checking syntax...")
    syntax_errors = []
    for i, filepath in enumerate(files):
        if i % 100 == 0 and i > 0:
            print(f"      Checked {i}/{len(files)}...")

        ok, error = check_syntax(filepath)
        if not ok:
            syntax_errors.append((filepath, error))

    print(f"      Files with syntax errors: {len(syntax_errors)}")

    # Fix syntax errors
    print("\n[3/4] Fixing syntax errors...")
    fixed_count = 0
    for filepath, error in syntax_errors:
        result = process_file(filepath, brain)
        if result["fixed"] and result["syntax_ok"]:
            fixed_count += 1
            print(f"      Fixed: {filepath}")

    print(f"      Fixed {fixed_count}/{len(syntax_errors)} files")

    # Run ruff on all files
    print("\n[4/4] Running Ruff on all files...")
    ruff_result = subprocess.run(
        ["ruff", "check", ".", "--fix", "--select", "E,W,F,I,UP"], capture_output=True, text=True
    )
    print(f"      Ruff exit code: {ruff_result.returncode}")

    # Final summary
    print(f"\n{'=' * 70}")
    print("AMOS BRAIN: Fix Complete")
    print(f"{'=' * 70}")
    print(f"Total files scanned: {len(files)}")
    print(f"Syntax errors found: {len(syntax_errors)}")
    print(f"Syntax errors fixed: {fixed_count}")
    print(f"Timestamp: {datetime.now(UTC).isoformat()}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
