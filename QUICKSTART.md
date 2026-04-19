# AMOS Local-First AI Platform - Quick Start

## New: Local Platform (Offline LLMs)

The AMOS Local Platform provides a complete offline AI development environment:

### Quick Setup (5 minutes)

```bash
# 1. Test platform components
python3 test_platform.py

# 2. Setup all tools
python3 amos_local_platform.py setup

# 3. Start LiteLLM proxy
python3 amos_local_platform.py start

# 4. Check status
python3 amos_local_platform.py status
```

### Components

| Component | Purpose | Command |
|-----------|---------|---------|
| **LiteLLM** | Model routing proxy | `python3 -m amos_model_fabric.litellm_setup start` |
| **Continue** | VS Code AI assistant | Config at `~/.continue/config.yaml` |
| **Aider** | Terminal AI coding | `aider --openai-api-base http://localhost:4000` |
| **OpenHands** | Autonomous AI engineer | `python3 -m amos_model_fabric.openhands_integration interactive` |
| **Repo Doctor** | Security verification | `python3 -m repo_doctor.security_scanner` |

### Requirements

- Python 3.10+
- Ollama (for local LLMs)
- Docker (for OpenHands)
- VS Code (for Continue)

---

# AMOS Brain API - Quick Start (Cloud)

**Domain:** `neurosyncai.tech`

## 1. Get API Key

Use the admin endpoint with your master key:

```bash
curl -X POST https://neurosyncai.tech/admin/keys \
  -H "X-Master-Key: your-master-key"
```

**Response:**
```json
{
  "api_key": "abc123...xyz",
  "message": "Store this key securely."
}
```

## 2. Make First Request

```bash
curl -X POST https://neurosyncai.tech/think \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "Benefits of TypeScript?"}'
```

## 3. Use Client Libraries

### Python
```python
from examples.python_client import AMOSBrainClient

client = AMOSBrainClient('https://neurosyncai.tech', 'your-api-key')
result = client.think("What are design patterns?")
print(result['content'])
```

### JavaScript
```javascript
import { AMOSBrainClient } from './examples/js_client.js';

const client = new AMOSBrainClient('https://neurosyncai.tech', 'your-api-key');
const result = await client.think("Benefits of microservices?");
console.log(result.content);
```

### React
```jsx
import { useAMOSBrain } from './examples/react_example';

function App() {
  const { think, loading } = useAMOSBrain('your-api-key');
  // Use think() in your components
}
```

## 4. Available Endpoints

| Endpoint | Method | Auth Required |
|----------|--------|---------------|
| `/health` | GET | No |
| `/think` | POST | Yes |
| `/decide` | POST | Yes |
| `/validate` | POST | Yes |
| `/admin/keys` | POST | Master Key |
| `/admin/stats` | GET | Master Key |

## 5. Rate Limits

- Default: 100 requests/minute per API key
- Admin endpoints: 1000 requests/minute

## 6. Deployment Status

Run verification:
```bash
python verify-deployment.py
```

Interactive tester:
- Open `test-api.html` in browser
- Or visit: `https://neurosyncai.tech/test-api.html`

---

**Full Documentation:** See `API_README.md`
