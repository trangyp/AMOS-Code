"""Backward-compatibility shim — real implementation is in skill/ package."""
from skill.executor import execute_skill  # noqa: F401
from skill.loader import (  # noqa: F401
    SkillDef,
    _parse_list_field,
    _parse_skill_file,
    find_skill,
    load_skills,
    substitute_arguments,
)

# Legacy constant — kept for tests that patch it
from skill.loader import _get_skill_paths as _gsp

SKILL_PATHS = _gsp()
