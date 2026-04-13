#!/usr/bin/env python3
"""
AMOS Launcher - Simple entry point

Usage:
    ./run_amos.py              # Run operational AMOS (default)
    ./run_amos.py --demo       # Run operational demo
    ./run_amos.py --version v5 # Run specific version
    ./run_amos.py --arch       # Show architecture

This is the simplest way to run AMOS.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Simple launcher that delegates to master controller."""
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Build command
    cmd = [sys.executable, str(script_dir / "amos_master_controller.py")]
    
    # Parse simple args
    args = sys.argv[1:]
    
    if not args:
        # Default: run operational
        cmd.extend(["--operational", "--demo"])
    elif "--demo" in args:
        cmd.extend(["--operational", "--demo"])
    elif "--arch" in args:
        cmd.append("--arch")
    elif "--version" in args:
        # Pass through version
        version_idx = args.index("--version")
        if version_idx + 1 < len(args):
            cmd.extend(["--version", args[version_idx + 1], "--demo"])
        else:
            cmd.extend(["--operational", "--demo"])
    else:
        # Pass through all args
        cmd.extend(args)
    
    # Run
    try:
        result = subprocess.run(cmd, cwd=str(script_dir))
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nAMOS stopped by user.")
        return 0
    except Exception as e:
        print(f"Error running AMOS: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
