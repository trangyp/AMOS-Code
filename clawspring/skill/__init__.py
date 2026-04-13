"""skill package — reusable prompt templates (skills)."""
from .loader import (  # noqa: F401
    SkillDef,
    load_skills,
    find_skill,
    substitute_arguments,
    register_builtin_skill,
    _parse_skill_file,
    _parse_list_field,
)
from .executor import execute_skill  # noqa: F401

# Importing builtin registers the built-in skills
from . import builtin as _builtin  # noqa: F401

# Register AMOS brain skills if available
try:
    import sys
    from pathlib import Path
    amos_path = Path(__file__).parent.parent.parent / "amos_brain"
    if str(amos_path.parent) not in sys.path:
        sys.path.insert(0, str(amos_path.parent))
    from amos_brain.skill import register_amos_skills
    register_amos_skills()
except Exception:
    pass  # AMOS skills optional

__all__ = [
    "SkillDef",
    "load_skills",
    "find_skill",
    "substitute_arguments",
    "register_builtin_skill",
    "execute_skill",
]
