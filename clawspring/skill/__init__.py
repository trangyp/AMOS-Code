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

__all__ = [
    "SkillDef",
    "load_skills",
    "find_skill",
    "substitute_arguments",
    "register_builtin_skill",
    "execute_skill",
]
