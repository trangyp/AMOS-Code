"""ClawSpring Plugin - Auto-registers AMOS brain with clawspring runtime."""


def register_with_clawspring() -> None:
    """Register AMOS brain components with clawspring if available."""
    try:
        # Import clawspring components
        # Import AMOS components
        from amos_brain.tools import amos_decide, amos_laws_check, amos_route, amos_status
        from clawspring.tools import register_tool

        # Register tools (lightweight - doesn't load brain)
        register_tool("amos_decide", amos_decide)
        register_tool("amos_laws_check", amos_laws_check)
        register_tool("amos_status", amos_status)
        register_tool("amos_route", amos_route)

        # Register skills from skill.py (lightweight - doesn't load brain)
        from amos_brain.skill import register_amos_skills

        register_amos_skills()

        print("[AMOS] Tools and skills registered successfully (brain loaded on demand)")

    except ImportError as e:
        # clawspring not available, skip
        print(f"[AMOS] ClawSpring not available ({e}), skipping registration")
    except Exception as e:
        print(f"[AMOS] Registration error: {e}")


# Auto-register on import
register_with_clawspring()
