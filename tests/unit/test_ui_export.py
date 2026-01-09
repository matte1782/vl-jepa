"""
Unit tests for UI export functionality.

SPEC: S013 - Gradio Web Interface
TEST_IDs: T013.E1-T013.E12

Tests export to Markdown, JSON, and SRT formats.
"""

import json
from dataclasses import dataclass, field

import pytest


# Mock data structures for testing (before implementation exists)
@dataclass
class MockVideoMetadata:
    """Mock video metadata for tests."""

    path: str = "test_video.mp4"
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    frame_count: int = 9000
    duration: float = 300.0  # 5 minutes
    codec: str = "h264"


@dataclass
class MockEventBoundary:
    """Mock event boundary for tests."""

    timestamp: float
    confidence: float
    previous_timestamp: float = 0.0


@dataclass
class MockTranscriptChunk:
    """Mock transcript chunk for tests."""

    text: str
    start: float
    end: float
    segment_count: int = 1


@dataclass
class MockProcessingResult:
    """Mock processing result for tests."""

    metadata: MockVideoMetadata = field(default_factory=MockVideoMetadata)
    events: list[MockEventBoundary] = field(default_factory=list)
    transcript_chunks: list[MockTranscriptChunk] = field(default_factory=list)
    processing_time: float = 10.5
    frame_count: int = 300
    error: str | None = None


@pytest.fixture
def sample_result() -> MockProcessingResult:
    """Create a complete mock processing result."""
    return MockProcessingResult(
        metadata=MockVideoMetadata(
            path="lecture_intro.mp4",
            width=1920,
            height=1080,
            fps=30.0,
            frame_count=9000,
            duration=300.0,
            codec="h264",
        ),
        events=[
            MockEventBoundary(timestamp=0.0, confidence=1.0, previous_timestamp=0.0),
            MockEventBoundary(timestamp=60.0, confidence=0.85, previous_timestamp=0.0),
            MockEventBoundary(timestamp=180.0, confidence=0.92, previous_timestamp=60.0),
        ],
        transcript_chunks=[
            MockTranscriptChunk(
                text="Welcome to the lecture on machine learning.",
                start=0.0,
                end=5.0,
            ),
            MockTranscriptChunk(
                text="Today we will discuss neural networks.",
                start=5.0,
                end=10.0,
            ),
            MockTranscriptChunk(
                text="Let's start with the basics of gradient descent.",
                start=60.0,
                end=68.0,
            ),
        ],
        processing_time=15.3,
        frame_count=300,
    )


@pytest.fixture
def minimal_result() -> MockProcessingResult:
    """Create a minimal processing result (no events/transcript)."""
    return MockProcessingResult(
        metadata=MockVideoMetadata(duration=60.0, frame_count=60),
        events=[],
        transcript_chunks=[],
        processing_time=2.0,
        frame_count=60,
    )


class TestExportFormat:
    """Tests for ExportFormat enum."""

    @pytest.mark.unit
    def test_export_format_values(self):
        """
        SPEC: S013
        TEST_ID: T013.E1
        Given: ExportFormat enum
        When: Accessing values
        Then: Has markdown, json, srt options
        """
        from vl_jepa.ui.export import ExportFormat

        assert ExportFormat.MARKDOWN == "markdown"
        assert ExportFormat.JSON == "json"
        assert ExportFormat.SRT == "srt"


