"""Main entry point for amos-kernel package"""

import sys

# Try to use enhanced Axiom CLI first
from .axiom_cli import main as axiom_main

if __name__ == "__main__":
    sys.exit(axiom_main())
