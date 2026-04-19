# AMOS Equation System API SDK

API Client SDKs for easy integration with the AMOS Equation System.

## Quick Start

### Python (Manual)

```python
import httpx

# List equations
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v1/equations/")
    equations = response.json()
    
# Create equation
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/equations/",
        json={
            "name": "Einstein's Equation",
            "latex": "E = mc^2",
            "equation_type": "physics"
        }
    )
    new_equation = response.json()
```

### JavaScript/TypeScript (Fetch)

```javascript
// List equations
const response = await fetch('http://localhost:8000/api/v1/equations/');
const equations = await response.json();

// Create equation
const response = await fetch('http://localhost:8000/api/v1/equations/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: "Einstein's Equation",
        latex: "E = mc^2",
        equation_type: "physics"
    })
});
const newEquation = await response.json();
```

## Auto-Generated Clients

Generate type-safe clients for your preferred language:

```bash
# Generate all clients
python sdk/generate_clients.py --all

# Generate specific language
python sdk/generate_clients.py --lang python
python sdk/generate_clients.py --lang typescript
python sdk/generate_clients.py --lang go
python sdk/generate_clients.py --lang java
python sdk/generate_clients.py --lang rust
```

### Supported Languages

| Language | Generator | Async Support |
|----------|-----------|---------------|
| Python | `python` | Yes (asyncio) |
| TypeScript | `typescript-fetch` | Yes (Promises) |
| JavaScript | `javascript` | Yes (Promises) |
| Go | `go` | Yes (goroutines) |
| Java | `java` | Yes (CompletableFuture) |
| Rust | `rust` | Yes (async/await) |

## Requirements

- Docker (for OpenAPI Generator)
- Running API server on localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
