"""Main entry point for AMOS kernel"""

import sys

from .doctor import main as doctor_main


def main() -> int:
    """Main entry point - delegates to doctor for now."""
    return doctor_main()


if __name__ == "__main__":
    sys.exit(main())
