"""
Session state management for Gradio UI.

IMPLEMENTS: S013 - Gradio Web Interface (State Management)

Provides:
- UIState: Dataclass for session state
- StateManager: Manager for state operations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class UIState:
    """
    Session state for the Gradio UI.

    IMPLEMENTS: S013.S1 - Session State

    Attributes:
        video_path: Path to the uploaded video.
        processing_result: Result from video processing.
        multimodal_index: Index for search queries.
        is_processing: Whether processing is in progress.
        current_query: Current search query string.
        search_results: Results from last search.
        selected_event_index: Index of selected event in timeline.
        error_message: Current error message (if any).
        dark_mode: Whether dark theme is active.
    """

    video_path: Path | None = None
    processing_result: Any | None = None  # ProcessingResult
    multimodal_index: Any | None = None  # MultimodalIndex
    is_processing: bool = False
    current_query: str = ""
    search_results: list[Any] = field(
        default_factory=list
    )  # list[MultimodalSearchResult]
    selected_event_index: int | None = None
    error_message: str | None = None
    dark_mode: bool = False
    current_timestamp: float = 0.0


class StateManager:
    """
    Manager for UI state operations.

    IMPLEMENTS: S013.S2 - State Management

    Provides methods to safely update and query state.
    """

    def __init__(self) -> None:
        """Initialize StateManager with empty state."""
        self._state = UIState()

    @property
    def state(self) -> UIState:
        """Get current state."""
        return self._state

    def reset(self) -> None:
        """
        Reset state to initial values.

        Clears all state except dark_mode preference.
        """
        dark_mode = self._state.dark_mode  # Preserve theme
        self._state = UIState(dark_mode=dark_mode)
        logger.info("State reset")

    def set_video(self, path: Path) -> None:
        """
        Set the video path.

        Args:
            path: Path to the video file.
        """
        self._state.video_path = path
        self._state.error_message = None
        logger.info(f"Video set: {path}")

    def set_processing_result(self, result: Any) -> None:
        """
        Set the processing result.

        Args:
            result: ProcessingResult from pipeline.
        """
        self._state.processing_result = result
        if hasattr(result, "multimodal_index"):
            self._state.multimodal_index = result.multimodal_index
        self._state.is_processing = False
        logger.info("Processing result set")

    def set_processing(self, is_processing: bool) -> None:
        """
        Set the processing flag.

        Args:
            is_processing: Whether processing is in progress.
        """
        self._state.is_processing = is_processing
        if is_processing:
            self._state.error_message = None

    def set_error(self, message: str) -> None:
        """
        Set an error message.

        Args:
            message: Error message to display.
        """
        self._state.error_message = message
        self._state.is_processing = False
        logger.error(f"Error set: {message}")

    def clear_error(self) -> None:
        """Clear any error message."""
        self._state.error_message = None

    def set_query(self, query: str) -> None:
        """
        Set the current search query.

        Args:
            query: Search query string.
        """
        self._state.current_query = query

    def set_search_results(self, results: list[Any]) -> None:
        """
        Set the search results.

        Args:
            results: List of MultimodalSearchResult.
        """
        self._state.search_results = results

    def select_event(self, index: int | None) -> None:
        """
        Select an event in the timeline.

        Args:
            index: Index of the event, or None to deselect.
        """
        self._state.selected_event_index = index

    def set_timestamp(self, timestamp: float) -> None:
        """
        Set the current video timestamp.

        Args:
            timestamp: Time in seconds.
        """
        self._state.current_timestamp = timestamp

    def toggle_dark_mode(self) -> bool:
        """
        Toggle dark mode.

        Returns:
            New dark mode state.
        """
        self._state.dark_mode = not self._state.dark_mode
        logger.info(f"Dark mode: {self._state.dark_mode}")
        return self._state.dark_mode

    def has_video(self) -> bool:
        """Check if a video is loaded."""
        return self._state.video_path is not None

    def has_results(self) -> bool:
        """Check if processing results are available."""
        return self._state.processing_result is not None

    def can_search(self) -> bool:
        """Check if search is available."""
        return self._state.multimodal_index is not None
