# AMOS-OpenClaw Integration Guide

## Overview

This guide establishes the bidirectional connection between:
- **AMOS-code** (Python): 14-layer cognitive architecture with 28 phases
- **OpenClaw-main** (TypeScript): Personal AI assistant framework with AMOS integration

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AMOS-OpenClaw Bridge                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐                    ┌──────────────┐                  │
│  │  AMOS Brain  │◄────── Bridge ────►│   OpenClaw   │                  │
│  │   (Python)   │    amos_brain/      │  (TypeScript)│                  │
│  │              │    clawspring_bridge  │  src/amos/   │                  │
│  │ • 14 Layers  │                    │  • 300+ files│                  │
│  │ • 28 Phases  │◄──────────────────►│  • 6 Layers  │                  │
│  │ • 180+ Equations│   MCP Protocol   │  • Agent SDK │                  │
│  └──────────────┘                    └──────────────┘                  │
│                                                                         │
│  Connection Methods:                                                   │
│  1. Direct Bridge (clawspring_bridge.py ↔ amos-integration.ts)        │
│  2. MCP Protocol (Model Context Protocol)                               │
│  3. API Gateway (REST/WebSocket)                                        │
│  4. File System Bridge (Shared state directory)                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Repository Structure

### AMOS-code (Local Path: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/`)
```
AMOS-code/
├── amos_brain/
│   ├── clawspring_bridge.py      # ← Bridge TO OpenClaw
│   ├── agent_bridge.py           # Agent orchestration bridge
│   ├── equation_bridge_integration.py  # Equation execution bridge
│   └── integration.py            # Core integration module
├── AMOS_ORGANISM_OS/
│   └── ... (14-layer organism architecture)
├── clawspring/                   # ClawSpring runtime integration
│   └── amos_brain/
│       └── amos_kernel_runtime.py  # AMOS kernel for ClawSpring
└── backend/
    └── api/                      # FastAPI endpoints for OpenClaw
```

### OpenClaw-main (Local Path: `/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main/`)
```
openclaw-main/
├── src/amos/                     # 300+ AMOS TypeScript modules
│   ├── amos-integration.ts       # ← Integration layer v4
│   ├── amos-execution-bridge.ts  # Execution bridge
│   ├── amos-brain-reading-kernel.ts  # Brain reading capabilities
│   ├── amos-cognitive-integration.ts # Cognitive integration
│   └── index.ts                  # AMOS exports
├── AMOS.md                       # AMOS documentation
└── README.md                     # "AMOS-Claws — Cognitive Intelligence System"
```

## Integration Methods

### Method 1: Direct Bridge (Recommended for Local Development)

**From AMOS-code to OpenClaw:**
```python
# In AMOS-code
from amos_brain.clawspring_bridge import create_amos_agent

# Create bridge instance
agent = create_amos_agent()

# Run with brain-enhanced processing
for event in agent.run_with_brain("Analyze this code", config):
    print(event)
```

**Configuration:**
- Add OpenClaw path to `PYTHONPATH`:
```bash
export PYTHONPATH="$PYTHONPATH:/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main"
```

### Method 2: MCP Protocol Bridge

**Setup MCP Server in AMOS-code:**
```python
# amos_mcp_server.py
from mcp.server import Server
from amos_brain.integration import get_amos_integration

app = Server("amos-brain")
amos = get_amos_integration()

@app.tool()
async def analyze_with_amos(text: str) -> dict:
    """Analyze text using AMOS 14-layer architecture."""
    return amos.analyze_with_rules(text)

@app.tool()
async def execute_equation(name: str, params: dict) -> dict:
    """Execute AMOS equation."""
    return await amos.execute_equation(name, params)
```

**Connect OpenClaw to MCP:**
```typescript
// In OpenClaw src/amos/amos-mcp-client.ts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const client = new Client({ name: "openclaw-amos", version: "1.0.0" });
await client.connect(transport);

// Use AMOS tools
const result = await client.callTool("analyze_with_amos", { text: input });
```

### Method 3: API Gateway Bridge

**Start AMOS API Server:**
```bash
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
python amos_fastapi_gateway.py
# Runs on http://localhost:8000
```

**Configure OpenClaw to use AMOS API:**
```typescript
// src/amos/amos-api-client.ts
const AMOS_API_BASE = "http://localhost:8000";

export async function callAmosBrain(endpoint: string, payload: any) {
  const response = await fetch(`${AMOS_API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json();
}
```

### Method 4: File System Bridge (State Sharing)

**Shared State Directory:**
```bash
mkdir -p ~/.amos-openclaw-bridge/state
```

**AMOS-code writes state:**
```python
# amos_brain/state_manager.py
import json
from pathlib import Path

STATE_DIR = Path.home() / ".amos-openclaw-bridge" / "state"

def export_state_for_openclaw(state: dict):
    state_file = STATE_DIR / "amos_state.json"
    state_file.write_text(json.dumps(state, indent=2))
