---
paths: "**/*.py"
---

# Python Code Standards

Rules for all Python code in this project.

## Type Hints (MANDATORY)

All functions MUST have complete type hints:

```python
# Good
def encode(self, frames: Tensor, *, normalize: bool = True) -> Tensor:
    ...

# Bad — NO TYPE HINTS
def encode(self, frames, normalize=True):
    ...
```

## Docstrings (Google Style)

All public functions MUST have docstrings:

```python
def encode_video(
    video_path: str,
    *,
    fps: float = 1.0,
) -> list[Tensor]:
    """
    Encode video file to embeddings.

    Args:
        video_path: Path to video file.
        fps: Frames per second to sample.

    Returns:
        List of embedding tensors.

    Raises:
        FileNotFoundError: If video doesn't exist.

    Example:
        >>> embeddings = encode_video("lecture.mp4")
    """
```

## Traceability

All implementation code MUST include trace comments:

```python
"""
Module docstring.

IMPLEMENTS: S001, S002
INVARIANTS: INV001
"""

def function() -> Result:
    """
    IMPLEMENTS: S001
    TEST_ID: T001.1
    """
```

## Error Handling

Use specific exceptions, never bare `except`:

```python
# Good
try:
    response = await client.get(url)
except httpx.TimeoutException:
    logger.warning("Timeout for %s", url)
    return cached_result

# Bad
try:
    result = do_something()
except:
    return None
```

## Logging

Use structured logging, never `print`:

```python
import logging
logger = logging.getLogger(__name__)

# Good
logger.info("Encoded %d frames in %.2fms", count, time_ms)

# Bad
print(f"Encoded {count} frames")
```

## Imports

Standard order:

```python
# Standard library
import json
from typing import TYPE_CHECKING

# Third party
import torch
from pydantic import BaseModel

# Local
from vl_jepa.core import types
```

## Quality Commands

```bash
# Format
ruff format src/

# Lint
ruff check src/

# Type check
mypy src/ --strict

# Test
pytest tests/ -v
```
