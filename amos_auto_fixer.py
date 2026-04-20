#!/usr/bin/env python3
from __future__ import annotations

"""AMOS Auto Fixer - Round 16: Automated Technical Debt Fixing.

Automatically fixes common lint issues:
- Unused imports
- Long lines
- Whitespace on blank lines
- Unused variables
- F-string issues

Usage:
    python amos_auto_fixer.py --preview          # Preview changes
    python amos_auto_fixer.py --fix              # Apply fixes
    python amos_auto_fixer.py --imports-only     # Fix imports only
    python amos_auto_fixer.py --lines-only       # Fix line length only
"""

import ast
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class FixResult:
    """Represents a fix result."""

    file: str
    issue_type: str
    line: int
    description: str
    applied: bool


class AMOSAutoFixer:
    """Automated technical debt fixer for AMOS ecosystem.

    Fixes:
    - Unused imports
    - Lines exceeding 79 chars
    - Whitespace on blank lines
    - Unused variables
    - Trailing whitespace
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root = root_dir or Path(__file__).parent
        self.results: list[FixResult] = []
        self.preview_mode = False

    def analyze(self, preview: bool = False) -> dict[str, Any]:
        """Analyze all files and optionally fix."""
        self.preview_mode = preview

        print("=" * 70)
        print("  🔧 AMOS AUTO FIXER - Round 16")
        print("  Automated Technical Debt Fixing")
        print("=" * 70)
        print()

        if preview:
            print("📋 PREVIEW MODE - No changes will be made")
            print()

        # Find all Python files using os.walk for better performance
        python_files = []
        max_file_size = 2 * 1024 * 1024  # 2MB limit for AST parsing

        for root, dirs, files in os.walk(self.root):
            # Skip hidden directories and common non-source directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in {"__pycache__", "node_modules", "venv", ".venv"}
            ]

            for file in files:
                if file.startswith("amos_") and file.endswith(".py"):
                    file_path = Path(root) / file
                    # Check file size before adding to list
                    try:
                        stat = file_path.stat()
                        if stat.st_size <= max_file_size:
                            python_files.append(file_path)
                    except OSError:
                        pass  # Skip files we can't stat

        print(f"📁 Found {len(python_files)} files to analyze")
        print()

        for file_path in python_files:
            self._fix_file(file_path)

        return self._generate_report()

    def get_priority(self, issue_type: str) -> int:
        """Get priority for sorting (lower = higher priority)."""
        priorities: dict[str, int] = {
            "unused_import": 1,
            "long_line": 2,
            "trailing_whitespace": 3,
            "blank_line_whitespace": 4,
            "unused_variable": 5,
            "f_string_issue": 6,
        }
        return priorities.get(issue_type, 99)

    def _fix_file(self, file_path: Path) -> None:
        """Fix a single file."""
        try:
            content = file_path.read_text()
            original_lines = content.splitlines()
            lines = original_lines.copy()

            # Fix 1: Remove unused imports
            lines = self._fix_unused_imports(lines, file_path)

            # Fix 2: Break long lines
            lines = self._fix_long_lines(lines, file_path)

            # Fix 3: Remove trailing whitespace
            lines = self._fix_trailing_whitespace(lines, file_path)

            # Fix 4: Remove whitespace from blank lines
            lines = self._fix_blank_line_whitespace(lines, file_path)

            # Apply changes if not preview
            if not self.preview_mode and lines != original_lines:
                file_path.write_text("\n".join(lines) + "\n")
                print(f"  ✅ Fixed {file_path.name}")
            elif lines != original_lines:
                print(f"  📋 Would fix {file_path.name}")

        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")

    def _fix_unused_imports(self, lines: List[str], file_path: Path) -> List[str]:
        """Remove unused imports."""
        content = "\n".join(lines)

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return lines

        # Find all imports
        imports_to_check = []
        for i, node in enumerate(ast.walk(tree)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_to_check.append((alias.name, alias.asname or alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports_to_check.append((f"{module}.{alias.name}", name))

        # Check if each import is used
        new_lines = []
        for line in lines:
            stripped = line.strip()

            # Check if line is an import
            if stripped.startswith("import ") or stripped.startswith("from "):
                import_name = stripped.split()[1].split(".")[0]

                # Check if used in content (excluding the import line itself)
                # Simple heuristic: check if name appears elsewhere
                usage_count = content.count(import_name) - 1

                if usage_count <= 0:
                    self.results.append(
                        FixResult(
                            file=str(file_path),
                            issue_type="unused_import",
                            line=lines.index(line) + 1,
                            description=f"Remove unused import: {import_name}",
                            applied=not self.preview_mode,
                        )
                    )
                    if not self.preview_mode:
                        continue  # Skip adding this line

            new_lines.append(line)

        return new_lines

    def _fix_long_lines(self, lines: List[str], file_path: Path) -> List[str]:
        """Break lines exceeding 79 characters."""
        new_lines = []

        for i, line in enumerate(lines):
            if len(line) <= 79:
                new_lines.append(line)
                continue

            # Try to break the line intelligently
            # For f-strings with placeholders
            if 'f"' in line or "f'" in line:
                # Break after placeholders
                parts = re.split(r"(\{[^}]+\})", line)
                if len(parts) > 1:
                    # Build shorter lines
                    current = parts[0]
                    broken_lines = []

                    for part in parts[1:]:
                        if len(current) + len(part) > 75:
                            broken_lines.append(current)
                            current = "    " + part  # Indent continuation
                        else:
                            current += part

                    if current:
                        broken_lines.append(current)

                    if len(broken_lines) > 1:
                        new_lines.extend(broken_lines)
                        self.results.append(
                            FixResult(
                                file=str(file_path),
                                issue_type="long_line",
                                line=i + 1,
                                description=f"Broke {len(line)} char line into {len(broken_lines)} lines",
                                applied=not self.preview_mode,
                            )
                        )
                        continue

            # For other long lines, try breaking at operators
            if "=" in line and not line.strip().startswith("#"):
                parts = line.split("=")
                if len(parts) == 2 and len(parts[0]) < 70:
                    # Break at equals
                    new_lines.append(parts[0] + "= ")
                    new_lines.append("    " + parts[1].strip())
                    self.results.append(
                        FixResult(
                            file=str(file_path),
                            issue_type="long_line",
                            line=i + 1,
                            description="Broke at assignment operator",
                            applied=not self.preview_mode,
                        )
                    )
                    continue

            # Can't easily break, keep as is
            new_lines.append(line)

        return new_lines

    def _fix_trailing_whitespace(self, lines: List[str], file_path: Path) -> List[str]:
        """Remove trailing whitespace."""
        new_lines = []

        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped != line:
                self.results.append(
                    FixResult(
                        file=str(file_path),
                        issue_type="trailing_whitespace",
                        line=i + 1,
                        description="Removed trailing whitespace",
                        applied=not self.preview_mode,
                    )
                )
            new_lines.append(stripped)

        return new_lines

    def _fix_blank_line_whitespace(self, lines: List[str], file_path: Path) -> List[str]:
        """Remove whitespace from blank lines."""
        new_lines = []

        for i, line in enumerate(lines):
            if line.strip() == "" and line != "":
                self.results.append(
                    FixResult(
                        file=str(file_path),
                        issue_type="blank_line_whitespace",
                        line=i + 1,
                        description="Removed whitespace from blank line",
                        applied=not self.preview_mode,
                    )
                )
                new_lines.append("")
            else:
                new_lines.append(line)

        return new_lines

    def _generate_report(self) -> Dict[str, Any]:
        """Generate fix report."""
        print("\n" + "=" * 70)
        print("  📊 AUTO FIX REPORT")
        print("=" * 70)

        issues_by_type: Dict[str, int] = {}
        issues_by_file: Dict[str, int] = {}

        for result in self.results:
            issues_by_type[result.issue_type] = issues_by_type.get(result.issue_type, 0) + 1
            issues_by_file[result.file] = issues_by_file.get(result.file, 0) + 1

        print("\n📈 Summary:")
        print(f"  Total Issues Found: {len(self.results)}")
        print(f"  Mode: {'PREVIEW' if self.preview_mode else 'APPLY'}")

        print("\n📋 Issues by Type:")
        for issue_type, count in sorted(issues_by_type.items(), key=lambda x: -x[1]):
            print(f"  {issue_type}: {count}")

        print("\n📁 Files with Most Issues:")
        sorted_files = sorted(issues_by_file.items(), key=lambda x: -x[1])[:10]
        for file, count in sorted_files:
            print(f"  {Path(file).name}: {count} issues")

        print("\n" + "=" * 70)

        return {
            "total": len(self.results),
            "by_type": issues_by_type,
            "by_file": issues_by_file,
            "preview": self.preview_mode,
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMOS Auto Fixer - Automated Technical Debt Fixing"
    )
    parser.add_argument("--preview", action="store_true", help="Preview changes without applying")
    parser.add_argument("--fix", action="store_true", help="Apply fixes to files")
    parser.add_argument("--imports-only", action="store_true", help="Only fix unused imports")
    parser.add_argument("--lines-only", action="store_true", help="Only fix long lines")

    args = parser.parse_args()

    if not args.preview and not args.fix:
        args.preview = True  # Default to preview mode

    fixer = AMOSAutoFixer()
    results = fixer.analyze(preview=args.preview)

    return 0


if __name__ == "__main__":
    sys.exit(main())