```

**OpenClaw reads state:**
```typescript
// src/amos/amos-state-reader.ts
import { readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";

const stateFile = join(homedir(), ".amos-openclaw-bridge", "state", "amos_state.json");

export function loadAmosState() {
  return JSON.parse(readFileSync(stateFile, "utf-8"));
}
```

## Feature Mapping

| AMOS-code Feature | OpenClaw Integration | Bridge File |
|-------------------|---------------------|-------------|
| 14-Layer Architecture | `src/amos/amos-cognitive-integration.ts` | Direct API |
| 180+ Equations | `src/amos/amos-equations-atlas.ts` | MCP Protocol |
| Brain Health Monitor | `src/amos/amos-observability.ts` | WebSocket |
| Self-Healing | `src/amos/amos-self-healing-controller.ts` | State Sync |
| Tiered Memory | `src/amos/amos-tiered-memory-integration.ts` | File Bridge |
| Security Scanner | `src/amos/security-scanner.ts` | Direct Import |
| Performance Analyzer | `src/amos/amos-performance-analyzer.ts` | MCP Tool |
| Multi-Agent | `src/amos/amos-multi-agent.ts` | Agent Bridge |

## Quick Start

### Step 1: Verify Repositories
```bash
# Check AMOS-code
ls /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_brain/clawspring_bridge.py

# Check OpenClaw
ls /Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main/src/amos/amos-integration.ts
```

### Step 2: Install Dependencies
```bash
# AMOS-code side
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
pip install -e .

# OpenClaw side  
cd /Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main
pnpm install
```

### Step 3: Start Bridge
```bash
# Terminal 1: Start AMOS API
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
python amos_api_server.py

# Terminal 2: Start OpenClaw with AMOS
cd /Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main
openclaw gateway --port 18789
```

### Step 4: Test Integration
```bash
# Test from OpenClaw CLI
openclaw agent --message "Analyze with AMOS" --thinking high

# Test from AMOS CLI
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
python amos_cli.py brain status
```

## Configuration

### Environment Variables
```bash
# ~/.amos-openclaw.env

# AMOS Configuration
AMOS_HOME=/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
AMOS_OPENCLAW_ENABLED=true
AMOS_BRIDGE_MODE=api  # api | mcp | file | direct

# OpenClaw Configuration  
OPENCLAW_AMOS_ENABLED=true
OPENCLAW_AMOS_API_URL=http://localhost:8000
OPENCLAW_AMOS_STATE_DIR=~/.amos-openclaw-bridge
```

## Advanced Integration

### Custom Bridge Implementation

Create a custom bridge for specific use cases:

```python
# custom_amos_openclaw_bridge.py
from amos_brain.clawspring_bridge import AMOSAgentBridge
from pathlib import Path
import json

class AMOSOpenClawUnifiedBridge:
    """Unified bridge combining AMOS 14-layer + OpenClaw agent capabilities."""
    
    def __init__(self):
        self.amos = AMOSAgentBridge()
        self.openclaw_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main")
        self.state_dir = Path.home() / ".amos-openclaw-bridge"
        
    async def unified_analysis(self, input_text: str) -> dict:
        """Run analysis through both systems."""
        # AMOS cognitive analysis
        amos_result = self.amos.analyze_problem(input_text)
        
        # Export for OpenClaw
        self._export_to_openclaw(amos_result)
        
        return {
            "amos_analysis": amos_result,
            "bridge_status": "connected",
            "layers_active": 14
        }
    
    def _export_to_openclaw(self, data: dict):
        """Export AMOS state to OpenClaw."""
        export_file = self.state_dir / "amos_export.json"
        export_file.write_text(json.dumps(data, indent=2))
```

## Troubleshooting

### Common Issues

1. **Path Not Found**
   ```bash
   # Verify paths
   ls -la /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
   ls -la /Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main
   ```

2. **Import Errors**
   ```bash
   # Add to PYTHONPATH
   export PYTHONPATH="$PYTHONPATH:/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
   export PYTHONPATH="$PYTHONPATH:/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main"
   ```

3. **Permission Denied**
   ```bash
   # Create bridge directory
   mkdir -p ~/.amos-openclaw-bridge/state
   chmod 755 ~/.amos-openclaw-bridge
   ```

## Resources

- **OpenClaw AMOS Docs**: `/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main/AMOS.md`
- **OpenClaw AGENTS.md**: `/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main/AGENTS.md`
- **AMOS Integration**: `/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main/src/amos/amos-integration.ts`
- **ClawSpring Bridge**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_brain/clawspring_bridge.py`

## Status

✅ **Integration Ready** - Both repositories contain bidirectional bridge implementations

- AMOS-code: `amos_brain/clawspring_bridge.py` ready for OpenClaw connection
- OpenClaw: `src/amos/amos-integration.ts` with 300+ AMOS modules
- Connection: Multiple bridge methods available (Direct, MCP, API, File)
