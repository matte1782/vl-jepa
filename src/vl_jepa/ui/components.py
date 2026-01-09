"""
Reusable UI components for Gradio interface.

IMPLEMENTS: S013 - Gradio Web Interface (UI Components)

Provides HTML-generating components for:
- Timeline visualization with event markers
- Event cards with confidence indicators
- Search results with query highlighting
- Transcript display with timestamps
"""

from __future__ import annotations

import html
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimelineEvent:
    """Event marker for timeline visualization.

    Attributes:
        timestamp: Event time in seconds.
        confidence: Confidence score (0.0 to 1.0).
        summary: Optional event description.
        event_type: Event category (event, topic_shift, keypoint).
    """

    timestamp: float
    confidence: float
    summary: str = ""
    event_type: str = "event"


@dataclass
class SearchResultDisplay:
    """Display data for a search result.

    Attributes:
        id: Result identifier.
        score: Relevance score (0.0 to 1.0).
        timestamp: Time position in video.
        text: Text content (for transcript results).
        modality: Source type (visual or transcript).
        frame_index: Frame number (for visual results).
    """

    id: int
    score: float
    timestamp: float
    modality: str
    text: str | None = None
    frame_index: int | None = None


@dataclass
class TranscriptChunkDisplay:
    """Display data for a transcript chunk.

    Attributes:
        text: Transcript text content.
        start: Start time in seconds.
        end: End time in seconds.
        is_active: Whether this chunk is currently playing.
    """

    text: str
    start: float
    end: float
    is_active: bool = False


def format_timestamp_display(seconds: float) -> str:
    """Format seconds to MM:SS for display.

    Handles edge cases like infinity and NaN by returning "0:00".
    """
    import math

    # Handle non-finite values (inf, -inf, nan)
    if not math.isfinite(seconds) or seconds < 0:
        return "0:00"
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes}:{secs:02d}"


def get_confidence_color(confidence: float, dark_mode: bool = False) -> str:
    """
    Get color for confidence level.

    Args:
        confidence: Confidence score (0.0 to 1.0).
        dark_mode: Whether to use dark mode colors.

    Returns:
        Hex color code.
    """
    if confidence >= 0.8:
        return "#4ade80" if dark_mode else "#22c55e"  # Green/success
    elif confidence >= 0.5:
        return "#fbbf24" if dark_mode else "#f59e0b"  # Amber/warning
    else:
        return "#f87171" if dark_mode else "#ef4444"  # Red/error


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text with ellipsis if too long.

    Args:
        text: Text to truncate.
        max_length: Maximum length before truncation.

    Returns:
        Original or truncated text with "...".
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def highlight_text(text: str, query: str) -> str:
    """
    Highlight query terms in text with <mark> tags.

    Args:
        text: Text to search in.
        query: Query terms to highlight.

    Returns:
        HTML string with highlights.
    """
    if not query or not query.strip():
        return html.escape(text)

    # Escape HTML in original text first
    escaped_text = html.escape(text)

    # Case-insensitive replacement
    pattern = re.compile(re.escape(html.escape(query)), re.IGNORECASE)

    def replacer(match: re.Match[str]) -> str:
        return f"<mark class='highlight'>{match.group(0)}</mark>"

    return pattern.sub(replacer, escaped_text)


def create_timeline(events: list[TimelineEvent], duration: float) -> str:
    """
    Create interactive timeline visualization.

    IMPLEMENTS: S013.C1 - Timeline Component

    Args:
        events: List of TimelineEvent objects.
        duration: Total video duration in seconds.

    Returns:
        HTML string for timeline display.
    """
    if duration <= 0:
        duration = 1.0  # Prevent division by zero

    markers_html = ""
    for event in events:
        position = (event.timestamp / duration) * 100
        color = get_confidence_color(event.confidence)
        tooltip = f"{format_timestamp_display(event.timestamp)} - {event.summary or event.event_type}"

        markers_html += f"""
        <div class="timeline-event"
             style="left: {position:.1f}%; background-color: {color};"
             title="{html.escape(tooltip)}"
             data-timestamp="{event.timestamp}">
        </div>
        """

    return f"""
    <div class="timeline-container">
        <div class="timeline-track">
            {markers_html}
        </div>
        <div class="timeline-labels">
            <span class="timeline-start">0:00</span>
            <span class="timeline-end">{format_timestamp_display(duration)}</span>
        </div>
    </div>
    """


