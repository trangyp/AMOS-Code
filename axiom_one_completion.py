#!/usr/bin/env python3
"""Axiom One - Code Completion Engine."""

import ast
from dataclasses import dataclass


@dataclass
class Suggestion:
    completion: str
    confidence: float
    description: str


class CompletionEngine:
    """AST-based code completion."""

    def complete(self, code_prefix: str) -> list[Suggestion]:
        """Generate completions from code prefix."""
        try:
            tree = ast.parse(code_prefix)

            # Context detection
            if not tree.body:
                return [Suggestion("import ", 0.8, "Start with import")]

            last = tree.body[-1]

            if isinstance(last, ast.FunctionDef):
                return [
                    Suggestion('    """Docstring."""', 0.9, "Function docstring"),
                    Suggestion("    pass", 0.8, "Function body placeholder"),
                ]

            if isinstance(last, ast.ClassDef):
                return [
                    Suggestion("    def __init__(self):", 0.9, "Constructor"),
                    Suggestion("    def process(self):", 0.7, "Method template"),
                ]

            return [Suggestion("# Continue implementation", 0.5, "Generic")]

        except SyntaxError:
            return [Suggestion("# Fix syntax", 0.3, "Syntax error detected")]


def demo():
    print("=" * 70)
    print("AXIOM ONE CODE COMPLETION")
    print("=" * 70)

    engine = CompletionEngine()

    # Test 1: Function definition
    code1 = "def process_data(data):"
    print(f"\nInput: {code1}")
    for s in engine.complete(code1):
        print(f"  • {s.completion} ({s.confidence}) - {s.description}")

    # Test 2: Class definition
    code2 = "class DataProcessor:"
    print(f"\nInput: {code2}")
    for s in engine.complete(code2):
        print(f"  • {s.completion} ({s.confidence}) - {s.description}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo()
