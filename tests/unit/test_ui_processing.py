"""
Unit tests for UI processing pipeline.

SPEC: S013 - Gradio Web Interface
TEST_IDs: T013.P1-T013.P12

Tests for ProcessingPipeline with progress callbacks.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestProcessingProgress:
    """Tests for ProcessingProgress dataclass."""

    @pytest.mark.unit
    def test_processing_progress_creation(self):
        """
        SPEC: S013
        TEST_ID: T013.P1
        Given: Progress parameters
        When: ProcessingProgress is created
        Then: Has correct attributes
        """
        from vl_jepa.ui.processing import ProcessingProgress

        progress = ProcessingProgress(
            stage="encoding",
            progress=0.5,
            message="Encoding frames...",
            current_step=4,
            total_steps=8,
        )

        assert progress.stage == "encoding"
        assert progress.progress == 0.5
        assert progress.message == "Encoding frames..."
        assert progress.current_step == 4
        assert progress.total_steps == 8


class TestProcessingResult:
    """Tests for ProcessingResult dataclass."""

    @pytest.mark.unit
    def test_processing_result_success(self):
        """
        SPEC: S013
        TEST_ID: T013.P2
        Given: Successful processing data
        When: ProcessingResult is created
        Then: Error is None, has_error is False
        """
        from vl_jepa.ui.processing import ProcessingResult

        result = ProcessingResult(
            video_path=Path("test.mp4"),
            duration=300.0,
            frame_count=300,
            events=[],
            transcript_chunks=[],
            processing_time=15.0,
        )

        assert result.error is None
        assert result.has_error is False

    @pytest.mark.unit
    def test_processing_result_error(self):
        """
        SPEC: S013
        TEST_ID: T013.P3
        Given: Error message
        When: ProcessingResult is created with error
        Then: has_error is True
        """
        from vl_jepa.ui.processing import ProcessingResult

        result = ProcessingResult(
            video_path=Path("test.mp4"),
            duration=0.0,
            frame_count=0,
            events=[],
            transcript_chunks=[],
            processing_time=0.0,
            error="Video decode failed",
        )

        assert result.has_error is True
        assert "decode failed" in result.error


class TestProcessingStage:
    """Tests for ProcessingStage enum."""

    @pytest.mark.unit
    def test_processing_stage_values(self):
        """
        SPEC: S013
        TEST_ID: T013.P4
        Given: ProcessingStage enum
        When: Accessing values
        Then: Has all expected stages
        """
        from vl_jepa.ui.processing import ProcessingStage

        assert ProcessingStage.LOADING == "loading"
        assert ProcessingStage.AUDIO_EXTRACTION == "audio_extraction"
        assert ProcessingStage.TRANSCRIPTION == "transcription"
        assert ProcessingStage.FRAME_SAMPLING == "frame_sampling"
        assert ProcessingStage.VISUAL_ENCODING == "visual_encoding"
        assert ProcessingStage.TEXT_ENCODING == "text_encoding"
        assert ProcessingStage.EVENT_DETECTION == "event_detection"
        assert ProcessingStage.INDEX_BUILDING == "index_building"


class TestProcessingPipeline:
    """Tests for ProcessingPipeline."""

    @pytest.fixture
    def mock_video_path(self, tmp_path: Path) -> Path:
        """Create a mock video path."""
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        return video_path

    @pytest.fixture
    def mock_pipeline(self):
        """Create pipeline with mock encoders."""
        from vl_jepa.ui.processing import ProcessingPipeline

        return ProcessingPipeline(use_placeholders=True)

    @pytest.mark.unit
    def test_pipeline_creation_with_placeholders(self):
        """
        SPEC: S013
        TEST_ID: T013.P5
        Given: use_placeholders=True
        When: ProcessingPipeline is created
        Then: Uses placeholder encoders
        """
        from vl_jepa.ui.processing import ProcessingPipeline

        pipeline = ProcessingPipeline(use_placeholders=True)

        assert pipeline._visual_encoder is not None
        assert pipeline._text_encoder is not None

    @pytest.mark.unit
    def test_pipeline_progress_callback_registered(self):
        """
        SPEC: S013
        TEST_ID: T013.P6
        Given: Progress callback
        When: ProcessingPipeline is created
        Then: Callback is stored
        """
        from vl_jepa.ui.processing import ProcessingPipeline

        callback = MagicMock()
        pipeline = ProcessingPipeline(
            use_placeholders=True,
            progress_callback=callback,
        )

        assert pipeline._progress_callback is callback

    @pytest.mark.unit
    def test_pipeline_emits_progress_for_all_stages(self, mock_video_path: Path):
        """
        SPEC: S013
        TEST_ID: T013.P7
        Given: Pipeline with callback
        When: process_video() is called
        Then: Callback receives updates for each stage
        """
        from vl_jepa.ui.processing import ProcessingPipeline, ProcessingStage

        callback = MagicMock()
        pipeline = ProcessingPipeline(
            use_placeholders=True,
            progress_callback=callback,
        )

        # Mock video processing internals
        with patch.object(pipeline, "_load_video") as mock_load:
            mock_load.return_value = MagicMock(
                duration=60.0,
                fps=30.0,
                frame_count=1800,
                width=1920,
                height=1080,
                codec="h264",
                path=str(mock_video_path),
            )
            with patch.object(pipeline, "_extract_audio") as mock_audio:
                mock_audio.return_value = None  # No audio
                with patch.object(pipeline, "_sample_frames") as mock_frames:
                    mock_frames.return_value = []
                    with patch.object(pipeline, "_encode_frames") as mock_encode:
                        mock_encode.return_value = ([], [])
                        with patch.object(pipeline, "_detect_events") as mock_events:
                            mock_events.return_value = []
                            with patch.object(
                                pipeline, "_build_index"
                            ) as mock_index:
                                mock_index.return_value = MagicMock()

                                pipeline.process_video(mock_video_path)

        # Verify callback was called multiple times
        assert callback.call_count >= 1

    @pytest.mark.unit
    def test_pipeline_handles_video_not_found(self, tmp_path: Path):
        """
        SPEC: S013
        TEST_ID: T013.P8
        EDGE_CASE: EC_UI_P1
        Given: Non-existent video path
        When: process_video() is called
        Then: Returns result with error
        """
        from vl_jepa.ui.processing import ProcessingPipeline

        pipeline = ProcessingPipeline(use_placeholders=True)
        non_existent = tmp_path / "does_not_exist.mp4"

        result = pipeline.process_video(non_existent)

        assert result.has_error is True
        assert "not found" in result.error.lower() or "not exist" in result.error.lower()

    @pytest.mark.unit
    def test_pipeline_handles_audio_failure_gracefully(self, mock_video_path: Path):
        """
        SPEC: S013
        TEST_ID: T013.P9
        EDGE_CASE: EC_UI_P2
        Given: Video with no audio
        When: process_video() is called
        Then: Continues without transcript
        """
        from vl_jepa.ui.processing import ProcessingPipeline

        pipeline = ProcessingPipeline(use_placeholders=True)

        # Mock to simulate audio extraction failure
        with patch.object(pipeline, "_load_video") as mock_load:
            mock_load.return_value = MagicMock(
                duration=60.0,
                fps=30.0,
                frame_count=1800,
                width=1920,
                height=1080,
                codec="h264",
                path=str(mock_video_path),
            )
            with patch.object(pipeline, "_extract_audio") as mock_audio:
                mock_audio.side_effect = Exception("No audio stream")
                with patch.object(pipeline, "_sample_frames") as mock_frames:
                    mock_frames.return_value = [
                        (np.random.randn(224, 224, 3).astype(np.float32), 0.0)
                    ]
                    with patch.object(pipeline, "_encode_frames") as mock_encode:
                        mock_encode.return_value = (
                            [np.random.randn(768).astype(np.float32)],
                            [0.0],
                        )
                        with patch.object(pipeline, "_detect_events") as mock_events:
                            mock_events.return_value = []
                            with patch.object(
                                pipeline, "_build_index"
                            ) as mock_index:
                                mock_index.return_value = MagicMock()

                                result = pipeline.process_video(mock_video_path)

        # Should succeed despite audio failure
        assert result.has_error is False
        assert len(result.transcript_chunks) == 0

    @pytest.mark.unit
    def test_calculate_progress(self):
        """
        SPEC: S013
        TEST_ID: T013.P10
        Given: Stage and substep info
        When: _calculate_progress() is called
        Then: Returns correct progress value
        """
        from vl_jepa.ui.processing import ProcessingPipeline, ProcessingStage

        pipeline = ProcessingPipeline(use_placeholders=True)

        # Stage 1 of 8 at 50% = (0 + 0.5) / 8 = 0.0625
        progress = pipeline._calculate_progress(
            ProcessingStage.LOADING,
            substep=0.5,
        )
        assert 0.0 <= progress <= 1.0

        # Last stage at 100% should be close to 1.0
        progress = pipeline._calculate_progress(
            ProcessingStage.INDEX_BUILDING,
            substep=1.0,
        )
        assert progress > 0.9


class TestUIState:
    """Tests for UIState dataclass."""

    @pytest.mark.unit
    def test_ui_state_default_values(self):
        """
        SPEC: S013
        TEST_ID: T013.P11
        Given: UIState with no arguments
        When: Created
        Then: Has sensible defaults
        """
        from vl_jepa.ui.state import UIState

        state = UIState()

        assert state.video_path is None
        assert state.processing_result is None
        assert state.is_processing is False
        assert state.current_query == ""
        assert state.search_results == []
        assert state.error_message is None
        assert state.dark_mode is False


class TestStateManager:
    """Tests for StateManager."""

    @pytest.mark.unit
    def test_state_manager_reset(self):
        """
        SPEC: S013
        TEST_ID: T013.P12
        Given: StateManager with state
        When: reset() is called
        Then: State is cleared
        """
        from vl_jepa.ui.state import StateManager, UIState

        manager = StateManager()
        manager.state.video_path = Path("test.mp4")
        manager.state.is_processing = True

        manager.reset()

        assert manager.state.video_path is None
        assert manager.state.is_processing is False

    @pytest.mark.unit
    def test_state_manager_set_processing(self):
        """
        SPEC: S013
        TEST_ID: T013.P13
        Given: StateManager
        When: set_processing() is called
        Then: is_processing flag is updated
        """
        from vl_jepa.ui.state import StateManager

        manager = StateManager()

        manager.set_processing(True)
        assert manager.state.is_processing is True

        manager.set_processing(False)
        assert manager.state.is_processing is False

    @pytest.mark.unit
    def test_state_manager_toggle_dark_mode(self):
        """
        SPEC: S013
        TEST_ID: T013.P14
        Given: StateManager
        When: toggle_dark_mode() is called
        Then: dark_mode is toggled
        """
        from vl_jepa.ui.state import StateManager

        manager = StateManager()
        assert manager.state.dark_mode is False

        manager.toggle_dark_mode()
        assert manager.state.dark_mode is True

        manager.toggle_dark_mode()
        assert manager.state.dark_mode is False
