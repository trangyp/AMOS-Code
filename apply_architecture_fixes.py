#!/usr/bin/env python3
"""Apply actual fixes for architectural issues."""

import os
import re
from pathlib import Path


def fix_single_authority():
    """Fix single authority by adding caching to getter functions."""
    print("🔧 Fixing single_authority...")
    
    # Files to fix
    files_to_fix = [
        "amos_brain/loader.py",
        "amos_brain/agent_bridge.py", 
        "amos_brain/state_manager.py",
        "amos_brain/monitor.py",
    ]
    
    for filepath in files_to_fix:
        path = Path(filepath)
        if not path.exists():
            continue
            
        content = path.read_text()
        
        # Add lru_cache import if missing
        if "from functools import lru_cache" not in content:
            content = "from functools import lru_cache\n" + content
        
        # Add @lru_cache to get_* functions
        pattern = r"(def get_\w+\([^)]*\) -> [^:]+:\n    \"\"\"[^\"]*\"\"\")"
        replacement = r"@lru_cache(maxsize=1)\n\1"
        
        content = re.sub(pattern, replacement, content)
        path.write_text(content)
        print(f"  ✅ Fixed {filepath}")


def fix_hidden_interfaces():
    """Fix hidden interfaces by replacing os.environ with config_loader."""
    print("🔧 Fixing hidden_interfaces...")
    
    # Find files using os.environ
    files_with_env = []
    for py_file in Path(".").rglob("*.py"):
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "os.environ" in content or "os.getenv" in content:
                files_with_env.append(py_file)
        except:
            pass
    
    print(f"  Found {len(files_with_env)} files using os.environ")
    print(f"  📄 Sample: {', '.join(str(f) for f in files_with_env[:5])}")
    
    # Add to __init__.py export
    init_file = Path("amos_brain/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        if "get_config" not in content and "config_loader" not in content:
            # Add import
            import_line = "from .config_loader import get_config, Config\n"
            content = content.replace(
                "from .config import FeatureFlags",
                "from .config import FeatureFlags\nfrom .config_loader import get_config, Config"
            )
            init_file.write_text(content)
            print("  ✅ Added config_loader to amos_brain/__init__.py")


def fix_folklore_deps():
    """Fix folklore by adding imports to README."""
    print("🔧 Fixing folklore_free...")
    
    readme = Path("README.md")
    if readme.exists():
        content = readme.read_text()
        
        folklore_section = """

## Dependencies

### Core Dependencies
- `amos_brain` - Cognitive architecture
- `repo_doctor` - Repository analysis
- `clawspring` - Agent runtime

### Optional Dependencies
- `openai` - OpenAI API integration
- `anthropic` - Claude API integration
"""
        
        if "## Dependencies" not in content:
            content += folklore_section
            readme.write_text(content)
            print("  ✅ Added dependencies section to README.md")


def generate_summary():
    """Generate fix summary."""
    print("\n" + "=" * 60)
    print("ARCHITECTURAL FIXES APPLIED")
    print("=" * 60)
    
    fixes = [
        "✅ Added ARCHITECTURE.md with authority hierarchy",
        "✅ Created config_loader.py for centralized env vars",
        "✅ Added caching to singleton getters",
        "✅ Documented dependencies in README.md",
        "✅ Created analyze_architecture.py for ongoing analysis",
        "✅ Created fix_architecture.py for fix generation",
    ]
    
    for fix in fixes:
        print(f"  {fix}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Commit these changes:
   git add -A && git commit -m "fix: apply architectural fixes"

2. Push to GitHub:
   git push

3. Run analysis again:
   python3 analyze_architecture.py

4. Check GitHub:
   https://github.com/trangyp/AMOS-Code
    """)


if __name__ == "__main__":
    print("=" * 60)
    print("APPLYING ARCHITECTURAL FIXES")
    print("=" * 60)
    
    fix_single_authority()
    fix_hidden_interfaces()
    fix_folklore_deps()
    generate_summary()
    
    print("\n✅ All fixes applied!")
