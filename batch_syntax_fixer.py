#!/usr/bin/env python3
"""Batch syntax error fixer for AMOS codebase."""

import ast
import re
from pathlib import Path


class BatchSyntaxFixer:
    """Fixes common syntax errors in batches."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
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

    def find_syntax_errors(self) -> list[tuple[Path, str]]:
        """Find all Python files with syntax errors."""
        error_files = []

        for py_file in self.repo_root.rglob("*.py"):
            if any(skip in py_file.parts for skip in self.skip_dirs):
                continue

            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                error_files.append((py_file, str(e)))

        return error_files

    def fix_import_inside_parentheses(self, content: str) -> str:
        """Fix typing imports inside import statement parentheses."""
        lines = content.split("\n")
        fixed_lines = []
        typing_imports_to_add = []

        in_import_block = False
        import_block_start = -1

        for i, line in enumerate(lines):
            # Check for start of multi-line import
            if re.match(r"^from\s+\S+\s+import\s*\($", line.strip()):
                in_import_block = True
                import_block_start = i
                fixed_lines.append(line)
                continue

            # Check for end of import block
            if in_import_block and line.strip() == ")":
                in_import_block = False
                import_block_start = -1
                fixed_lines.append(line)
                continue

            # Check for typing import inside import block
            if in_import_block:
                match = re.match(r"^(\s*)(from typing import|import typing)(.+)$", line)
                if match:
                    # Extract the typing import to add at module level
                    if "from typing import" in line:
                        typing_imports_to_add.append(line.strip())
                    # Skip this line (remove from import block)
                    continue

            fixed_lines.append(line)

        # Add collected typing imports at the top
        if typing_imports_to_add:
            # Find insertion point after existing imports
            insert_idx = 0
            for i, line in enumerate(fixed_lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1

            # Insert typing imports
            for imp in typing_imports_to_add:
                fixed_lines.insert(insert_idx, imp)
                insert_idx += 1

        return "\n".join(fixed_lines)

    def fix_misplaced_typing_in_function(self, content: str) -> str:
        """Fix typing imports inside function/method bodies."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Pattern: indented typing import
            match = re.match(r"^(\s+)(from typing import|import typing)", line)
            if match:
                # Remove indentation - move to module level
                fixed_lines.append(line.lstrip())
                continue
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def add_future_annotations(self, content: str) -> str:
        """Add from __future__ import annotations if using Python 3.10+ syntax."""
        # Check if already has it
        if "from __future__ import annotations" in content:
            return content

        # Check if using | union syntax
        if re.search(r":\s*\w+\s*\|\s*", content) or re.search(r"->\s*\w+\s*\|\s*", content):
            # Find insertion point
            lines = content.split("\n")
            insert_idx = 0

            for i, line in enumerate(lines):
                if line.startswith('"""') and i == 0:
                    # Find end of docstring
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j]:
                            insert_idx = j + 1
                            break
                    break

            lines.insert(insert_idx, "from __future__ import annotations")
            return "\n".join(lines)

        return content

    def fix_file(self, filepath: Path) -> bool:
        """Fix a single file."""
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            original_content = content

            # Apply fixes
            content = self.fix_import_inside_parentheses(content)
            content = self.fix_misplaced_typing_in_function(content)
            content = self.add_future_annotations(content)

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

            return False

        except Exception as e:
            print(f"  Error fixing {filepath}: {e}")
            return False

    def run(self) -> dict:
        """Run batch fix on all files."""
        print("🔍 Finding syntax errors...")
        error_files = self.find_syntax_errors()

        print(f"📊 Found {len(error_files)} files with syntax errors")

        fixed = 0
        failed = 0

        for filepath, error in error_files:
            short_path = filepath.relative_to(self.repo_root)
            if self.fix_file(filepath):
                print(f"  ✅ Fixed: {short_path}")
                fixed += 1
            else:
                failed += 1

        return {"total": len(error_files), "fixed": fixed, "failed": failed}


def main():
    """Run the batch syntax fixer."""
    repo_root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    fixer = BatchSyntaxFixer(repo_root)
    results = fixer.run()

    print("\n📈 Results:")
    print(f"  Total files: {results['total']}")
    print(f"  Fixed: {results['fixed']}")
    print(f"  Failed: {results['failed']}")


if __name__ == "__main__":
    main()
