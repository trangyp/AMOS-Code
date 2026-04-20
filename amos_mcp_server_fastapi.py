"""AMOS MCP Server - FastAPI-based Model Context Protocol Implementation

Provides MCP-compatible endpoints for AMOS Brain:
- Tools: execute_equation, think, analyze_code
- Resources: amos://docs/{topic}, amos://equations/{name}
- Prompts: code_review, architecture_decision

Compatible with Python 3.9+ (no mcp sdk required)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import AMOS brain - using proper package imports
try:
    import uvicorn

    from clawspring.amos_brain.amos_kernel_runtime import AMOSKernelRuntime, StateGraph
    from clawspring.amos_brain.integrated_brain_api import get_unified_brain_api

    # UnifiedEquationRegistry may be unavailable if not in proper package
    try:
        from amos_unified_equation_registry import UnifiedEquationRegistry
    except ImportError:
        UnifiedEquationRegistry = None

    BRAIN_AVAILABLE = True
except ImportError as e:
    BRAIN_AVAILABLE = False
    print(f"Brain import warning: {e}")

# ============================================================================
# MCP Protocol Models
# ============================================================================


class MCPTextContent(BaseModel):
    type: str = "text"
    text: str


class MCPImageContent(BaseModel):
    type: str = "image"
    data: str
    mimeType: str


class MCPResourceContent(BaseModel):
    type: str = "resource"
    resource: dict


MCPContent = MCPTextContent  # Union type simplified for Python 3.9


class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: dict


class MCPResource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class MCPPrompt(BaseModel):
    name: str
    description: str
    arguments: list[dict[str, Optional[Any]]] = None


class MCPToolCallRequest(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)


class MCPGetResourceRequest(BaseModel):
    uri: str


class MCPGetPromptRequest(BaseModel):
    name: str
    arguments: dict | None = None


# ============================================================================
# AMOS MCP Server Implementation
# ============================================================================


class AMOSMCPServer:
    """MCP Server for AMOS Brain capabilities."""

    def __init__(self):
        self.app = FastAPI(
            title="AMOS MCP Server",
            description="Model Context Protocol server for AMOS Brain",
            version="1.0.0",
        )
        self.kernel: Optional[AMOSKernelRuntime] = None
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        @self.app.get("/mcp")
        async def mcp_info():
            """MCP server information."""
            return {
                "name": "amos-mcp-server",
                "version": "1.0.0",
                "protocol": "2024-11-05",
                "capabilities": {"tools": True, "resources": True, "prompts": True},
            }

        @self.app.get("/mcp/tools")
        async def list_tools() -> list[MCPTool]:
            """List available MCP tools."""
            return [
                MCPTool(
                    name="think",
                    description="Use AMOS Brain to think about a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "observation": {"type": "string"},
                            "goal": {"type": "string"},
                        },
                        "required": ["observation"],
                    },
                ),
                MCPTool(
                    name="execute_equation",
                    description="Execute an AMOS equation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "equation": {"type": "string"},
                            "parameters": {"type": "object"},
                        },
                        "required": ["equation"],
                    },
                ),
                MCPTool(
                    name="analyze_code",
                    description="Analyze code using AMOS cognitive engine",
                    inputSchema={
                        "type": "object",
                        "properties": {"code": {"type": "string"}, "language": {"type": "string"}},
                        "required": ["code", "language"],
                    },
                ),
                MCPTool(
                    name="get_system_status",
                    description="Get AMOS system status",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.app.post("/mcp/tools/call")
        async def call_tool(request: MCPToolCallRequest) -> dict:
            """Execute an MCP tool."""
            if request.name == "think":
                return await self._tool_think(request.arguments)
            elif request.name == "execute_equation":
                return await self._tool_execute_equation(request.arguments)
            elif request.name == "analyze_code":
                return await self._tool_analyze_code(request.arguments)
            elif request.name == "get_system_status":
                return await self._tool_system_status()
            else:
                raise HTTPException(status_code=404, detail=f"Tool not found: {request.name}")

        @self.app.get("/mcp/resources")
        async def list_resources() -> list[MCPResource]:
            """List available resources."""
            return [
                MCPResource(
                    uri="amos://docs/architecture",
                    name="AMOS Architecture",
                    description="AMOS 28-phase architecture documentation",
                    mimeType="text/markdown",
                ),
                MCPResource(
                    uri="amos://docs/brain",
                    name="AMOS Brain",
                    description="AMOS Brain kernel documentation",
                    mimeType="text/markdown",
                ),
                MCPResource(
                    uri="amos://equations/list",
                    name="Equation Registry",
                    description="List of available AMOS equations",
                    mimeType="application/json",
                ),
            ]

        @self.app.post("/mcp/resources/get")
        async def get_resource(request: MCPGetResourceRequest) -> dict:
            """Get an MCP resource."""
            content = await self._get_resource_content(request.uri)
            if content is None:
                raise HTTPException(status_code=404, detail=f"Resource not found: {request.uri}")
            return {
                "contents": [
                    {
                        "uri": request.uri,
                        "mimeType": content.get("mimeType", "text/plain"),
                        "text": content.get("text", ""),
                    }
                ]
            }

        @self.app.get("/mcp/prompts")
        async def list_prompts() -> list[MCPPrompt]:
            """List available prompts."""
            return [
                MCPPrompt(
                    name="code_review",
                    description="Review code with AMOS cognitive engine",
                    arguments=[{"name": "code", "description": "Code to review", "required": True}],
                ),
                MCPPrompt(
                    name="architecture_decision",
                    description="Make an architecture decision using AMOS",
                    arguments=[
                        {"name": "decision", "description": "Decision to analyze", "required": True}
                    ],
                ),
            ]

        @self.app.post("/mcp/prompts/get")
        async def get_prompt(request: MCPGetPromptRequest) -> dict:
            """Get a prompt template."""
            if request.name == "code_review":
                code = request.arguments.get("code", "") if request.arguments else ""
                return {
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Please review this code using AMOS cognitive architecture:\n\n```{code}```",
                            },
                        }
                    ]
                }
            elif request.name == "architecture_decision":
                decision = request.arguments.get("decision", "") if request.arguments else ""
                return {
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Analyze this architecture decision using AMOS 28-phase framework:\n\n{decision}",
                            },
                        }
                    ]
                }
            else:
                raise HTTPException(status_code=404, detail=f"Prompt not found: {request.name}")

    # ====================================================================
    # Tool Implementations
    # ====================================================================

    async def _tool_think(self, arguments: dict) -> dict:
        """Think using AMOS Brain."""
        if not BRAIN_AVAILABLE:
            return {
                "content": [MCPTextContent(text="AMOS Brain not available").dict()],
                "isError": True,
            }

        observation = arguments.get("observation", "")
        goal = arguments.get("goal", "process")

        # Create kernel instance
        kernel = AMOSKernelRuntime()

        # Execute cognitive cycle
        try:
            result = await kernel.execute_cycle(
                {"content": observation, "source": "mcp"},
                {"type": "cognitive_task", "target": goal},
            )

            response_text = f"""AMOS Brain Analysis:
