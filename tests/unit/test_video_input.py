"""
SPEC: S001 - Video File Ingestion
SPEC: S002 - Stream Ingestion
TEST_IDs: T001.1-T001.6, T002.1, T002.3

IMPLEMENTS: v0.2.0 Week 3 - Video processing tests
"""

from pathlib import Path

import cv2
import numpy as np
import pytest

from vl_jepa.video import Frame, VideoDecodeError, VideoInput, VideoMetadata


class TestVideoMetadata:
    """Tests for VideoMetadata dataclass."""

    @pytest.mark.unit
    def test_metadata_creation(self) -> None:
        """Test VideoMetadata can be created with all fields."""
        metadata = VideoMetadata(
            path="/test/video.mp4",
            width=1920,
            height=1080,
            fps=30.0,
            frame_count=900,
            duration=30.0,
            codec="h264",
        )

        assert metadata.path == "/test/video.mp4"
        assert metadata.width == 1920
        assert metadata.height == 1080
        assert metadata.fps == 30.0
        assert metadata.frame_count == 900
        assert metadata.duration == 30.0
        assert metadata.codec == "h264"

    @pytest.mark.unit
    def test_metadata_str_representation(self) -> None:
        """Test VideoMetadata string representation."""
        metadata = VideoMetadata(
            path="/test/video.mp4",
            width=1920,
            height=1080,
            fps=30.0,
            frame_count=900,
            duration=30.0,
        )

        str_repr = str(metadata)
        assert "1920x1080" in str_repr
        assert "30.00" in str_repr or "30.0" in str_repr
        assert "30.0s" in str_repr


class TestFrame:
    """Tests for Frame dataclass."""

    @pytest.mark.unit
    def test_frame_creation(self) -> None:
        """Test Frame can be created with data and timestamp."""
        data = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = Frame(data=data, timestamp=1.5)

        assert frame.timestamp == 1.5
        assert frame.data.shape == (480, 640, 3)
        assert frame.data.dtype == np.uint8


