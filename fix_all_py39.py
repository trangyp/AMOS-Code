#!/usr/bin/env python3
"""Fix all Python 3.9 compatibility issues in AMOS codebase."""
import os
import re
import sys

def fix_file(filepath):
    """Fix Python 3.9 issues in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    fixes = []
    
    # Fix 1: from datetime import UTC
    if 'from datetime import UTC' in content:
        content = content.replace(
            'from datetime import UTC',
            'from datetime import datetime, timezone\nUTC = timezone.utc'
        )
        fixes.append('datetime.UTC import')
    
    # Fix 2: from datetime import datetime, UTC
    if 'from datetime import datetime, UTC' in content:
        content = content.replace(
            'from datetime import datetime, UTC',
            'from datetime import datetime, timezone\nUTC = timezone.utc'
        )
        fixes.append('datetime, UTC import')
    
    # Fix 3: datetime.UTC usage
    if 'datetime.UTC' in content and 'timezone' in content:
        content = content.replace('datetime.UTC', 'UTC')
        fixes.append('datetime.UTC usage')
    
    # Fix 4: Union type syntax for Python 3.9
    # Add Union import if using | syntax
    if ' | ' in content and 'from __future__' not in content:
        # Check if Union is already imported
        if 'from typing import' in content and 'Union' not in content:
            # Add Union to imports
            content = re.sub(
                r'from typing import ([^\n]+)',
                lambda m: f'from typing import {m.group(1)}, Union',
                content
            )
            fixes.append('Union import added')
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return fixes
    return []

def main():
    """Scan and fix all Python files."""
    fixed_files = []
    errors = []
    
    for root, dirs, files in os.walk('.'):
        # Skip problematic directories
        dirs[:] = [d for d in dirs if d not in [
            '.git', 'node_modules', '__pycache__', '.venv',
            'AMOS_REPOS', 'third_party'
        ]]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    fixes = fix_file(filepath)
                    if fixes:
                        fixed_files.append((filepath, fixes))
                        print(f"Fixed: {filepath}")
                        for fix in fixes:
                            print(f"  - {fix}")
                except Exception as e:
                    errors.append((filepath, str(e)))
    
    print(f"\n{'='*60}")
    print(f"Fixed {len(fixed_files)} files")
    if errors:
        print(f"Errors: {len(errors)}")
        for filepath, err in errors[:5]:
            print(f"  {filepath}: {err}")

if __name__ == "__main__":
    main()
