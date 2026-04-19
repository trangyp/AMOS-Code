# AMOS Offline LLM Coding Guide

This guide explains how to use the strongest offline LLM coding models with AMOS Brain.

## Quick Start

Run the setup script to automatically install and configure the best offline coding model:

```bash
python setup_offline_coding_llm.py
```

This will:
1. Check if Ollama is installed (install if needed)
2. Start the Ollama service
3. Download **Qwen 2.5 Coder** (state-of-the-art coding model)
4. Configure AMOS to use the offline model
5. Test the integration

## Recommended Coding Models

| Model | Size | Best For | VRAM Required |
|-------|------|----------|---------------|
| **qwen2.5-coder:32b** | 32B | Maximum coding performance | ~24GB |
| **qwen2.5-coder:14b** | 14B | Best balance | ~10GB |
| **deepseek-coder-v2:16b** | 16B | Code completion | ~12GB |
| **codellama:70b** | 70B | Largest CodeLlama | ~48GB |
| **codellama:34b** | 34B | Balanced CodeLlama | ~24GB |
| **phi4:14b** | 14B | Efficient coding | ~10GB |
| **llama3.3:70b** | 70B | General + coding | ~48GB |

## Manual Installation

If you prefer to install manually:

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
# Or download from https://ollama.com/download
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from: https://ollama.com/download

### 2. Start Ollama

```bash
ollama serve
```

### 3. Download a Coding Model

```bash
# Best overall coding model (recommended)
ollama pull qwen2.5-coder:14b

# Or for maximum performance (requires more VRAM)
ollama pull qwen2.5-coder:32b

# Alternative: DeepSeek Coder
ollama pull deepseek-coder-v2:16b
```

### 4. Configure AMOS

Add to your `.env` file:

```bash
OLLAMA_MODEL=qwen2.5-coder:14b
OLLAMA_HOST=http://localhost:11434
```

## Using with AMOS Brain

### Python API

```python
from backend.llm_providers import llm_router, LLMRequest, Message
import asyncio

async def code_with_amos():
    # The router automatically prefers Ollama when available
    request = LLMRequest(
        messages=[
            Message(role="system", content="You are an expert Python developer."),
            Message(role="user", content="Write a recursive factorial function with type hints.")
        ],
        temperature=0.7
    )
    
    response = await llm_router.route_request(request)
    print(response.content)
    print(f"Model: {response.model}")
    print(f"Latency: {response.latency_ms:.0f}ms")

asyncio.run(code_with_amos())
```

### Via CLI

```bash
# If your CLI supports brain commands
python amos_cli.py brain "Generate a Python function to parse JSON safely"
```

### Via Cognitive Engine

```python
from amos_brain.cognitive_engine import get_cognitive_engine

engine = get_cognitive_engine()
engine.initialize()

result = engine.process(
    query="Refactor this code to use async/await",
    domain="software_engineering",
    context={"code": "your code here"}
)

print(result.content)
print(f"Confidence: {result.confidence}")
```

### Direct Ollama Provider

```python
from backend.llm_providers import OllamaProvider, LLMRequest, Message

async def use_ollama_directly():
    provider = OllamaProvider()
    
    request = LLMRequest(
        messages=[
            Message(role="user", content="Explain Python decorators")
        ],
        model="qwen2.5-coder:14b",  # Specify exact model
        temperature=0.5
    )
    
    response = await provider.complete(request)
    print(response.content)

import asyncio
asyncio.run(use_ollama_directly())
```

## Provider Priority

The AMOS LLM Router uses this priority:

1. **Ollama** (local/offline) - Used first if available
2. **OpenAI** (cloud) - Fallback if Ollama unavailable
3. **Anthropic** (cloud) - Fallback if OpenAI unavailable
4. **Mock** (local) - Ultimate fallback

To force a specific provider:

```python
# Force Ollama
response = await llm_router.route_request(request, preference="ollama")

# Force OpenAI
response = await llm_router.route_request(request, preference="openai")
```

## Streaming Responses

For real-time code generation:

```python
async def stream_code():
    request = LLMRequest(
        messages=[
            Message(role="user", content="Write a FastAPI endpoint")
        ],
        stream=True
    )
    
    async for chunk in llm_router.route_stream(request, preference="ollama"):
        print(chunk, end="", flush=True)

asyncio.run(stream_code())
```

## Checking Available Models

```python
from backend.llm_providers import OllamaProvider

provider = OllamaProvider()
models = provider.get_available_models()
print(f"Available models: {models}")
print(f"Ollama enabled: {provider.is_enabled()}")
```

## Troubleshooting

### Ollama not running

```bash
# Start Ollama
ollama serve

# Or run in background
nohup ollama serve > /dev/null 2>&1 &
```

### Model not found

```bash
# List downloaded models
ollama list

# Pull a model
ollama pull qwen2.5-coder:14b
```

### Out of memory

Use a smaller model:
```bash
ollama pull qwen2.5-coder:7b  # Smaller version
ollama pull phi4:14b           # Efficient alternative
```

### Connection refused

Ensure Ollama is running on the correct port:
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Set custom host if needed
export OLLAMA_HOST=http://localhost:11434
```

## Performance Tips

1. **First inference is slow** - Model loading takes time; subsequent requests are faster
2. **Use quantization** - Ollama models are already quantized for efficiency
3. **Enable GPU** - Ollama automatically uses GPU if available
4. **Keep model loaded** - Don't stop Ollama between requests

## Model Comparison for Coding

| Task | Best Model | Notes |
|------|-----------|-------|
| Code generation | qwen2.5-coder:32b | State-of-the-art |
| Code completion | deepseek-coder-v2 | Optimized for fill-in-middle |
| Refactoring | qwen2.5-coder:14b | Balanced performance |
| Documentation | phi4:14b | Efficient and capable |
| Debugging | llama3.3:70b | Strong reasoning |

## Resources

- [Ollama Models](https://ollama.com/library)
- [Qwen 2.5 Coder](https://huggingface.co/Qwen/Qwen2.5-Coder)
- [DeepSeek Coder](https://huggingface.co/deepseek-ai/deepseek-coder)
