"""Entry point for running amos_brain as a module.

Usage:
    python -m amos_brain
"""

import os
import sys

# Add parent to path for launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amos_brain_launcher import main

if __name__ == "__main__":
    sys.exit(main())
