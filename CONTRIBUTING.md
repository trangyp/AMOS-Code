# Contributing to AMOS Brain

Thank you for your interest in contributing to AMOS Brain! This document provides guidelines and instructions for contributing.

## 🎯 Development Philosophy

AMOS Brain follows these core principles:

1. **Structured Reasoning** - All decisions should be transparent and traceable
2. **Deterministic Behavior** - Same inputs should produce same outputs
3. **Law Compliance** - Global Laws L1-L6 must be enforced
4. **Type Safety** - Full TypeScript and Pydantic typing
5. **Test Coverage** - All new features require tests

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+ (for frontend)
- **Python** 3.11+ (for backend)
- **Docker** & Docker Compose (for full stack)
- **Git** (for version control)

### Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/amos.git
   cd amos
   ```

2. **Install dependencies**
   ```bash
   make install
   # Or manually:
   cd dashboard && npm install
   cd backend && pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp dashboard/.env.example dashboard/.env
   cp backend/.env.example backend/.env
   # Edit .env files with your configuration
   ```

4. **Start development servers**
   ```bash
   make dev
   ```

## 📝 Contribution Guidelines

### Code Style

**Frontend (TypeScript/React):**
- Use functional components with hooks
- Follow React best practices
- Use TypeScript strict mode
- Run `npm run lint` before committing

**Backend (Python/FastAPI):**
- Follow PEP 8 style guide
- Use type hints everywhere
- Document all functions with docstrings
- Run `flake8` before committing

### Commit Messages

Follow conventional commits format:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/dependency changes

Examples:
```
feat: add WebSocket reconnection logic
fix: resolve memory leak in checkpoint system
docs: update API documentation for AGENTS.md
```

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Refactoring

### Pull Request Process

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** with proper tests

3. **Run tests locally**
   ```bash
   make test
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new cognitive subsystem"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/my-feature
   ```

6. **Open a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)
   - Test results

### Testing Requirements

All contributions must include:

- **Unit tests** for new functions/components
- **Integration tests** for API endpoints
- **Type checking** passes (`npm run type-check`)
- **Linting** passes (`npm run lint`)

### Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Modifying environment variables
- Updating deployment procedures

## 🧪 Testing Guide

### Running Tests

```bash
# All tests
make test

# Frontend only
cd dashboard && npm test

# Backend only
cd backend && pytest

# With coverage
cd dashboard && npm run test:coverage
cd backend && pytest --cov=.
```

### Writing Tests

**Frontend (Vitest + React Testing Library):**
```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ModeSwitcher } from './ModeSwitcher';

describe('ModeSwitcher', () => {
  it('renders all three modes', () => {
    render(<ModeSwitcher />);
    expect(screen.getByText('Seed')).toBeInTheDocument();
    expect(screen.getByText('Growth')).toBeInTheDocument();
    expect(screen.getByText('Full')).toBeInTheDocument();
  });
});
```

**Backend (pytest + FastAPI TestClient):**
```python
def test_get_cognitive_mode(client):
    response = client.get("/api/cognitive/mode")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] in ["seed", "growth", "full"]
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description** - What happened?
2. **Steps to reproduce** - How to trigger the bug?
3. **Expected behavior** - What should happen?
4. **Actual behavior** - What actually happened?
5. **Environment** - OS, browser, versions
6. **Screenshots** - If applicable

Use the bug report template when available.

## 💡 Feature Requests

For feature requests:

1. Check if the feature already exists
2. Check if it's already requested (search issues)
3. Open a new issue with:
   - Clear description
   - Use case explanation
   - Proposed implementation (if you have ideas)

## 🔒 Security

If you discover a security vulnerability:

**DO NOT** open a public issue.

Instead, email: security@amos.dev (replace with actual security contact)

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Getting Help

- **Discord:** [AMOS Community](https://discord.gg/amos) (replace with actual link)
- **GitHub Issues:** For bugs and features
- **GitHub Discussions:** For questions and ideas
- **Email:** contact@amos.dev

## 🎯 Good First Issues

Look for issues labeled:
- `good first issue` - Easy tasks for newcomers
- `help wanted` - Tasks where we need community help
- `documentation` - Docs improvements

## 🏆 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing others' private information
- Other unethical conduct

## 🎨 Design Guidelines

When contributing UI changes:

- Follow the Glassmorphism 2.0 design system
- Use the existing color palette
- Maintain responsive design
- Test on multiple screen sizes
- Ensure accessibility (WCAG 2.1 AA)

## 🚀 Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- `MAJOR` - Breaking changes
- `MINOR` - New features (backward compatible)
- `PATCH` - Bug fixes (backward compatible)

## 📝 Additional Resources

- [DEVELOPMENT.md](./DEVELOPMENT.md) - Detailed development setup
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture docs
- [API_DOCS.md](./backend/API_DOCS.md) - API documentation

---

Thank you for contributing to AMOS Brain! 🧠✨

*Together, we're building the future of AI cognition.*
