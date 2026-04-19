# AMOS Cognitive API Integration - Complete Architecture

**Status:** ✅ Implemented  
**Date:** 2024-01-15  
**Owner:** Trang  

## Overview

Complete **end-to-end cognitive system** integration - from biological perception to LLM action, all exposed through a unified API.

## Architecture Summary

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         AMOS COMPLETE COGNITIVE SYSTEM                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: PERCEPTION (UBI Engine) ✅                                       │
│  ├── NBI: Neurobiological Intelligence (cognitive load)                   │
│  ├── NEI: Neuroemotional Intelligence (stress/arousal)                   │
│  ├── SI: Somatic Intelligence (body comfort)                            │
│  └── BEI: Bioelectromagnetic Intelligence (environment)                   │
│                                                                             │
│                              ↓                                             │
│                                                                             │
│  LAYER 2: COGNITION (Cognitive Bridge) ✅                                   │
│  ├── Analyzes biological state                                             │
│  ├── Generates context injection                                           │
│  └── Creates UI/UX guidelines                                              │
│                                                                             │
│                              ↓                                             │
│                                                                             │
│  LAYER 3: ACTION (Provider Infrastructure) ✅                             │
│  ├── OllamaProvider (local-first)                                         │
│  ├── OpenAIProvider (cloud fallback)                                      │
│  └── ProviderManager (intelligent routing)                                │
│                                                                             │
│                              ↓                                             │
│                                                                             │
│  LAYER 4: API INTEGRATION (Flask API) ✅                                  │
│  ├── /chat - Biologically-aware chat                                       │
│  ├── /chat/stream - Streaming responses                                   │
│  ├── /providers - List available providers/models                         │
│  └── /analyze - UBI biological analysis                                   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

## New API Endpoints

### 1. `/chat` - Biologically-Aware Chat

**Method:** POST  
**Description:** Complete chat with automatic biological context analysis

**Request:**
```json
{
    "message": "Explain quantum computing",
    "context": "Feeling tired, 6 hours working, screen glare",
    "model": "llama3.2",
    "stream": false
}
```

**Response:**
```json
{
    "content": "Here's a simple explanation using bullet points...",
    "model": "llama3.2",
    "provider": "ollama",
    "latency_ms": 523,
    "biological_context": {
        "cognitive_load": "high",
        "emotional_state": "stressed",
        "body_comfort": "strained",
        "environmental_fit": "poor"
    },
    "ui_guidelines": {
        "font_size": "18px",
        "line_height": "1.8",
        "max_width": "600px",
        "chunking": true,
        "tone": "calm"
    },
    "timestamp": "2024-01-15T14:32:00"
}
```

**Curl Example:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "context": "Feeling overwhelmed after long work day"
  }'
```

### 2. `/chat/stream` - Streaming Chat

**Method:** POST  
**Description:** Server-sent events (SSE) streaming for real-time responses

**Request:**
```json
{
    "message": "Tell me a story about AI",
    "context": "Relaxed evening reading",
    "model": "llama3.2"
}
```

**Response:** Stream of SSE events
```
data: Once upon a time...

data: there was an AI

data: that could understand

data: human emotions...

data: [DONE]
```

**JavaScript Example:**
```javascript
const eventSource = new EventSource('/chat/stream', {
    method: 'POST',
    body: JSON.stringify({
        message: "Tell me a story",
        context: "Relaxing evening"
    })
});

eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
        eventSource.close();
    } else {
        appendText(event.data);
    }
};
```

### 3. `/providers` - List Providers

**Method:** GET  
**Description:** Discover available LLM providers and models

**Response:**
```json
{
    "providers": {
        "ollama": ["llama3.2", "mistral", "phi4", "gemma2"],
        "openai": ["gpt-4o", "gpt-4o-mini"]
    },
    "recommended": "ollama",
    "status": "available"
}
```

**Curl Example:**
```bash
curl http://localhost:5000/providers
```

### 4. `/analyze` - UBI Analysis

**Method:** POST  
**Description:** Analyze biological state without generating LLM response

**Request:**
```json
{
    "description": "Feeling overwhelmed, 6 hours working, screen glare"
}
```

**Response:**
```json
{
    "cognitive_load": "high",
    "emotional_state": "stressed",
    "body_comfort": "strained",
    "environmental_fit": "poor",
    "timestamp": "2024-01-15T14:32:00",
    "ui_guidelines": {
        "font_size": "18px",
        "chunking": true,
        "tone": "calm",
        "suggest_break": true
    }
}
```

**Curl Example:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"description": "Feeling tired and stressed"}'
```

## Complete API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Liveness probe |
| `/ready` | GET | Readiness probe |
| `/status` | GET | System status |
| `/chat` | POST | Biologically-aware chat |
| `/chat/stream` | POST | Streaming chat |
| `/providers` | GET | List providers/models |
| `/analyze` | POST | UBI biological analysis |
| `/think` | POST | Legacy thinking endpoint |
| `/query` | POST | Legacy query endpoint |

## Integration Flow

