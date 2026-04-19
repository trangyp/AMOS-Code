# AMOS LLM Provider Infrastructure Architecture

**Status:** ✅ Implemented  
**Date:** 2024-01-15  
**Owner:** Trang  

## Overview

Complete multi-provider LLM infrastructure with **local-first** strategy, intelligent routing, and UBI (Unified Biological Intelligence) integration.

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE ACTION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User Input                                                        │
│      ↓                                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ProviderManager (Intelligent Router)                     │  │
│  │  ├── Detects biological context                            │  │
│  │  ├── Selects best provider                                │  │
│  │  └── Handles fallback                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│      ↓                                                             │
│  ┌─────────────┬─────────────┬─────────────┐                  │
│  │   Ollama    │  OpenAI     │  Anthropic  │                  │
│  │  (Local)    │  (Cloud)    │  (Cloud)    │                  │
│  │             │             │             │                  │
│  │ • llama3.2  │ • gpt-4o    │ • claude-3  │                  │
│  │ • mistral   │ • gpt-4o-m  │             │                  │
│  │ • phi4      │ • gpt-3.5   │             │                  │
│  └─────────────┴─────────────┴─────────────┘                  │
│      ↓                                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Biologically-Enhanced Response                           │  │
│  │  └── Context-aware, UI-adapted output                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Strategy

### 1. Local-First Architecture

| Priority | Provider | When Used | Benefits |
|----------|----------|-----------|----------|
| **1** | Ollama | Always try first | Privacy, no API costs, low latency |
| **2** | OpenAI | Ollama fails | Reliability, advanced models |
| **3** | Anthropic | OpenAI fails | Alternative, different capabilities |

### 2. Intelligent Routing

```python
# Routing Logic
if model contains "llama/mistral/phi/gemma":
    → Try Ollama first
if model contains "gpt":
    → Try OpenAI
if Ollama unavailable:
    → Fallback to OpenAI
if both fail:
    → Return error with helpful message
```

## Components

### 1. BaseProvider (Abstract)

```python
class BaseProvider(ABC):
    """Foundation for all providers"""
    
    async def complete(self, request: LLMRequest) -> LLMResponse
    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]
    async def get_available_models(self) -> List[str]
```

### 2. OllamaProvider (Local)

**Endpoint:** `http://localhost:11434`

```python
# Auto-detection
async def _check_ollama_running() -> bool:
    GET /api/tags  # Returns available models

# Chat completion
POST /api/chat
{
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "..."}],
    "stream": false,
    "options": {"temperature": 0.7}
}
```

**Supported Models:**
- llama3.2 (default)
- llama3.1
- mistral
- codellama
- phi4
- gemma2

### 3. OpenAIProvider (Cloud)

**Endpoint:** `https://api.openai.com/v1`

```python
# Chat completion
POST /chat/completions
Headers: Authorization: Bearer {api_key}
Body: {
    "model": "gpt-4o-mini",
    "messages": [...],
    "temperature": 0.7
}
```

**Supported Models:**
- gpt-4o
- gpt-4o-mini (default fallback)
- gpt-4-turbo
- gpt-3.5-turbo

### 4. ProviderManager (Router)

```python
class ProviderManager:
    """Intelligent provider routing with UBI integration"""
    
    async def complete(
        messages: List[Message],
        model: Optional[str] = None,
        provider: Optional[str] = None,  # Force specific provider
        temperature: float = 0.7,
        biological_context_description: Optional[str] = None,  # UBI input
    ) -> LLMResponse
```

## UBI Integration

### Biological Context Injection

```python
# Example: User describes their state
user_state = "Feeling overwhelmed, 6 hours working, screen glare"

# ProviderManager automatically:
1. Calls UBI Engine → Analyzes biological state
2. Creates CognitiveContext
3. Injects into LLM prompt:

[AMOS Biological Context - 14:32]
- User cognitive load: high
- Emotional state: stressed
- Physical comfort: strained
- Environment: poor

Adapt response accordingly:
- High cognitive load → Simplify, bullet points
- Stressed → Calm tone, reassurance
- Physical strain → Minimize interaction steps
- Poor environment → Larger text, high contrast

[User Request]
Explain quantum computing
```

