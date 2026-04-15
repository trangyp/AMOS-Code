"""
AMOS Backend API - FastAPI Application

The cognitive engine powering the AMOS Dashboard.

Architecture:
- FastAPI for high-performance async API
- Pydantic for type-safe data models
- In-memory storage (rapid prototyping - upgradeable to DB)
- WebSocket for real-time frontend updates
- REST endpoints for all 11 cognitive subsystems

Creator: Trang Phan
Version: 3.0.0
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import json
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="AMOS API",
    description="Absolute Meta Operating System - Cognitive Backend",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================

class CognitiveMode(BaseModel):
    mode: str  # seed, growth, full
    layers: int
    confidence: float
    active: bool

class ReasoningLevel(BaseModel):
    level: int
    name: str
    confidence: float
    status: str
    timestamp: str

class MCPServer(BaseModel):
    id: str
    name: str
    type: str
    status: str
    url: str
    last_ping: str

class AgentTask(BaseModel):
    id: str
    name: str
    description: str
    status: str  # pending, running, complete, error
    priority: int
    progress: float
    created_at: str
    completed_at: Optional[str] = None

class MemoryEntry(BaseModel):
    id: str
    type: str  # episodic, semantic, procedural, working, long_term
    content: str
    importance: int
    tags: List[str]
    timestamp: str
    access_count: int

class Checkpoint(BaseModel):
    id: str
    name: str
    timestamp: str
    files_changed: int
    lines_added: int
    lines_removed: int
    description: str
    branch: str

class OrchestraAgent(BaseModel):
    id: str
    name: str
    tier: int
    instrument: str
    status: str
    task: str
    progress: float
    color: str

class SystemStatus(BaseModel):
    status: str
    uptime: str
    confidence: float
    active_layers: int
    total_layers: int
    components: Dict[str, str]

class AGENTSFile(BaseModel):
    id: str
    path: str
    scope: str
    sections: Dict[str, str]
    last_modified: str

# ============================================================================
# IN-MEMORY DATA STORE (Rapid Prototyping)
# ============================================================================

# Cognitive State
cognitive_state = {
    "mode": "growth",
    "layers": 3,
    "confidence": 0.87,
    "active": True
}

# Reasoning Levels
reasoning_levels = [
    {"level": 1, "name": "Brain Loader", "confidence": 0.95, "status": "active", "timestamp": datetime.now().isoformat()},
    {"level": 2, "name": "Rule of 2", "confidence": 0.88, "status": "active", "timestamp": datetime.now().isoformat()},
    {"level": 3, "name": "Rule of 4", "confidence": 0.82, "status": "processing", "timestamp": datetime.now().isoformat()},
]

# MCP Servers
mcp_servers = [
    {"id": "1", "name": "GitHub", "type": "git", "status": "connected", "url": "https://api.github.com", "last_ping": datetime.now().isoformat()},
    {"id": "2", "name": "Slack", "type": "messaging", "status": "connected", "url": "https://slack.com/api", "last_ping": datetime.now().isoformat()},
    {"id": "3", "name": "PostgreSQL", "type": "database", "status": "connected", "url": "postgresql://localhost:5432", "last_ping": datetime.now().isoformat()},
    {"id": "4", "name": "Filesystem", "type": "storage", "status": "connected", "url": "file://local", "last_ping": datetime.now().isoformat()},
]

# Background Agents
agents = [
    {"id": "agent-1", "name": "Code Analyzer", "description": "Analyzing codebase structure", "status": "running", "priority": 1, "progress": 65.0, "created_at": datetime.now().isoformat()},
    {"id": "agent-2", "name": "Test Runner", "description": "Running unit tests", "status": "pending", "priority": 2, "progress": 0.0, "created_at": datetime.now().isoformat()},
    {"id": "agent-3", "name": "Doc Generator", "description": "Generating documentation", "status": "complete", "priority": 3, "progress": 100.0, "created_at": datetime.now().isoformat(), "completed_at": datetime.now().isoformat()},
]

# Persistent Memory
memories = [
    {"id": "mem-1", "type": "episodic", "content": "Implemented AMOSL compiler with 8 invariants", "importance": 9, "tags": ["compiler", "amosl", "milestone"], "timestamp": datetime.now().isoformat(), "access_count": 42},
    {"id": "mem-2", "type": "semantic", "content": "Architecture pattern: Layered cognitive system", "importance": 8, "tags": ["architecture", "pattern"], "timestamp": datetime.now().isoformat(), "access_count": 28},
    {"id": "mem-3", "type": "procedural", "content": "How to validate cognitive invariants", "importance": 7, "tags": ["validation", "invariants"], "timestamp": datetime.now().isoformat(), "access_count": 15},
]

# Checkpoints
checkpoints = [
    {"id": "cp-1", "name": "Initial Setup", "timestamp": datetime.now().isoformat(), "files_changed": 12, "lines_added": 450, "lines_removed": 0, "description": "Project initialization", "branch": "main"},
    {"id": "cp-2", "name": "AMOSL Complete", "timestamp": datetime.now().isoformat(), "files_changed": 8, "lines_added": 1200, "lines_removed": 45, "description": "Compiler implementation", "branch": "main"},
    {"id": "cp-3", "name": "Dashboard Built", "timestamp": datetime.now().isoformat(), "files_changed": 15, "lines_added": 2100, "lines_removed": 120, "description": "Frontend implementation", "branch": "main"},
]

# Agent Orchestra
orchestra_agents = [
    {"id": "orch-1", "name": "Frontend Virtuoso", "tier": 1, "instrument": "strings", "status": "performing", "task": "Implement React component", "progress": 65.0, "color": "#f59e0b"},
    {"id": "orch-2", "name": "Backend Bassist", "tier": 1, "instrument": "winds", "status": "performing", "task": "Build API endpoint", "progress": 80.0, "color": "#3b82f6"},
    {"id": "orch-3", "name": "Test Percussionist", "tier": 2, "instrument": "percussion", "status": "waiting", "task": "Write unit tests", "progress": 0.0, "color": "#ef4444"},
]

# AGENTS.md Files
agents_files = [
    {"id": "global", "path": "~/.config/AMOS/AGENTS.md", "scope": "global", "sections": {"overview": "Global preferences", "tech_stack": "Python, TypeScript"}, "last_modified": datetime.now().isoformat()},
    {"id": "project", "path": "./AGENTS.md", "scope": "project", "sections": {"overview": "AMOS Dashboard Project", "architecture": "14-layer cognitive system"}, "last_modified": datetime.now().isoformat()},
]

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "AMOS API",
        "version": "3.0.0",
        "description": "Absolute Meta Operating System - Cognitive Backend",
        "creator": "Trang Phan",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "components": {
            "cognitive": "active",
            "memory": "active",
            "agents": "active",
            "mcp": "active"
        }
    }

# ============================================================================
# COGNITIVE MODE ENDPOINTS
# ============================================================================

@app.get("/api/cognitive/mode", response_model=CognitiveMode)
async def get_cognitive_mode():
    """Get current cognitive mode"""
    return CognitiveMode(**cognitive_state)

@app.post("/api/cognitive/mode")
async def set_cognitive_mode(mode: str):
    """Set cognitive mode (seed, growth, full)"""
    global cognitive_state
    if mode not in ["seed", "growth", "full"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use: seed, growth, full")
    
    layers = {"seed": 1, "growth": 3, "full": 14}
    cognitive_state = {
        "mode": mode,
        "layers": layers[mode],
        "confidence": 0.87 if mode == "growth" else (0.91 if mode == "seed" else 0.94),
        "active": True
    }
    
    # Broadcast update to all connected clients
    await manager.broadcast({
        "type": "cognitive_mode_changed",
        "data": cognitive_state
    })
    
    return cognitive_state

# ============================================================================
# REASONING ENDPOINTS
# ============================================================================

@app.get("/api/reasoning/levels", response_model=List[ReasoningLevel])
async def get_reasoning_levels():
    """Get all reasoning levels (L1-L3)"""
    return [ReasoningLevel(**level) for level in reasoning_levels]

@app.get("/api/reasoning/level/{level_id}")
async def get_reasoning_level(level_id: int):
    """Get specific reasoning level"""
    level = next((l for l in reasoning_levels if l["level"] == level_id), None)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    return ReasoningLevel(**level)

# ============================================================================
# MCP ENDPOINTS
# ============================================================================

@app.get("/api/mcp/servers", response_model=List[MCPServer])
async def get_mcp_servers():
    """Get all MCP servers"""
    return [MCPServer(**server) for server in mcp_servers]

@app.post("/api/mcp/servers/{server_id}/connect")
async def connect_mcp_server(server_id: str):
    """Connect to an MCP server"""
    server = next((s for s in mcp_servers if s["id"] == server_id), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    server["status"] = "connected"
    server["last_ping"] = datetime.now().isoformat()
    
    await manager.broadcast({
        "type": "mcp_server_connected",
        "data": server
    })
    
    return MCPServer(**server)

@app.post("/api/mcp/servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str):
    """Disconnect from an MCP server"""
    server = next((s for s in mcp_servers if s["id"] == server_id), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    server["status"] = "disconnected"
    
    await manager.broadcast({
        "type": "mcp_server_disconnected",
        "data": server
    })
    
    return MCPServer(**server)

# ============================================================================
# BACKGROUND AGENTS ENDPOINTS
# ============================================================================

@app.get("/api/agents/tasks", response_model=List[AgentTask])
async def get_agent_tasks():
    """Get all agent tasks"""
    return [AgentTask(**task) for task in agents]

@app.post("/api/agents/tasks")
async def create_agent_task(task: Dict[str, Any]):
    """Create a new agent task"""
    new_task = {
        "id": f"agent-{len(agents) + 1}",
        "name": task.get("name", "New Task"),
        "description": task.get("description", ""),
        "status": "pending",
        "priority": task.get("priority", 1),
        "progress": 0.0,
        "created_at": datetime.now().isoformat(),
    }
    agents.append(new_task)
    
    await manager.broadcast({
        "type": "agent_task_created",
        "data": new_task
    })
    
    return AgentTask(**new_task)

@app.post("/api/agents/tasks/{task_id}/cancel")
async def cancel_agent_task(task_id: str):
    """Cancel an agent task"""
    task = next((t for t in agents if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["status"] = "cancelled"
    
    await manager.broadcast({
        "type": "agent_task_cancelled",
        "data": task
    })
    
    return AgentTask(**task)

# ============================================================================
# PERSISTENT MEMORY ENDPOINTS
# ============================================================================

@app.get("/api/memory/entries", response_model=List[MemoryEntry])
async def get_memory_entries(type: Optional[str] = None):
    """Get memory entries (optionally filtered by type)"""
    filtered = memories
    if type:
        filtered = [m for m in memories if m["type"] == type]
    return [MemoryEntry(**entry) for entry in filtered]

@app.post("/api/memory/entries")
async def create_memory_entry(entry: Dict[str, Any]):
    """Create a new memory entry"""
    new_entry = {
        "id": f"mem-{len(memories) + 1}",
        "type": entry.get("type", "semantic"),
        "content": entry.get("content", ""),
        "importance": entry.get("importance", 5),
        "tags": entry.get("tags", []),
        "timestamp": datetime.now().isoformat(),
        "access_count": 0
    }
    memories.append(new_entry)
    
    await manager.broadcast({
        "type": "memory_entry_created",
        "data": new_entry
    })
    
    return MemoryEntry(**new_entry)

@app.get("/api/memory/search")
async def search_memory(query: str):
    """Search memory entries"""
    results = [m for m in memories if query.lower() in m["content"].lower()]
    return {"query": query, "results": [MemoryEntry(**r) for r in results], "count": len(results)}

# ============================================================================
# CHECKPOINTS ENDPOINTS
# ============================================================================

@app.get("/api/checkpoints", response_model=List[Checkpoint])
async def get_checkpoints():
    """Get all checkpoints"""
    return [Checkpoint(**cp) for cp in checkpoints]

@app.post("/api/checkpoints")
async def create_checkpoint(checkpoint: Dict[str, Any]):
    """Create a new checkpoint"""
    new_checkpoint = {
        "id": f"cp-{len(checkpoints) + 1}",
        "name": checkpoint.get("name", f"Checkpoint {len(checkpoints) + 1}"),
        "timestamp": datetime.now().isoformat(),
        "files_changed": checkpoint.get("files_changed", 0),
        "lines_added": checkpoint.get("lines_added", 0),
        "lines_removed": checkpoint.get("lines_removed", 0),
        "description": checkpoint.get("description", ""),
        "branch": checkpoint.get("branch", "main")
    }
    checkpoints.append(new_checkpoint)
    
    await manager.broadcast({
        "type": "checkpoint_created",
        "data": new_checkpoint
    })
    
    return Checkpoint(**new_checkpoint)

@app.post("/api/checkpoints/{checkpoint_id}/rewind")
async def rewind_to_checkpoint(checkpoint_id: str):
    """Rewind to a specific checkpoint"""
    checkpoint = next((c for c in checkpoints if c["id"] == checkpoint_id), None)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    await manager.broadcast({
        "type": "checkpoint_rewind",
        "data": checkpoint
    })
    
    return {"message": f"Rewound to checkpoint {checkpoint_id}", "checkpoint": Checkpoint(**checkpoint)}

# ============================================================================
# AGENT ORCHESTRA ENDPOINTS
# ============================================================================

@app.get("/api/orchestra/agents", response_model=List[OrchestraAgent])
async def get_orchestra_agents():
    """Get all orchestra agents"""
    return [OrchestraAgent(**agent) for agent in orchestra_agents]

@app.get("/api/orchestra/status")
async def get_orchestra_status():
    """Get orchestra performance status"""
    performing = len([a for a in orchestra_agents if a["status"] == "performing"])
    complete = len([a for a in orchestra_agents if a["status"] == "complete"])
    
    return {
        "performing": performing,
        "complete": complete,
        "waiting": len(orchestra_agents) - performing - complete,
        "message": f"{performing} agents performing in harmony"
    }

# ============================================================================
# AGENTS.MD ENDPOINTS
# ============================================================================

@app.get("/api/agents-md/files", response_model=List[AGENTSFile])
async def get_agents_md_files():
    """Get all AGENTS.md files"""
    return [AGENTSFile(**file) for file in agents_files]

@app.get("/api/agents-md/files/{file_id}")
async def get_agents_md_file(file_id: str):
    """Get specific AGENTS.md file"""
    file = next((f for f in agents_files if f["id"] == file_id), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return AGENTSFile(**file)

@app.put("/api/agents-md/files/{file_id}")
async def update_agents_md_file(file_id: str, sections: Dict[str, str]):
    """Update AGENTS.md file sections"""
    file = next((f for f in agents_files if f["id"] == file_id), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    file["sections"].update(sections)
    file["last_modified"] = datetime.now().isoformat()
    
    await manager.broadcast({
        "type": "agents_md_updated",
        "data": file
    })
    
    return AGENTSFile(**file)

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get overall system status"""
    return SystemStatus(
        status="operational",
        uptime="running",
        confidence=cognitive_state["confidence"],
        active_layers=cognitive_state["layers"],
        total_layers=14,
        components={
            "mcp": "active",
            "agents": "active",
            "memory": "active",
            "checkpoints": "ready"
        }
    )

