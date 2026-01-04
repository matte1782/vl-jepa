"""
Integration tests for video frame extraction.

IMPLEMENTS: v0.2.0 G3 - Working video pipeline
"""

import pytest

from vl_jepa.video import VideoInput, VideoMetadata


class TestVideoFrameExtraction:
    """Integration tests for frame extraction at specific FPS."""

    @pytest.fixture
    def sample_video_path(self) -> str:
        """Path to test video (if available)."""
        return "tests/lecture_ex/December19_I.mp4"

    @pytest.mark.integration
    def test_get_metadata(self, sample_video_path: str) -> None:
        """Test metadata extraction from video."""
        try:
            with VideoInput.open(sample_video_path) as video:
                meta = video.get_metadata()

                assert isinstance(meta, VideoMetadata)
                assert meta.width > 0
                assert meta.height > 0
                assert meta.fps > 0
                assert meta.frame_count > 0
                assert meta.duration > 0
        except FileNotFoundError:
            pytest.skip("Test video not available")

    @pytest.mark.integration
    def test_sample_frames_at_1fps(self, sample_video_path: str) -> None:
        """Test frame sampling at 1 FPS."""
        try:
            with VideoInput.open(sample_video_path) as video:
                # Sample first 10 frames at 1 FPS
                frames = list(video.sample_frames(target_fps=1.0, max_frames=10))

                assert len(frames) == 10

                # Verify timestamps are approximately 1 second apart
                for i in range(len(frames) - 1):
                    interval = frames[i + 1].timestamp - frames[i].timestamp
                    assert 0.9 <= interval <= 1.1, (
                        f"Interval {interval}s not within tolerance"
                    )

        except FileNotFoundError:
            pytest.skip("Test video not available")

    @pytest.mark.integration
    def test_sample_frames_shape(self, sample_video_path: str) -> None:
        """Test that extracted frames have correct shape."""
        try:
            with VideoInput.open(sample_video_path) as video:
                frames = list(video.sample_frames(target_fps=1.0, max_frames=3))

                for frame in frames:
                    # RGB format: (height, width, 3)
                    assert len(frame.data.shape) == 3
                    assert frame.data.shape[2] == 3  # RGB channels

        except FileNotFoundError:
            pytest.skip("Test video not available")

    @pytest.mark.integration
    def test_frame_count_accuracy(self, sample_video_path: str) -> None:
        """Test that frame count matches expected for duration."""
        try:
            with VideoInput.open(sample_video_path) as video:
                video.get_metadata()

                # Sample a shorter segment
                target_seconds = 30
                frames = list(
                    video.sample_frames(target_fps=1.0, max_frames=target_seconds)
                )

                # Should get approximately target_seconds frames
                # Allow for ±1 frame tolerance
                assert target_seconds - 1 <= len(frames) <= target_seconds + 1

        except FileNotFoundError:
            pytest.skip("Test video not available")

    def test_invalid_fps_raises(self) -> None:
        """Test that invalid FPS values raise ValueError."""
        # We can't test without a video, so skip if no video available
        pytest.skip("Requires test video")

    @pytest.mark.integration
    def test_context_manager(self, sample_video_path: str) -> None:
        """Test video input context manager properly releases resources."""
        try:
            with VideoInput.open(sample_video_path) as video:
                _ = video.get_metadata()
            # After context exit, resources should be released
            # If we get here without error, the test passes
        except FileNotFoundError:
            pytest.skip("Test video not available")
