"""
SPEC: S004, S006 - Encoder Interface Definitions

Protocol classes for visual and text encoders.

IMPLEMENTS: Gate 0.3 - Encoder Interface Design
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, runtime_checkable

import numpy as np

# Standard embedding dimension for visual encoders
VISUAL_EMBEDDING_DIM: int = 768

# Standard embedding dimension for text encoders (before projection)
TEXT_EMBEDDING_DIM: int = 384


@runtime_checkable
class VisualEncoderProtocol(Protocol):
    """Protocol for visual encoders.

    All visual encoders must implement this interface.
    Produces 768-dimensional L2-normalized embeddings from frames.

    INVARIANTS:
        INV005: Output shape is (B, 768)
        INV006: Embeddings are L2-normalized
    """

    EMBEDDING_DIM: int

    @abstractmethod
    def encode(self, frames: np.ndarray) -> np.ndarray:
        """Encode frames to embeddings.

        Args:
            frames: Batch of frames, shape (B, 3, 224, 224), float32 [-1, 1]

        Returns:
            Embeddings, shape (B, 768), L2-normalized
        """
        ...

    @abstractmethod
    def encode_single(self, frame: np.ndarray) -> np.ndarray:
        """Encode a single frame.

        Args:
            frame: Single frame, shape (3, 224, 224)

        Returns:
            Embedding, shape (768,)
        """
        ...


@runtime_checkable
class TextEncoderProtocol(Protocol):
    """Protocol for text encoders.

    All text encoders must implement this interface.
    Produces 768-dimensional L2-normalized embeddings from text.

    INVARIANTS:
        INV009: Output shape is (768,)
        INV010: Embeddings are L2-normalized
    """

    VISUAL_DIM: int

    @abstractmethod
    def encode(self, text: str) -> np.ndarray:
        """Encode text to embedding.

        Args:
            text: Query text

        Returns:
            L2-normalized embedding (768,)

        Raises:
            ValueError: If text is empty
        """
        ...

    @abstractmethod
    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts.

        Args:
            texts: List of query texts

        Returns:
            L2-normalized embeddings (N, 768)
        """
        ...


def validate_visual_embedding(embedding: np.ndarray, batch: bool = True) -> None:
    """Validate visual embedding meets invariants.

    Args:
        embedding: Embedding to validate
        batch: If True, expects (B, 768), else (768,)

    Raises:
        ValueError: If embedding doesn't meet invariants
    """
    if batch:
        if embedding.ndim != 2:
            raise ValueError(f"Expected 2D array (B, D), got {embedding.ndim}D")
        if embedding.shape[1] != VISUAL_EMBEDDING_DIM:
            raise ValueError(
                f"Expected dim {VISUAL_EMBEDDING_DIM}, got {embedding.shape[1]}"
            )
    else:
        if embedding.ndim != 1:
            raise ValueError(f"Expected 1D array (D,), got {embedding.ndim}D")
        if embedding.shape[0] != VISUAL_EMBEDDING_DIM:
            raise ValueError(
                f"Expected dim {VISUAL_EMBEDDING_DIM}, got {embedding.shape[0]}"
            )

    # Check L2 normalization (within tolerance)
    if batch:
        norms = np.linalg.norm(embedding, axis=1)
    else:
        norms = np.array([np.linalg.norm(embedding)])

    if not np.allclose(norms, 1.0, rtol=1e-4):
        raise ValueError(f"Embeddings not L2-normalized. Norms: {norms}")


def validate_text_embedding(embedding: np.ndarray) -> None:
    """Validate text embedding meets invariants.

    Args:
        embedding: Embedding to validate

    Raises:
        ValueError: If embedding doesn't meet invariants
    """
    if embedding.ndim != 1:
        raise ValueError(f"Expected 1D array (D,), got {embedding.ndim}D")
    if embedding.shape[0] != VISUAL_EMBEDDING_DIM:
        raise ValueError(
            f"Expected dim {VISUAL_EMBEDDING_DIM}, got {embedding.shape[0]}"
        )

    # Check L2 normalization (within tolerance)
    norm = np.linalg.norm(embedding)
    if not np.isclose(norm, 1.0, rtol=1e-4):
        raise ValueError(f"Embedding not L2-normalized. Norm: {norm}")
