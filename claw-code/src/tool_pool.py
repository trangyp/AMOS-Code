from dataclasses import dataclass

from .models import PortingModule
from .permissions import ToolPermissionContext
from .tools import get_tools
from typing import Optional, Tuple


@dataclass(frozen=True)
class ToolPool:
    tools: Tuple[PortingModule, ...]
    simple_mode: bool
    include_mcp: bool

    def as_markdown(self) -> str:
        lines = [
            "# Tool Pool",
            "",
            f"Simple mode: {self.simple_mode}",
            f"Include MCP: {self.include_mcp}",
            f"Tool count: {len(self.tools)}",
        ]
        lines.extend(f"- {tool.name} — {tool.source_hint}" for tool in self.tools[:15])
        return "\n".join(lines)


def assemble_tool_pool(
    simple_mode: bool = False,
    include_mcp: bool = True,
    permission_context: Optional[ToolPermissionContext] = None,
) -> ToolPool:
    return ToolPool(
        tools=get_tools(
            simple_mode=simple_mode, include_mcp=include_mcp, permission_context=permission_context
        ),
        simple_mode=simple_mode,
        include_mcp=include_mcp,
    )