def create_event_card(event: TimelineEvent) -> str:
    """
    Create styled event card.

    IMPLEMENTS: S013.C2 - Event Card Component

    Args:
        event: TimelineEvent to display.

    Returns:
        HTML string for event card.
    """
    timestamp_str = format_timestamp_display(event.timestamp)
    confidence_pct = int(event.confidence * 100)
    color = get_confidence_color(event.confidence)
    summary = event.summary or "Event detected"

    return f"""
    <div class="event-card" data-timestamp="{event.timestamp}">
        <div class="event-header">
            <span class="event-timestamp">[{timestamp_str}]</span>
            <span class="event-confidence" style="color: {color};">{confidence_pct}%</span>
        </div>
        <div class="event-type">{html.escape(event.event_type)}</div>
        <div class="event-summary">{html.escape(summary)}</div>
    </div>
    """


def create_search_result(result: SearchResultDisplay, query: str) -> str:
    """
    Create search result with highlighted matches.

    IMPLEMENTS: S013.C3 - Search Result Component

    Args:
        result: SearchResultDisplay to render.
        query: Query string for highlighting.

    Returns:
        HTML string for search result.
    """
    timestamp_str = format_timestamp_display(result.timestamp)
    score_pct = int(result.score * 100)
    modality_icon = "🎬" if result.modality == "visual" else "📝"
    modality_label = "Frame" if result.modality == "visual" else "Transcript"

    # Text content with highlighting
    text_html = ""
    if result.text:
        highlighted = highlight_text(result.text, query)
        text_html = f'<div class="search-result-text">{highlighted}</div>'
    elif result.modality == "visual":
        text_html = f'<div class="search-result-text">Visual match at frame {result.frame_index or "N/A"}</div>'

    return f"""
    <div class="search-result" data-timestamp="{result.timestamp}">
        <div class="search-result-header">
            <span class="search-result-modality">{modality_icon} {modality_label}</span>
            <span class="search-result-timestamp">[{timestamp_str}]</span>
            <span class="search-result-score">{score_pct}% match</span>
        </div>
        {text_html}
    </div>
    """


def create_transcript_display(chunks: list[TranscriptChunkDisplay]) -> str:
    """
    Create transcript display with timestamps.

    IMPLEMENTS: S013.C4 - Transcript Display Component

    Args:
        chunks: List of transcript chunks to display.

    Returns:
        HTML string for transcript.
    """
    if not chunks:
        return '<div class="transcript-empty">No transcript available.</div>'

    chunks_html = ""
    for chunk in chunks:
        start_str = format_timestamp_display(chunk.start)
        end_str = format_timestamp_display(chunk.end)
        active_class = " transcript-chunk-active" if chunk.is_active else ""

        chunks_html += f"""
        <div class="transcript-chunk{active_class}"
             data-start="{chunk.start}"
             data-end="{chunk.end}">
            <span class="transcript-timestamp">[{start_str} - {end_str}]</span>
            <span class="transcript-text">{html.escape(chunk.text)}</span>
        </div>
        """

    return f"""
    <div class="transcript-container">
        {chunks_html}
    </div>
    """


def create_summary_display(
    video_name: str,
    duration: float,
    event_count: int,
    transcript_length: int,
    processing_time: float,
) -> str:
    """
    Create summary display for processed video.

    IMPLEMENTS: S013.C5 - Summary Display Component

    Args:
        video_name: Name of the video file.
        duration: Video duration in seconds.
        event_count: Number of detected events.
        transcript_length: Number of transcript chunks.
        processing_time: Time taken to process.

    Returns:
        HTML string for summary.
    """
    duration_str = format_timestamp_display(duration)

    return f"""
    <div class="summary-container">
        <h2 class="summary-title">{html.escape(video_name)}</h2>
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-icon">⏱️</span>
                <span class="stat-label">Duration</span>
                <span class="stat-value">{duration_str}</span>
            </div>
            <div class="stat-item">
                <span class="stat-icon">📍</span>
                <span class="stat-label">Events</span>
                <span class="stat-value">{event_count}</span>
            </div>
            <div class="stat-item">
                <span class="stat-icon">📝</span>
                <span class="stat-label">Transcript Segments</span>
                <span class="stat-value">{transcript_length}</span>
            </div>
            <div class="stat-item">
                <span class="stat-icon">⚡</span>
                <span class="stat-label">Processing Time</span>
                <span class="stat-value">{processing_time:.1f}s</span>
            </div>
        </div>
    </div>
    """


