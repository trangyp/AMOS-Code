#!/usr/bin/env python3
"""Comprehensive Syntax Fixer - Batch fix all remaining syntax errors."""

import ast
import re
from pathlib import Path
from typing import List, Tuple


def scan_syntax_errors(repo_path: str) -> List[Tuple[Path, str]]:
    """Scan all Python files for syntax errors."""
    errors = []
    root = Path(repo_path).resolve()
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ruff_cache", ".pytest_cache", ".mypy_cache"}
    
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


def fix_common_patterns(filepath: Path) -> bool:
    """Fix common syntax error patterns."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content
        
        # Pattern 1: Fix __future__ imports inside classes/functions
        # Move them to the top of the file
        lines = content.split("\n")
        new_lines = []
        future_import = None
        insert_idx = 0
        
        # Find module docstring end
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track docstring state
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring:
                    in_docstring = False
                else:
                    in_docstring = True
            
            # Check if this is a future import
            if "from __future__ import" in stripped and i > 2:
                future_import = stripped
                continue
            
            new_lines.append(line)
        
        # If we found a misplaced __future__ import, insert it at the right place
        if future_import:
            # Find insertion point (after docstring)
            in_docstring = False
            for i, line in enumerate(new_lines):
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_docstring = not in_docstring
                elif not in_docstring and stripped and not stripped.startswith("#"):
                    new_lines.insert(i, future_import)
                    new_lines.insert(i+1, "")
                    break
        
        content = "\n".join(new_lines)
        
        # Pattern 2: Fix imports inside parenthesized import blocks
        content = re.sub(
            r'from\s+\S+\s+import\s*\(\s*\n\s*from\s+typing\s+import\s+([^\n]+)\n',
            lambda m: f'from typing import {m.group(1)}\n\nfrom \\\w+ import (\n',
            content
        )
        
        # Pattern 3: Fix duplicate typing imports
        content = re.sub(
            r'(from typing import [^\n]+)\n\s*from typing import ([^\n]+)',
            lambda m: f'{m.group(1).rstrip()}, {m.group(2)}',
            content
        )
        
        # Pattern 4: Remove duplicate imports on same line
        content = re.sub(r'from typing import (\w+), \1', r'from typing import \1', content)
        
        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True
        return False
        
    except Exception as e:
        print(f"  Error fixing {filepath}: {e}")
        return False


def main():
    repo_path = "."
    print(f"Scanning {repo_path} for syntax errors...")
    
    errors = scan_syntax_errors(repo_path)
    print(f"Found {len(errors)} files with syntax errors")
    
    fixed_count = 0
    for filepath, error in errors:
        print(f"\nFixing: {filepath}")
        print(f"  Error: {error}")
        
        if fix_common_patterns(filepath):
            print(f"  ✓ Applied pattern fixes")
            fixed_count += 1
            
            # Verify fix
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                ast.parse(content)
                print(f"  ✓ Syntax now valid")
            except SyntaxError as e:
                print(f"  ✗ Still has syntax error: Line {e.lineno}: {e.msg}")
        else:
            print(f"  ✗ No fixable patterns found")
    
    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count}/{len(errors)} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
