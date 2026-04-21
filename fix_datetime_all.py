#!/usr/bin/env python3
"""Fix all datetime.utcnow() deprecation warnings using AMOS brain."""
import sys
from pathlib import Path

sys.path.insert(0, '.')
sys.path.insert(0, 'AMOS_REPOS/AMOS-Code')

from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest

REPO_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

fixes = 0
errors = []

def fix_file(filepath: Path) -> bool:
    """Fix datetime.utcnow() in a single file."""
    global fixes
    
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        # Check if file has datetime imports
        if 'from datetime import datetime' not in content:
            return False
            
        # Add timezone import if missing
        if 'timezone' not in content:
            content = content.replace(
                'from datetime import datetime',
                'from datetime import datetime, timezone'
            )
        
        # Replace datetime.utcnow() with datetime.now(timezone.utc)
        content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            fixes += 1
            print(f"✓ Fixed: {filepath.relative_to(REPO_ROOT)}")
            return True
            
    except Exception as e:
        errors.append((filepath, str(e)))
    
    return False

# Use repo_doctor to find all Python files
print("🔍 Scanning with AMOS repo_doctor...")
ingest = TreeSitterIngest(REPO_ROOT)

# Find files in main repo (not AMOS_REPOS)
for filepath in REPO_ROOT.rglob("*.py"):
    if 'AMOS_REPOS' in str(filepath) or '__pycache__' in str(filepath):
        continue
    
    # Check if file has datetime.utcnow()
    try:
        content = filepath.read_text(errors='ignore')
        if 'datetime.utcnow()' in content:
            fix_file(filepath)
    except:
        pass

print(f"\n✅ Total files fixed: {fixes}")
if errors:
    print(f"⚠️  Errors: {len(errors)}")