def create_progress_display(
    stage: str,
    progress: float,
    message: str,
) -> str:
    """
    Create progress display for processing.

    IMPLEMENTS: S013.C6 - Progress Display Component

    Args:
        stage: Current processing stage name.
        progress: Progress percentage (0.0 to 1.0).
        message: Current status message.

    Returns:
        HTML string for progress display.
    """
    progress_pct = int(progress * 100)

    return f"""
    <div class="progress-container">
        <div class="progress-header">
            <span class="progress-stage">{html.escape(stage)}</span>
            <span class="progress-percentage">{progress_pct}%</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {progress_pct}%;"></div>
        </div>
        <div class="progress-message">{html.escape(message)}</div>
    </div>
    """


# =============================================================================
# LEVEL B: SKELETON LOADING COMPONENTS
# =============================================================================


def create_skeleton_timeline() -> str:
    """
    Create skeleton loading state for timeline.

    Returns:
        HTML string for timeline skeleton.
    """
    return """
    <div class="skeleton-timeline-wrapper">
        <div class="skeleton-timeline">
            <div class="skeleton-pulse"></div>
        </div>
        <div class="skeleton-labels">
            <div class="skeleton-text skeleton-text-sm"></div>
            <div class="skeleton-text skeleton-text-sm"></div>
        </div>
    </div>
    """


def create_skeleton_summary() -> str:
    """
    Create skeleton loading state for summary panel.

    Returns:
        HTML string for summary skeleton.
    """
    return """
    <div class="skeleton-summary">
        <div class="skeleton-title"></div>
        <div class="skeleton-stats-grid">
            <div class="skeleton-stat-card">
                <div class="skeleton-icon"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text skeleton-text-lg"></div>
            </div>
            <div class="skeleton-stat-card">
                <div class="skeleton-icon"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text skeleton-text-lg"></div>
            </div>
            <div class="skeleton-stat-card">
                <div class="skeleton-icon"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text skeleton-text-lg"></div>
            </div>
            <div class="skeleton-stat-card">
                <div class="skeleton-icon"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text skeleton-text-lg"></div>
            </div>
        </div>
    </div>
    """


def create_skeleton_events(count: int = 3) -> str:
    """
    Create skeleton loading state for events list.

    Args:
        count: Number of skeleton event cards to show.

    Returns:
        HTML string for events skeleton.
    """
    cards = ""
    for i in range(count):
        delay = i * 0.1
        cards += f"""
        <div class="skeleton-event-card" style="animation-delay: {delay}s;">
            <div class="skeleton-event-header">
                <div class="skeleton-text skeleton-text-sm"></div>
                <div class="skeleton-badge"></div>
            </div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text skeleton-text-lg"></div>
        </div>
        """

    return f"""
    <div class="skeleton-events-list">
        {cards}
    </div>
    """


def create_skeleton_transcript(lines: int = 5) -> str:
    """
    Create skeleton loading state for transcript.

    Args:
        lines: Number of skeleton transcript lines.

    Returns:
        HTML string for transcript skeleton.
    """
    chunks = ""
    for i in range(lines):
        delay = i * 0.08
        # Vary widths for more realistic look
        width = 90 - (i % 3) * 15
        chunks += f"""
        <div class="skeleton-transcript-chunk" style="animation-delay: {delay}s;">
            <div class="skeleton-timestamp"></div>
            <div class="skeleton-text" style="width: {width}%;"></div>
        </div>
        """

    return f"""
    <div class="skeleton-transcript">
        {chunks}
    </div>
    """


