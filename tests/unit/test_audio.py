"""
Tests for audio transcription module.

IMPLEMENTS: v0.2.0 G7 - Audio Transcription Tests
"""

import pytest

from vl_jepa.audio import (
    PlaceholderTranscriber,
    TranscriberProtocol,
    TranscriptChunk,
    TranscriptChunker,
    TranscriptSegment,
    check_ffmpeg_available,
    chunk_transcript,
    validate_segments,
)


class TestTranscriptSegment:
    """Tests for TranscriptSegment dataclass."""

    def test_segment_creation(self) -> None:
        """Create a basic segment."""
        segment = TranscriptSegment(
            text="Hello world",
            start=0.0,
            end=2.5,
        )

        assert segment.text == "Hello world"
        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.confidence == 1.0  # Default
        assert segment.language == "en"  # Default

    def test_segment_duration(self) -> None:
        """Duration property calculates correctly."""
        segment = TranscriptSegment(
            text="Test",
            start=10.0,
            end=15.5,
        )

        assert segment.duration == 5.5

    def test_segment_with_all_fields(self) -> None:
        """Create segment with all fields."""
        segment = TranscriptSegment(
            text="Ciao mondo",
            start=5.0,
            end=8.0,
            confidence=0.95,
            language="it",
        )

        assert segment.language == "it"
        assert segment.confidence == 0.95


class TestValidateSegments:
    """Tests for segment validation."""

    def test_empty_segments_valid(self) -> None:
        """Empty list is valid."""
        validate_segments([])  # Should not raise

    def test_single_segment_valid(self) -> None:
        """Single segment is valid."""
        segments = [
            TranscriptSegment(text="Hello", start=0.0, end=1.0),
        ]
        validate_segments(segments)  # Should not raise

    def test_sorted_segments_valid(self) -> None:
        """Properly sorted segments are valid."""
        segments = [
            TranscriptSegment(text="First", start=0.0, end=1.0),
            TranscriptSegment(text="Second", start=1.0, end=2.0),
            TranscriptSegment(text="Third", start=2.5, end=3.5),
        ]
        validate_segments(segments)  # Should not raise

    def test_unsorted_segments_invalid(self) -> None:
        """Unsorted segments raise ValueError."""
        segments = [
            TranscriptSegment(text="Second", start=2.0, end=3.0),
            TranscriptSegment(text="First", start=0.0, end=1.0),  # Out of order
        ]

        with pytest.raises(ValueError, match="not sorted"):
            validate_segments(segments)

    def test_overlapping_segments_invalid(self) -> None:
        """Overlapping segments raise ValueError."""
        segments = [
            TranscriptSegment(text="First", start=0.0, end=2.0),
            TranscriptSegment(text="Second", start=1.5, end=3.0),  # Overlaps
        ]

        with pytest.raises(ValueError, match="overlap"):
            validate_segments(segments)

    def test_invalid_confidence_too_low(self) -> None:
        """Confidence below 0 raises ValueError."""
        segments = [
            TranscriptSegment(text="Bad", start=0.0, end=1.0, confidence=-0.1),
        ]

        with pytest.raises(ValueError, match="confidence"):
            validate_segments(segments)

    def test_invalid_confidence_too_high(self) -> None:
        """Confidence above 1 raises ValueError."""
        segments = [
            TranscriptSegment(text="Bad", start=0.0, end=1.0, confidence=1.5),
        ]

        with pytest.raises(ValueError, match="confidence"):
            validate_segments(segments)


class TestPlaceholderTranscriber:
    """Tests for PlaceholderTranscriber."""

    def test_implements_protocol(self) -> None:
        """PlaceholderTranscriber implements TranscriberProtocol."""
        transcriber = PlaceholderTranscriber()
        assert isinstance(transcriber, TranscriberProtocol)

    def test_transcribe_returns_segments(self) -> None:
        """transcribe() returns list of segments."""
        transcriber = PlaceholderTranscriber(segment_duration=60.0)
        segments = transcriber.transcribe("fake_audio.wav")

        assert len(segments) > 0
        assert all(isinstance(s, TranscriptSegment) for s in segments)

    def test_transcribe_segments_are_valid(self) -> None:
        """Generated segments pass validation."""
        transcriber = PlaceholderTranscriber()
        segments = transcriber.transcribe("fake_audio.wav")

        # Should not raise
        validate_segments(segments)

    def test_transcribe_respects_language(self) -> None:
        """Language parameter is respected."""
        transcriber = PlaceholderTranscriber()
        segments = transcriber.transcribe("fake_audio.wav", language="it")

        assert all(s.language == "it" for s in segments)

    def test_transcribe_with_words(self) -> None:
        """transcribe_with_words() returns sentences and words."""
        transcriber = PlaceholderTranscriber()
        sentences, words = transcriber.transcribe_with_words("fake_audio.wav")

        assert len(sentences) > 0
        assert len(words) > 0
        assert len(words) > len(sentences)  # More words than sentences

    def test_word_timestamps_are_valid(self) -> None:
        """Word-level timestamps pass validation."""
        transcriber = PlaceholderTranscriber()
        sentences, words = transcriber.transcribe_with_words("fake_audio.wav")

        # Both should be valid
        validate_segments(sentences)
        validate_segments(words)


class TestFFmpegAvailability:
    """Tests for FFmpeg availability check."""

    def test_check_ffmpeg_returns_bool(self) -> None:
        """check_ffmpeg_available() returns boolean."""
        result = check_ffmpeg_available()
        assert isinstance(result, bool)

    @pytest.mark.skipif(
        not check_ffmpeg_available(),
        reason="FFmpeg not installed",
    )
    def test_ffmpeg_is_available(self) -> None:
        """FFmpeg is available on this system."""
        assert check_ffmpeg_available() is True


