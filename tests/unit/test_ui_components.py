"""
Unit tests for UI components.

SPEC: S013 - Gradio Web Interface
TEST_IDs: T013.C1-T013.C15

Tests for timeline, event cards, search results, and utility functions.
"""

import pytest


class TestTimelineEvent:
    """Tests for TimelineEvent dataclass."""

    @pytest.mark.unit
    def test_timeline_event_creation(self):
        """
        SPEC: S013
        TEST_ID: T013.C1
        Given: Event parameters
        When: TimelineEvent is created
        Then: Has correct attributes
        """
        from vl_jepa.ui.components import TimelineEvent

        event = TimelineEvent(
            timestamp=60.0,
            confidence=0.85,
            summary="Topic change",
            event_type="topic_shift",
        )

        assert event.timestamp == 60.0
        assert event.confidence == 0.85
        assert event.summary == "Topic change"
        assert event.event_type == "topic_shift"

    @pytest.mark.unit
    def test_timeline_event_default_type(self):
        """
        SPEC: S013
        TEST_ID: T013.C2
        Given: Event without type
        When: TimelineEvent is created
        Then: Uses default type 'event'
        """
        from vl_jepa.ui.components import TimelineEvent

        event = TimelineEvent(timestamp=0.0, confidence=1.0)

        assert event.event_type == "event"


class TestCreateTimeline:
    """Tests for timeline visualization."""

    @pytest.mark.unit
    def test_timeline_with_no_events(self):
        """
        SPEC: S013
        TEST_ID: T013.C3
        EDGE_CASE: EC_UI_004
        Given: Empty event list
        When: create_timeline() is called
        Then: Returns valid HTML with no markers
        """
        from vl_jepa.ui.components import create_timeline

        html = create_timeline(events=[], duration=300.0)

        assert "<div" in html
        assert "timeline" in html.lower()

    @pytest.mark.unit
    def test_timeline_positions_events_correctly(self):
        """
        SPEC: S013
        TEST_ID: T013.C4
        Given: Events at 0s, 60s in 300s video
        When: create_timeline() is called
        Then: Events positioned at 0%, 20%
        """
        from vl_jepa.ui.components import TimelineEvent, create_timeline

        events = [
            TimelineEvent(timestamp=0.0, confidence=1.0),
            TimelineEvent(timestamp=60.0, confidence=0.85),
        ]

        html = create_timeline(events=events, duration=300.0)

        # Events should have position styling
        assert "0%" in html or "0.0%" in html or "left: 0" in html or "left:0" in html
        assert "20%" in html or "20.0%" in html

    @pytest.mark.unit
    def test_timeline_event_colors_by_confidence(self):
        """
        SPEC: S013
        TEST_ID: T013.C5
        Given: Events with different confidence levels
        When: create_timeline() is called
        Then: High confidence = success color, low = warning
        """
        from vl_jepa.ui.components import TimelineEvent, create_timeline

        events = [
            TimelineEvent(timestamp=0.0, confidence=0.95),  # High
            TimelineEvent(timestamp=60.0, confidence=0.50),  # Low
        ]

        html = create_timeline(events=events, duration=300.0)

        # Should have different color indicators
        assert "success" in html or "#22c55e" in html or "#4ade80" in html
        assert "warning" in html or "#f59e0b" in html or "#fbbf24" in html

    @pytest.mark.unit
    def test_timeline_zero_duration_handled(self):
        """
        SPEC: S013
        TEST_ID: T013.C6
        EDGE_CASE: EC_UI_005
        Given: Zero duration
        When: create_timeline() is called
        Then: Returns valid HTML (no division by zero)
        """
        from vl_jepa.ui.components import TimelineEvent, create_timeline

        events = [TimelineEvent(timestamp=0.0, confidence=1.0)]

        # Should not raise
        html = create_timeline(events=events, duration=0.0)
        assert html is not None


