"""
SPEC: Multimodal Index for Visual + Transcript Search

Combines visual frame embeddings and transcript text embeddings
in a unified search index.

IMPLEMENTS: v0.2.0 Week 3 - Multimodal Integration
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

from .index import EmbeddingIndex

logger = logging.getLogger(__name__)


class Modality(str, Enum):
    """Embedding modality type."""

    VISUAL = "visual"
    TRANSCRIPT = "transcript"


@dataclass
class MultimodalEntry:
    """Entry in the multimodal index.

    Stores embedding with metadata about source and timing.
    """

    id: int
    modality: Modality
    timestamp: float  # seconds from video start
    embedding: np.ndarray

    # Modality-specific data
    frame_index: int | None = None  # For visual
    text: str | None = None  # For transcript
    segment_id: int | None = None  # For transcript

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MultimodalSearchResult:
    """Search result from multimodal index."""

    id: int
    score: float
    modality: Modality
    timestamp: float
    text: str | None = None
    frame_index: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RankingConfig:
    """Configuration for multimodal ranking.

    IMPLEMENTS: v0.2.0 Week 3 Day 4 - Weighted fusion ranking

    Attributes:
        visual_weight: Weight for visual similarity scores (0-1)
        transcript_weight: Weight for transcript similarity scores (0-1)
        time_decay: Decay factor for temporal distance (0 = no decay)
        time_reference: Reference timestamp for time decay (None = no decay)
    """

    visual_weight: float = 0.3
    transcript_weight: float = 0.7
    time_decay: float = 0.0
    time_reference: float | None = None

    def __post_init__(self) -> None:
        """Validate weights."""
        if not 0 <= self.visual_weight <= 1:
            raise ValueError("visual_weight must be in [0, 1]")
        if not 0 <= self.transcript_weight <= 1:
            raise ValueError("transcript_weight must be in [0, 1]")
        if not 0 <= self.time_decay <= 1:
            raise ValueError("time_decay must be in [0, 1]")


class MultimodalIndex:
    """Unified index for visual and transcript embeddings.

    IMPLEMENTS: v0.2.0 G4 - Multimodal search
    INVARIANTS:
        - All embeddings are 768-dim
        - All embeddings are L2-normalized
        - Timestamps sync between modalities (±1s tolerance)

    Example:
        index = MultimodalIndex()

        # Add visual frames
        for frame, timestamp in frames:
            emb = visual_encoder.encode(frame)
            index.add_visual(emb, timestamp, frame_index=i)

        # Add transcript
        for chunk in transcript_chunks:
            emb = text_encoder.encode(chunk.text)
            index.add_transcript(emb, chunk.start, chunk.end, chunk.text)

        # Search
        results = index.search(query_emb, k=10)
        for r in results:
            print(f"[{r.modality}] {r.timestamp:.1f}s: {r.text or 'frame'}")
    """

    DIM: int = 768

    def __init__(self, dimension: int = 768) -> None:
        """Initialize multimodal index.

        Args:
            dimension: Embedding dimension (default 768)
        """
        self._dimension = dimension
        self._index = EmbeddingIndex(dimension=dimension)
        self._entries: dict[int, MultimodalEntry] = {}
        self._next_id = 0

        # Separate tracking for each modality
        self._visual_ids: list[int] = []
        self._transcript_ids: list[int] = []

        logger.info("MultimodalIndex initialized, dim=%d", dimension)

    @property
    def size(self) -> int:
        """Total number of entries."""
        return self._index.size

    @property
    def visual_count(self) -> int:
        """Number of visual entries."""
        return len(self._visual_ids)

    @property
    def transcript_count(self) -> int:
        """Number of transcript entries."""
        return len(self._transcript_ids)

    def _get_next_id(self) -> int:
        """Get next unique ID."""
        id_ = self._next_id
        self._next_id += 1
        return id_

    def add_visual(
        self,
        embedding: np.ndarray,
        timestamp: float,
        frame_index: int,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Add visual frame embedding.

        Args:
            embedding: L2-normalized 768-dim embedding
            timestamp: Frame timestamp in seconds
            frame_index: Frame index in video
            metadata: Optional additional metadata

        Returns:
            Entry ID
        """
        id_ = self._get_next_id()

        entry = MultimodalEntry(
            id=id_,
            modality=Modality.VISUAL,
            timestamp=timestamp,
            embedding=embedding,
            frame_index=frame_index,
            metadata=metadata or {},
        )

        # Add to FAISS index with metadata
        index_metadata = {
            "modality": Modality.VISUAL.value,
            "timestamp": timestamp,
            "frame_index": frame_index,
            **(metadata or {}),
        }
        self._index.add(embedding, id=id_, metadata=index_metadata)

        # Store entry
        self._entries[id_] = entry
        self._visual_ids.append(id_)

        logger.debug(
            "Added visual entry: id=%d, timestamp=%.2f, frame=%d",
            id_,
            timestamp,
            frame_index,
        )

        return id_

    def add_transcript(
        self,
        embedding: np.ndarray,
        start_time: float,
        end_time: float,
        text: str,
        segment_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Add transcript text embedding.

        Args:
            embedding: L2-normalized 768-dim embedding
            start_time: Segment start time in seconds
            end_time: Segment end time in seconds
            text: Transcript text
            segment_id: Optional segment identifier
            metadata: Optional additional metadata

        Returns:
            Entry ID
        """
        id_ = self._get_next_id()

        # Use center timestamp for search alignment
        timestamp = (start_time + end_time) / 2

        entry = MultimodalEntry(
            id=id_,
            modality=Modality.TRANSCRIPT,
            timestamp=timestamp,
            embedding=embedding,
            text=text,
            segment_id=segment_id,
            metadata={
                "start_time": start_time,
                "end_time": end_time,
                **(metadata or {}),
            },
        )

        # Add to FAISS index with metadata
        index_metadata = {
            "modality": Modality.TRANSCRIPT.value,
            "timestamp": timestamp,
            "start_time": start_time,
            "end_time": end_time,
            "text": text[:200] if text else None,  # Truncate for storage
            **(metadata or {}),
        }
        self._index.add(embedding, id=id_, metadata=index_metadata)

        # Store entry
        self._entries[id_] = entry
        self._transcript_ids.append(id_)

        logger.debug(
            "Added transcript entry: id=%d, time=%.2f-%.2f, text='%s...'",
            id_,
            start_time,
            end_time,
            text[:30] if text else "",
        )

        return id_

    def search(
        self,
        query: np.ndarray,
        k: int = 10,
        modality: Modality | None = None,
    ) -> list[MultimodalSearchResult]:
        """Search for similar entries.

        Args:
            query: Query embedding (768,)
            k: Number of results
            modality: Filter by modality (None = all)

        Returns:
            List of MultimodalSearchResult sorted by score
        """
        # Get more results if filtering, then filter
        search_k = k * 3 if modality else k

        raw_results = self._index.search(query, k=search_k)

        results = []
        for r in raw_results:
            entry = self._entries.get(r.id)
            if entry is None:
                continue

            # Filter by modality if specified
            if modality and entry.modality != modality:
                continue

            results.append(
                MultimodalSearchResult(
                    id=r.id,
                    score=r.score,
                    modality=entry.modality,
                    timestamp=entry.timestamp,
                    text=entry.text,
                    frame_index=entry.frame_index,
                    metadata=r.metadata,
                )
            )

            if len(results) >= k:
                break

        return results

    def search_visual(
        self,
        query: np.ndarray,
        k: int = 5,
    ) -> list[MultimodalSearchResult]:
        """Search visual entries only."""
        return self.search(query, k=k, modality=Modality.VISUAL)

    def search_transcript(
        self,
        query: np.ndarray,
        k: int = 5,
    ) -> list[MultimodalSearchResult]:
        """Search transcript entries only."""
        return self.search(query, k=k, modality=Modality.TRANSCRIPT)

    def search_multimodal(
        self,
        query: np.ndarray,
        k: int = 10,
        config: RankingConfig | None = None,
    ) -> list[MultimodalSearchResult]:
        """Search across both modalities with weighted fusion ranking.

        IMPLEMENTS: v0.2.0 Week 3 Day 4 - Multimodal search with ranking

        This method queries both visual and transcript indices separately,
        applies modality-specific weights, and fuses results using a
        weighted scoring algorithm.

        Args:
            query: Query embedding (768,)
            k: Number of final results to return
            config: Ranking configuration (uses defaults if None)

        Returns:
            List of MultimodalSearchResult sorted by fused score

        Example:
            config = RankingConfig(visual_weight=0.3, transcript_weight=0.7)
            results = index.search_multimodal(query_emb, k=10, config=config)
        """
        if config is None:
            config = RankingConfig()

        # Get results from each modality (get more to have enough after fusion)
        fetch_k = k * 2
        visual_results = self.search_visual(query, k=fetch_k)
        transcript_results = self.search_transcript(query, k=fetch_k)

        # Apply weights and collect all results
        scored_results: dict[int, MultimodalSearchResult] = {}

        for r in visual_results:
            weighted_score = r.score * config.visual_weight
            if config.time_decay > 0 and config.time_reference is not None:
                weighted_score *= self._apply_time_decay(
                    r.timestamp, config.time_reference, config.time_decay
                )
            scored_results[r.id] = MultimodalSearchResult(
                id=r.id,
                score=weighted_score,
                modality=r.modality,
                timestamp=r.timestamp,
                text=r.text,
                frame_index=r.frame_index,
                metadata=r.metadata,
            )

        for r in transcript_results:
            weighted_score = r.score * config.transcript_weight
            if config.time_decay > 0 and config.time_reference is not None:
                weighted_score *= self._apply_time_decay(
                    r.timestamp, config.time_reference, config.time_decay
                )
            scored_results[r.id] = MultimodalSearchResult(
                id=r.id,
                score=weighted_score,
                modality=r.modality,
                timestamp=r.timestamp,
                text=r.text,
                frame_index=r.frame_index,
                metadata=r.metadata,
            )

        # Sort by weighted score and return top k
        sorted_results = sorted(
            scored_results.values(), key=lambda x: x.score, reverse=True
        )
        return sorted_results[:k]

    def _apply_time_decay(
        self,
        timestamp: float,
        reference: float,
        decay: float,
    ) -> float:
        """Apply exponential time decay to score.

        Args:
            timestamp: Entry timestamp
            reference: Reference timestamp
            decay: Decay factor (0-1, higher = more decay)

        Returns:
            Decay multiplier (0-1)
        """
        time_diff = abs(timestamp - reference)
        # Exponential decay: e^(-decay * time_diff)
        # At time_diff=0: returns 1.0
        # As time_diff increases: approaches 0
        return float(np.exp(-decay * time_diff))

    def search_by_timestamp(
        self,
        timestamp: float,
        tolerance: float = 1.0,
    ) -> list[MultimodalSearchResult]:
        """Find entries near a timestamp.

        Args:
            timestamp: Target time in seconds
            tolerance: Time window (±tolerance), must be positive

        Returns:
            Entries within time window, sorted by distance

        Raises:
            ValueError: If tolerance is not positive
        """
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")

        results = []

        for id_, entry in self._entries.items():
            time_diff = abs(entry.timestamp - timestamp)
            if time_diff <= tolerance:
                results.append(
                    MultimodalSearchResult(
                        id=id_,
                        score=1.0 - (time_diff / tolerance),  # Closer = higher score
                        modality=entry.modality,
                        timestamp=entry.timestamp,
                        text=entry.text,
                        frame_index=entry.frame_index,
                    )
                )

        # Sort by score (proximity)
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def get_entry(self, id_: int) -> MultimodalEntry | None:
        """Get entry by ID."""
        return self._entries.get(id_)

    def get_aligned_context(
        self,
        timestamp: float,
        visual_tolerance: float = 1.0,
        transcript_tolerance: float = 2.0,
    ) -> dict[str, list[MultimodalSearchResult]]:
        """Get aligned visual and transcript context for a timestamp.

        Implements audio-visual sync strategy from AUDIO_VISUAL_SYNC.md.

        Args:
            timestamp: Target time in seconds
            visual_tolerance: Tolerance for visual frames (default ±1s), must be positive
            transcript_tolerance: Tolerance for transcript (default ±2s), must be positive

        Returns:
            Dict with 'visual' and 'transcript' result lists

        Raises:
            ValueError: If any tolerance is not positive
        """
        if visual_tolerance <= 0 or transcript_tolerance <= 0:
            raise ValueError("tolerance values must be positive")

        visual_results = []
        transcript_results = []

        for id_, entry in self._entries.items():
            if entry.modality == Modality.VISUAL:
                time_diff = abs(entry.timestamp - timestamp)
                if time_diff <= visual_tolerance:
                    visual_results.append(
                        MultimodalSearchResult(
                            id=id_,
                            score=1.0 - (time_diff / visual_tolerance),
                            modality=entry.modality,
                            timestamp=entry.timestamp,
                            frame_index=entry.frame_index,
                        )
                    )
            else:  # TRANSCRIPT
                # Check if timestamp falls within segment
                start = entry.metadata.get("start_time", entry.timestamp)
                end = entry.metadata.get("end_time", entry.timestamp)

                # Expand by tolerance
                if (
                    start - transcript_tolerance
                    <= timestamp
                    <= end + transcript_tolerance
                ):
                    # Score based on overlap
                    overlap = min(end, timestamp + transcript_tolerance) - max(
                        start, timestamp - transcript_tolerance
                    )
                    score = overlap / (2 * transcript_tolerance)
                    transcript_results.append(
                        MultimodalSearchResult(
                            id=id_,
                            score=max(0, score),
                            modality=entry.modality,
                            timestamp=entry.timestamp,
                            text=entry.text,
                        )
                    )

        # Sort by score
        visual_results.sort(key=lambda x: x.score, reverse=True)
        transcript_results.sort(key=lambda x: x.score, reverse=True)

        return {
            "visual": visual_results,
            "transcript": transcript_results,
        }

    def save(self, path: Path) -> None:
        """Save multimodal index to disk.

        Args:
            path: Base path for index files
        """
        path = Path(path)

        # Save FAISS index
        self._index.save(path)

        # Save entries as JSON
        entries_data = {}
        for id_, entry in self._entries.items():
            entries_data[str(id_)] = {
                "modality": entry.modality.value,
                "timestamp": entry.timestamp,
                "frame_index": entry.frame_index,
                "text": entry.text,
                "segment_id": entry.segment_id,
                "metadata": entry.metadata,
            }

        multimodal_path = path.with_suffix(".multimodal.json")
        with open(multimodal_path, "w") as f:
            json.dump(
                {
                    "next_id": self._next_id,
                    "visual_ids": self._visual_ids,
                    "transcript_ids": self._transcript_ids,
                    "entries": entries_data,
                },
                f,
                indent=2,
            )

        logger.info(
            "Saved multimodal index to %s: %d visual, %d transcript",
            path,
            self.visual_count,
            self.transcript_count,
        )

    @classmethod
    def load(cls, path: Path) -> MultimodalIndex:
        """Load multimodal index from disk.

        Args:
            path: Base path for index files

        Returns:
            Loaded MultimodalIndex
        """
        path = Path(path)
        index = cls()

        # Load FAISS index
        index._index = EmbeddingIndex.load(path)

        # Load entries
        multimodal_path = path.with_suffix(".multimodal.json")
        if multimodal_path.exists():
            with open(multimodal_path) as f:
                data = json.load(f)

            index._next_id = data.get("next_id", 0)
            index._visual_ids = data.get("visual_ids", [])
            index._transcript_ids = data.get("transcript_ids", [])

            for id_str, entry_data in data.get("entries", {}).items():
                id_ = int(id_str)
                index._entries[id_] = MultimodalEntry(
                    id=id_,
                    modality=Modality(entry_data["modality"]),
                    timestamp=entry_data["timestamp"],
                    embedding=np.zeros(index._dimension),  # Not stored, use index
                    frame_index=entry_data.get("frame_index"),
                    text=entry_data.get("text"),
                    segment_id=entry_data.get("segment_id"),
                    metadata=entry_data.get("metadata", {}),
                )

        logger.info(
            "Loaded multimodal index from %s: %d visual, %d transcript",
            path,
            index.visual_count,
            index.transcript_count,
        )

        return index

    def __repr__(self) -> str:
        return (
            f"MultimodalIndex(visual={self.visual_count}, "
            f"transcript={self.transcript_count}, total={self.size})"
        )
