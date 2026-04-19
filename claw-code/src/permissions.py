from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class ToolPermissionContext:
    deny_names: frozenset[str] = field(default_factory=frozenset)
    deny_prefixes: Tuple[str, ...] = ()

    @classmethod
    def from_iterables(
        cls, deny_names: List[str] = None, deny_prefixes: List[str] = None
    ) -> ToolPermissionContext:
        return cls(
            deny_names=frozenset(name.lower() for name in (deny_names or [])),
            deny_prefixes=tuple(prefix.lower() for prefix in (deny_prefixes or [])),
        )

    def blocks(self, tool_name: str) -> bool:
        lowered = tool_name.lower()
        return lowered in self.deny_names or any(
            lowered.startswith(prefix) for prefix in self.deny_prefixes
        )
