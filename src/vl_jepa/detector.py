"""
SPEC: S005 - Event Detection

Semantic boundary detection in embedding sequences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EventBoundary:
    """Detected event boundary.

    INVARIANT: INV008 - confidence in [0.0, 1.0]
    """

    timestamp: float
    confidence: float
    previous_timestamp: float

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1], got {self.confidence}")


class EventDetector:
    """Detects semantic event boundaries in embedding sequences.

    IMPLEMENTS: S005
    INVARIANTS: INV007, INV008

    Uses cosine distance between consecutive embeddings to detect
    topic/scene changes in lectures.

    Example:
        detector = EventDetector(threshold=0.3, min_event_gap=30.0)
        for frame in video.frames():
            embedding = encoder.encode(frame)
            event = detector.process(embedding, frame.timestamp)
            if event:
                print(f"Event at {event.timestamp}s")
    """

    def __init__(
        self,
        threshold: float = 0.3,
        min_event_gap: float = 30.0,
        smoothing_window: int = 5,
    ) -> None:
        """Initialize event detector.

        Args:
            threshold: Cosine distance threshold for event detection
            min_event_gap: Minimum seconds between events (INV007)
            smoothing_window: Number of embeddings to average for smoothing
        """
        self._threshold = threshold
        self._min_event_gap = min_event_gap
        self._smoothing_window = smoothing_window

        # State
        self._embedding_buffer: list[np.ndarray] = []
        self._last_embedding: np.ndarray | None = None
        self._last_event_time: float = -float("inf")

    def process(
        self,
        embedding: np.ndarray,
        timestamp: float,
    ) -> EventBoundary | None:
        """Process a new embedding.

        INVARIANT: INV007 - Events separated by >= min_event_gap
        INVARIANT: INV008 - Confidence in [0.0, 1.0]

        Args:
            embedding: L2-normalized embedding (768,)
            timestamp: Timestamp in seconds

        Returns:
            EventBoundary if event detected, None otherwise
        """
        # Add to smoothing buffer
        self._embedding_buffer.append(embedding)
        if len(self._embedding_buffer) > self._smoothing_window:
            self._embedding_buffer.pop(0)

        # Get smoothed embedding
        smoothed = self._get_smoothed_embedding()

        # First embedding - no comparison possible
        if self._last_embedding is None:
            self._last_embedding = smoothed
            return None

        # Compute cosine distance
        distance = self._cosine_distance(self._last_embedding, smoothed)

        # Check if event should be triggered
        event = None
        if distance > self._threshold:
            # INV007: Check minimum gap
            if timestamp - self._last_event_time >= self._min_event_gap:
                # INV008: Confidence = normalized distance
                confidence = min(distance / (self._threshold * 2), 1.0)

                event = EventBoundary(
                    timestamp=timestamp,
                    confidence=confidence,
                    previous_timestamp=self._last_event_time
                    if self._last_event_time > 0
                    else 0.0,
                )

                self._last_event_time = timestamp
                logger.debug(
                    f"Event detected at {timestamp:.2f}s, "
                    f"distance={distance:.3f}, confidence={confidence:.3f}"
                )

        # Update state
        self._last_embedding = smoothed

        return event

    def _get_smoothed_embedding(self) -> np.ndarray:
        """Get smoothed embedding from buffer."""
        if len(self._embedding_buffer) == 1:
            return self._embedding_buffer[0]

        # Average embeddings
        stacked = np.stack(self._embedding_buffer)
        averaged = np.mean(stacked, axis=0)

        # Re-normalize (handle zero norm edge case)
        norm = np.linalg.norm(averaged)
        if norm < 1e-8:
            return self._embedding_buffer[-1]  # Fall back to latest
        result: np.ndarray = averaged / norm
        return result

    def _cosine_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine distance between two embeddings.

        Distance = 1 - cosine_similarity
        Range: [0, 2] where 0 = identical, 2 = opposite
        """
        similarity = float(np.dot(a, b))
        return 1.0 - similarity

    def reset(self) -> None:
        """Reset detector state for new video."""
        self._embedding_buffer = []
        self._last_embedding = None
        self._last_event_time = -float("inf")
