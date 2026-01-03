"""
SPEC: S004 - DINOv2 Visual Encoder

DINOv2 ViT-L/14 visual encoder for frame embeddings.

IMPLEMENTS: Gate 0.1 - Technical Spike, v0.2.0 G1
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from .base import VISUAL_EMBEDDING_DIM

if TYPE_CHECKING:
    import torch

logger = logging.getLogger(__name__)


class DINOv2LoadError(Exception):
    """Raised when DINOv2 model loading fails."""

    pass


class DINOv2Encoder:
    """DINOv2 visual encoder for frame embeddings.

    IMPLEMENTS: S004
    INVARIANTS: INV005, INV006

    Uses DINOv2 ViT-L/14 from HuggingFace transformers.
    Produces 1024-dimensional embeddings projected to 768-dimensional.

    Example:
        encoder = DINOv2Encoder.load(device="cuda")
        embeddings = encoder.encode(frames)  # (B, 768)
    """

    EMBEDDING_DIM: int = VISUAL_EMBEDDING_DIM
    DINOV2_DIM: int = 1024  # DINOv2 ViT-L output dimension
    MODEL_NAME: str = "facebook/dinov2-large"

    def __init__(
        self,
        model: torch.nn.Module,
        processor: object,
        device: str = "cpu",
    ) -> None:
        """Initialize encoder with loaded model.

        Args:
            model: Loaded DINOv2 model
            processor: Image processor for preprocessing
            device: Device to run inference on
        """
        import torch

        self._model = model
        self._processor = processor
        self._device = device

        # Projection from DINOv2 1024-dim to standard 768-dim
        self._projection = torch.nn.Linear(
            self.DINOV2_DIM, self.EMBEDDING_DIM, bias=False
        ).to(device)

        # Initialize with orthogonal projection
        torch.nn.init.orthogonal_(self._projection.weight)

        logger.info("DINOv2Encoder initialized on %s", device)

    @classmethod
    def load(cls, device: str | None = None) -> DINOv2Encoder:
        """Load DINOv2 encoder from HuggingFace.

        Args:
            device: Device to load to (auto-detect if None)

        Returns:
            Initialized DINOv2Encoder

        Raises:
            DINOv2LoadError: If model cannot be loaded
        """
        import torch

        try:
            from transformers import AutoImageProcessor, AutoModel

            # Auto-detect device
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"

            logger.info("Loading DINOv2 ViT-L from %s...", cls.MODEL_NAME)

            # Load processor and model
            processor = AutoImageProcessor.from_pretrained(cls.MODEL_NAME)
            model = AutoModel.from_pretrained(cls.MODEL_NAME)
            model = model.to(device)
            model.train(False)  # Set to inference mode (equivalent to .eval())

            logger.info("DINOv2 loaded successfully on %s", device)

            return cls(model, processor, device)

        except ImportError as e:
            raise DINOv2LoadError(
                "transformers package not installed. "
                "Install with: pip install transformers torch"
            ) from e
        except Exception as e:
            raise DINOv2LoadError(f"Failed to load DINOv2: {e}") from e

    def _preprocess(self, frames: np.ndarray) -> torch.Tensor:
        """Preprocess frames for DINOv2.

        Args:
            frames: Batch of frames, shape (B, 3, 224, 224), float32 [-1, 1]

        Returns:
            Preprocessed tensor for model input
        """
        import torch

        # DINOv2 expects images in [0, 1] range with specific normalization
        # Our input is in [-1, 1], convert to [0, 1]
        frames_01 = (frames + 1.0) / 2.0

        # Convert to torch and apply normalization
        frames_tensor = torch.from_numpy(frames_01).float().to(self._device)

        # DINOv2 ImageNet normalization
        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(self._device)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(self._device)

        normalized = (frames_tensor - mean) / std

        return normalized

    def encode(self, frames: np.ndarray) -> np.ndarray:
        """Encode frames to embeddings.

        INVARIANT: INV005 - Output shape is (B, 768)
        INVARIANT: INV006 - Embeddings are L2-normalized

        Args:
            frames: Batch of frames, shape (B, 3, 224, 224), float32 [-1, 1]

        Returns:
            Embeddings, shape (B, 768), L2-normalized
        """
        import torch

        if frames.ndim != 4:
            raise ValueError(f"Expected 4D tensor (B,C,H,W), got {frames.ndim}D")

        B, C, H, W = frames.shape
        if C != 3:
            raise ValueError(f"Expected 3 channels, got {C}")

        with torch.no_grad():
            # Preprocess
            x = self._preprocess(frames)

            # Resize if not 224x224 (DINOv2 supports multiple sizes)
            if H != 224 or W != 224:
                x = torch.nn.functional.interpolate(
                    x, size=(224, 224), mode="bilinear", align_corners=False
                )

            # Forward pass - get CLS token embedding
            outputs = self._model(x)
            embeddings = outputs.last_hidden_state[:, 0]  # CLS token

            # Project from 1024 to 768
            embeddings = self._projection(embeddings)

            # L2 normalize (INV006)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            # Convert to numpy
            result: np.ndarray = embeddings.cpu().numpy()

        return result

    def encode_single(self, frame: np.ndarray) -> np.ndarray:
        """Encode a single frame.

        Args:
            frame: Single frame, shape (3, 224, 224)

        Returns:
            Embedding, shape (768,)
        """
        batch = frame[np.newaxis, ...]
        embeddings = self.encode(batch)
        result: np.ndarray = embeddings[0]
        return result


def check_dinov2_available() -> bool:
    """Check if DINOv2 can be loaded.

    Returns:
        True if all dependencies are available
    """
    import importlib.util

    torch_available = importlib.util.find_spec("torch") is not None
    transformers_available = importlib.util.find_spec("transformers") is not None

    return torch_available and transformers_available
