# AMOS Brain API - Quick Start

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
