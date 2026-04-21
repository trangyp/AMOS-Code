#!/usr/bin/env python3
"""AMOS Vision Runner - Task Execution Interface

Execute vision tasks through the AMOS cognitive substrate.
Integrates with all 6 repositories for comprehensive task processing.

Usage:
    python vision_run.py "analyze codebase structure"
    python vision_run.py --task heal --target AMOS_ORGANISM_OS
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "AMOS_ORGANISM_OS"))


class VisionRunner:
    """Execute vision tasks using AMOS cognitive infrastructure."""
    
    def __init__(self):
        self.root = REPO_ROOT
        self.repos = [
            "AMOS-Code", "AMOS-Consulting", "AMOS-Claws",
            "Mailinhconect", "AMOS-Invest", "AMOS-UNIVERSE"
        ]
        
    def run_vision(self, description: str) -> dict:
        """Run a vision task."""
        print("=" * 70)
        print("AMOS VISION RUNNER")
        print("=" * 70)
        print(f"Task: {description}")
        print("-" * 70)
        
        # Check all 6 repos
        active_repos = []
        for repo in self.repos:
            path = self.root / "AMOS_REPOS" / repo
            if path.exists():
                active_repos.append(repo)
                print(f"  ✓ {repo}")
            else:
                print(f"  ✗ {repo}")
                
        # Try to use brain
        try:
            from amos_brain import think
            result = think(description)
            print(f"\n🧠 Brain result: {result.content[:200]}...")
            return {"success": True, "repos": active_repos, "result": result}
        except Exception as e:
            print(f"\n⚠️  Brain unavailable: {e}")
            return {"success": False, "repos": active_repos, "error": str(e)}
            
    def heal_mode(self, target: str | None = None) -> dict:
        """Run healing on target."""
        print("=" * 70)
        print("AMOS HEALING MODE")
        print("=" * 70)
        
        if target:
            print(f"Target: {target}")
        else:
            print("Target: Full system scan")
            
        # Run self-heal script if available
        heal_script = self.root / "amos_self_heal_py39.py"
        if heal_script.exists():
            print(f"\nRunning: {heal_script}")
            import subprocess
            result = subprocess.run(["python3", str(heal_script)], 
                                 capture_output=True, text=True)
            print(result.stdout[:1000])
            return {"success": result.returncode == 0}
        else:
            print("❌ Heal script not found")
            return {"success": False}


def main():
    parser = argparse.ArgumentParser(description="AMOS Vision Runner")
    parser.add_argument("vision", nargs="?", help="Vision description to execute")
    parser.add_argument("--task", choices=["heal", "analyze", "build"],
                       help="Task type")
    parser.add_argument("--target", help="Target for task")
    args = parser.parse_args()
    
    runner = VisionRunner()
    
    if args.task == "heal":
        result = runner.heal_mode(args.target)
    elif args.vision:
        result = runner.run_vision(args.vision)
    else:
        # Default: show status
        result = runner.run_vision("system status check")
        
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
