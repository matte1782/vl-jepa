# VL-JEPA Lecture Summarizer

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
