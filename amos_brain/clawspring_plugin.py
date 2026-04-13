"""ClawSpring Plugin - Auto-registers AMOS brain with clawspring runtime."""
from __future__ import annotations

import sys
import os


def register_with_clawspring() -> None:
    """Register AMOS brain components with clawspring if available."""
    try:
        # Import clawspring components
        from clawspring.skill.loader import register_builtin_skill
        from clawspring.tools import register_tool

        # Import AMOS components
        from amos_brain.integration import get_amos_integration
        from amos_brain.tools import (
            amos_decide, amos_laws_check, amos_status, amos_route
        )

        # Initialize brain
        amos = get_amos_integration()
        if amos._initialized:
            print("[AMOS] Brain integration active - 12 engines, 6 laws")

        # Register tools
        register_tool("amos_decide", amos_decide)
        register_tool("amos_laws_check", amos_laws_check)
        register_tool("amos_status", amos_status)
        register_tool("amos_route", amos_route)

        # Register skills from skill.py
        from amos_brain.skill import register_amos_skills
        register_amos_skills()

        print("[AMOS] Tools and skills registered successfully")

    except ImportError as e:
        # clawspring not available, skip
        print(f"[AMOS] ClawSpring not available ({e}), skipping registration")
    except Exception as e:
        print(f"[AMOS] Registration error: {e}")


# Auto-register on import
register_with_clawspring()
