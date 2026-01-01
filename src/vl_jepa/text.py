"""
SPEC: S006 - Text Encoding with Projection

MiniLM text encoder with projection to visual embedding space.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class TextEncoder:
    """Text encoder with projection to visual embedding space.

    IMPLEMENTS: S006
    INVARIANTS: INV009, INV010

    Uses all-MiniLM-L6-v2 (384-dim) with learned projection to 768-dim
    to match visual encoder output space.

    Example:
        encoder = TextEncoder.load()
        embedding = encoder.encode("What is gradient descent?")
        # embedding.shape == (768,)
    """

    TEXT_DIM: int = 384
    VISUAL_DIM: int = 768
    MAX_TOKENS: int = 256

    def __init__(
        self,
        model: Any,
        projection: np.ndarray | None = None,
    ) -> None:
        """Initialize text encoder.

        Args:
            model: Sentence transformer model
            projection: Optional projection matrix (384, 768)
        """
        self._model = model
        self._projection = projection

        # Default projection: simple expansion with L2 normalization
        if self._projection is None:
            self._projection = self._default_projection()

    @classmethod
    def load(cls, model_name: str = "all-MiniLM-L6-v2") -> TextEncoder:
        """Load text encoder.

        Args:
            model_name: Sentence transformer model name

        Returns:
            Initialized TextEncoder
        """
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(model_name)
            logger.info(f"Loaded text encoder: {model_name}")

            return cls(model)

        except ImportError:
            logger.warning(
                "sentence-transformers not installed, using placeholder encoder"
            )
            return cls(None)

    def _default_projection(self) -> np.ndarray:
        """Create default projection matrix.

        Simple approach: tile 384-dim to 768-dim and normalize.
        Real implementation would use a learned projection.
        """
        # Identity-like projection with padding
        proj = np.zeros((self.TEXT_DIM, self.VISUAL_DIM), dtype=np.float32)
        proj[:, : self.TEXT_DIM] = np.eye(self.TEXT_DIM)
        proj[:, self.TEXT_DIM :] = np.eye(self.TEXT_DIM)
        return proj

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

        # Check length and warn if truncated
        words = text.split()
        if len(words) > self.MAX_TOKENS:
            logger.warning(
                f"Text has {len(words)} tokens, truncating to {self.MAX_TOKENS}"
            )
            text = " ".join(words[: self.MAX_TOKENS])

        # Encode with model
        if self._model is not None:
            text_embedding = self._model.encode(text, convert_to_numpy=True)
        else:
            # Placeholder: random embedding for testing
            text_embedding = np.random.randn(self.TEXT_DIM).astype(np.float32)

        # Project to visual space
        projected = text_embedding @ self._projection

        # L2 normalize (INV010)
        projected = projected / np.linalg.norm(projected)

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
