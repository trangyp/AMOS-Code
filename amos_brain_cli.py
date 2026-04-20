#!/usr/bin/env python3
"""Backward compatibility shim - delegates to amos_brain.cli.

This file is deprecated. Use `python -m amos_brain.cli` or `amos-cli` instead.
"""

import sys
import warnings

warnings.warn(
    "amos_brain_cli.py is deprecated. Use `python -m amos_brain.cli` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from amos_brain.cli import main

if __name__ == "__main__":
    sys.exit(main())
