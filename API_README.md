# AMOS Brain API

**Domain:** `neurosyncai.tech`  
**Base URL:** `https://neurosyncai.tech`

## Overview

AMOS Brain API exposes the AMOS cognitive architecture via REST endpoints. Use it for:

- **Thinking:** Get cognitive analysis on any topic
- **Decision Making:** Structured decisions with reasoning
- **Validation:** Check actions against global laws
- **Status:** Monitor brain health and capabilities

## Quick Start

### Health Check
```bash
curl https://neurosyncai.tech/health
```

### Test Thinking
```bash
curl -X POST https://neurosyncai.tech/think \
  -H "Content-Type: application/json" \
  -d '{"query": "Benefits of microservices?", "domain": "software"}'
```

## Endpoints

### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "amos-brain-api",
  "domain": "neurosyncai.tech"
}
```

### GET /status
Get full brain system status.

**Response:**
```json
{
  "success": true,
  "status": {
    "status": "operational",
    "layers": {...},
    "law_compliance": {...}
  }
}
```

### POST /think
Cognitive analysis of a query.

**Request:**
```json
{
  "query": "Your question or task",
  "domain": "software"  // optional: software, science, business
}
```

**Response:**
```json
{
  "success": true,
  "content": "Analysis result...",
  "reasoning": ["step 1", "step 2"],
  "confidence": "high",
  "law_compliant": true,
  "violations": [],
  "metadata": {...}
}
```

### POST /decide
Structured decision making.

**Request:**
```json
{
  "question": "Should we adopt X?",
  "options": ["Option A", "Option B", "Option C"]
}
```

**Response:**
```json
{
  "approved": true,
  "decision_id": "DEC-1234",
  "reasoning": "...",
  "risk_level": "low",
  "law_violations": [],
  "alternative_actions": [...]
}
```

### POST /validate
Validate an action against global laws.

**Request:**
```json
{"action": "Description of the action"}
```

**Response:**
```json
{
  "valid": true,
  "violations": [],
  "action": "..."
}
```

## Client Libraries

### Python
```python
import requests

API_URL = "https://neurosyncai.tech"

# Think
response = requests.post(f"{API_URL}/think", json={
    "query": "Best practices for API design?",
    "domain": "software"
})
print(response.json()["content"])

# Decide
decision = requests.post(f"{API_URL}/decide", json={
    "question": "Which database to use?",
    "options": ["PostgreSQL", "MongoDB", "SQLite"]
})
print(decision.json()["reasoning"])
```

See `examples/python_client.py` for complete client.

## Global Laws

All operations are validated against AMOS Global Laws:

- **L1:** Law of Law (actions must be lawful)
- **L2:** Rule of 2 (minimum 2 perspectives)
- **L3:** Rule of 4 (4-quadrant analysis)
- **L4:** Structural Integrity
- **L5:** Communication Clarity
- **L6:** UBI Alignment

Violations are returned in the `violations` field.

## Dashboard

Interactive API tester available at:  
`https://neurosyncai.tech/test-api.html`

## Rate Limits

- Default: 100 requests/minute
- Contact for increased limits

## Support

- Domain: neurosyncai.tech
- Repository: AMOS-code
- Deployment: Hostinger + Docker