class TestExportMarkdown:
    """Tests for Markdown export."""

    @pytest.mark.unit
    def test_includes_video_metadata(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E2
        Given: ProcessingResult with metadata
        When: export_markdown() is called
        Then: Output contains video info (duration, resolution)
        """
        from vl_jepa.ui.export import export_markdown

        result = export_markdown(sample_result)

        assert "lecture_intro.mp4" in result
        assert "1920" in result or "1080" in result
        assert "5:00" in result or "300" in result  # Duration

    @pytest.mark.unit
    def test_includes_events_as_list(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E3
        Given: ProcessingResult with events
        When: export_markdown() is called
        Then: Events formatted with timestamps
        """
        from vl_jepa.ui.export import export_markdown

        result = export_markdown(sample_result)

        # Should have event section
        assert "Event" in result or "event" in result
        # Should have timestamps
        assert "0:00" in result or "00:00" in result
        assert "1:00" in result or "01:00" in result or "60" in result

    @pytest.mark.unit
    def test_includes_transcript(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E4
        Given: ProcessingResult with transcript
        When: export_markdown() is called
        Then: Transcript text included
        """
        from vl_jepa.ui.export import export_markdown

        result = export_markdown(sample_result)

        assert "Welcome to the lecture" in result
        assert "neural networks" in result

    @pytest.mark.unit
    def test_handles_missing_transcript(self, minimal_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E5
        EDGE_CASE: EC_UI_001
        Given: ProcessingResult without transcript
        When: export_markdown() is called
        Then: Export succeeds without transcript section
        """
        from vl_jepa.ui.export import export_markdown

        result = export_markdown(minimal_result)

        # Should still have basic structure
        assert "test_video.mp4" in result
        # Should indicate no transcript or just skip section
        assert result is not None
        assert len(result) > 0

    @pytest.mark.unit
    def test_markdown_is_valid_format(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E6
        Given: ProcessingResult
        When: export_markdown() is called
        Then: Output is valid Markdown with headers
        """
        from vl_jepa.ui.export import export_markdown

        result = export_markdown(sample_result)

        # Should have Markdown headers
        assert result.startswith("#") or "# " in result
        # Should have list items or bullet points for events
        assert "-" in result or "*" in result or "1." in result


class TestExportJSON:
    """Tests for JSON export."""

    @pytest.mark.unit
    def test_valid_json_output(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E7
        Given: ProcessingResult
        When: export_json() is called
        Then: Output parses as valid JSON
        """
        from vl_jepa.ui.export import export_json

        result = export_json(sample_result)

        # Should parse without error
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    @pytest.mark.unit
    def test_includes_all_fields(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E8
        Given: ProcessingResult
        When: export_json() is called
        Then: JSON contains metadata, events, transcript
        """
        from vl_jepa.ui.export import export_json

        result = export_json(sample_result)
        parsed = json.loads(result)

        # Required top-level keys
        assert "metadata" in parsed
        assert "events" in parsed
        assert "transcript" in parsed

        # Metadata fields
        assert parsed["metadata"]["duration"] == 300.0
        assert parsed["metadata"]["resolution"] == "1920x1080"

        # Events
        assert len(parsed["events"]) == 3
        assert parsed["events"][0]["timestamp"] == 0.0

        # Transcript
        assert len(parsed["transcript"]) == 3
        assert "Welcome" in parsed["transcript"][0]["text"]

    @pytest.mark.unit
    def test_handles_empty_events(self, minimal_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E9
        EDGE_CASE: EC_UI_002
        Given: ProcessingResult with no events
        When: export_json() is called
        Then: JSON has empty events array
        """
        from vl_jepa.ui.export import export_json

        result = export_json(minimal_result)
        parsed = json.loads(result)

        assert parsed["events"] == []
        assert parsed["transcript"] == []


class TestExportSRT:
    """Tests for SRT subtitle export."""

    @pytest.mark.unit
    def test_valid_srt_format(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E10
        Given: ProcessingResult with transcript
        When: export_srt() is called
        Then: Output is valid SRT format
        """
        from vl_jepa.ui.export import export_srt

        result = export_srt(sample_result)

        # SRT format: index, timestamp line, text, blank line
        lines = result.strip().split("\n")

        # First line should be "1"
        assert lines[0] == "1"

        # Second line should have timestamp format: 00:00:00,000 --> 00:00:05,000
        assert "-->" in lines[1]
        assert "," in lines[1]  # SRT uses comma for milliseconds

        # Third line should be text
        assert "Welcome" in lines[2]

    @pytest.mark.unit
    def test_srt_timestamp_format(self, sample_result: MockProcessingResult):
        """
        SPEC: S013
        TEST_ID: T013.E11
        Given: ProcessingResult with transcript
        When: export_srt() is called
        Then: Timestamps in HH:MM:SS,mmm format
        """
        from vl_jepa.ui.export import export_srt

        result = export_srt(sample_result)

        # Should have proper SRT timestamp format
        assert "00:00:00,000" in result or "00:00:00,0" in result
        assert "00:00:05,000" in result or "00:00:05,0" in result

    @pytest.mark.unit
    def test_empty_transcript_returns_empty(
        self, minimal_result: MockProcessingResult
    ):
        """
        SPEC: S013
        TEST_ID: T013.E12
        EDGE_CASE: EC_UI_003
        Given: ProcessingResult with no transcript
        When: export_srt() is called
        Then: Returns empty string
        """
        from vl_jepa.ui.export import export_srt

        result = export_srt(minimal_result)

        assert result == "" or result.strip() == ""

    @pytest.mark.unit
    def test_multiline_text_collapsed_to_single_line(self):
        """
        SPEC: S013
        TEST_ID: T013.E15
        EDGE_CASE: EC_UI_004
        Given: Transcript chunk with embedded newlines
        When: export_srt() is called
        Then: Newlines replaced with spaces, no SRT format corruption
        """
        from vl_jepa.ui.export import export_srt

        # Create result with multi-line text
        result_with_multiline = MockProcessingResult(
            transcript_chunks=[
                MockTranscriptChunk(
                    text="Line 1\nLine 2\n\nLine 3",
                    start=0.0,
                    end=5.0,
                ),
                MockTranscriptChunk(
                    text="Text with\r\nWindows newlines\rand old Mac returns",
                    start=5.0,
                    end=10.0,
                ),
            ],
        )

        srt = export_srt(result_with_multiline)
        lines = srt.split("\n")

        # SRT structure: index, timestamp, text, blank line
        # Entry 1: lines 0-3
        # Entry 2: lines 4-7
        # Verify no embedded newlines break the structure

        # First subtitle
        assert lines[0] == "1"
        assert "-->" in lines[1]
        # Text should be on single line with spaces instead of newlines
        assert "Line 1 Line 2 Line 3" in lines[2]
        assert lines[3] == ""  # Blank separator

        # Second subtitle
        assert lines[4] == "2"
        assert "-->" in lines[5]
        # Windows and Mac newlines also collapsed
        assert "\n" not in lines[6]
        assert "\r" not in lines[6]
        assert "Windows newlines" in lines[6]
        assert lines[7] == ""  # Blank separator


class TestFormatTimestamp:
    """Tests for timestamp formatting utility."""

    @pytest.mark.unit
    def test_format_seconds_to_mmss(self):
        """
        SPEC: S013
        TEST_ID: T013.E13
        Given: Time in seconds
        When: format_timestamp() is called
        Then: Returns MM:SS format
        """
        from vl_jepa.ui.export import format_timestamp

        assert format_timestamp(0) == "0:00"
        assert format_timestamp(65) == "1:05"
        assert format_timestamp(3661) == "61:01"

    @pytest.mark.unit
    def test_format_timestamp_srt(self):
        """
        SPEC: S013
        TEST_ID: T013.E14
        Given: Time in seconds
        When: format_timestamp_srt() is called
        Then: Returns HH:MM:SS,mmm format
        """
        from vl_jepa.ui.export import format_timestamp_srt

        assert format_timestamp_srt(0.0) == "00:00:00,000"
        assert format_timestamp_srt(65.5) == "00:01:05,500"
        assert format_timestamp_srt(3661.123) == "01:01:01,123"
