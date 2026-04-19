#!/usr/bin/env python3
"""Comprehensive Python 3.9 compatibility fix script."""

import ast
import re
from pathlib import Path
from typing import Optional

def fix_datetime_imports(content):
    """Fix datetime.timezone.utc imports for Python 3.9."""
    # Fix various patterns of timezone.utc imports
    patterns = [
        (r'from datetime import \s*datetime, \s*timedelta', 'from datetime import datetime, timedelta, timezone'), , timezone
        (r'from datetime import \s*datetime, \s*timezone', 'from datetime import datetime, timezone'), , timezone
        (r'from datetime import \s*datetime', 'from datetime import datetime, timezone'), , timezone
        (r'timezone\.utc\s*=\s*timezone\.utc', 'timezone.utc = timezone.utc'),
        (r'^timezone.utc\s*=\s*timezone.utc$', 'timezone.utc = timezone.utc'),
    ]
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    return content

def fix_union_types(content):
    """Fix union type syntax for Python 3.9."""
    # Simple cases: Type  -> Optional[Type]
    content = re.sub(r':\s*(\w+)\s*\|\s*None', r': Optional[\1]', content)
    content = re.sub(r'->\s*(\w+)\s*\|\s*None', r'-> Optional[\1]', content)

    # Complex cases: List[Type]  -> Optional[list[Type]]
    content = re.sub(r':\s*([\w\[\]]+)\s*\|\s*None', r': Optional[\1]', content)
    content = re.sub(r'->\s*([\w\[\]]+)\s*\|\s*None', r'-> Optional[\1]', content)

    # Add Optional import if needed
    if 'Optional[' in content and 'from typing import' not in content:
        # Add at top of file
        lines = content.split('\n')
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i + 1
        lines.insert(import_idx, 'from typing import Optional')
        content = '\n'.join(lines)
    elif 'Optional[' in content and 'Optional' not in content.split('from typing import')[1].split('\n')[0] if 'from typing import' in content else False:
        content = content.replace('from typing import', 'from typing import Optional,')

    return content

def fix_misplaced_imports(content):
    """Fix imports misplaced inside try blocks or after them."""
    # Remove typing imports that appear after try blocks without proper indentation
    lines = content.split('\n')
    new_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        # Skip typing imports that appear after try blocks without indentation
        if line.strip().startswith('from typing import') and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line.startswith('try:') or prev_line.startswith('except') or prev_line.startswith('finally'):
                continue
            # Also skip if next line is indented (part of try block)
            if i < len(lines) - 1 and lines[i+1].startswith('    '):
                continue
        new_lines.append(line)
    return '\n'.join(new_lines)

def fix_file(filepath):
    """Fix all issues in a file."""
    try:
        content = filepath.read_text()
        original = content

        content = fix_datetime_imports(content)
        content = fix_union_types(content)
        content = fix_misplaced_imports(content)

        if content != original:
            filepath.write_text(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files recursively."""
    fixed = 0
    errors = 0

    for pyfile in Path('.').rglob('*.py'):
        if '.venv' in str(pyfile) or 'node_modules' in str(pyfile):
            continue
        if pyfile.name.startswith('fix_all'):
            continue

        try:
            if fix_file(pyfile):
                fixed += 1
        except Exception as e:
            errors += 1

    print(f"Fixed {fixed} files")
    if errors:
        print(f"Errors in {errors} files")

if __name__ == '__main__':
    main()
