#!/usr/bin/env python3
"""Backward compatibility shim - delegates to amos_brain.launcher.

This file is deprecated. Use `python -m amos_brain.launcher` or `amos-launcher` instead.
"""

import sys
import warnings

warnings.warn(
    "amos_brain_launcher.py is deprecated. Use `python -m amos_brain.launcher` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from amos_brain.launcher import main

if __name__ == "__main__":
    sys.exit(main())