## Usage Examples

### Simple Completion

```python
from backend.llm_providers_complete import complete

# Simple usage (auto-routes to available provider)
response = await complete(
    prompt="Explain quantum computing",
    biological_context="Feeling tired after long work day"
)
print(response)  # Biologically-aware explanation
```

### Advanced Usage

```python
from backend.llm_providers_complete import get_provider_manager, Message

manager = get_provider_manager()

# Force specific provider and model
response = await manager.complete(
    messages=[Message(role="user", content="Write Python code")],
    model="llama3.2",
    provider="ollama",  # Force Ollama
    biological_context_description="Energized, ready for complex coding",
    temperature=0.5
)

print(f"Model: {response.model}")
print(f"Provider: {response.provider}")
print(f"Latency: {response.latency_ms}ms")
print(f"Content: {response.content}")
```

### Streaming

```python
async for chunk in manager.complete_stream(
    messages=[Message(role="user", content="Tell me a story")],
    biological_context_description="Relaxed, enjoying evening reading"
):
    print(chunk, end="", flush=True)
```

### Get Available Models

```python
models = await manager.get_available_models()
# Returns: {"ollama": ["llama3.2", "mistral"], "openai": ["gpt-4o", "gpt-4o-mini"]}
```

## Integration Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Integration Chain                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Dashboard/API → User enters prompt + state          │
│                      ↓                                   │
│  2. ProviderManager → Analyzes biological context        │
│                      ↓                                   │
│  3. UBI Engine      → NBI/NEI/SI/BEI analysis            │
│                      ↓                                   │
│  4. Router          → Selects provider (Ollama/OpenAI)  │
│                      ↓                                   │
│  5. Provider        → Sends biologically-enhanced prompt│
│                      ↓                                   │
│  6. LLM             → Generates context-aware response    │
│                      ↓                                   │
│  7. UI              → Renders with appropriate guidelines │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# OpenAI (optional - for cloud fallback)
export OPENAI_API_KEY="sk-..."

# Ollama (auto-detected, no config needed)
# Must be running on http://localhost:11434
```

### Starting Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.2
ollama pull mistral
ollama pull phi4

# Start server (runs on :11434)
ollama serve
```

## Performance

| Provider | Latency | Privacy | Cost | Reliability |
|----------|---------|---------|------|-------------|
| Ollama | ~500ms | ✅ Full | Free | Depends on setup |
| OpenAI | ~1000ms | ❌ Cloud | $$$ | 99.9% SLA |

## Fallback Strategy

```python
try:
    # Try Ollama first (local, private)
    return await ollama.complete(request)
except Exception as e:
    print(f"Ollama failed: {e}")
    
    # Fallback to OpenAI (reliable)
    if openai.available:
        return await openai.complete(request)
    
    # All failed
    raise Exception("No LLM provider available. Start Ollama or check API keys.")
```

## Research Foundation

Based on:
- **LiteLLM** - Unified LLM interface (100+ providers)
- **Local-first AI** - Privacy-preserving architecture
- **UBI Framework** - Biological state-aware computing
- **Cognitive Architecture 2024** - Perception-Cognition-Action loops

## Files Created

| File | Purpose | LOC |
|------|---------|-----|
| `backend/llm_providers_complete.py` | Complete provider infrastructure | ~600 |
| `docs/LLM_PROVIDER_ARCHITECTURE.md` | This documentation | ~400 |

## Next Steps

Future enhancements:
1. **Anthropic Claude Provider** - Add claude-3 support
2. **Model Caching** - Cache responses for similar queries
3. **Cost Tracking** - Track API usage across providers
4. **A/B Testing** - Compare model performance
5. **Fine-tuning** - Custom models for specific domains