class TestCreateEventCard:
    """Tests for event card component."""

    @pytest.mark.unit
    def test_event_card_contains_timestamp(self):
        """
        SPEC: S013
        TEST_ID: T013.C7
        Given: TimelineEvent
        When: create_event_card() is called
        Then: HTML contains formatted timestamp
        """
        from vl_jepa.ui.components import TimelineEvent, create_event_card

        event = TimelineEvent(timestamp=125.0, confidence=0.9, summary="Key point")

        html = create_event_card(event)

        # 125 seconds = 2:05
        assert "2:05" in html

    @pytest.mark.unit
    def test_event_card_contains_confidence(self):
        """
        SPEC: S013
        TEST_ID: T013.C8
        Given: TimelineEvent with confidence
        When: create_event_card() is called
        Then: HTML shows confidence percentage
        """
        from vl_jepa.ui.components import TimelineEvent, create_event_card

        event = TimelineEvent(timestamp=0.0, confidence=0.85)

        html = create_event_card(event)

        assert "85%" in html or "85" in html

    @pytest.mark.unit
    def test_event_card_contains_summary(self):
        """
        SPEC: S013
        TEST_ID: T013.C9
        Given: TimelineEvent with summary
        When: create_event_card() is called
        Then: HTML contains summary text
        """
        from vl_jepa.ui.components import TimelineEvent, create_event_card

        event = TimelineEvent(
            timestamp=60.0, confidence=0.9, summary="Introduction to neural networks"
        )

        html = create_event_card(event)

        assert "Introduction to neural networks" in html


class TestCreateSearchResult:
    """Tests for search result display."""

    @pytest.mark.unit
    def test_search_result_highlights_query(self):
        """
        SPEC: S013
        TEST_ID: T013.C10
        Given: Search result and query
        When: create_search_result() is called
        Then: Query terms wrapped in highlight
        """
        from vl_jepa.ui.components import SearchResultDisplay, create_search_result

        result = SearchResultDisplay(
            id=1,
            score=0.95,
            timestamp=120.0,
            text="This lecture covers neural networks in depth.",
            modality="transcript",
        )

        html = create_search_result(result, query="neural networks")

        # Should have highlighting
        assert "<mark>" in html or "highlight" in html
        assert "neural networks" in html.lower()

    @pytest.mark.unit
    def test_search_result_case_insensitive_highlight(self):
        """
        SPEC: S013
        TEST_ID: T013.C11
        Given: Query with different case
        When: create_search_result() is called
        Then: Highlights regardless of case
        """
        from vl_jepa.ui.components import SearchResultDisplay, create_search_result

        result = SearchResultDisplay(
            id=1,
            score=0.9,
            timestamp=0.0,
            text="Machine Learning is fascinating.",
            modality="transcript",
        )

        html = create_search_result(result, query="machine learning")

        # Original case preserved but highlighted
        assert "Machine Learning" in html
        assert "<mark>" in html or "highlight" in html

    @pytest.mark.unit
    def test_search_result_shows_modality(self):
        """
        SPEC: S013
        TEST_ID: T013.C12
        Given: Search result with modality
        When: create_search_result() is called
        Then: Shows whether visual or transcript
        """
        from vl_jepa.ui.components import SearchResultDisplay, create_search_result

        visual_result = SearchResultDisplay(
            id=1, score=0.9, timestamp=30.0, modality="visual"
        )
        transcript_result = SearchResultDisplay(
            id=2, score=0.85, timestamp=45.0, text="Some text", modality="transcript"
        )

        visual_html = create_search_result(visual_result, query="test")
        transcript_html = create_search_result(transcript_result, query="test")

        assert "visual" in visual_html.lower() or "frame" in visual_html.lower()
        assert (
            "transcript" in transcript_html.lower() or "text" in transcript_html.lower()
        )

    @pytest.mark.unit
    def test_search_result_shows_score(self):
        """
        SPEC: S013
        TEST_ID: T013.C13
        Given: Search result with score
        When: create_search_result() is called
        Then: Shows relevance score
        """
        from vl_jepa.ui.components import SearchResultDisplay, create_search_result

        result = SearchResultDisplay(
            id=1, score=0.92, timestamp=0.0, text="Test", modality="transcript"
        )

        html = create_search_result(result, query="test")

        # Score as percentage
        assert "92%" in html or "0.92" in html

    @pytest.mark.unit
    def test_search_result_formats_timestamp(self):
        """
        SPEC: S013
        TEST_ID: T013.C14
        Given: Search result with timestamp
        When: create_search_result() is called
        Then: Timestamp in MM:SS format
        """
        from vl_jepa.ui.components import SearchResultDisplay, create_search_result

        result = SearchResultDisplay(
            id=1, score=0.9, timestamp=185.0, text="Content", modality="transcript"
        )

        html = create_search_result(result, query="content")

        # 185 seconds = 3:05
        assert "3:05" in html


