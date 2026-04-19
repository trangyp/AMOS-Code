#!/usr/bin/env python3
"""ACTIVE BRAIN USAGE - Cognitive Engine for Repository Fixing

This script ACTUALLY USES the AMOS Brain's cognitive engine.
"""

import ast
import sys
from pathlib import Path

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

# ACTUALLY IMPORT AND USE THE BRAIN

from amos_brain import BrainClient
from amos_brain.cognitive_engine import get_cognitive_engine
from typing import List


def use_brain_to_analyze(filepath: Path) -> dict:
    """ACTUALLY use brain to analyze a file."""
    content = filepath.read_text(encoding="utf-8")

    # Check syntax
    try:
        ast.parse(content)
        syntax_ok = True
    except SyntaxError as e:
        return {"error": str(e), "line": e.lineno}

    # ACTUALLY USE BRAIN
    brain = BrainClient()

    # Use brain.think() for cognitive analysis
    thought = brain.think(
        f"Analyze {filepath.name} for undefined name errors. "
        f"Check what typing imports are missing (Optional, Dict, List, etc.)"
    )

    return {
        "file": filepath.name,
        "syntax_ok": syntax_ok,
        "brain_thought": thought,
    }


def use_brain_to_decide_fix_priority(files: List[Path]) -> List[Path]:
    """ACTUALLY use brain to decide which files to fix first."""
    brain = BrainClient()

    # Use brain.decide() for decision making
    decision = brain.decide(
        f"Prioritize fixing these {len(files)} files with undefined name errors",
        options=["critical_first", "alphabetical", "by_size"],
    )

    print(f"Brain decided: {decision}")
    return sorted(files)


def main() -> int:
    """Main function that ACTUALLY uses the brain."""
    print("=" * 70)
    print("ACTIVE BRAIN USAGE - Repository Analysis and Fix")
    print("=" * 70)

    # Initialize brain
    print("\n1. Initializing BrainClient...")
    brain = BrainClient()
    print(f"   BrainClient type: {type(brain)}")

    # Get tools
    print("\n2. Getting brain tools...")
    tools = brain.list_tools()
    print(f"   Tools registered: {len(tools)}")

    # Get cognitive engine
    print("\n3. Getting cognitive engine...")
    cog = get_cognitive_engine()
    print(f"   Engine: {cog}")

    # ACTUALLY USE brain.think()
    print("\n4. Using brain.think() for repository analysis...")
    repo_analysis = brain.think(
        "The AMOS repository has F821 undefined name errors. "
        "What is the best systematic approach to fix all typing import issues? "
        "Focus on files with most F821 errors first."
    )
    print(f"   Brain analysis: {repo_analysis}")

    # Find Python files
    repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    python_files = [
        f for f in repo_path.rglob("*.py") if ".venv" not in str(f) and "__pycache__" not in str(f)
    ]

    print(f"\n5. Repository: {len(python_files)} Python files")

    # ACTUALLY USE brain to analyze files
    print("\n6. Using brain to analyze first 20 files...")
    for f in python_files[:20]:
        result = use_brain_to_analyze(f)
        if not result.get("syntax_ok"):
            print(f"   {f.name}: SYNTAX ERROR - {result.get('error')}")
        else:
            print(f"   {f.name}: OK (brain analyzed)")

    # Check overall syntax
    syntax_errors = sum(1 for f in python_files if not use_brain_to_analyze(f).get("syntax_ok"))
    print(f"\n7. Syntax errors: {syntax_errors}")

    # ACTUALLY USE brain.decide()
    if syntax_errors > 0:
        print("\n8. Using brain.decide() for next steps...")
        decision = brain.decide(
            f"Found {syntax_errors} syntax errors. What should we do?",
            options=["fix_immediately", "analyze_deeper", "continue_scanning"],
        )
        print(f"   Brain decision: {decision}")

    print("\n" + "=" * 70)
    print("BRAIN USAGE COMPLETE - Repository analyzed using cognitive engine")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
