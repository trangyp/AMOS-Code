#!/usr/bin/env python3
"""Cookbook Demo Runner - Execute cookbook workflows.

Provides a standalone entry point for running cookbook demos.
"""

from amos_brain.cookbook import run_cookbook_demo


def main() -> None:
    """Run the cookbook demo."""
    print("=" * 60)
    print("AMOS Brain Cookbook Demos")
    print("=" * 60)
    print()
    run_cookbook_demo()


if __name__ == "__main__":
    main()
