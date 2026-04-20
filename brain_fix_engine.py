#!/usr/bin/env python3
"""Brain-powered codebase fix engine.

Uses AMOS Brain patterns to automatically fix:
- Python 3.10 union syntax -> Python 3.9 compatible
- Deprecated datetime.now(timezone.utc) -> datetime.now(timezone.utc)
- Missing imports
- Broken references
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


class BrainFixEngine:
    """Automatic code fix engine using brain patterns."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.fixed_files: list[Path] = []
        self.errors: list[tuple] = []

    def scan_and_fix(self, dry_run: bool = False) -> dict[str, Any]:
        """Scan repository and fix all issues."""
        results = {"scanned": 0, "fixed": 0, "errors": 0, "files": []}

        for py_file in self.repo_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            results["scanned"] += 1

            try:
                fixed = self.fix_file(py_file, dry_run)
                if fixed:
                    results["fixed"] += 1
                    results["files"].append(str(py_file.relative_to(self.repo_path)))
            except Exception as e:
                results["errors"] += 1
                self.errors.append((py_file, str(e)))

        return results

    def fix_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Fix a single Python file. Returns True if changes made."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return False

        original = content
        changes = []

        # Fix 1: Python 3.10 union syntax in type annotations
        # Pattern:variable: Optional[Type] -> Optional[Type]
        union_pattern = r"([\w\[\],\s]+):\s*(\w+(?:\[.*?\])?)\s*\|\s*None"
        matches = list(re.finditer(union_pattern, content))
        for match in matches:
            var_part = match.group(1).strip()
            type_part = match.group(2)
            old = match.group(0)
            new = f"{var_part}: {type_part} | None"
            content = content.replace(old, new)
            changes.append(f"Union syntax: {old} -> {new}")

        # Fix 2: Return type union syntax
        # Pattern: -> Optional[Type] -> -> Optional[Type]
        return_pattern = r"(->\s*)(\w+(?:\[.*?\])?)\s*\|\s*None"
        matches = list(re.finditer(return_pattern, content))
        for match in matches:
            arrow = match.group(1)
            type_part = match.group(2)
            old = match.group(0)
            new = f"{arrow}{type_part} | None"
            content = content.replace(old, new)
            changes.append(f"Return union: {old} -> {new}")

        # Fix 3: Parameter union syntax
        # Pattern: param: str | Path -> param: str | Path
        param_union_pattern = r"(\w+):\s*(\w+)\s*\|\s*(\w+)"
        matches = list(re.finditer(param_union_pattern, content))
        for match in matches:
            param = match.group(1)
            type1 = match.group(2)
            type2 = match.group(3)
            # Skip if already Optional or common cases
            if type2 in ("None", "type"):
                continue
            old = match.group(0)
            new = f"{param}: {type1} | {type2}"
            content = content.replace(old, new)
            changes.append(f"Param union: {old} -> {new}")

        # Fix 4: Add typing imports if needed
        if "" in content and "from typing import" in content:
            typing_import_line = content.split("from typing import")[1].split("\n")[0]
            if "Optional" not in typing_import_line:
                # Need to add Optional to imports
                content = re.sub(
                    r"(from typing import\s+)([^\n]+)",
                    lambda m: (
                        f"{m.group(1)}{m.group(2)}, Optional"
                        if "Optional" not in m.group(2)
                        else m.group(0)
                    ),
                    content,
                )
                changes.append("Added Optional import")

        if "" in content and "from typing import" in content:
            typing_import_line = content.split("from typing import")[1].split("\n")[0]
            if "Union" not in typing_import_line:
                content = re.sub(
                    r"(from typing import\s+)([^\n]+)",
                    lambda m: (
                        f"{m.group(1)}{m.group(2)}, Union"
                        if "Union" not in m.group(2)
                        else m.group(0)
                    ),
                    content,
                )
                changes.append("Added Union import")

        # Fix 5: datetime.now(timezone.utc) deprecation
        if "datetime.now(timezone.utc)" in content:
            content = content.replace("datetime.now(timezone.utc)", "datetime.now(timezone.utc)")
            changes.append("Fixed datetime.now(timezone.utc) -> datetime.now(timezone.utc)")

        # Verify syntax is still valid
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return False

        # Write if changes made and not dry run
        if content != original and not dry_run:
            file_path.write_text(content, encoding="utf-8")
            print(f"Fixed {file_path.relative_to(self.repo_path)}: {len(changes)} changes")
            for c in changes[:3]:
                print(f"  - {c}")
            return True
        elif content != original:
            print(f"Would fix {file_path.relative_to(self.repo_path)}: {len(changes)} changes")
            return True

        return False


if __name__ == "__main__":
    import sys

    repo = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
    )
    dry = "--dry-run" in sys.argv

    engine = BrainFixEngine(repo)
    results = engine.scan_and_fix(dry_run=dry)

    print(f"\n{'=' * 50}")
    print("Brain Fix Engine Results:")
    print(f"  Files scanned: {results['scanned']}")
    print(f"  Files fixed: {results['fixed']}")
    print(f"  Errors: {results['errors']}")
    print(f"{'=' * 50}")
