"""skill package — reusable prompt templates (skills)."""

# Importing builtin registers the built-in skills
from . import builtin as _builtin  # noqa: F401
from .executor import execute_skill  # noqa: F401
from .loader import (  # noqa: F401
    SkillDef,
    _parse_list_field,
    _parse_skill_file,
    find_skill,
    load_skills,
    register_builtin_skill,
    substitute_arguments,
)

# Register AMOS brain skills if available
# Note: We import from root skill package (not clawspring.skill) to ensure
# all skills go to the same registry that clawspring uses
try:
    from amos_brain.skill import register_amos_skills

    register_amos_skills()
except Exception:
    pass  # amos_brain not available, skip skill registration

__all__ = [
    "SkillDef",
    "load_skills",
    "find_skill",
    "substitute_arguments",
    "register_builtin_skill",
    "execute_skill",
]
