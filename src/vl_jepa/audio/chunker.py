"""
SPEC: Transcript Chunking for Embedding

Splits transcript segments into time-aligned chunks for text embedding.

IMPLEMENTS: v0.2.0 G7 - Audio Transcription
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field

from .base import TranscriptSegment

logger = logging.getLogger(__name__)


@dataclass
class TranscriptChunk:
    """A chunk of transcript text with time alignment.

    IMPLEMENTS: v0.2.0 G7

    Represents a time window of transcript text for embedding.
    Each chunk contains concatenated text from segments within its window.

    Attributes:
        text: Combined text from all segments in this window
        start: Start time of the window (seconds)
        end: End time of the window (seconds)
        segment_count: Number of segments included
        metadata: Optional extra metadata
    """

    text: str
    start: float
    end: float
    segment_count: int = 1
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Duration of the chunk in seconds."""
        return self.end - self.start

    def __repr__(self) -> str:
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"TranscriptChunk({self.start:.1f}-{self.end:.1f}s: {preview!r})"


class TranscriptChunker:
    """Splits transcript segments into time-aligned chunks.

    IMPLEMENTS: v0.2.0 G7
    INVARIANTS:
        INV_CHUNK_001: Chunks are sorted by start time
        INV_CHUNK_002: Chunks don't overlap
        INV_CHUNK_003: No empty chunks

    Strategies:
        - Fixed window: Split into fixed-duration windows (default: 30s)
        - Sliding window: Overlapping windows for context continuity
        - Segment boundary: Respect natural segment boundaries

    Example:
        chunker = TranscriptChunker(window_size=30.0)
        segments = transcriber.transcribe("lecture.mp3")

        for chunk in chunker.chunk(segments):
            embedding = text_encoder.encode(chunk.text)
            store(chunk.start, chunk.end, embedding)
    """

    def __init__(
        self,
        window_size: float = 30.0,
        overlap: float = 0.0,
        min_text_length: int = 10,
    ) -> None:
        """Initialize chunker.

        Args:
            window_size: Window size in seconds (default: 30.0)
            overlap: Overlap between windows in seconds (default: 0.0)
            min_text_length: Minimum text length for a valid chunk (default: 10)

        Raises:
            ValueError: If window_size <= 0 or overlap >= window_size
        """
        if window_size <= 0:
            raise ValueError(f"window_size must be positive, got {window_size}")
        if overlap < 0:
            raise ValueError(f"overlap must be non-negative, got {overlap}")
        if overlap >= window_size:
            raise ValueError(
                f"overlap ({overlap}) must be less than window_size ({window_size})"
            )

        self._window_size = window_size
        self._overlap = overlap
        self._min_text_length = min_text_length

        logger.debug(
            "TranscriptChunker: window=%.1fs, overlap=%.1fs",
            window_size,
            overlap,
        )

    @property
    def window_size(self) -> float:
        """Window size in seconds."""
        return self._window_size

    @property
    def overlap(self) -> float:
        """Overlap between windows in seconds."""
        return self._overlap

    def chunk(
        self,
        segments: list[TranscriptSegment],
    ) -> Iterator[TranscriptChunk]:
        """Chunk transcript segments into time windows.

        Args:
            segments: List of transcript segments (must be sorted by start time)

        Yields:
            TranscriptChunk for each time window with text

        Note:
            Empty windows (no segments) are skipped.
            Windows with text shorter than min_text_length are skipped.
        """
        if not segments:
            logger.warning("No segments to chunk")
            return

        # Find time range
        min_time = segments[0].start
        max_time = max(seg.end for seg in segments)

        logger.info(
            "Chunking %d segments (%.1f-%.1f s) into %.1fs windows",
            len(segments),
            min_time,
            max_time,
            self._window_size,
        )

        # Calculate step (window - overlap)
        step = self._window_size - self._overlap

        # Generate windows
        window_start = min_time
        chunks_yielded = 0

        while window_start < max_time:
            window_end = window_start + self._window_size

            # Find segments in this window
            window_segments = self._segments_in_window(
                segments, window_start, window_end
            )

            if window_segments:
                # Combine text
                text = " ".join(seg.text for seg in window_segments)

                # Skip if too short
                if len(text) >= self._min_text_length:
                    chunk = TranscriptChunk(
                        text=text,
                        start=window_start,
                        end=min(window_end, max_time),
                        segment_count=len(window_segments),
                    )
                    yield chunk
                    chunks_yielded += 1

            window_start += step

        logger.info(
            "Generated %d chunks from %d segments", chunks_yielded, len(segments)
        )

    def chunk_by_segments(
        self,
        segments: list[TranscriptSegment],
        max_segments_per_chunk: int = 5,
    ) -> Iterator[TranscriptChunk]:
        """Chunk by grouping segments, respecting natural boundaries.

        Args:
            segments: List of transcript segments
            max_segments_per_chunk: Maximum segments to combine

        Yields:
            TranscriptChunk for each group of segments
        """
        if not segments:
            return

        logger.info(
            "Chunking %d segments (max %d per chunk)",
            len(segments),
            max_segments_per_chunk,
        )

        current_segments: list[TranscriptSegment] = []
        chunks_yielded = 0

        for seg in segments:
            current_segments.append(seg)

            # Check if we should create a chunk
            if len(current_segments) >= max_segments_per_chunk:
                chunk = self._create_chunk_from_segments(current_segments)
                if chunk:
                    yield chunk
                    chunks_yielded += 1
                current_segments = []

        # Handle remaining segments
        if current_segments:
            chunk = self._create_chunk_from_segments(current_segments)
            if chunk:
                yield chunk
                chunks_yielded += 1

        logger.info("Generated %d chunks", chunks_yielded)

    def _segments_in_window(
        self,
        segments: list[TranscriptSegment],
        start: float,
        end: float,
    ) -> list[TranscriptSegment]:
        """Find segments that overlap with a time window.

        A segment is included if it overlaps with the window:
        - Segment starts before window ends AND
        - Segment ends after window starts
        """
        result = []
        for seg in segments:
            # Check for overlap
            if seg.start < end and seg.end > start:
                result.append(seg)
        return result

    def _create_chunk_from_segments(
        self,
        segments: list[TranscriptSegment],
    ) -> TranscriptChunk | None:
        """Create a chunk from a list of segments."""
        if not segments:
            return None

        text = " ".join(seg.text for seg in segments)

        if len(text) < self._min_text_length:
            return None

        return TranscriptChunk(
            text=text,
            start=segments[0].start,
            end=segments[-1].end,
            segment_count=len(segments),
        )


def chunk_transcript(
    segments: list[TranscriptSegment],
    window_size: float = 30.0,
    overlap: float = 0.0,
) -> list[TranscriptChunk]:
    """Convenience function to chunk transcript segments.

    Args:
        segments: List of transcript segments
        window_size: Window size in seconds
        overlap: Overlap between windows in seconds

    Returns:
        List of TranscriptChunk
    """
    chunker = TranscriptChunker(window_size=window_size, overlap=overlap)
    return list(chunker.chunk(segments))
