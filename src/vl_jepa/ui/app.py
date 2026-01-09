"""
Main Gradio application for Lecture Mind.

IMPLEMENTS: S013 - Gradio Web Interface
IMPLEMENTS: v0.3.0 G1 - Gradio Web UI

Premium SaaS-style interface for:
- Video upload and processing
- Real-time progress tracking
- Multimodal search (visual + transcript)
- Event timeline visualization
- Export to Markdown/JSON/SRT
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import gradio as gr

from vl_jepa.ui.components import (
    SearchResultDisplay,
    TimelineEvent,
    TranscriptChunkDisplay,
    create_event_card,
    create_search_result,
    create_summary_display,
    create_timeline,
    create_transcript_display,
    format_timestamp_display,
)
from vl_jepa.ui.export import (
    export_json,
    export_markdown,
    export_srt,
)
from vl_jepa.ui.processing import (
    ProcessingPipeline,
    ProcessingProgress,
    ProcessingResult,
)
from vl_jepa.ui.styles import CUSTOM_CSS

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def create_app(
    use_placeholders: bool = True,
    share: bool = False,
) -> gr.Blocks:
    """
    Create the Lecture Mind Gradio application.

    IMPLEMENTS: S013.A1 - Main Application

    Args:
        use_placeholders: Use placeholder encoders (for testing).
        share: Create a public share link.

    Returns:
        Configured gr.Blocks application.
    """
    # Level C: Enhanced accessibility and interaction JavaScript
    keyboard_shortcuts_js = """
    <!-- Skip link for keyboard users -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <!-- Live region for screen reader announcements -->
    <div id="sr-announcements" aria-live="polite" aria-atomic="true" class="sr-only"></div>

    <script>
    // =====================================================================
    // LEVEL C: ACCESSIBILITY & INTERACTION ENHANCEMENTS
    // =====================================================================

    // Screen reader announcement helper
    function announce(message, priority = 'polite') {
        const announcer = document.getElementById('sr-announcements');
        if (announcer) {
            announcer.setAttribute('aria-live', priority);
            announcer.textContent = '';
            setTimeout(() => { announcer.textContent = message; }, 100);
        }
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // "/" to focus search (when not in input)
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            e.preventDefault();
            const searchInput = document.querySelector('input[placeholder*="gradient"]');
            if (searchInput) {
                searchInput.focus();
                announce('Search field focused');
            }
        }

        // "Escape" to blur active element
        if (e.key === 'Escape') {
            document.activeElement?.blur();
            announce('Focus cleared');
        }

        // "?" to show keyboard shortcuts help
        if (e.key === '?' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            announce('Keyboard shortcuts: Press slash to search, Escape to clear focus, Arrow keys to navigate tabs');
        }
    });

    // Tab navigation with arrow keys (ARIA best practice)
    document.addEventListener('keydown', function(e) {
        const tab = e.target.closest('[role="tab"]');
        if (!tab) return;

        const tablist = tab.closest('[role="tablist"]');
        if (!tablist) return;

        const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
        const currentIndex = tabs.indexOf(tab);

        let newIndex = -1;

        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            newIndex = (currentIndex + 1) % tabs.length;
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        } else if (e.key === 'Home') {
            e.preventDefault();
            newIndex = 0;
        } else if (e.key === 'End') {
            e.preventDefault();
            newIndex = tabs.length - 1;
        }

        if (newIndex >= 0) {
            tabs[newIndex].focus();
            tabs[newIndex].click();
            announce(tabs[newIndex].textContent + ' tab selected');
        }
    });

    // Auto-scroll to results after processing
    window.addEventListener('gradio:render', function() {
        const progress = document.querySelector('.progress-message');
        if (progress && progress.textContent.includes('✅')) {
            const summary = document.querySelector('[id*="summary"]');
            if (summary) {
                summary.scrollIntoView({ behavior: 'smooth' });
                announce('Processing complete. Results are ready.');
            }
        }
    });

    // Toast auto-dismiss functionality
    function setupToasts() {
        document.querySelectorAll('.toast[data-duration]').forEach(toast => {
            const duration = parseInt(toast.dataset.duration);
            if (duration > 0) {
                setTimeout(() => {
                    toast.style.animation = 'toastSlideOut 0.3s ease forwards';
                    setTimeout(() => toast.remove(), 300);
                }, duration);
            }
        });
    }

    // Observe for new toasts
    const toastObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.classList && node.classList.contains('toast')) {
                    setupToasts();
                }
            });
        });
    });

    const toastContainer = document.getElementById('toast-container');
    if (toastContainer) {
        toastObserver.observe(toastContainer, { childList: true });
    }

    // Reduced motion check
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReducedMotion.matches) {
        document.documentElement.classList.add('reduced-motion');
    }

    // Focus management for modals/dialogs
    function trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        element.addEventListener('keydown', function(e) {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        });
    }

    // Add main content ID for skip link
    document.addEventListener('DOMContentLoaded', function() {
        const mainContent = document.querySelector('.gradio-container > .main');
        if (mainContent) {
            mainContent.id = 'main-content';
            mainContent.setAttribute('tabindex', '-1');
        }
    });

    // Button click feedback (visual ripple respects reduced motion)
    document.addEventListener('click', function(e) {
        const button = e.target.closest('button, .btn-primary, .btn-secondary');
        if (!button || prefersReducedMotion.matches) return;

        button.classList.add('clicked');
        setTimeout(() => button.classList.remove('clicked'), 400);
    });
    </script>

    <style>
    /* Toast slide out animation */
    @keyframes toastSlideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }

    /* Button click state */
    button.clicked, .btn-primary.clicked, .btn-secondary.clicked {
        transform: scale(0.97);
    }
    </style>
    """

    # Build the interface
    with gr.Blocks(
        title="Lecture Mind - AI Lecture Summarizer",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="slate",
            neutral_hue="slate",
        ),
        css=CUSTOM_CSS,
        head=keyboard_shortcuts_js,
        fill_height=True,
    ) as app:
        # State variables (for Gradio - per-session isolation)
        processing_result_state = gr.State(value=None)
        dark_mode_state = gr.State(value=False)
        temp_files_state = gr.State(value=[])  # Track temp files for cleanup

        # =====================================================================
        # HEADER
        # =====================================================================
        with gr.Row(elem_classes=["app-header"]):
            with gr.Column(scale=8):
                gr.Markdown(
                    "# Lecture Mind",
                    elem_classes=["app-title"],
                )
                gr.Markdown(
                    "AI-powered lecture analysis with visual and transcript search",
                    elem_classes=["app-subtitle"],
                )
            with gr.Column(scale=2):
                dark_mode_btn = gr.Button(
                    value="🌙 Dark Mode",
                    size="sm",
                    elem_classes=["theme-toggle"],
                )

        # =====================================================================
        # MAIN CONTENT (Split Pane: 60/40)
        # =====================================================================
        with gr.Row():
            # -----------------------------------------------------------------
            # LEFT PANEL: Video + Timeline (60%)
            # -----------------------------------------------------------------
            with gr.Column(scale=6, elem_classes=["video-panel"]):
                video_input = gr.Video(
                    label="Upload Lecture Video",
                    sources=["upload"],
                    elem_classes=["video-upload-zone"],
                )

                # Timeline (shown after processing)
                timeline_html = gr.HTML(
                    value="<div class='timeline-placeholder'>Upload a video to see the event timeline</div>",
                    label="Event Timeline",
                )

                # Process button
                with gr.Row():
                    process_btn = gr.Button(
                        "🎬 Analyze Lecture",
                        variant="primary",
                        size="lg",
                        elem_classes=["btn-primary"],
                    )
                    clear_btn = gr.Button(
                        "Clear",
                        variant="secondary",
                        size="lg",
                        elem_classes=["btn-secondary"],
                    )

                # Progress display
                status_text = gr.Markdown(
                    value="Ready to analyze",
                    elem_classes=["progress-message"],
                )

            # -----------------------------------------------------------------
            # RIGHT PANEL: Results Tabs (40%)
            # -----------------------------------------------------------------
            with gr.Column(scale=4, elem_classes=["results-panel"]):
                with gr.Tabs():
                    # Summary Tab
                    with gr.Tab("Summary", id="summary"):
                        summary_html = gr.HTML(
                            value="<div class='summary-placeholder'>Process a video to see the summary</div>",
                        )

                    # Search Tab
                    with gr.Tab("Search", id="search"):
                        search_input = gr.Textbox(
                            label="Search transcript and visual content",
                            placeholder="What is gradient descent?",
                            lines=1,
                        )
                        with gr.Row():
                            search_btn = gr.Button("🔍 Search", variant="primary")
                            search_k = gr.Slider(
                                minimum=1,
                                maximum=20,
                                value=5,
                                step=1,
                                label="Results",
                            )
                        search_results_html = gr.HTML(
                            value="<div class='search-placeholder'>Enter a query to search</div>",
                        )

                    # Events Tab
                    with gr.Tab("Events", id="events"):
                        events_html = gr.HTML(
                            value="<div class='events-placeholder'>Process a video to see detected events</div>",
                        )

                    # Transcript Tab
                    with gr.Tab("Transcript", id="transcript"):
                        transcript_html = gr.HTML(
                            value="<div class='transcript-placeholder'>Process a video to see the transcript</div>",
                        )

                    # Export Tab
                    with gr.Tab("Export", id="export"):
                        gr.Markdown("### Export Options")
                        with gr.Row():
                            export_format = gr.Radio(
                                choices=["Markdown", "JSON", "SRT (Subtitles)"],
                                value="Markdown",
                                label="Format",
                            )
                        export_btn = gr.Button(
                            "📥 Download",
                            variant="primary",
                            elem_classes=["btn-primary"],
                        )
                        export_file = gr.File(
                            label="Download",
                            visible=False,
                        )

        # =====================================================================
        # EVENT HANDLERS
        # =====================================================================

        def process_video(
            video_file: str | None,
            progress: gr.Progress = gr.Progress(track_tqdm=True),  # noqa: B008
        ) -> tuple[str, str, str, str, str, Any]:
            """Process uploaded video and return results for all tabs."""
            if video_file is None:
                return (
                    "<div class='timeline-placeholder'>Upload a video first</div>",
                    "<div class='summary-placeholder'>No video uploaded</div>",
                    "<div class='events-placeholder'>No video uploaded</div>",
                    "<div class='transcript-placeholder'>No video uploaded</div>",
                    "Please upload a video",
                    None,
                )

            video_path = Path(video_file)

            # Progress callback
            def on_progress(p: ProcessingProgress) -> None:
                progress(p.progress, desc=p.message)

            # Create pipeline with callback
            proc_pipeline = ProcessingPipeline(
                use_placeholders=use_placeholders,
                progress_callback=on_progress,
            )

            # Process
            result = proc_pipeline.process_video(video_path)

            if result.has_error:
                error_msg = f"Error: {result.error}"
                return (
                    "<div class='timeline-placeholder'>Processing failed</div>",
                    f"<div class='summary-error'>{error_msg}</div>",
                    "<div class='events-placeholder'>Processing failed</div>",
                    "<div class='transcript-placeholder'>Processing failed</div>",
                    error_msg,
                    None,
                )

            # Build Timeline
            timeline_events = [
                TimelineEvent(
                    timestamp=e.timestamp,
                    confidence=e.confidence,
                    summary=f"Event at {format_timestamp_display(e.timestamp)}",
                )
                for e in result.events
            ]
            timeline = create_timeline(timeline_events, result.duration)

            # Build Summary
            summary = create_summary_display(
                video_name=video_path.name,
                duration=result.duration,
                event_count=len(result.events),
                transcript_length=len(result.transcript_chunks),
                processing_time=result.processing_time,
            )

            # Build Events
            if result.events:
                events_cards = "\n".join(
                    [
                        create_event_card(
                            TimelineEvent(
                                timestamp=e.timestamp,
                                confidence=e.confidence,
                                summary=f"Event at {format_timestamp_display(e.timestamp)}",
                            )
                        )
                        for e in result.events
                    ]
                )
                events = f"<div class='events-list'>{events_cards}</div>"
            else:
                events = "<div class='events-empty'>No events detected</div>"

            # Build Transcript
            if result.transcript_chunks:
                transcript_chunks_display = [
                    TranscriptChunkDisplay(
                        text=c.text,
                        start=c.start,
                        end=c.end,
                    )
                    for c in result.transcript_chunks
                ]
                transcript = create_transcript_display(transcript_chunks_display)
            else:
                transcript = (
                    "<div class='transcript-empty'>No transcript available</div>"
                )

            status = f"✅ Processed in {result.processing_time:.1f}s"

            return (timeline, summary, events, transcript, status, result)

        def search_content(
            query: str,
            k: int,
            result: ProcessingResult | None,
        ) -> str:
            """Search multimodal index."""
            if not query.strip():
                return "<div class='search-placeholder'>Enter a search query</div>"

            if result is None or result.multimodal_index is None:
                return "<div class='search-placeholder'>Process a video first</div>"

            try:
                # Encode query
                from vl_jepa.encoders.placeholder import PlaceholderTextEncoder

                text_encoder = PlaceholderTextEncoder(seed=42)
                query_embedding = text_encoder.encode(query)

                # Search
                search_results = result.multimodal_index.search(
                    query_embedding,
                    k=int(k),
                )

                if not search_results:
                    return "<div class='search-empty'>No results found</div>"

                # Build results HTML
                results_html = ""
                for r in search_results:
                    display = SearchResultDisplay(
                        id=r.id,
                        score=r.score,
                        timestamp=r.timestamp if hasattr(r, "timestamp") else 0.0,
                        modality=r.modality.value
                        if hasattr(r, "modality")
                        else "visual",
                        text=r.text if hasattr(r, "text") else None,
                        frame_index=r.frame_index
                        if hasattr(r, "frame_index")
                        else None,
                    )
                    results_html += create_search_result(display, query)

                return f"<div class='search-results-list'>{results_html}</div>"

            except Exception:
                logger.exception("Search failed")
                return "<div class='search-error'>Search failed. Please try again.</div>"

        def export_results(
            format_choice: str,
            result: ProcessingResult | None,
            temp_files: list[str],
        ) -> tuple[str | None, list[str]]:
            """Export results to file.

            Returns:
                Tuple of (file_path, updated_temp_files_list).
            """
            if result is None:
                return None, temp_files

            # Create export data structure
            from dataclasses import dataclass

            @dataclass
            class ExportData:
                metadata: Any
                events: list
                transcript_chunks: list
                processing_time: float
                frame_count: int

            export_data = ExportData(
                metadata=result.metadata,
                events=result.events,
                transcript_chunks=result.transcript_chunks,
                processing_time=result.processing_time,
                frame_count=result.frame_count,
            )

            try:
                if format_choice == "Markdown":
                    content = export_markdown(export_data)
                    filename = "lecture_summary.md"
                elif format_choice == "JSON":
                    content = export_json(export_data)
                    filename = "lecture_data.json"
                else:  # SRT
                    content = export_srt(export_data)
                    filename = "lecture_subtitles.srt"

                # Save to temp file
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=f".{filename.split('.')[-1]}",
                    delete=False,
                    encoding="utf-8",
                ) as f:
                    f.write(content)
                    temp_path = f.name

                # Track temp file for later cleanup
                updated_temp_files = temp_files + [temp_path]
                return temp_path, updated_temp_files

            except Exception:
                logger.exception("Export failed")
                return None, temp_files

        def toggle_dark_mode(current: bool) -> tuple[bool, str]:
            """Toggle dark mode."""
            new_mode = not current
            btn_text = "☀️ Light Mode" if new_mode else "🌙 Dark Mode"
            return new_mode, btn_text

        def clear_all(
            temp_files: list[str],
        ) -> tuple[None, str, str, str, str, str, None, list[str]]:
            """Clear all state and clean up temp files."""
            import os

            # Clean up tracked temp files
            for temp_path in temp_files:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        logger.debug(f"Cleaned up temp file: {temp_path}")
                except OSError as e:
                    logger.warning(f"Failed to clean up temp file {temp_path}: {e}")

            return (
                None,  # video
                "<div class='timeline-placeholder'>Upload a video to see the event timeline</div>",
                "<div class='summary-placeholder'>Process a video to see the summary</div>",
                "<div class='events-placeholder'>Process a video to see detected events</div>",
                "<div class='transcript-placeholder'>Process a video to see the transcript</div>",
                "Ready to analyze",
                None,  # result state
                [],  # cleared temp files list
            )

        # -----------------------------------------------------------------
        # Wire up events
        # -----------------------------------------------------------------

        # Process button
        process_btn.click(
            fn=process_video,
            inputs=[video_input],
            outputs=[
                timeline_html,
                summary_html,
                events_html,
                transcript_html,
                status_text,
                processing_result_state,
            ],
            show_progress="full",
        )

        # Search button
        search_btn.click(
            fn=search_content,
            inputs=[search_input, search_k, processing_result_state],
            outputs=[search_results_html],
        )

        # Search on enter
        search_input.submit(
            fn=search_content,
            inputs=[search_input, search_k, processing_result_state],
            outputs=[search_results_html],
        )

        # Export button (with temp file tracking)
        export_btn.click(
            fn=export_results,
            inputs=[export_format, processing_result_state, temp_files_state],
            outputs=[export_file, temp_files_state],
        )

        # Dark mode toggle with JavaScript to apply CSS class
        dark_mode_js = """
        () => {
            document.body.classList.toggle('dark');
            document.documentElement.classList.toggle('dark');
            const container = document.querySelector('.gradio-container');
            if (container) container.classList.toggle('dark');
        }
        """
        dark_mode_btn.click(
            fn=toggle_dark_mode,
            inputs=[dark_mode_state],
            outputs=[dark_mode_state, dark_mode_btn],
            js=dark_mode_js,
        )

        # Clear button (with temp file cleanup)
        clear_btn.click(
            fn=clear_all,
            inputs=[temp_files_state],
            outputs=[
                video_input,
                timeline_html,
                summary_html,
                events_html,
                transcript_html,
                status_text,
                processing_result_state,
                temp_files_state,
            ],
        )

    return app


def launch(
    share: bool = False,
    server_port: int = 7860,
    server_name: str = "127.0.0.1",
    use_placeholders: bool = True,
) -> None:
    """
    Launch the Lecture Mind application.

    Args:
        share: Create a public share link.
        server_port: Port to run the server on.
        server_name: Server host to bind to (use 0.0.0.0 for Docker).
        use_placeholders: Use placeholder encoders.
    """
    app = create_app(use_placeholders=use_placeholders, share=share)
    app.launch(
        share=share,
        server_port=server_port,
        server_name=server_name,
        show_error=True,
    )


# Entry point for direct execution
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Lecture Mind - AI Lecture Summarizer")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"),
        help="Server host (use 0.0.0.0 for Docker)",
    )
    parser.add_argument(
        "--no-placeholders",
        action="store_true",
        help="Use real encoders instead of placeholders",
    )

    args = parser.parse_args()

    launch(
        share=args.share,
        server_port=args.port,
        server_name=args.host,
        use_placeholders=not args.no_placeholders,
    )
