<div align="center">
  <img src="docs/amos-logo.svg" alt="AMOS Brain Logo" width="180">
  <h1>AMOS Brain</h1>
  <p><strong>Absolute Meta Operating System</strong></p>
  <p>A comprehensive AI agent framework with structured reasoning, cognitive compliance, and multi-agent orchestration.</p>
</div>

---

## 🧠 What is AMOS Brain?

AMOS Brain is a unified cognitive architecture that adds structured reasoning capabilities to AI agents:

- **Rule of 2** - Dual perspective analysis (L2 reasoning)
- **Rule of 4** - Four quadrant systems thinking (L3 reasoning)
- **6 Global Laws** - L1-L6 compliance enforcement
- **12 Domain Engines** - Routing to specialized intelligence
- **Memory & Recall** - Persistent reasoning history
- **Analytics Dashboard** - Decision pattern insights
- **Multi-Agent Orchestration** - Coordinated agent teams

---

## 🚀 Quick Start

### Local LLM Mode (Recommended)

Run AMOS with local models (Ollama, LM Studio, vLLM) - no API keys needed:

```bash
# With Ollama (default)
export AMOS_MODEL=llama3.2:latest
python amos_local.py

# With LM Studio
export AMOS_LLM_BACKEND=lmstudio
export AMOS_MODEL=your-model-name
python amos_local.py

# Health check only
python amos_local.py --check
```

### Legacy Mode (Cloud Providers)

```bash
# Unified launcher - discover all features
python amos_brain_launcher.py

# Or start with tutorial
python amos_brain_tutorial.py

# Or use the CLI
python amos_brain_cli.py
```

See `amos_brain/README.md` and `AMOS_BRAIN_GUIDE.md` for full documentation.

---

## � Local LLM Configuration

The new `amos_local.py` launcher puts local models first, with AMOS as the governance layer.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AMOS_LLM_BACKEND` | Backend type: `ollama`, `lmstudio`, `vllm`, `llamacpp` | `ollama` |
| `AMOS_MODEL` | Model name to use | `qwen2.5:14b-instruct` |
| `AMOS_BASE_URL` | Custom server URL | Auto-detected by backend |
| `AMOS_API_KEY` | API key for OpenAI-compatible | `local` |
| `AMOS_TEMPERATURE` | Sampling temperature | `0.2` |

### Backend-Specific Setup

**Ollama:**
```bash
# Install and start Ollama
ollama serve

# Pull a model
ollama pull llama3.2:latest

# Run AMOS
export AMOS_MODEL=llama3.2:latest
python amos_local.py
```

**LM Studio:**
```bash
# 1. Start LM Studio
# 2. Load a model in the UI
# 3. Enable local server (port 1234)
# 4. Run AMOS
export AMOS_LLM_BACKEND=lmstudio
export AMOS_MODEL=your-model-name
python amos_local.py
```

**vLLM:**
```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-chat-hf

# Run AMOS
export AMOS_LLM_BACKEND=vllm
export AMOS_MODEL=meta-llama/Llama-2-7b-chat-hf
python amos_local.py
```

### Features

- **Streaming responses** - Tokens appear in real-time as model generates
- **Automatic retries** - 3 retries with exponential backoff for resilience
- **Health validation** - Checks model availability before starting
- **Configuration validation** - Early error detection with actionable messages
- **Actionable errors** - Clear guidance when things fail (e.g., "Run: ollama pull llama3.2")

---

## �📦 Project Structure

| Component | Description |
|-----------|-------------|
| `amos_brain/` | Core brain implementation with cognitive architecture |
| `clawspring/` | AI assistant runtime with multi-provider support |
| `AMOS_ORGANISM_OS/` | Organism-level operating system |
| `memory/` | Persistent memory system |
| `skill/` | Skill system with built-in capabilities |
| `multi_agent/` | Multi-agent orchestration |

---

## ✨ Key Features

### Multi-Provider Support
- Anthropic Claude
- OpenAI GPT/o-series
- Google Gemini
- Ollama (local models)
- LM Studio, vLLM, custom endpoints

### Cognitive Architecture
- 6 levels of reasoning (L1-L6)
- Global Laws enforcement
- Domain-specific engines
- Decision analytics

### Agent Capabilities
- 18+ built-in tools
- Persistent memory (dual-scope)
- Skill system with templates
- Multi-agent brainstorming
- Git worktree isolation

---

## 📚 Documentation

- **AMOS_BRAIN_GUIDE.md** - Complete brain documentation
- **AMOS_COGNITIVE_RUNTIME_README.md** - Runtime guide
- **amos_brain/README.md** - Core brain docs

---

## 🔧 Installation

```bash
pip install -e .

# With all optional dependencies
pip install -e ".[clawspring,dev]"
```

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 👤 Founder

**Trang Phan (Trang Q. Phan)**

Visionary technologist and AI architect dedicated to creating structured, compliant, and trustworthy AI systems. AMOS Brain represents years of research in cognitive architectures, multi-agent systems, and AI safety.

[LinkedIn](https://www.linkedin.com/in/trangqphan/) | GitHub: [@trangyp](https://github.com/trangyp)

---

**AMOS Project** - Building the future of AI cognition.

*Crafted with ❤️ by Trang Phan*
