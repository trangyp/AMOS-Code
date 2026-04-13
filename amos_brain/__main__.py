"""Entry point for running amos_brain as a module.

Usage:
    python -m amos_brain
"""
from __future__ import annotations

import sys
import os

# Add parent to path for launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amos_brain_launcher import main

if __name__ == "__main__":
    sys.exit(main())
