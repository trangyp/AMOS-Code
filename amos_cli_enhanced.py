#!/usr/bin/env python3
"""Enhanced AMOS CLI - Real Tool Using AMOS Brain Components.

Usage:
    python amos_cli_enhanced.py scan
    python amos_cli_enhanced.py fix
    python amos_cli_enhanced.py status
"""

import argparse
import ast
import os
import sys
from pathlib import Path

# Add AMOS to path
sys.path.insert(0, str(Path(__file__).parent))


def scan_project():
    """Scan project for issues using AMOS patterns."""
    print("AMOS Brain: Scanning project...")
    
    issues = {
        'syntax': [],
        'long_lines': [],
        'bare_except': [],
        'trailing_ws': []
    }
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Syntax check
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        issues['syntax'].append((filepath, str(e)[:30]))
                        continue
                    
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if len(line) > 100:
                            issues['long_lines'].append((filepath, i))
                        if line.strip() == 'except:':
                            issues['bare_except'].append((filepath, i))
                        if line != line.rstrip():
                            issues['trailing_ws'].append(filepath)
                            
                except Exception:
                    pass
    
    print(f"\nScan Results:")
    print(f"  Syntax errors: {len(issues['syntax'])}")
    print(f"  Long lines: {len(issues['long_lines'])}")
    print(f"  Bare except: {len(issues['bare_except'])}")
    print(f"  Trailing WS: {len(set(issues['trailing_ws']))}")
    
    return issues


def fix_issues():
    """Fix detected issues."""
    print("AMOS Brain: Applying fixes...")
    fixed = 0
    
    # Fix bare except
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'except:' in content:
                        new_content = content.replace('except:', 'except Exception:')
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            fixed += 1
                            print(f"  Fixed: {filepath}")
                except Exception:
                    pass
    
    print(f"\nFixed {fixed} files")


def show_status():
    """Show AMOS system status."""
    print("AMOS Brain System Status")
    print("=" * 50)
    
    # Check kernel
    try:
        from amos_kernel import get_unified_kernel
        print("[OK] AMOS Kernel: Available")
    except ImportError:
        print("[X] AMOS Kernel: Not available")
    
    # Check brain
    try:
        from amos_brain import get_brain
        print("[OK] AMOS Brain: Available")
    except ImportError:
        print("[X] AMOS Brain: Not available")
    
    # Check cognitive engine
    try:
        from amos_kernel.active_cognitive_engine import ActiveCognitiveEngine
        print("[OK] Cognitive Engine: Available")
    except ImportError:
        print("[X] Cognitive Engine: Not available")
    
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='AMOS Enhanced CLI')
    parser.add_argument('command', choices=['scan', 'fix', 'status'])
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_project()
    elif args.command == 'fix':
        fix_issues()
    elif args.command == 'status':
        show_status()


if __name__ == '__main__':
    main()
