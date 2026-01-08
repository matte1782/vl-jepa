# Contributing to Lecture Mind

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/matte1782/lecture-mind.git
cd lecture-mind

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev,ml,audio,ui]"

# Install pre-commit hooks
pre-commit install
```

## Code Quality Standards

### Before Submitting

```bash
# Format code
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/ --strict

# Run tests
pytest tests/ -v
```

### Style Guide

- Python 3.10+ with full type hints
- Follow PEP 8 (enforced by ruff)
- Docstrings in Google style
- Tests required for new features

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following our code style
4. **Write tests** for new functionality
5. **Ensure CI passes** locally:
   ```bash
   ruff check src/ && ruff format --check src/ && pytest tests/
   ```
6. **Commit** with clear messages:
   ```
   feat: add new visual encoder support
   fix: resolve memory leak in frame sampling
   docs: update installation guide
   ```
7. **Push** and create a Pull Request

## PR Requirements

- [ ] All CI checks pass
- [ ] Tests cover new code
- [ ] Documentation updated if needed
- [ ] No secrets or credentials committed
- [ ] Follows existing code patterns

## Commit Message Convention

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Code Review

- PRs require at least 1 approval
- Address review comments promptly
- Keep PRs focused and reasonably sized

## Questions?

Open an issue with the `question` label.

---

*By contributing, you agree that your contributions will be licensed under the MIT License.*
