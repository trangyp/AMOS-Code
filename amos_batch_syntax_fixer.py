#!/usr/bin/env python3
"""
AMOS Batch Syntax Fixer
Automated syntax error detection and fixing for AMOS codebase.
Uses BrainClient for intelligent analysis when available.
"""

import ast
import re
from pathlib import Path
from typing import List, Optional


class SyntaxFixer:
    """Fixes common syntax errors in Python files."""

    def __init__(self):
        self.skip_dirs = {
            '.venv', 'node_modules', '__pycache__', '.git',
            '.pytest_cache', '.ruff_cache', '.hypothesis',
            '.benchmarks', 'profiling_results', 'amos_logs'
        }
        self.fixed_count = 0
        self.failed_count = 0

    def find_syntax_errors(self, root: Path = Path('.')) -> List[tuple[str, int, str]]:
        """Find all Python files with syntax errors."""
        errors = []
        for py_file in root.rglob('*.py'):
            if any(skip in str(py_file) for skip in self.skip_dirs):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                errors.append((str(py_file), e.lineno, str(e)))
        return errors

    def fix_misplaced_typing_imports(self, content: str) -> str:
        """Fix typing imports that are indented inside functions/classes."""
        lines = content.split('\n')
        fixed_lines = []
        typing_imports_to_move = []

        for i, line in enumerate(lines):
            # Check if this is a misplaced typing import (indented but not at module level)
            if re.match(r'^[ \t]+from typing import', line) or re.match(r'^[ \t]+import typing', line):
                # Check if we're inside a function/class by looking at previous lines
                is_module_level = True
                for j in range(i-1, -1, -1):
                    prev_line = lines[j]
                    if prev_line.strip() and not prev_line.strip().startswith('#'):
                        # Check if previous non-empty line ends with : (function/class definition)
                        if prev_line.rstrip().endswith(':'):
                            # Check if it's a def or class
                            if re.match(r'^[ \t]*(def|class|async def)\s', prev_line):
                                is_module_level = False
                                break
                        # If we hit an unindented line, we're at module level
                        if not prev_line.startswith((' ', '\t')):
                            break

                if not is_module_level:
                    # Capture the import to move it
                    stripped = line.strip()
                    typing_imports_to_move.append(stripped)
                    continue  # Skip this line

            fixed_lines.append(line)

        # If we have imports to move, add them at the top
        if typing_imports_to_move:
            # Find where to insert (after other imports or at the very top)
            insert_idx = 0
            for i, line in enumerate(fixed_lines):
                if line.strip().startswith(('from ', 'import ')):
                    insert_idx = i + 1

            for imp in typing_imports_to_move:
                fixed_lines.insert(insert_idx, imp)
                insert_idx += 1

        return '\n'.join(fixed_lines)

    def fix_missing_parens(self, content: str) -> str:
        """Fix missing closing parentheses in common patterns."""
        # Fix Tool() calls without closing paren
        patterns = [
            (r'Tool\([^)]+\n\n', self._fix_tool_paren),
            (r'Binding\([^)]+\n\n', self._fix_binding_paren),
        ]

        for pattern, fixer in patterns:
            content = re.sub(pattern, fixer, content)

        return content

    def _fix_tool_paren(self, match: re.Match) -> str:
        text = match.group(0)
        # Add closing paren before the double newline
        return text.rstrip('\n') + ')\n\n'

    def _fix_binding_paren(self, match: re.Match) -> str:
        text = match.group(0)
        return text.rstrip('\n') + ')\n\n'

    def fix_future_imports(self, content: str) -> str:
        """Fix misplaced __future__ imports."""
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Remove __future__ imports that are inside functions/classes
            if re.match(r'^[ \t]+from __future__ import', line):
                continue  # Skip misplaced future imports
            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_file(self, filepath: Path) -> bool:
        """Attempt to fix syntax errors in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                original = f.read()

            # Apply fixes
            content = original
            content = self.fix_misplaced_typing_imports(content)
            content = self.fix_future_imports(content)
            content = self.fix_missing_parens(content)

            # Verify syntax
            try:
                ast.parse(content)
            except SyntaxError:
                return False

            # Write back if changed
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_count += 1
                return True

            return False

        except Exception as e:
            self.failed_count += 1
            return False

    def run(self) -> dict:
        """Run the batch fixer on all files."""
        print("=" * 60)
        print("AMOS BATCH SYNTAX FIXER")
        print("=" * 60)

        # Find all syntax errors
        print("\n[1/3] Scanning for syntax errors...")
        errors = self.find_syntax_errors()
        print(f"Found {len(errors)} files with syntax errors")

        # Try to fix each file
        print("\n[2/3] Attempting to fix files...")
        fixed_files = []
        failed_files = []

        for filepath, lineno, error in errors:
            path = Path(filepath)
            if self.fix_file(path):
                fixed_files.append(filepath)
                print(f"  Fixed: {filepath}")
            else:
                failed_files.append((filepath, lineno, error))

        # Report
        print(f"\n[3/3] Fix Report:")
        print(f"  Fixed: {len(fixed_files)} files")
        print(f"  Failed: {len(failed_files)} files")

        if failed_files:
            print(f"\n  Failed files (need manual fix):")
            for f, line, err in failed_files[:10]:
                print(f"    {f}:{line}")

        return {
            'total_errors': len(errors),
            'fixed': len(fixed_files),
            'failed': len(failed_files),
            'fixed_files': fixed_files,
            'failed_files': failed_files
        }


def main():
    fixer = SyntaxFixer()
    results = fixer.run()

    # Exit with error code if there are still failed files
    if results['failed'] > 0:
        print(f"\n⚠️ {results['failed']} files still have syntax errors")
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