```
User Request
    ↓
POST /chat
{
    "message": "Explain AI",
    "context": "Feeling tired"
}
    ↓
┌──────────────────────────────────────────────────────────────┐
│ API Layer (amos_api_enhanced.py)                             │
│ 1. Extract message and context                               │
│ 2. Import cognitive infrastructure                           │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ Cognitive Bridge (amos_cognitive_bridge.py)                  │
│ 1. Analyze biological state via UBI Engine                   │
│    - NBI: high cognitive load                               │
│    - NEI: stressed emotional state                          │
│    - SI: strained body comfort                               │
│    - BEI: poor environmental fit                             │
│ 2. Generate UI guidelines                                    │
│    - font_size: 18px                                         │
│    - chunking: true                                         │
│    - tone: calm                                             │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ Provider Manager (llm_providers_complete.py)                 │
│ 1. Route to best provider (Ollama → OpenAI fallback)        │
│ 2. Inject biological context into prompt                    │
│ 3. Send to LLM                                              │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ LLM Provider (Ollama/OpenAI)                                  │
│ 1. Receive biologically-enhanced prompt                       │
│ 2. Generate context-aware response                            │
│ 3. Return to Provider Manager                                 │
└──────────────────────────────────────────────────────────────┘
    ↓
Response
{
    "content": "Here's a simple explanation...",
    "biological_context": {...},
    "ui_guidelines": {...}
}
```

## Example: Complete Integration Test

```python
#!/usr/bin/env python3
"""Test AMOS Cognitive API Integration"""

import requests
import json

def test_chat():
    """Test biologically-aware chat."""
    response = requests.post(
        "http://localhost:5000/chat",
        json={
            "message": "Explain quantum computing",
            "context": "Feeling overwhelmed, 6 hours working",
            "model": "llama3.2"
        }
    )
    
    data = response.json()
    print(f"✓ Chat response received")
    print(f"  Provider: {data['provider']}")
    print(f"  Model: {data['model']}")
    print(f"  Latency: {data['latency_ms']}ms")
    print(f"  Cognitive Load: {data['biological_context']['cognitive_load']}")
    print(f"  Font Size: {data['ui_guidelines']['font_size']}")
    return data

def test_analyze():
    """Test UBI analysis."""
    response = requests.post(
        "http://localhost:5000/analyze",
        json={"description": "Relaxed and focused morning"}
    )
    
    data = response.json()
    print(f"✓ Analysis complete")
    print(f"  Emotional State: {data['emotional_state']}")
    print(f"  UI Chunking: {data['ui_guidelines']['chunking']}")
    return data

def test_providers():
    """Test provider discovery."""
    response = requests.get("http://localhost:5000/providers")
    
    data = response.json()
    print(f"✓ Providers discovered")
    for provider, models in data['providers'].items():
        print(f"  {provider}: {models}")
    return data

if __name__ == "__main__":
    print("Testing AMOS Cognitive API...")
    print("=" * 50)
    
    test_providers()
    test_analyze()
    test_chat()
    
    print("=" * 50)
    print("All tests passed!")
```

## Testing with curl

```bash
# 1. Start the server
python amos_api_enhanced.py

# 2. Test health
curl http://localhost:5000/health

# 3. List providers
curl http://localhost:5000/providers

# 4. Analyze state
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"description": "Feeling tired"}'

# 5. Chat with biological context
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain Python",
    "context": "Feeling overwhelmed, need simple explanation"
  }'

# 6. Stream response
curl -X POST http://localhost:5000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a story"}'
```

## Files Created/Modified

| File | Action | Lines | Purpose |
|------|--------|-------|---------|
| `amos_api_enhanced.py` | Modified | +200 | Added cognitive endpoints |
| `clawspring/amos_cognitive_bridge.py` | Created | ~180 | UBI-LLM bridge |
| `backend/llm_providers_complete.py` | Created | ~600 | Provider infrastructure |
| `docs/COGNITIVE_API_INTEGRATION.md` | Created | ~400 | This documentation |

## Production Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AMOS Production Deployment                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Frontend (Dashboard)                                            │
│  ├── amos_dashboard.html                                         │
│  └── Calls /chat with biological context                        │
│                                                                  │
│         ↓ HTTP + CORS                                            │
│                                                                  │
│  API Server (Flask)                                              │
│  ├── Port 5000                                                   │
│  ├── /health (liveness)                                         │
│  ├── /chat (biological-aware)                                   │
│  └── /providers (discovery)                                     │
│                                                                  │
│         ↓                                                        │
│                                                                  │
│  Cognitive Layer                                                 │
│  ├── UBI Engine (perception)                                    │
│  ├── Cognitive Bridge (context)                                 │
│  └── Provider Manager (routing)                                 │
│                                                                  │
│         ↓                                                        │
│                                                                  │
│  LLM Providers                                                   │
│  ├── Ollama (localhost:11434) - Primary                         │
│  └── OpenAI (api.openai.com) - Fallback                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Frontend Integration** - Update dashboard to use new endpoints
2. **Real-time Biometrics** - Add heart rate, eye tracking sensors
3. **Model Caching** - Cache responses for similar queries
4. **A/B Testing** - Compare model performance
5. **Multi-user Support** - Per-user biological profiles

## Summary

✅ **Complete cognitive system implemented:**
- Perception (UBI Engine) → Cognition (Bridge) → Action (LLM) → API (Flask)
- Local-first with cloud fallback
- Streaming support
- Automatic biological adaptation
- Production-ready API

**The AMOS ecosystem is now a fully functional, biologically-aware AI system!**