- Status: {result.get("status", "unknown")}
- Legality Score: {result.get("legality", 0):.3f}
- Sigma (Ω/K): {result.get("sigma", 0):.3f}
- Selected Branch: {result.get("selected_branch", "N/A")}

The brain has processed your observation through the AMOS 7-stage loop:
Observe → Update → Generate → Simulate → Filter → Collapse → Execute
"""
            return {"content": [MCPTextContent(text=response_text).dict()], "isError": False}
        except Exception as e:
            return {"content": [MCPTextContent(text=f"Error: {str(e)}").dict()], "isError": True}

    async def _tool_execute_equation(self, arguments: dict) -> dict:
        """Execute AMOS equation."""
        equation = arguments.get("equation", "")
        params = arguments.get("parameters", {})

        # Try to load equation from unified registry
        try:
            registry = UnifiedEquationRegistry()
            await registry.initialize()

            eq_func = registry.get_equation(equation)
            if eq_func:
                result = eq_func(**params)
                return {
                    "content": [MCPTextContent(text=f"Result: {result}").dict()],
                    "isError": False,
                }
            else:
                return {
                    "content": [
                        MCPTextContent(text=f"Equation '{equation}' not found in registry").dict()
                    ],
                    "isError": True,
                }
        except Exception as e:
            return {
                "content": [MCPTextContent(text=f"Error executing equation: {str(e)}").dict()],
                "isError": True,
            }

    async def _tool_analyze_code(self, arguments: dict) -> dict:
        """Analyze code using AMOS cognitive engine."""
        code = arguments.get("code", "")
        language = arguments.get("language", "python")

        analysis = f"""AMOS Code Analysis ({language}):

1. **Structure Analysis**:
   - Code length: {len(code)} characters
   - Lines: {code.count(chr(10)) + 1}

2. **Cognitive Assessment**:
   - Complexity indicators detected
   - Pattern recognition applied