class TestCreateTranscriptDisplay:
    """Tests for transcript display."""

    @pytest.mark.unit
    def test_transcript_display_basic(self):
        """
        SPEC: S013
        TEST_ID: T013.C15
        Given: Transcript chunks
        When: create_transcript_display() is called
        Then: Returns formatted HTML
        """
        from vl_jepa.ui.components import TranscriptChunkDisplay, create_transcript_display

        chunks = [
            TranscriptChunkDisplay(text="Hello world", start=0.0, end=5.0),
            TranscriptChunkDisplay(text="How are you", start=5.0, end=10.0),
        ]

        html = create_transcript_display(chunks)

        assert "Hello world" in html
        assert "How are you" in html
        assert "0:00" in html
        assert "0:05" in html


class TestUtilityFunctions:
    """Tests for component utility functions."""

    @pytest.mark.unit
    def test_get_confidence_color_high(self):
        """
        SPEC: S013
        TEST_ID: T013.C16
        Given: High confidence (>0.8)
        When: get_confidence_color() is called
        Then: Returns success color
        """
        from vl_jepa.ui.components import get_confidence_color

        color = get_confidence_color(0.9)

        assert color in ["#22c55e", "#4ade80", "success"]

    @pytest.mark.unit
    def test_get_confidence_color_medium(self):
        """
        SPEC: S013
        TEST_ID: T013.C17
        Given: Medium confidence (0.5-0.8)
        When: get_confidence_color() is called
        Then: Returns warning color
        """
        from vl_jepa.ui.components import get_confidence_color

        color = get_confidence_color(0.6)

        assert color in ["#f59e0b", "#fbbf24", "warning"]

    @pytest.mark.unit
    def test_get_confidence_color_low(self):
        """
        SPEC: S013
        TEST_ID: T013.C18
        Given: Low confidence (<0.5)
        When: get_confidence_color() is called
        Then: Returns error color
        """
        from vl_jepa.ui.components import get_confidence_color

        color = get_confidence_color(0.3)

        assert color in ["#ef4444", "#f87171", "error"]

    @pytest.mark.unit
    def test_truncate_text_short(self):
        """
        SPEC: S013
        TEST_ID: T013.C19
        Given: Short text
        When: truncate_text() is called
        Then: Returns unchanged
        """
        from vl_jepa.ui.components import truncate_text

        text = "Short text"
        result = truncate_text(text, max_length=50)

        assert result == text

    @pytest.mark.unit
    def test_truncate_text_long(self):
        """
        SPEC: S013
        TEST_ID: T013.C20
        Given: Long text
        When: truncate_text() is called
        Then: Truncates with ellipsis
        """
        from vl_jepa.ui.components import truncate_text

        text = "This is a very long text that should be truncated"
        result = truncate_text(text, max_length=20)

        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

    @pytest.mark.unit
    def test_highlight_text_multiple_matches(self):
        """
        SPEC: S013
        TEST_ID: T013.C21
        Given: Text with multiple query matches
        When: highlight_text() is called
        Then: All matches highlighted
        """
        from vl_jepa.ui.components import highlight_text

        text = "Neural networks use neural computations"
        result = highlight_text(text, query="neural")

        # Count highlight tags (tag has class attribute: <mark class='highlight'>)
        highlight_count = result.lower().count("<mark ")
        assert highlight_count == 2


# =============================================================================
# LEVEL B: SKELETON COMPONENT TESTS
# =============================================================================


class TestSkeletonComponents:
    """Tests for Level B skeleton loading components."""

    @pytest.mark.unit
    def test_skeleton_timeline_has_structure(self):
        """
        SPEC: S013
        TEST_ID: T013.B1.1
        Given: Call to create_skeleton_timeline
        When: Function is invoked
        Then: Returns HTML with skeleton classes
        """
        from vl_jepa.ui.components import create_skeleton_timeline

        result = create_skeleton_timeline()

        assert "skeleton-timeline-wrapper" in result
        assert "skeleton-timeline" in result
        assert "skeleton-pulse" in result

    @pytest.mark.unit
    def test_skeleton_summary_has_stats_grid(self):
        """
        SPEC: S013
        TEST_ID: T013.B1.2
        Given: Call to create_skeleton_summary
        When: Function is invoked
        Then: Returns HTML with stats grid
        """
        from vl_jepa.ui.components import create_skeleton_summary

        result = create_skeleton_summary()

        assert "skeleton-summary" in result
        assert "skeleton-stats-grid" in result
        assert "skeleton-stat-card" in result

    @pytest.mark.unit
    def test_skeleton_events_respects_count(self):
        """
        SPEC: S013
        TEST_ID: T013.B1.3
        Given: Count parameter
        When: create_skeleton_events is called
        Then: Returns correct number of skeleton cards
        """
        from vl_jepa.ui.components import create_skeleton_events

        result = create_skeleton_events(count=5)

        assert result.count("skeleton-event-card") == 5

    @pytest.mark.unit
    def test_skeleton_transcript_varies_widths(self):
        """
        SPEC: S013
        TEST_ID: T013.B1.4
        Given: Lines parameter
        When: create_skeleton_transcript is called
        Then: Returns skeleton with varied widths
        """
        from vl_jepa.ui.components import create_skeleton_transcript

        result = create_skeleton_transcript(lines=3)

        assert "skeleton-transcript" in result
        assert "skeleton-transcript-chunk" in result
        # Should have width variations
        assert "width:" in result

    @pytest.mark.unit
    def test_skeleton_search_results_count(self):
        """
        SPEC: S013
        TEST_ID: T013.B1.5
        Given: Count parameter
        When: create_skeleton_search_results is called
        Then: Returns correct number of results
        """
        from vl_jepa.ui.components import create_skeleton_search_results

        result = create_skeleton_search_results(count=4)

        # Count individual result divs (with style attribute), not the wrapper
        assert result.count('class="skeleton-search-result"') == 4


