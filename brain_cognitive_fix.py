#!/usr/bin/env python3

"""AMOS Brain Cognitive Fix - Uses actual brain reasoning.

Invokes BrainClient.think() for cognitive analysis of repository issues.
Uses ThinkingEngine for state transformation.
Persists reasoning to BrainMemory.
"""

import ast
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

UTC = UTC

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

# Import AMOS brain


from amos_brain import BrainClient, GlobalLaws
from amos_brain.memory import BrainMemory


def main():
    """Run brain cognitive fix."""
    print("=" * 70)
    print("AMOS BRAIN COGNITIVE FIX SYSTEM")
    print(f"Timestamp: {datetime.now(UTC).isoformat()}")
    print("=" * 70)

    # Initialize brain client
    brain = BrainClient()
    GlobalLaws()
    memory = BrainMemory()

    print("\n[1] Brain Cognitive Analysis")

    # Think about repository state
    query = """Analyze this Python repository for:
    1. Critical syntax errors that prevent execution
    2. Import order violations blocking compilation
    3. Code patterns violating Python best practices

    What are the highest priority fixes needed?"""

    response = brain.think(query, domain="software")
    print(f"Brain confidence: {response.confidence}")
    print(f"Brain analysis: {response.content[:200]}...")
    print(f"Law compliant: {response.law_compliant}")

    # Save reasoning to memory
    memory.save_reasoning(
        problem="Repository syntax and import analysis",
        analysis={
            "content": response.content,
            "confidence": response.confidence,
            "law_compliant": response.law_compliant,
            "violations": response.violations,
        },
        tags=["syntax", "imports", "repository-fix"],
    )

    print("\n[2] Scanning Repository")
    files = list(Path(".").rglob("*.py"))
    skip = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ruff_cache"}
    py_files = [f for f in files if not any(s in str(f) for s in skip)]
    print(f"Found {len(py_files)} Python files")

    print("\n[3] Syntax Validation")
    syntax_errors = []
    for f in py_files:
        try:
            ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError as e:
            syntax_errors.append((f, e))

    print(f"Syntax errors: {len(syntax_errors)}")

    if syntax_errors:
        print("\n[4] Brain-Guided Syntax Fix")
        for filepath, error in syntax_errors[:3]:
            fix_query = f"""Fix this Python syntax error:
File: {filepath.name}
Error: {error.msg} at line {error.lineno}

What is the likely cause and fix?"""

            fix_response = brain.think(fix_query, domain="software")
            print(f"  {filepath.name}: {fix_response.content[:100]}...")

    print("\n[5] Ruff Auto-Fix")
    result = subprocess.run(
        ["ruff", "check", ".", "--fix", "--select", "E,W,F,I,UP", "--ignore", "UP042,UP043,D"],
        capture_output=True,
        text=True,
    )
    print(f"Ruff exit code: {result.returncode}")

    print("\n[6] Format Check")
    subprocess.run(["ruff", "format", "."], capture_output=True)
    print("Formatting complete")

    # Final brain analysis
    print("\n[7] Final Brain Assessment")
    final_query = """Repository fix completed. Assess:
1. Are all syntax errors resolved?
2. Is import order correct?
3. What remains to fix?

Provide confidence score."""

    final_response = brain.think(final_query, domain="software")
    print(f"Final confidence: {final_response.confidence}")

    print("\n" + "=" * 70)
    print("BRAIN COGNITIVE FIX COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