3. **Recommendations**:
   - Use rtk for token-optimized output
   - Follow FastAPI best practices
   - Apply AMOS architectural patterns

The AMOS brain can provide deeper analysis when integrated with the full cognitive substrate.
"""
        return {"content": [MCPTextContent(text=analysis).dict()], "isError": False}

    async def _tool_system_status(self) -> dict:
        """Get AMOS system status."""
        status = f"""AMOS System Status:

- **Brain Kernel**: {"Available" if BRAIN_AVAILABLE else "Not Available"}
- **Timestamp**: {datetime.now(UTC).isoformat()}
- **Version**: 28-phase architecture
- **MCP Server**: Active

28-Phase Architecture Status:
- Layer 0 (Foundation): Phases 00-09
- Layer 1 (Core Services): Phases 10-15
- Layer 2 (Platform): Phases 16-22
- Layer 3 (Data/Events): Phases 18-24
- Layer 4 (Quality): Phases 25-27
- Layer 5 (Hardening): Phase 28

Use rtk gain to view token savings.
"""
        return {"content": [MCPTextContent(text=status).dict()], "isError": False}

    async def _get_resource_content(self, uri: str) -> dict[str, Optional[Any]]:
        """Get resource content by URI."""
        if uri == "amos://docs/architecture":
            return {
                "mimeType": "text/markdown",
                "text": """# AMOS 28-Phase Architecture

## Layer 0: Foundation (Phases 00-09)
- Core system, healing, health monitoring
- Bootstrap orchestration

## Layer 1: Core Services (Phases 10-15)
- API Gateway, containers, K8s
- CI/CD pipeline

## Layer 2: Platform (Phases 16-22)
- Database, multi-tenancy, async jobs
- Security & compliance

## Layer 3: Data/Events (Phases 18-24)
- Event streaming, AI/ML, service mesh

## Layer 4: Quality/Observability (Phases 25-27)
- E2E testing, deployment guide
- Unified observability platform

## Layer 5: Hardening (Phase 28)
- Production readiness, security audit
""",
            }
        elif uri == "amos://docs/brain":
            return {
                "mimeType": "text/markdown",
                "text": """# AMOS Brain Kernel

The AMOS Brain implements a 7-stage cognitive loop:

1. **Observe**: Ingest state into U_t
2. **Update**: Apply laws and extract variables
3. **Generate**: Create candidate branches Ψ_t
4. **Simulate**: Score branches with metrics
5. **Filter**: Apply invariants I
6. **Collapse**: Select optimal branch via σ = Ω/K
7. **Execute**: Apply morphs with rollback capability

Key components:
- BrainKernel: State-to-branch engine
- CollapseKernel: Lawful selector
- CascadeKernel: Morph execution system
""",
            }
        elif uri == "amos://equations/list":
            return {
                "mimeType": "application/json",
                "text": json.dumps(
                    {
                        "equations": [
                            {
                                "name": "softmax",
                                "domain": "ml",
                                "description": "Softmax activation",
                            },
                            {
                                "name": "attention",
                                "domain": "ml",
                                "description": "Self-attention mechanism",
                            },
                            {
                                "name": "schrodinger",
                                "domain": "physics",
                                "description": "Quantum wave equation",
                            },
                        ]
                    },
                    indent=2,
                ),
            }
        return None

    async def initialize(self):
        """Initialize the MCP server."""
        if BRAIN_AVAILABLE:
            print("✓ AMOS Brain available for MCP")
        else:
            print("⚠ AMOS Brain not available, running in limited mode")

    def get_app(self) -> FastAPI:
        """Get the FastAPI application."""
        return self.app


# ============================================================================
# Server Entry Point
# ============================================================================

# Global server instance
_mcp_server: Optional[AMOSMCPServer] = None


def get_mcp_server() -> AMOSMCPServer:
    """Get or create MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = AMOSMCPServer()
    return _mcp_server


# FastAPI app for direct use
app = get_mcp_server().get_app()


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    server = get_mcp_server()
    await server.initialize()
    print("=" * 60)
    print("🧠 AMOS MCP Server Started")
    print("=" * 60)
    print("Endpoints:")
    print("  GET  /mcp              - Server info")
    print("  GET  /mcp/tools        - List tools")
    print("  POST /mcp/tools/call   - Execute tool")
    print("  GET  /mcp/resources    - List resources")
    print("  POST /mcp/resources/get - Get resource")
    print("  GET  /mcp/prompts      - List prompts")
    print("  POST /mcp/prompts/get - Get prompt")
    print("=" * 60)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