class TestTranscriptChunk:
    """Tests for TranscriptChunk dataclass."""

    def test_chunk_creation(self) -> None:
        """Create a basic chunk."""
        chunk = TranscriptChunk(
            text="Hello world from lecture",
            start=0.0,
            end=30.0,
        )

        assert chunk.text == "Hello world from lecture"
        assert chunk.start == 0.0
        assert chunk.end == 30.0
        assert chunk.segment_count == 1  # Default

    def test_chunk_duration(self) -> None:
        """Duration property calculates correctly."""
        chunk = TranscriptChunk(
            text="Test",
            start=10.0,
            end=40.0,
        )

        assert chunk.duration == 30.0


class TestTranscriptChunker:
    """Tests for TranscriptChunker."""

    @pytest.fixture
    def sample_segments(self) -> list[TranscriptSegment]:
        """Sample transcript segments for testing."""
        return [
            TranscriptSegment(text="First segment", start=0.0, end=5.0),
            TranscriptSegment(text="Second segment", start=5.0, end=10.0),
            TranscriptSegment(text="Third segment", start=10.0, end=15.0),
            TranscriptSegment(text="Fourth segment", start=20.0, end=25.0),
            TranscriptSegment(text="Fifth segment", start=30.0, end=35.0),
            TranscriptSegment(text="Sixth segment", start=35.0, end=40.0),
        ]

    def test_chunker_creation(self) -> None:
        """Create chunker with default settings."""
        chunker = TranscriptChunker()

        assert chunker.window_size == 30.0
        assert chunker.overlap == 0.0

    def test_chunker_custom_window(self) -> None:
        """Create chunker with custom window size."""
        chunker = TranscriptChunker(window_size=60.0, overlap=10.0)

        assert chunker.window_size == 60.0
        assert chunker.overlap == 10.0

    def test_invalid_window_size(self) -> None:
        """Negative window size raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            TranscriptChunker(window_size=0)

        with pytest.raises(ValueError, match="positive"):
            TranscriptChunker(window_size=-10)

    def test_invalid_overlap(self) -> None:
        """Overlap >= window_size raises ValueError."""
        with pytest.raises(ValueError, match="overlap"):
            TranscriptChunker(window_size=30.0, overlap=30.0)

        with pytest.raises(ValueError, match="overlap"):
            TranscriptChunker(window_size=30.0, overlap=40.0)

    def test_chunk_empty_segments(self) -> None:
        """Empty segments returns no chunks."""
        chunker = TranscriptChunker()
        chunks = list(chunker.chunk([]))

        assert len(chunks) == 0

    def test_chunk_single_window(
        self, sample_segments: list[TranscriptSegment]
    ) -> None:
        """Segments fitting in one window produce one chunk."""
        # Take only first 3 segments (0-15s)
        segments = sample_segments[:3]
        chunker = TranscriptChunker(window_size=30.0)
        chunks = list(chunker.chunk(segments))

        assert len(chunks) == 1
        assert "First segment" in chunks[0].text
        assert "Second segment" in chunks[0].text
        assert "Third segment" in chunks[0].text

    def test_chunk_multiple_windows(
        self, sample_segments: list[TranscriptSegment]
    ) -> None:
        """Segments spanning multiple windows produce multiple chunks."""
        chunker = TranscriptChunker(window_size=20.0)
        chunks = list(chunker.chunk(sample_segments))

        # 0-40s with 20s windows: 0-20, 20-40 = 2 chunks
        assert len(chunks) >= 2

    def test_chunk_overlap(self, sample_segments: list[TranscriptSegment]) -> None:
        """Overlapping windows share segments."""
        chunker = TranscriptChunker(window_size=20.0, overlap=10.0)
        chunks = list(chunker.chunk(sample_segments))

        # With overlap, we get more chunks
        assert len(chunks) >= 2

    def test_chunks_are_sorted(self, sample_segments: list[TranscriptSegment]) -> None:
        """Chunks are sorted by start time."""
        chunker = TranscriptChunker(window_size=15.0)
        chunks = list(chunker.chunk(sample_segments))

        for i in range(1, len(chunks)):
            assert chunks[i].start >= chunks[i - 1].start

    def test_chunk_by_segments(self, sample_segments: list[TranscriptSegment]) -> None:
        """chunk_by_segments groups segments."""
        chunker = TranscriptChunker()
        chunks = list(
            chunker.chunk_by_segments(sample_segments, max_segments_per_chunk=3)
        )

        # 6 segments / 3 per chunk = 2 chunks
        assert len(chunks) == 2
        assert chunks[0].segment_count == 3
        assert chunks[1].segment_count == 3


class TestChunkTranscriptFunction:
    """Tests for chunk_transcript convenience function."""

    def test_chunk_transcript_basic(self) -> None:
        """Basic chunk_transcript usage."""
        segments = [
            TranscriptSegment(text="Hello world", start=0.0, end=10.0),
            TranscriptSegment(text="How are you", start=10.0, end=20.0),
        ]

        chunks = chunk_transcript(segments, window_size=30.0)

        assert len(chunks) == 1
        assert "Hello world" in chunks[0].text
        assert "How are you" in chunks[0].text

    def test_chunk_transcript_with_overlap(self) -> None:
        """chunk_transcript with overlap."""
        segments = [
            TranscriptSegment(text="First part", start=0.0, end=15.0),
            TranscriptSegment(text="Second part", start=15.0, end=30.0),
            TranscriptSegment(text="Third part", start=30.0, end=45.0),
        ]

        chunks = chunk_transcript(segments, window_size=30.0, overlap=15.0)

        # With 50% overlap, we should get overlapping chunks
        assert len(chunks) >= 2
