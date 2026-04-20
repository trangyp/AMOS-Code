"""Entry point for running amos_brain as a module.

Usage:
    python -m amos_brain
"""

import sys

from amos_brain.cli import main

if __name__ == "__main__":
    sys.exit(main())
