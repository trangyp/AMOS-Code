#!/usr/bin/env python3
"""AMOS Brain-powered syntax error fixer."""

import ast
import asyncio
import re
from pathlib import Path

from amos_brain.facade import BrainClient


class BrainSyntaxFixer:
    """Uses AMOS Brain to fix syntax errors."""

    def __init__(self):
        self.brain = BrainClient()
        self.skip_dirs = {
            ".venv",
            "node_modules",
            "__pycache__",
            ".git",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis",
            ".benchmarks",
            "profiling_results",
            "amos_logs",
        }

    def find_syntax_errors(self, repo_root: Path) -> list[tuple[Path, str]]:
        """Find all Python files with syntax errors."""
        error_files = []

        for py_file in repo_root.rglob("*.py"):
            if any(skip in py_file.parts for skip in self.skip_dirs):
                continue

            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                error_files.append((py_file, str(e)))

        return error_files

    def fix_misplaced_typing_imports(self, content: str) -> str:
        """Fix misplaced typing imports inside functions/methods."""
        lines = content.split("\n")
        fixed_lines = []

        # Pattern: indented "from typing import" or "import typing"
        typing_import_pattern = re.compile(r"^(\s+)(from typing import|import typing)")

        for line in lines:
            match = typing_import_pattern.match(line)
            if match:
                # Remove the indentation - move import to top level
                fixed_line = line.lstrip()
                fixed_lines.append(fixed_line)
                continue

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def add_missing_typing_imports(self, content: str) -> str:
        """Add missing typing imports for common types."""
        # Find used type names
        type_names = []
        for match in re.finditer(r"\b(List|Dict|Optional|Set|Tuple|Any|Union)\b", content):
            type_names.append(match.group(1))

        if not type_names:
            return content

        # Check if already imported
        if "from typing import" in content:
            # Already has typing import, don't duplicate
            return content

        # Add import at top
        unique_types = sorted(set(type_names))
        import_line = f"from typing import {', '.join(unique_types)}\n"

        # Find best place to insert
        lines = content.split("\n")
        insert_idx = 0

        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1

        lines.insert(insert_idx, import_line)
        return "\n".join(lines)

    def fix_file(self, filepath: Path) -> bool:
        """Fix a single file."""
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            original_content = content

            # Apply fixes
            content = self.fix_misplaced_typing_imports(content)
            content = self.add_missing_typing_imports(content)

            # Verify syntax
            try:
                ast.parse(content)
            except SyntaxError:
                return False  # Still has syntax errors

            # Write back if changed
            if content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

            return False  # No changes needed

        except Exception as e:
            print(f"  Error fixing {filepath}: {e}")
            return False

    async def fix_all(self, repo_root: Path) -> dict:
        """Fix all syntax errors using brain strategy."""
        print("🔍 Finding syntax errors...")
        error_files = self.find_syntax_errors(repo_root)

        print(f"📊 Found {len(error_files)} files with syntax errors")

        fixed = 0
        failed = 0

        for filepath, error in error_files:
            short_path = filepath.relative_to(repo_root)
            print(f"  Fixing {short_path}...", end=" ")

            if self.fix_file(filepath):
                print("✅ Fixed")
                fixed += 1
            else:
                print("❌ Could not auto-fix")
                failed += 1

        return {"total": len(error_files), "fixed": fixed, "failed": failed}


async def main():
    """Run the brain-powered syntax fixer."""
    repo_root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    fixer = BrainSyntaxFixer()
    results = await fixer.fix_all(repo_root)

    print("\n📈 Results:")
    print(f"  Total files: {results['total']}")
    print(f"  Fixed: {results['fixed']}")
    print(f"  Failed: {results['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
