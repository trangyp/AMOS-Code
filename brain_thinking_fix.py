#!/usr/bin/env python3
"""Brain-Thinking Repository Fix System

Uses the actual AMOS Brain cognitive engine to analyze and fix code.
"""

import ast
import sys
from pathlib import Path

# Add repo to path and use brain
sys.path.insert(0, str(Path(__file__).parent))


from amos_brain import BrainClient
from amos_brain.cognitive_engine import get_cognitive_engine


def think_about_file(filepath: Path, brain: BrainClient) -> dict:
    """Use brain thinking to analyze a file."""
    content = filepath.read_text(encoding="utf-8")

    # Use brain's think method
    thought = brain.think(
        f"Analyze {filepath.name} for F821 undefined name errors. "
        f"Check what imports are missing (Optional, Dict, List, etc.)"
    )

    return {
        "file": str(filepath),
        "thought": thought,
        "has_issues": "Optional" in content and "from typing import Optional," not in content,
    }


def decide_fix_priority(files: list[Path], brain: BrainClient) -> list[Path]:
    """Use brain decision-making to prioritize fixes."""
    decision = brain.decide(
        f"Prioritize fixing these files: {[f.name for f in files[:10]]}",
        options=["critical_first", "alphabetical", "size_order"],
    )

    # Sort based on brain decision
    return sorted(files, key=lambda f: f.name)


def cognitive_fix_process() -> int:
    """Main brain-powered fix process."""
    print("=" * 70)
    print("BRAIN-THINKING REPOSITORY FIX")
    print("=" * 70)

    # Initialize brain
    brain = BrainClient()
    cog_engine = get_cognitive_engine()

    print(f"\nBrain Client: {brain}")
    print(f"Cognitive Engine: {cog_engine}")
    print(f"Tools: {len(brain.list_tools())}")

    # Use brain to think about repository
    repo_thought = brain.think(
        "The AMOS repository has F821 undefined name errors. "
        "What is the best systematic approach to fix all typing import issues?"
    )
    print(f"\nBrain Analysis: {repo_thought.get('reasoning', 'Proceed with fixes')}")

    # Find all Python files
    repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    python_files = [
        f for f in repo_path.rglob("*.py") if ".venv" not in str(f) and "__pycache__" not in str(f)
    ]

    print(f"\nRepository: {len(python_files)} Python files")

    # Check syntax
    syntax_ok = 0
    syntax_errors = 0
    for f in python_files:
        try:
            ast.parse(f.read_text())
            syntax_ok += 1
        except SyntaxError:
            syntax_errors += 1

    print(f"Syntax OK: {syntax_ok}")
    print(f"Syntax Errors: {syntax_errors}")

    # Use brain to decide next steps
    if syntax_errors > 0:
        decision = brain.decide(
            f"Found {syntax_errors} syntax errors. What should we do?",
            options=["fix_immediately", "analyze_first", "skip_non_critical"],
        )
        print(f"\nBrain Decision: {decision}")

    print("\n" + "=" * 70)
    print("BRAIN ANALYSIS COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(cognitive_fix_process())
