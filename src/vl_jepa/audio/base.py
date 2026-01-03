"""
SPEC: Audio Transcription Interface Definitions

Protocol classes for audio transcription.

IMPLEMENTS: v0.2.0 G7 - Audio Transcription
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class TranscriptSegment:
    """A segment of transcribed audio with timestamps.

    Attributes:
        text: The transcribed text
        start: Start time in seconds
        end: End time in seconds
        confidence: Transcription confidence (0-1)
        language: Detected language code (e.g., "en", "it")
    """

    text: str
    start: float
    end: float
    confidence: float = 1.0
    language: str = "en"

    @property
    def duration(self) -> float:
        """Duration of the segment in seconds."""
        return self.end - self.start

    def __repr__(self) -> str:
        return (
            f"TranscriptSegment({self.start:.1f}-{self.end:.1f}s: {self.text[:50]}...)"
        )


@runtime_checkable
class TranscriberProtocol(Protocol):
    """Protocol for audio transcribers.

    All transcribers must implement this interface.
    Produces timestamped transcript segments from audio.

    INVARIANTS:
        INV_AUDIO_001: Segments are sorted by start time
        INV_AUDIO_002: Segments don't overlap (start[i+1] >= end[i])
        INV_AUDIO_003: Confidence is in [0, 1]
    """

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> list[TranscriptSegment]:
        """Transcribe audio file to segments.

        Args:
            audio_path: Path to audio file (wav, mp3, etc.)
            language: Language code (None for auto-detect)

        Returns:
            List of TranscriptSegment with timestamps
        """
        ...

    @abstractmethod
    def transcribe_with_words(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> tuple[list[TranscriptSegment], list[TranscriptSegment]]:
        """Transcribe with word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detect)

        Returns:
            Tuple of (sentence_segments, word_segments)
        """
        ...


def validate_segments(segments: list[TranscriptSegment]) -> None:
    """Validate transcript segments meet invariants.

    Args:
        segments: List of segments to validate

    Raises:
        ValueError: If segments don't meet invariants
    """
    if not segments:
        return

    # INV_AUDIO_001: Sorted by start time
    for i in range(1, len(segments)):
        if segments[i].start < segments[i - 1].start:
            raise ValueError(
                f"Segments not sorted: {segments[i - 1].start} > {segments[i].start}"
            )

    # INV_AUDIO_002: No overlap
    for i in range(1, len(segments)):
        if segments[i].start < segments[i - 1].end:
            raise ValueError(
                f"Segments overlap: {segments[i - 1].end} > {segments[i].start}"
            )

    # INV_AUDIO_003: Confidence in [0, 1]
    for seg in segments:
        if not 0 <= seg.confidence <= 1:
            raise ValueError(f"Invalid confidence: {seg.confidence}")
