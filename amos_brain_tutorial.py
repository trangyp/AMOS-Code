#!/usr/bin/env python3
"""Backward compatibility shim - delegates to amos_brain.tutorial.

This file is deprecated. Use `python -m amos_brain.tutorial` or `amos-tutorial` instead.
"""

import sys
import warnings

warnings.warn(
    "amos_brain_tutorial.py is deprecated. Use `python -m amos_brain.tutorial` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from amos_brain.tutorial import main

if __name__ == "__main__":
    sys.exit(main())