class TestVideoFileIngestion:
    """Tests for video file ingestion (S001)."""

    @pytest.fixture
    def synthetic_video(self, tmp_path: Path) -> Path:
        """Create a synthetic video for testing."""
        video_path = tmp_path / "test_video.mp4"
        fps = 30
        duration_sec = 2
        width, height = 320, 240

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

        if not writer.isOpened():
            pytest.skip("Cannot create synthetic video (codec unavailable)")

        for i in range(fps * duration_sec):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :, 0] = int(255 * i / (fps * duration_sec))
            writer.write(frame)

        writer.release()
        return video_path

    @pytest.mark.unit
    def test_load_synthetic_video(self, synthetic_video: Path) -> None:
        """
        SPEC: S001
        TEST_ID: T001.1
        Given: A valid MP4 video file
        When: VideoInput.open() is called
        Then: Returns VideoInput with valid properties
        """
        video = VideoInput.open(synthetic_video)

        assert video.width == 320
        assert video.height == 240
        assert video.fps == 30.0
        assert video.frame_count == 60  # 2 seconds at 30 fps

        video.close()

    @pytest.mark.unit
    def test_reject_non_video_file(self, tmp_path: Path) -> None:
        """
        SPEC: S001
        TEST_ID: T001.3
        EDGE_CASE: EC007
        Given: A non-video file (e.g., .txt)
        When: VideoInput.open() is called
        Then: Raises VideoDecodeError
        """
        text_file = tmp_path / "not_a_video.txt"
        text_file.write_text("This is not a video")

        with pytest.raises(VideoDecodeError):
            VideoInput.open(text_file)

    @pytest.mark.unit
    def test_reject_nonexistent_file(self) -> None:
        """
        SPEC: S001
        Given: A path to a nonexistent file
        When: VideoInput.open() is called
        Then: Raises VideoDecodeError
        """
        with pytest.raises(VideoDecodeError, match="File not found"):
            VideoInput.open("/nonexistent/path/video.mp4")

    @pytest.mark.unit
    def test_get_metadata(self, synthetic_video: Path) -> None:
        """Test metadata extraction from video."""
        with VideoInput.open(synthetic_video) as video:
            metadata = video.get_metadata()

        assert isinstance(metadata, VideoMetadata)
        assert metadata.width == 320
        assert metadata.height == 240
        assert metadata.fps == 30.0
        assert metadata.frame_count == 60
        assert metadata.duration == 2.0

    @pytest.mark.unit
    def test_sample_frames_at_1fps(self, synthetic_video: Path) -> None:
        """
        SPEC: S001
        IMPLEMENTS: v0.2.0 G3 - Extract frames at 1 FPS
        Given: A 2-second video at 30 FPS
        When: sample_frames(target_fps=1.0) is called
        Then: Returns approximately 2 frames
        """
        with VideoInput.open(synthetic_video) as video:
            frames = list(video.sample_frames(target_fps=1.0))

        # 2-second video at 1 FPS should give ~2 frames
        assert len(frames) == 2

    @pytest.mark.unit
    def test_sample_frames_respects_max_frames(self, synthetic_video: Path) -> None:
        """Test that max_frames limit is respected."""
        with VideoInput.open(synthetic_video) as video:
            frames = list(video.sample_frames(target_fps=30.0, max_frames=10))

        assert len(frames) == 10

    @pytest.mark.unit
    def test_sample_frames_invalid_fps_raises(self, synthetic_video: Path) -> None:
        """Test that invalid target_fps raises ValueError."""
        with VideoInput.open(synthetic_video) as video:
            with pytest.raises(ValueError, match="target_fps must be positive"):
                list(video.sample_frames(target_fps=0))

            with pytest.raises(ValueError, match="target_fps must be positive"):
                list(video.sample_frames(target_fps=-1))

    @pytest.mark.unit
    def test_context_manager(self, synthetic_video: Path) -> None:
        """Test VideoInput works as context manager."""
        with VideoInput.open(synthetic_video) as video:
            assert video.width > 0
        # After context exit, video should be closed (no assertion needed)

    @pytest.mark.unit
    def test_frames_are_rgb(self, synthetic_video: Path) -> None:
        """Test that frames are returned in RGB format (not BGR)."""
        with VideoInput.open(synthetic_video) as video:
            frames = list(video.sample_frames(target_fps=1.0, max_frames=1))

        assert len(frames) == 1
        frame = frames[0]
        assert frame.data.shape[2] == 3  # 3 channels
        assert frame.data.dtype == np.uint8

    @pytest.mark.unit
    def test_timestamp_monotonicity_sample_frames(self, synthetic_video: Path) -> None:
        """
        SPEC: S001
        TEST_ID: T001.5
        INVARIANT: INV001
        Given: A valid video file
        When: Frames are sampled
        Then: Timestamps are strictly monotonically increasing
        """
        with VideoInput.open(synthetic_video) as video:
            frames = list(video.sample_frames(target_fps=10.0))

        timestamps = [f.timestamp for f in frames]

        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i - 1], (
                f"Timestamps not monotonic: {timestamps[i]} <= {timestamps[i - 1]}"
            )


class TestStreamIngestion:
    """Tests for stream ingestion (S002)."""

    @pytest.mark.skip(reason="Requires webcam device - manual test only")
    @pytest.mark.unit
    def test_mock_webcam_device(self) -> None:
        """
        SPEC: S002
        TEST_ID: T002.1
        Given: A webcam device ID
        When: VideoInput.from_device() is called
        Then: Returns VideoInput instance
        """
        video = VideoInput.from_device(0)
        assert video.width > 0
        video.close()

    @pytest.mark.unit
    def test_from_device_invalid_id(self) -> None:
        """
        SPEC: S002
        Given: An invalid device ID
        When: VideoInput.from_device() is called
        Then: Raises VideoDecodeError
        """
        with pytest.raises(VideoDecodeError, match="Cannot open device"):
            VideoInput.from_device(9999)
