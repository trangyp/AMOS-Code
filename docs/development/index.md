# Development Guide

Contribute to AMOS and extend its capabilities.

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Docker (optional, for testing)

### Setup

```bash
# Clone the repository
git clone https://github.com/trangyp/AMOS-Code.git
cd AMOS-Code

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Development Sections

### [Development Setup](setup.md)
Complete development environment setup.

### [Testing](testing.md)
Writing and running tests.

### [Contributing](contributing.md)
Guidelines for contributing to AMOS.

---

## Project Structure

```
AMOS-Code/
├── amos_brain/           # Core AMOS brain
├── amosl/               # AMOS Language
├── clawspring/          # LLM providers
├── repo_doctor/         # Repository monitoring
├── tests/               # Test suite
├── docs/                # Documentation
├── .github/             # GitHub workflows
├── docker-compose.amos.yml
├── mkdocs.yml           # Documentation config
├── pyproject.toml       # Project config
└── requirements.txt     # Dependencies
```

## Code Quality

We maintain high code quality standards:

- **Type Hints**: All functions should have type annotations
- **Docstrings**: Google-style docstrings for all public APIs
- **Tests**: Minimum 80% code coverage
- **Linting**: All code must pass ruff and mypy checks

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Contributing Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -am 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. **Create** a Pull Request

---

## Community

- **Discussions**: [GitHub Discussions](https://github.com/trangyp/AMOS-Code/discussions)
- **Issues**: [GitHub Issues](https://github.com/trangyp/AMOS-Code/issues)
- **Discord**: [AMOS Community](https://discord.gg/amos-ai)

---

!!! info "License"
    By contributing to AMOS, you agree that your contributions will be licensed under the MIT License.
