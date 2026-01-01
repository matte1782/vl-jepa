"""
SPEC: S004, S006 - Placeholder Encoder Implementations

Placeholder encoders for testing without real models.

IMPLEMENTS: Gate 0.3 - Encoder Interface Design
"""

from __future__ import annotations

import logging

import numpy as np

from .base import (
    TEXT_EMBEDDING_DIM,
    VISUAL_EMBEDDING_DIM,
    TextEncoderProtocol,
    VisualEncoderProtocol,
)

logger = logging.getLogger(__name__)


class PlaceholderVisualEncoder:
    """Placeholder visual encoder for testing.

    IMPLEMENTS: S004 (placeholder)
    INVARIANTS: INV005, INV006

    Uses random projections to produce consistent embeddings.
    Real encoders (DINOv2, CLIP) should replace this.

    Example:
        encoder = PlaceholderVisualEncoder()
        embeddings = encoder.encode(frames)  # (B, 768)
    """

    EMBEDDING_DIM: int = VISUAL_EMBEDDING_DIM

    def __init__(self, seed: int = 42, device: str = "cpu") -> None:
        """Initialize placeholder encoder.

        Args:
            seed: Random seed for reproducible projections
            device: Device for computation (ignored, for interface compat)
        """
        self._device = device
        self._rng = np.random.RandomState(seed)

        # Fixed random projection matrix for consistency
        self._projection = self._rng.randn(3 * 224 * 224, self.EMBEDDING_DIM)
        self._projection = self._projection.astype(np.float32)

        logger.info("Initialized PlaceholderVisualEncoder (seed=%d)", seed)

    def encode(self, frames: np.ndarray) -> np.ndarray:
        """Encode frames to embeddings.

        INVARIANT: INV005 - Output shape is (B, 768)
        INVARIANT: INV006 - Embeddings are L2-normalized

        Args:
            frames: Batch of frames, shape (B, 3, 224, 224), float32 [-1, 1]

        Returns:
            Embeddings, shape (B, 768), L2-normalized
        """
        if frames.ndim != 4:
            raise ValueError(f"Expected 4D tensor (B,C,H,W), got {frames.ndim}D")

        B, C, H, W = frames.shape
        if C != 3 or H != 224 or W != 224:
            raise ValueError(f"Expected (B,3,224,224), got (B,{C},{H},{W})")

        # Flatten and project
        flat = frames.reshape(B, -1).astype(np.float32)
        embeddings = flat @ self._projection

        # L2 normalize (INV006)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)  # Avoid division by zero
        embeddings = embeddings / norms

        result: np.ndarray = embeddings.astype(np.float32)
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


class PlaceholderTextEncoder:
    """Placeholder text encoder for testing.

    IMPLEMENTS: S006 (placeholder)
    INVARIANTS: INV009, INV010

    Uses hash-based projections to produce consistent embeddings.
    Real encoders (sentence-transformers) should replace this.

    Example:
        encoder = PlaceholderTextEncoder()
        embedding = encoder.encode("What is gradient descent?")
    """

    TEXT_DIM: int = TEXT_EMBEDDING_DIM
    VISUAL_DIM: int = VISUAL_EMBEDDING_DIM
    MAX_TOKENS: int = 256

    def __init__(self, seed: int = 42) -> None:
        """Initialize placeholder encoder.

        Args:
            seed: Random seed for reproducible embeddings
        """
        self._rng = np.random.RandomState(seed)
        self._projection = self._create_projection()

        logger.info("Initialized PlaceholderTextEncoder (seed=%d)", seed)

    def _create_projection(self) -> np.ndarray:
        """Create projection matrix from TEXT_DIM to VISUAL_DIM."""
        proj = np.zeros((self.TEXT_DIM, self.VISUAL_DIM), dtype=np.float32)
        proj[:, : self.TEXT_DIM] = np.eye(self.TEXT_DIM)
        proj[:, self.TEXT_DIM :] = np.eye(self.TEXT_DIM)
        return proj

    def _text_to_embedding(self, text: str) -> np.ndarray:
        """Convert text to pseudo-embedding using hash.

        Produces consistent embeddings for the same text.
        """
        # Use hash to create seed for this text
        text_hash = hash(text) & 0xFFFFFFFF
        text_rng = np.random.RandomState(text_hash)
        embedding = text_rng.randn(self.TEXT_DIM).astype(np.float32)
        return embedding

    def encode(self, text: str) -> np.ndarray:
        """Encode text to embedding.

        INVARIANT: INV009 - Output shape is (768,)
        INVARIANT: INV010 - L2-normalized

        Args:
            text: Query text

        Returns:
            L2-normalized embedding (768,)

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Truncate if too long
        words = text.split()
        if len(words) > self.MAX_TOKENS:
            logger.warning(
                "Text has %d tokens, truncating to %d",
                len(words),
                self.MAX_TOKENS,
            )
            text = " ".join(words[: self.MAX_TOKENS])

        # Get text embedding
        text_embedding = self._text_to_embedding(text)

        # Project to visual space
        projected = text_embedding @ self._projection

        # L2 normalize (INV010)
        norm = np.linalg.norm(projected)
        if norm > 1e-8:
            projected = projected / norm

        result: np.ndarray = projected.astype(np.float32)
        return result

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts.

        Args:
            texts: List of query texts

        Returns:
            L2-normalized embeddings (N, 768)
        """
        embeddings = [self.encode(t) for t in texts]
        return np.stack(embeddings, axis=0)


# Type assertions for Protocol compliance
def _check_protocols() -> None:
    """Verify implementations match protocols at import time."""
    placeholder_visual: VisualEncoderProtocol = PlaceholderVisualEncoder()
    placeholder_text: TextEncoderProtocol = PlaceholderTextEncoder()
    # These assignments will fail type checking if protocols don't match
    _ = placeholder_visual, placeholder_text
