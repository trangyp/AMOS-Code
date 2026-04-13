# AMOS Brain MCP Integration Guide

Connect AMOS Brain to AI assistants using the Model Context Protocol (MCP).

## What is MCP?

Model Context Protocol (MCP) is an open protocol by Anthropic that enables AI assistants to discover and use external tools. AMOS Brain exposes its cognitive capabilities as MCP tools.

## Available Tools

| Tool | Description |
|------|-------------|
| `amos_reasoning` | Apply Rule of 2 and Rule of 4 analysis |
| `amos_decide` | Full decision analysis workflow |
| `amos_laws_check` | Check compliance with Global Laws |
| `amos_status` | Get brain status and capabilities |
| `amosl_compile` | Compile AMOSL source code |

## Integration Methods

### 1. ClawSpring Integration (stdio)

Add to your `~/.clawspring/mcp.json`:

```json
{
  "mcpServers": {
    "amos": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/AMOS-code/amos_mcp_server.py"]
    }
  }
}
```

### 2. Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "amos": {
      "command": "python3",
      "args": ["/path/to/AMOS-code/amos_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/AMOS-code"
      }
    }
  }
}
```

### 3. Cursor Integration

Add to Cursor settings (Settings > Features > MCP):

```json
{
  "mcpServers": {
    "amos": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/AMOS-code/amos_mcp_server.py"]
    }
  }
}
```

### 4. Windsurf Integration

Add to `~/.windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "amos": {
      "command": "python3",
      "args": ["/path/to/AMOS-code/amos_mcp_server.py"]
    }
  }
}
```

## Usage Examples

### Reasoning Analysis

Ask your AI assistant:

```
Use AMOS Brain to analyze: Should we build a mobile app or web app first?
Domain: software
```

The assistant will call `amos_reasoning` and return:
- Rule of 2 confidence score
- Rule of 4 quadrant analysis
- Structural integrity assessment
- Recommendations

### Decision Making

```
Ask AMOS to decide: Which database should we use?
Options: PostgreSQL, MongoDB, SQLite
```

The assistant will call `amos_decide` with:
- Decision question
- List of options
- Return recommendation with risk level

### AMOSL Compilation

```
Compile this AMOSL code:
ontology {
  classical {
    entity User {
      name: Text
      age: Int
    }
  }
}
```

The assistant will call `amosl_compile` and return:
- CIR blocks count
- QIR registers count
- BIR species count
- HIR bridges count
- Invariant validation status

## Testing the MCP Server

Run the server in stdio mode:

```bash
cd /path/to/AMOS-code
python3 amos_mcp_server.py
```

The server will read JSON-RPC requests from stdin and write responses to stdout.

## Troubleshooting

### Server Not Starting

1. Check Python path: Ensure `AMOS-code` is in `PYTHONPATH`
2. Install dependencies: `pip install -r requirements.txt`
3. Verify imports: `python3 -c "from amos_brain import get_amos_integration"`

### Tools Not Showing

1. Restart your AI assistant after configuration
2. Check MCP server logs for errors
3. Verify JSON-RPC communication: Server uses stdio

### Connection Errors

1. Ensure server has execute permissions
2. Check file paths are absolute
3. Verify Python version: Requires Python 3.8+

## Advanced Configuration

### Environment Variables

```bash
export AMOS_API_KEY="your_api_key"  # For API access
export AMOS_LOG_LEVEL="debug"        # Enable debug logging
```

### Custom Base URL

Edit `amos_mcp_server.py` to use a custom API endpoint:

```python
DEFAULT_BASE_URL = "https://your-domain.com"
```

## Next Steps

- [SDK Documentation](SDK.md) - Python and JavaScript SDKs
- [API Reference](API_README.md) - REST API documentation
- [Dashboard Guide](DASHBOARD.md) - Web interface

## Support

- Website: https://neurosyncai.tech
- Documentation: https://neurosyncai.tech/docs
- Community: https://github.com/trangyp/AMOS-Code

---

**AMOS Brain** - Absolute Meta Operating System  
Created by Trang Phan