@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get system metrics"""
    return {
        "components": {
            "mcp_servers": len(mcp_servers),
            "agent_tasks": len(agents),
            "memory_entries": len(memories),
            "checkpoints": len(checkpoints),
            "orchestra_agents": len(orchestra_agents)
        },
        "performance": {
            "confidence": cognitive_state["confidence"],
            "active_layers": cognitive_state["layers"],
            "mode": cognitive_state["mode"]
        }
    }

# ============================================================================
# WEBSOCKET ENDPOINT (Real-time Updates)
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connected",
            "data": {
                "cognitive_mode": cognitive_state,
                "system_status": "operational",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif data.get("type") == "subscribe":
                    channel = data.get("channel", "all")
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": channel
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print("=" * 60)
    print("🧠 AMOS Backend API Starting...")
    print("=" * 60)
    print(f"Version: 3.0.0")
    print(f"Creator: Trang Phan")
    print(f"Architecture: 14-Layer Cognitive System")
    print(f"Mode: {cognitive_state['mode']}")
    print(f"Active Layers: {cognitive_state['layers']}")
    print("=" * 60)
    print("📡 API Endpoints:")
    print("  - GET  /")
    print("  - GET  /health")
    print("  - GET  /api/cognitive/mode")
    print("  - GET  /api/reasoning/levels")
    print("  - GET  /api/mcp/servers")
    print("  - GET  /api/agents/tasks")
    print("  - GET  /api/memory/entries")
    print("  - GET  /api/checkpoints")
    print("  - GET  /api/orchestra/agents")
    print("  - GET  /api/agents-md/files")
    print("  - GET  /api/system/status")
    print("  - WS   /ws")
    print("=" * 60)
    print("🚀 Ready for connections!")
    print("=" * 60)

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