def create_skeleton_search_results(count: int = 3) -> str:
    """
    Create skeleton loading state for search results.

    Args:
        count: Number of skeleton results to show.

    Returns:
        HTML string for search skeleton.
    """
    results = ""
    for i in range(count):
        delay = i * 0.1
        results += f"""
        <div class="skeleton-search-result" style="animation-delay: {delay}s;">
            <div class="skeleton-result-header">
                <div class="skeleton-badge"></div>
                <div class="skeleton-text skeleton-text-sm"></div>
                <div class="skeleton-text skeleton-text-sm"></div>
            </div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text" style="width: 70%;"></div>
        </div>
        """

    return f"""
    <div class="skeleton-search-results">
        {results}
    </div>
    """


# =============================================================================
# LEVEL B: MULTI-STAGE PROGRESS VISUALIZATION
# =============================================================================


PROCESSING_STAGES = [
    ("loading", "Loading", "📂"),
    ("audio", "Audio", "🔊"),
    ("transcription", "Transcription", "📝"),
    ("frames", "Frames", "🎞️"),
    ("encoding", "Encoding", "🧠"),
    ("embedding", "Embedding", "📊"),
    ("detection", "Detection", "🔍"),
    ("indexing", "Indexing", "📁"),
]


def create_multi_stage_progress(
    current_stage: str,
    progress: float,
    message: str,
) -> str:
    """
    Create multi-stage progress visualization with stage indicators.

    IMPLEMENTS: S013.C7 - Multi-Stage Progress Component

    Args:
        current_stage: Current processing stage key.
        progress: Overall progress (0.0 to 1.0).
        message: Current status message.

    Returns:
        HTML string for multi-stage progress.
    """
    progress_pct = int(progress * 100)

    # Find current stage index
    current_idx = -1
    for i, (key, _, _) in enumerate(PROCESSING_STAGES):
        if key == current_stage:
            current_idx = i
            break

    # Build stage indicators
    stages_html = ""
    for i, (_key, label, icon) in enumerate(PROCESSING_STAGES):
        if i < current_idx:
            state_class = "stage-completed"
            state_icon = "✓"
        elif i == current_idx:
            state_class = "stage-active"
            state_icon = icon
        else:
            state_class = "stage-pending"
            state_icon = icon

        stages_html += f"""
        <div class="progress-stage-item {state_class}" title="{label}">
            <span class="stage-icon">{state_icon}</span>
            <span class="stage-label">{label}</span>
        </div>
        """

    return f"""
    <div class="multi-stage-progress">
        <div class="progress-stages">
            {stages_html}
        </div>
        <div class="progress-bar-wrapper">
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: {progress_pct}%;">
                    <div class="progress-bar-shimmer"></div>
                </div>
            </div>
            <span class="progress-percentage-label">{progress_pct}%</span>
        </div>
        <div class="progress-message-box">
            <span class="progress-spinner"></span>
            <span class="progress-message-text">{html.escape(message)}</span>
        </div>
    </div>
    """


# =============================================================================
# LEVEL B: TOAST NOTIFICATIONS
# =============================================================================


def create_toast(
    message: str,
    toast_type: str = "info",
    duration: int = 3000,
    dismissible: bool = True,
) -> str:
    """
    Create toast notification HTML.

    Args:
        message: Notification message.
        toast_type: Type of toast (success, error, warning, info).
        duration: Auto-dismiss duration in ms (0 for no auto-dismiss).
        dismissible: Whether user can manually dismiss.

    Returns:
        HTML string for toast notification.
    """
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }
    icon = icons.get(toast_type, "ℹ️")

    dismiss_btn = ""
    if dismissible:
        dismiss_btn = '<button class="toast-dismiss" onclick="this.parentElement.remove()">×</button>'

    return f"""
    <div class="toast toast-{toast_type}" data-duration="{duration}">
        <span class="toast-icon">{icon}</span>
        <span class="toast-message">{html.escape(message)}</span>
        {dismiss_btn}
    </div>
    """


def create_toast_container() -> str:
    """
    Create container for toast notifications.

    Returns:
        HTML string for toast container.
    """
    return """
    <div id="toast-container" class="toast-container"></div>
    """
