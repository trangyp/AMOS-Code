# Getting Started with AMOS

Welcome! This guide will help you get up and running with AMOS in minutes.

## Prerequisites

- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 2GB free space
- **Optional**: Docker for containerized deployment

## Installation Methods

Choose the method that best fits your needs:

### Option 1: pip Install (Recommended)

```bash
pip install amos-brain
```

### Option 2: From Source

```bash
git clone https://github.com/trangyp/AMOS-Code.git
cd AMOS-Code
pip install -e ".[dev]"
```

### Option 3: Docker

```bash
docker pull ghcr.io/trangyp/amos:latest
docker run -p 8080:8080 ghcr.io/trangyp/amos:latest
```

## Quick Verification

Verify your installation:

```bash
python -c "from amos_unified_system import AMOSUnifiedSystem; print('✓ AMOS installed successfully')"
```

## Next Steps

- [Installation Guide](installation.md) - Detailed installation options
- [Quick Start](quickstart.md) - Your first AMOS application
- [Configuration](configuration.md) - Customize AMOS for your environment

---

## Need Help?

- 📖 Browse the [User Guide](../user-guide/index.md)
- 🔍 Search the [API Reference](../api-reference/index.md)
- 💬 Join [GitHub Discussions](https://github.com/trangyp/AMOS-Code/discussions)
