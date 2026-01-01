# Lecture Mind

[![CI](https://github.com/matte1782/lecture-mind/actions/workflows/ci.yml/badge.svg)](https://github.com/matte1782/lecture-mind/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Event-aware lecture summarizer using V-JEPA visual encoder for real-time, context-aware summaries and retrieval.

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# Process a video
vl-jepa process lecture.mp4 --output data/

# Query processed lecture
vl-jepa query data/ --question "What is machine learning?"

# List detected events
vl-jepa events data/
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev,ml]"

# Run tests
pytest tests/ -v

# Lint and format
ruff check src/ && ruff format src/

# Type check
mypy src/ --strict
```

## License

MIT
