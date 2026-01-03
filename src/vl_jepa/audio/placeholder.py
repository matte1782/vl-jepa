"""
SPEC: Placeholder Audio Transcriber

Placeholder transcriber for testing without Whisper.

IMPLEMENTS: v0.2.0 G7 - Audio Transcription (placeholder)
"""

from __future__ import annotations

import logging

from .base import TranscriberProtocol, TranscriptSegment

logger = logging.getLogger(__name__)


class PlaceholderTranscriber:
    """Placeholder transcriber for testing.

    IMPLEMENTS: v0.2.0 G7 (placeholder)

    Generates fake transcript segments for testing the pipeline.
    Real transcription requires WhisperTranscriber.

    Example:
        transcriber = PlaceholderTranscriber()
        segments = transcriber.transcribe("audio.wav")
    """

    def __init__(self, segment_duration: float = 30.0) -> None:
        """Initialize placeholder transcriber.

        Args:
            segment_duration: Duration of each fake segment in seconds
        """
        self._segment_duration = segment_duration
        logger.info("Initialized PlaceholderTranscriber")

    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> list[TranscriptSegment]:
        """Generate placeholder transcript segments.

        Args:
            audio_path: Path to audio file (not actually read)
            language: Language code (ignored)

        Returns:
            List of placeholder TranscriptSegment
        """
        # Generate fake segments (assume 10 minutes of audio)
        duration = 600.0  # 10 minutes
        segments = []

        current_time = 0.0
        segment_idx = 0

        while current_time < duration:
            end_time = min(current_time + self._segment_duration, duration)

            segment = TranscriptSegment(
                text=f"[Placeholder transcript segment {segment_idx + 1}] "
                f"This is simulated transcription for testing purposes. "
                f"Install faster-whisper for real transcription.",
                start=current_time,
                end=end_time,
                confidence=0.95,
                language=language or "en",
            )
            segments.append(segment)

            current_time = end_time
            segment_idx += 1

        logger.info(
            "Generated %d placeholder segments for %s",
            len(segments),
            audio_path,
        )

        return segments

    def transcribe_with_words(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> tuple[list[TranscriptSegment], list[TranscriptSegment]]:
        """Generate placeholder segments with fake word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: Language code

        Returns:
            Tuple of (sentence_segments, word_segments)
        """
        sentences = self.transcribe(audio_path, language)

        # Generate fake word segments
        words = []
        for sentence in sentences:
            # Split into fake words
            word_texts = sentence.text.split()
            word_duration = sentence.duration / max(len(word_texts), 1)

            current_time = sentence.start
            for word_text in word_texts:
                word = TranscriptSegment(
                    text=word_text,
                    start=current_time,
                    end=current_time + word_duration,
                    confidence=0.9,
                    language=sentence.language,
                )
                words.append(word)
                current_time += word_duration

        return sentences, words


# Type assertion for Protocol compliance
def _check_protocol() -> None:
    """Verify implementation matches protocol."""
    placeholder: TranscriberProtocol = PlaceholderTranscriber()
    _ = placeholder
