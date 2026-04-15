#!/usr/bin/env python3
"""Verify AMOS Server & Environment Setup"""

import sys
from pathlib import Path


def check():
    print("=" * 60)
    print("AMOS SERVER & ENVIRONMENT SETUP VERIFICATION")
    print("=" * 60)

    # 1. Check Organism
    print("\n[1] AMOS Organism...")
    try:
        sys.path.insert(0, "AMOS_ORGANISM_OS")
        from organism import AmosOrganism

        org = AmosOrganism()
        status = org.status()
        subs = len(status.get("active_subsystems", []))
        print(f"  ✓ OK - {subs} subsystems active")
    except Exception as e:
        print(f"  ✗ FAIL - {e}")
        return False

    # 2. Check World Model
    print("\n[2] World Model Engine...")
    try:
        sys.path.insert(0, "AMOS_ORGANISM_OS/08_WORLD_MODEL")
        from world_model_engine import WorldModelEngine

        engine = WorldModelEngine()
        print(f"  ✓ OK - {len(engine.sectors.sectors)} sectors loaded")
    except Exception as e:
        print(f"  ✗ FAIL - {e}")

    # 3. Check Legal Engine
    print("\n[3] Legal Brain Engine...")
    try:
        sys.path.insert(0, "AMOS_ORGANISM_OS/11_LEGAL_BRAIN")
        from legal_engine import LegalEngine

        engine = LegalEngine(Path("AMOS_ORGANISM_OS"))
        print(f"  ✓ OK - {len(engine.rules)} rules active")
    except Exception as e:
        print(f"  ✗ FAIL - {e}")

    # 4. Check API Server
    print("\n[4] API Server...")
    try:
        sys.path.insert(0, "AMOS_ORGANISM_OS")
        from INTERFACES.api_server import APIServer

        server = APIServer(org, host="localhost", port=8765)
        print("  ✓ OK - Ready on port 8765")
    except Exception as e:
        print(f"  ✗ FAIL - {e}")

    # 5. Check MCP Config
    print("\n[5] MCP Configuration...")
    mcp_path = Path.home() / ".clawspring" / "mcp.json"
    if mcp_path.exists():
        print(f"  ✓ OK - Config at {mcp_path}")
    else:
        print("  ⚠ MISSING - Run setup to create")

    print("\n" + "=" * 60)
    print("SETUP VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nTo start the API server:")
    print("  cd AMOS_ORGANISM_OS && python run.py api")
    print("\nTo use the CLI:")
    print("  cd AMOS_ORGANISM_OS && python run.py cli")
    print("\nTo check status:")
    print("  cd AMOS_ORGANISM_OS && python run.py status")
    print("=" * 60)
    return True


if __name__ == "__main__":
    check()
