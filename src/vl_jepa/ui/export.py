"""
Export functionality for UI results.

IMPLEMENTS: S013 - Gradio Web Interface (Export Tab)
INVARIANTS: INV_UI_001 - Export outputs are valid format

Provides export to:
- Markdown: Human-readable summary document
- JSON: Machine-readable structured data
- SRT: Subtitle file for video players
"""

from __future__ import annotations

import json
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Supported export formats."""

    MARKDOWN = "markdown"
    JSON = "json"
    SRT = "srt"


# Protocol for type checking without circular imports
@runtime_checkable
class VideoMetadataProtocol(Protocol):
    """Protocol for video metadata."""

    path: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float
    codec: str


@runtime_checkable
class EventBoundaryProtocol(Protocol):
    """Protocol for event boundaries."""

    timestamp: float
    confidence: float


@runtime_checkable
class TranscriptChunkProtocol(Protocol):
    """Protocol for transcript chunks."""

    text: str
    start: float
    end: float


@runtime_checkable
class ProcessingResultProtocol(Protocol):
    """Protocol for processing results."""

    metadata: Any  # VideoMetadataProtocol
    events: list[Any]  # list[EventBoundaryProtocol]
    transcript_chunks: list[Any]  # list[TranscriptChunkProtocol]
    processing_time: float
    frame_count: int
    error: str | None


def _escape_markdown(text: str) -> str:
    """
    Escape Markdown special characters to prevent content injection.

    Args:
        text: Raw text that may contain Markdown syntax.

    Returns:
        Text with Markdown special characters escaped.
    """
    # Characters that have special meaning in Markdown
    special_chars = ["\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!", "|"]
    result = text
    for char in special_chars:
        result = result.replace(char, f"\\{char}")
    return result


def format_timestamp(seconds: float | int) -> str:
    """
    Format seconds to MM:SS display format.

    Handles edge cases like infinity and NaN by returning "0:00".

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted string like "5:30" or "65:01".

    Example:
        >>> format_timestamp(65)
        '1:05'
        >>> format_timestamp(3661)
        '61:01'
    """
    import math

    # Handle non-finite values (inf, -inf, nan) and negative
    if not math.isfinite(seconds) or seconds < 0:
        return "0:00"
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes}:{secs:02d}"


def format_timestamp_srt(seconds: float) -> str:
    """
    Format seconds to SRT timestamp format (HH:MM:SS,mmm).

    Handles edge cases like infinity and NaN by returning "00:00:00,000".

    Args:
        seconds: Time in seconds with decimals.

    Returns:
        Formatted string like "00:01:05,500".

    Example:
        >>> format_timestamp_srt(65.5)
        '00:01:05,500'
    """
    import math

    # Handle non-finite values (inf, -inf, nan) and negative
    if not math.isfinite(seconds) or seconds < 0:
        return "00:00:00,000"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def export_markdown(result: ProcessingResultProtocol) -> str:
    """
    Export processing result to Markdown format.

    IMPLEMENTS: S013.E1 - Markdown Export

    Args:
        result: ProcessingResult with metadata, events, and transcript.

    Returns:
        Formatted Markdown document string.

    Example:
        >>> md = export_markdown(result)
        >>> print(md)
        # Lecture Summary: lecture.mp4
        ...
    """
    lines: list[str] = []
    metadata = result.metadata

    # Header
    lines.append(f"# Lecture Summary: {metadata.path}")
    lines.append("")

    # Video Info
    lines.append("## Video Information")
    lines.append("")
    lines.append(f"- **Duration**: {format_timestamp(metadata.duration)}")
    lines.append(f"- **Resolution**: {metadata.width}x{metadata.height}")
    lines.append(f"- **Frame Rate**: {metadata.fps:.1f} fps")
    lines.append(f"- **Codec**: {metadata.codec}")
    lines.append(f"- **Frames Processed**: {result.frame_count}")
    lines.append(f"- **Processing Time**: {result.processing_time:.1f}s")
    lines.append("")

    # Events
    if result.events:
        lines.append("## Events Detected")
        lines.append("")
        for i, event in enumerate(result.events, 1):
            timestamp = format_timestamp(event.timestamp)
            confidence = event.confidence * 100
            lines.append(
                f"{i}. **[{timestamp}]** - Event (confidence: {confidence:.0f}%)"
            )
        lines.append("")
    else:
        lines.append("## Events Detected")
        lines.append("")
        lines.append("*No events detected.*")
        lines.append("")

    # Transcript
    if result.transcript_chunks:
        lines.append("## Transcript")
        lines.append("")
        for chunk in result.transcript_chunks:
            start = format_timestamp(chunk.start)
            end = format_timestamp(chunk.end)
            lines.append(f"**[{start} - {end}]**")
            # Escape user content to prevent Markdown injection
            lines.append(_escape_markdown(chunk.text))
            lines.append("")
    else:
        lines.append("## Transcript")
        lines.append("")
        lines.append("*No transcript available.*")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("*Generated by Lecture Mind - VL-JEPA Lecture Summarizer*")

    return "\n".join(lines)


def export_json(result: ProcessingResultProtocol) -> str:
    """
    Export processing result to JSON format.

    IMPLEMENTS: S013.E2 - JSON Export

    Args:
        result: ProcessingResult with metadata, events, and transcript.

    Returns:
        JSON string with structured data.

    Example:
        >>> json_str = export_json(result)
        >>> data = json.loads(json_str)
        >>> data["metadata"]["duration"]
        300.0
    """
    metadata = result.metadata

    data = {
        "metadata": {
            "path": metadata.path,
            "duration": metadata.duration,
            "resolution": f"{metadata.width}x{metadata.height}",
            "fps": metadata.fps,
            "codec": metadata.codec,
            "frame_count": result.frame_count,
            "processing_time": result.processing_time,
        },
        "events": [
            {
                "timestamp": event.timestamp,
                "timestamp_formatted": format_timestamp(event.timestamp),
                "confidence": event.confidence,
            }
            for event in result.events
        ],
        "transcript": [
            {
                "text": chunk.text,
                "start": chunk.start,
                "end": chunk.end,
                "start_formatted": format_timestamp(chunk.start),
                "end_formatted": format_timestamp(chunk.end),
            }
            for chunk in result.transcript_chunks
        ],
    }

    return json.dumps(data, indent=2, ensure_ascii=False)


def export_srt(result: ProcessingResultProtocol) -> str:
    """
    Export transcript to SRT subtitle format.

    IMPLEMENTS: S013.E3 - SRT Export

    Args:
        result: ProcessingResult with transcript chunks.

    Returns:
        SRT formatted string for video subtitles.
        Returns empty string if no transcript.

    Example:
        >>> srt = export_srt(result)
        >>> print(srt)
        1
        00:00:00,000 --> 00:00:05,000
        Welcome to the lecture.
        ...
    """
    if not result.transcript_chunks:
        return ""

    lines: list[str] = []

    for i, chunk in enumerate(result.transcript_chunks, 1):
        # Subtitle index
        lines.append(str(i))

        # Timestamp line
        start_ts = format_timestamp_srt(chunk.start)
        end_ts = format_timestamp_srt(chunk.end)
        lines.append(f"{start_ts} --> {end_ts}")

        # Text (remove any embedded newlines/carriage returns for clean SRT)
        # SRT format uses blank lines as separators, so multi-line text breaks parsing
        text = chunk.text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        # Collapse multiple spaces and strip
        text = " ".join(text.split())
        lines.append(text)

        # Blank line separator
        lines.append("")

    return "\n".join(lines)


def export_summary(
    result: ProcessingResultProtocol,
    format: ExportFormat,
    include_transcript: bool = True,
    include_events: bool = True,
) -> str:
    """
    Export processing result to specified format.

    IMPLEMENTS: S013.E4 - Unified Export API

    Args:
        result: ProcessingResult to export.
        format: Target format (markdown, json, srt).
        include_transcript: Whether to include transcript.
        include_events: Whether to include events.

    Returns:
        Formatted export string.

    Raises:
        ValueError: If format is unsupported.
    """
    if format == ExportFormat.MARKDOWN:
        return export_markdown(result)
    elif format == ExportFormat.JSON:
        return export_json(result)
    elif format == ExportFormat.SRT:
        return export_srt(result)
    else:
        raise ValueError(f"Unsupported export format: {format}")
