# Axiom One Platform

Unified Software Operating Platform - Code Studio, Repo Graph, Build Forge, and AI Agents.

## Quick Start

### Option 1: Standalone Server (Recommended)
No dependencies required - uses only Python stdlib:

```bash
# Start the server
python axiom_one_standalone.py --port 8001

# Or use system Python
/usr/bin/python3 axiom_one_standalone.py
```

### Option 2: Full FastAPI Integration
Requires fixing Python 3.14 compatibility issues:

```bash
# With Python 3.10-3.12
pip install fastapi uvicorn pydantic
python -m axiom_one.server
```

## API Endpoints

### Code Studio
- `GET /api/repos/{id}/files` - List repository files
- `GET /api/repos/{id}/files/content?path=...` - Read file
- `PUT /api/repos/{id}/files/content` - Write file
- `GET /api/repos/{id}/commits` - Commit history
- `POST /api/repos/{id}/commits` - Create commit
- `POST /api/repos/{id}/branches` - Create branch

### AI Repo Health Agent
- `POST /api/repos/{id}/health/analyze` - Run AI analysis
- `POST /api/repos/{id}/health/fix` - Apply auto-fixes

### Workspaces
- `GET /api/workspaces` - List workspaces
- `POST /api/workspaces` - Create workspace
- `GET /api/repositories` - List repositories
- `POST /api/repositories` - Create repository

### System
- `GET /health` - Health check
- `GET /` - API documentation

## Features

### 1. AI Repo Health Agent
Automatically detects:
- Broken imports (modules not found)
- Missing essential files (README.md, .gitignore)
- Hardcoded path assumptions
- Potential hardcoded secrets

Auto-fixes:
- Creates .gitignore with Python best practices

### 2. Repository Graph
- File tree with git status
- Commit history with author info
- Branch management
- File read/write operations

### 3. Terminal (WebSocket Ready)
- Async subprocess execution
- Output streaming support
- Session management

## Dashboard

Open `axiom_one_dashboard.html` in your browser for the complete UI:
- File Explorer
- Code Editor
- Terminal Panel
- Git/Repo Graph Panel
- AI Health Panel

## Example Usage

```bash
# Create a workspace
curl -X POST http://localhost:8001/api/workspaces \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "slug": "my-project"}'

# Create a repository
curl -X POST http://localhost:8001/api/repositories \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "ws-xxx", "name": "my-repo"}'

# Run AI health analysis
curl -X POST http://localhost:8001/api/repos/{repo_id}/health/analyze

# Apply auto-fixes
curl -X POST http://localhost:8001/api/repos/{repo_id}/health/fix
```

## Integration with AMOS Brain

The Axiom One platform integrates with the AMOS Brain system:
- `/backend/api/axiom_one.py` - FastAPI router with brain integration
- Uses `BrainClient` from `amos_brain/facade.py` for cognitive capabilities

## Architecture

```
Axiom One Platform
├── Code Studio (Editor, Terminal, Git)
├── Repo Graph (Dependency Analysis)
├── Build Forge (CI/CD Pipeline)
├── Runtime Orbit (Deployment Management)
├── Pulse (Monitoring)
└── AI Agents (Code Assistant, Repo Health, Debug)
```

## File Structure

```
axiom_one/
├── __init__.py           # Package init
├── models.py            # Data models (Pydantic)
├── git_service.py       # Git operations
└── server.py            # FastAPI server

backend/api/
└── axiom_one.py         # Integrated API router

axiom_one_standalone.py  # Standalone stdlib server
axiom_one_dashboard.html # UI dashboard
```

## Owner
Trang Phan
