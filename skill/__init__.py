"""skill package — reusable prompt templates (skills)."""

# Importing builtin registers the built-in skills
from . import builtin as _builtin  # noqa: F401
from . import builtin_amos as _builtin_amos  # noqa: F401
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

__all__ = [
    "SkillDef",
    "load_skills",
    "find_skill",
    "substitute_arguments",
    "register_builtin_skill",
    "execute_skill",
]
