---
paths: "src/vl_jepa/**/*.py"
---

# ML Engineering Standards

Rules for ML code in this project.

## Reproducibility

Always set seeds:

```python
def set_seed(seed: int = 42) -> None:
    """Set all seeds for reproducibility."""
    import random
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
```

## Configuration

Use dataclasses for configs:

```python
from dataclasses import dataclass

@dataclass
class EncoderConfig:
    """Encoder configuration."""
    model_name: str = "vit_large_patch16_224"
    embed_dim: int = 768
    device: str = "cuda"
    batch_size: int = 32
```

## Model Loading

Use safe loading practices with safetensors:

```python
import safetensors.torch

def load_model(path: str) -> nn.Module:
    # Use safetensors for secure model loading
    state_dict = safetensors.torch.load_file(path)
    model.load_state_dict(state_dict)
    return model
```

## Tensor Operations

Always validate shapes:

```python
def encode(self, frames: Tensor) -> Tensor:
    if frames.ndim != 4:
        raise ValueError(f"Expected 4D tensor (B,C,H,W), got {frames.ndim}D")

    B, C, H, W = frames.shape
    if C != 3:
        raise ValueError(f"Expected 3 channels, got {C}")
```

## Device Handling

Be explicit about devices:

```python
class Encoder:
    def __init__(self, device: str = "cuda") -> None:
        self.device = torch.device(device)
        self.model = self.model.to(self.device)

    def encode(self, frames: Tensor) -> Tensor:
        frames = frames.to(self.device)
```

## Memory Management

Clear GPU memory when done:

```python
@contextmanager
def inference_mode():
    """Context manager for inference."""
    with torch.no_grad():
        yield
    torch.cuda.empty_cache()
```

## Logging

Log important metrics:

```python
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Encoded batch: shape=%s, device=%s, time=%.2fms",
    result.shape,
    result.device,
    time_ms,
)
```

## No Magic Numbers

Use constants:

```python
EMBED_DIM = 768
PATCH_SIZE = 16
```
