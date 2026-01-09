"""
VL-JEPA Lecture Summarizer - Gradio Web UI.

IMPLEMENTS: S013 - Gradio Web Interface
VERSION: v0.3.0

This module provides a spectacular, premium web interface for:
- Video upload and processing
- Real-time progress tracking
- Multimodal search (visual + transcript)
- Event timeline visualization
- Export to Markdown/JSON/SRT

Example:
    >>> from vl_jepa.ui import create_app, launch
    >>> app = create_app()
    >>> app.launch()

    # Or directly:
    >>> from vl_jepa.ui import launch
    >>> launch(share=True)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Lazy imports for gradio-dependent modules (gradio is optional)
if TYPE_CHECKING:
    from vl_jepa.ui.app import create_app, launch

# Components
from vl_jepa.ui.components import (
    PROCESSING_STAGES,
    SearchResultDisplay,
    TimelineEvent,
    TranscriptChunkDisplay,
    create_event_card,
    create_multi_stage_progress,
    create_progress_display,
    create_search_result,
    create_skeleton_events,
    create_skeleton_search_results,
    create_skeleton_summary,
    create_skeleton_timeline,
    create_skeleton_transcript,
    create_summary_display,
    create_timeline,
    create_toast,
    create_toast_container,
    create_transcript_display,
    format_timestamp_display,
    get_confidence_color,
    highlight_text,
    truncate_text,
)
from vl_jepa.ui.export import (
    ExportFormat,
    export_json,
    export_markdown,
    export_srt,
    export_summary,
    format_timestamp,
    format_timestamp_srt,
)

# Processing
from vl_jepa.ui.processing import (
    ProcessingPipeline,
    ProcessingProgress,
    ProcessingResult,
    ProcessingStage,
)

# State
from vl_jepa.ui.state import (
    StateManager,
    UIState,
)

# Styles
from vl_jepa.ui.styles import (
    CUSTOM_CSS,
    DARK_THEME,
    LIGHT_THEME,
    get_css,
    get_theme_colors,
)

__all__ = [
    # Export
    "ExportFormat",
    "export_markdown",
    "export_json",
    "export_srt",
    "export_summary",
    "format_timestamp",
    "format_timestamp_srt",
    # Components
    "TimelineEvent",
    "SearchResultDisplay",
    "TranscriptChunkDisplay",
    "create_timeline",
    "create_event_card",
    "create_search_result",
    "create_transcript_display",
    "create_summary_display",
    "create_progress_display",
    "format_timestamp_display",
    "get_confidence_color",
    "truncate_text",
    "highlight_text",
    # Level B Components
    "PROCESSING_STAGES",
    "create_skeleton_timeline",
    "create_skeleton_summary",
    "create_skeleton_events",
    "create_skeleton_transcript",
    "create_skeleton_search_results",
    "create_multi_stage_progress",
    "create_toast",
    "create_toast_container",
    # Styles
    "LIGHT_THEME",
    "DARK_THEME",
    "CUSTOM_CSS",
    "get_css",
    "get_theme_colors",
    # State
    "UIState",
    "StateManager",
    # Processing
    "ProcessingStage",
    "ProcessingProgress",
    "ProcessingResult",
    "ProcessingPipeline",
    # App (lazy loaded - requires gradio)
    "create_app",
    "launch",
]


def __getattr__(name: str):
    """Lazy loading for gradio-dependent modules."""
    if name in ("create_app", "launch"):
        from vl_jepa.ui.app import create_app, launch

        if name == "create_app":
            return create_app
        return launch
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
