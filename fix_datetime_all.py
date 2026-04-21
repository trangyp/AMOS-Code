#!/usr/bin/env python3
"""Fix all datetime.UTC compatibility issues for Python 3.9."""
import os
import re

fixes = 0
errors = []

for root, dirs, files in os.walk('.'):
    # Skip certain directories
    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                original = content
                
                # Fix 1: from datetime import UTC
                if 'from datetime import UTC' in content:
                    content = content.replace(
                        'from datetime import UTC',
                        'from datetime import datetime, timezone\nUTC = timezone.utc'
                    )
                    fixes += 1
                    print(f"Fixed: {filepath}")
                
                # Fix 2: datetime.UTC usage
                if 'datetime.UTC' in content and 'from datetime import' in content:
                    # Check if timezone is already imported
                    if 'timezone' not in content:
                        content = content.replace(
                            'from datetime import',
                            'from datetime import datetime, timezone\nUTC = timezone.utc\n# from datetime import'
                        )
                        content = content.replace('# from datetime import', 'from datetime import', 1)
                    
                    # Replace datetime.UTC with UTC
                    content = content.replace('datetime.UTC', 'UTC')
                    if content != original:
                        fixes += 1
                        print(f"Fixed datetime.UTC: {filepath}")
                
                if content != original:
                    with open(filepath, 'w') as f:
                        f.write(content)
                        
            except Exception as e:
                errors.append((filepath, str(e)))

print(f"\nTotal fixes: {fixes}")
if errors:
    print(f"\nErrors: {len(errors)}")
    for filepath, err in errors[:5]:
        print(f"  {filepath}: {err}")