class TestMultiStageProgress:
    """Tests for Level B multi-stage progress component."""

    @pytest.mark.unit
    def test_multi_stage_progress_shows_stages(self):
        """
        SPEC: S013
        TEST_ID: T013.B2.1
        Given: Current stage and progress
        When: create_multi_stage_progress is called
        Then: Shows all stage indicators
        """
        from vl_jepa.ui.components import create_multi_stage_progress

        result = create_multi_stage_progress(
            current_stage="encoding",
            progress=0.5,
            message="Encoding frames...",
        )

        assert "multi-stage-progress" in result
        assert "progress-stages" in result
        assert "stage-active" in result

    @pytest.mark.unit
    def test_multi_stage_progress_marks_completed(self):
        """
        SPEC: S013
        TEST_ID: T013.B2.2
        Given: Stage at indexing (late stage)
        When: create_multi_stage_progress is called
        Then: Earlier stages marked completed
        """
        from vl_jepa.ui.components import create_multi_stage_progress

        result = create_multi_stage_progress(
            current_stage="indexing",
            progress=0.9,
            message="Building index...",
        )

        # Should have completed stages (checkmark)
        assert "stage-completed" in result
        assert "✓" in result

    @pytest.mark.unit
    def test_multi_stage_progress_shows_percentage(self):
        """
        SPEC: S013
        TEST_ID: T013.B2.3
        Given: Progress value
        When: create_multi_stage_progress is called
        Then: Shows percentage label
        """
        from vl_jepa.ui.components import create_multi_stage_progress

        result = create_multi_stage_progress(
            current_stage="frames",
            progress=0.35,
            message="Sampling frames...",
        )

        assert "35%" in result
        assert "progress-percentage-label" in result


class TestToastNotifications:
    """Tests for Level B toast notification components."""

    @pytest.mark.unit
    def test_toast_has_message_and_icon(self):
        """
        SPEC: S013
        TEST_ID: T013.B4.1
        Given: Toast message and type
        When: create_toast is called
        Then: Contains icon and message
        """
        from vl_jepa.ui.components import create_toast

        result = create_toast("Operation successful", toast_type="success")

        assert "toast-success" in result
        assert "Operation successful" in result
        assert "✅" in result

    @pytest.mark.unit
    def test_toast_error_variant(self):
        """
        SPEC: S013
        TEST_ID: T013.B4.2
        Given: Error toast type
        When: create_toast is called
        Then: Has error styling
        """
        from vl_jepa.ui.components import create_toast

        result = create_toast("Something went wrong", toast_type="error")

        assert "toast-error" in result
        assert "❌" in result

    @pytest.mark.unit
    def test_toast_dismissible(self):
        """
        SPEC: S013
        TEST_ID: T013.B4.3
        Given: Dismissible toast
        When: create_toast is called with dismissible=True
        Then: Has dismiss button
        """
        from vl_jepa.ui.components import create_toast

        result = create_toast("Info message", dismissible=True)

        assert "toast-dismiss" in result

    @pytest.mark.unit
    def test_toast_container(self):
        """
        SPEC: S013
        TEST_ID: T013.B4.4
        Given: Call to create_toast_container
        When: Function is invoked
        Then: Returns container HTML
        """
        from vl_jepa.ui.components import create_toast_container

        result = create_toast_container()

        assert "toast-container" in result
        assert 'id="toast-container"' in result
