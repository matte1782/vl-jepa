"""
SPEC: S007 - Embedding Index (FAISS)

FAISS-based embedding index for similarity search.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with ID, score, and optional metadata."""

    id: int
    score: float
    metadata: dict[str, Any] | None = None


class EmbeddingIndex:
    """FAISS embedding index for similarity search.

    IMPLEMENTS: S007
    INVARIANTS: INV011, INV012

    Features:
    - Flat index for small collections (<1000)
    - Automatic IVF transition for large collections

    Example:
        index = EmbeddingIndex()
        index.add(embedding, id=0)
        results = index.search(query, k=5)
    """

    DIM: int = 768
    IVF_THRESHOLD: int = 1000  # Switch to IVF above this

    def __init__(self, dimension: int = 768) -> None:
        """Initialize empty index.

        Args:
            dimension: Embedding dimension
        """
        self._dimension = dimension
        self._index: Any = None
        self._id_map: list[int] = []
        self._metadata: dict[int, dict[str, Any]] = {}
        self._use_ivf = False

        self._init_index()

    def _init_index(self) -> None:
        """Initialize FAISS index."""
        try:
            import faiss

            # Start with flat index
            self._index = faiss.IndexFlatIP(self._dimension)
            logger.debug(f"Initialized flat index, dim={self._dimension}")

        except ImportError:
            logger.warning("FAISS not installed, using numpy fallback")
            self._index = None
            self._embeddings: list[np.ndarray] = []

    @property
    def size(self) -> int:
        """Get number of embeddings in index."""
        return len(self._id_map)

    def add(
        self,
        embedding: np.ndarray,
        id: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add single embedding to index.

        Args:
            embedding: L2-normalized embedding (768,)
            id: Unique identifier
            metadata: Optional metadata dict
        """
        self.add_batch(
            embeddings=embedding.reshape(1, -1),
            ids=[id],
            metadata=[metadata] if metadata else None,
        )

    def add_batch(
        self,
        embeddings: np.ndarray,
        ids: list[int],
        metadata: list[dict[str, Any]] | dict[int, dict[str, Any]] | None = None,
    ) -> None:
        """Add batch of embeddings to index.

        EDGE_CASE: EC038 - IVF transition at 1000 vectors

        Args:
            embeddings: L2-normalized embeddings (N, 768)
            ids: List of unique identifiers
            metadata: Optional list of metadata dicts
        """
        if len(embeddings) != len(ids):
            raise ValueError("embeddings and ids must have same length")

        # Ensure float32
        embeddings = embeddings.astype(np.float32)

        # Check if we need to transition to IVF
        new_size = self.size + len(embeddings)
        transitioned_to_ivf = False
        if new_size >= self.IVF_THRESHOLD and not self._use_ivf:
            self._transition_to_ivf(embeddings)
            transitioned_to_ivf = True

        # Add to index (skip if just transitioned - IVF already has the embeddings)
        if not transitioned_to_ivf:
            if self._index is not None:
                self._index.add(embeddings)
            else:
                # Numpy fallback
                for emb in embeddings:
                    self._embeddings.append(emb)

        # Update mappings
        self._id_map.extend(ids)

        if metadata:
            if isinstance(metadata, dict):
                # Dict keyed by id
                for id_, meta in metadata.items():
                    if meta:
                        self._metadata[id_] = meta
            else:
                # List of metadata
                for id_, meta in zip(ids, metadata, strict=False):
                    if meta:
                        self._metadata[id_] = meta

        logger.debug(f"Added {len(embeddings)} embeddings, total={self.size}")

    def _transition_to_ivf(self, new_embeddings: np.ndarray) -> None:
        """Transition from flat to IVF index.

        EDGE_CASE: EC038
        """
        try:
            import faiss

            logger.info(f"Transitioning to IVF index at {self.size} vectors")

            # Get all existing embeddings
            if self._index is not None and self.size > 0:
                existing = self._reconstruct_all()
                all_embeddings = np.concatenate([existing, new_embeddings], axis=0)
            else:
                all_embeddings = new_embeddings

            # Create IVF index
            nlist = max(int(np.sqrt(len(all_embeddings))), 10)
            quantizer = faiss.IndexFlatIP(self._dimension)
            new_index = faiss.IndexIVFFlat(quantizer, self._dimension, nlist)

            # Train and add
            new_index.train(all_embeddings)
            new_index.add(all_embeddings)

            self._index = new_index
            self._use_ivf = True

        except Exception as e:
            logger.error(f"IVF transition failed: {e}, keeping flat index")

    def _reconstruct_all(self) -> np.ndarray:
        """Reconstruct all embeddings from index."""
        import faiss

        if isinstance(self._index, faiss.IndexFlatIP):
            result: np.ndarray = faiss.rev_swig_ptr(
                self._index.get_xb(), self.size * self._dimension
            ).reshape(self.size, self._dimension)
            return result
        else:
            # For IVF, we'd need to iterate - simplified here
            embeddings = []
            for i in range(self.size):
                embeddings.append(self._index.reconstruct(i))
            result = np.stack(embeddings)
            return result

    def search(
        self,
        query: np.ndarray,
        k: int = 5,
    ) -> list[SearchResult]:
        """Search for similar embeddings.

        INVARIANT: INV012 - Returns exactly min(k, size) results

        Args:
            query: Query embedding (768,)
            k: Number of results to return

        Returns:
            List of SearchResult, sorted by score descending
        """
        if self.size == 0:
            return []

        # Ensure proper shape
        query = query.reshape(1, -1).astype(np.float32)
        k = min(k, self.size)  # INV012

        if self._index is not None:
            scores, indices = self._index.search(query, k)
            scores = scores[0]
            indices = indices[0]
        else:
            # Numpy fallback
            all_emb = np.stack(self._embeddings)
            scores = all_emb @ query.T
            scores = scores.flatten()
            indices = np.argsort(scores)[::-1][:k]
            scores = scores[indices]

        results = []
        for score, idx in zip(scores, indices, strict=False):
            if idx < 0:  # FAISS returns -1 for missing
                continue

            id_ = self._id_map[idx]
            results.append(
                SearchResult(
                    id=id_,
                    score=float(score),
                    metadata=self._metadata.get(id_),
                )
            )

        return results

    def save(self, path: Path) -> None:
        """Save index to file.

        Args:
            path: Path to save index
        """
        path = Path(path)

        if self._index is not None:
            import faiss

            faiss.write_index(self._index, str(path.with_suffix(".faiss")))

        # Save mappings as JSON (safe serialization)
        mappings = {
            "id_map": self._id_map,
            "metadata": {str(k): v for k, v in self._metadata.items()},
        }
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(mappings, f)

        logger.info(f"Saved index to {path}")

    @classmethod
    def load(cls, path: Path) -> EmbeddingIndex:
        """Load index from file.

        Args:
            path: Path to index file

        Returns:
            Loaded EmbeddingIndex
        """
        path = Path(path)
        index = cls()

        # Load FAISS index
        faiss_path = path.with_suffix(".faiss")
        if faiss_path.exists():
            import faiss

            index._index = faiss.read_index(str(faiss_path))

        # Load mappings from JSON (safe deserialization)
        json_path = path.with_suffix(".json")
        if json_path.exists():
            with open(json_path) as f:
                mappings = json.load(f)
            index._id_map = mappings.get("id_map", [])
            index._metadata = {
                int(k): v for k, v in mappings.get("metadata", {}).items()
            }

        logger.info(f"Loaded index from {path}, size={index.size}")

        return index
