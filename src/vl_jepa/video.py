"""
SPEC: S001 - Video File Ingestion
SPEC: S002 - Stream Ingestion

Video input handling for files and live streams.

IMPLEMENTS: v0.2.0 G3 - Working video pipeline
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoDecodeError(Exception):
    """Raised when video decoding fails."""

    pass


@dataclass
class Frame:
    """A video frame with timestamp.

    INVARIANT: INV001 - Timestamps are strictly monotonically increasing.
    """

    data: np.ndarray
    timestamp: float  # seconds from video start


@dataclass
class VideoMetadata:
    """Video file metadata.

    IMPLEMENTS: v0.2.0 G3 - Video metadata extraction
    """

    path: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float  # seconds
    codec: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Human-readable summary."""
        return (
            f"Video: {self.path}\n"
            f"  Resolution: {self.width}x{self.height}\n"
            f"  FPS: {self.fps:.2f}\n"
            f"  Duration: {self.duration:.1f}s ({self.duration / 60:.1f} min)\n"
            f"  Frames: {self.frame_count}"
        )


class VideoInput:
    """Video input handler for files and streams.

    IMPLEMENTS: S001, S002
    INVARIANTS: INV001, INV002

    Example:
        video = VideoInput.open("lecture.mp4")
        for frame in video.frames():
            process(frame)
    """

    def __init__(
        self,
        capture: cv2.VideoCapture,
        source: str,
        buffer_size: int = 10,
    ) -> None:
        """Initialize video input.

        Args:
            capture: OpenCV video capture object
            source: Source identifier (path or device ID)
            buffer_size: Maximum frames to buffer (INV002: <= 10)
        """
        self._capture = capture
        self._source = source
        self._buffer_size = min(buffer_size, 10)  # INV002
        self._last_timestamp: float = -1.0

    @classmethod
    def open(cls, path: str | Path) -> VideoInput:
        """Open a video file.

        IMPLEMENTS: S001

        Args:
            path: Path to video file (MP4, WebM, etc.)

        Returns:
            VideoInput instance

        Raises:
            VideoDecodeError: If file cannot be opened or is not a video
        """
        path = Path(path)

        if not path.exists():
            raise VideoDecodeError(f"File not found: {path}")

        capture = cv2.VideoCapture(str(path))

        if not capture.isOpened():
            raise VideoDecodeError(f"Cannot decode video: {path}")

        # Verify it's actually a video by reading a frame
        ret, _ = capture.read()
        if not ret:
            capture.release()
            raise VideoDecodeError(f"Cannot read frames from: {path}")

        # Reset to beginning
        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        return cls(capture, str(path))

    @classmethod
    def from_device(cls, device_id: int = 0) -> VideoInput:
        """Open a camera/webcam device.

        IMPLEMENTS: S002

        Args:
            device_id: Camera device ID (default: 0)

        Returns:
            VideoInput instance

        Raises:
            VideoDecodeError: If device cannot be opened
        """
        capture = cv2.VideoCapture(device_id)

        if not capture.isOpened():
            raise VideoDecodeError(f"Cannot open device: {device_id}")

        return cls(capture, f"device:{device_id}")

    @property
    def fps(self) -> float:
        """Get video frame rate."""
        return float(self._capture.get(cv2.CAP_PROP_FPS))

    @property
    def frame_count(self) -> int:
        """Get total frame count (0 for live streams)."""
        return int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def width(self) -> int:
        """Get frame width."""
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        """Get frame height."""
        return int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def duration(self) -> float:
        """Get video duration in seconds."""
        if self.fps > 0:
            return self.frame_count / self.fps
        return 0.0

    @property
    def codec(self) -> str:
        """Get video codec fourcc code."""
        fourcc = int(self._capture.get(cv2.CAP_PROP_FOURCC))
        return "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    def get_metadata(self) -> VideoMetadata:
        """Get video metadata.

        IMPLEMENTS: v0.2.0 G3

        Returns:
            VideoMetadata object with all video properties
        """
        return VideoMetadata(
            path=self._source,
            width=self.width,
            height=self.height,
            fps=self.fps,
            frame_count=self.frame_count,
            duration=self.duration,
            codec=self.codec,
        )

    def frames(self) -> Iterator[Frame]:
        """Iterate over video frames.

        INVARIANT: INV001 - Timestamps strictly monotonically increasing.

        Yields:
            Frame objects with data and timestamp

        Note:
            Corrupted frames are skipped with a warning logged.
        """
        while True:
            ret, data = self._capture.read()

            if not ret:
                break

            # Get timestamp in seconds
            timestamp = self._capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            # INV001: Enforce monotonicity
            if timestamp <= self._last_timestamp:
                logger.warning(
                    f"Non-monotonic timestamp {timestamp} <= {self._last_timestamp}, "
                    "skipping frame"
                )
                continue

            self._last_timestamp = timestamp

            # Convert BGR to RGB
            data_rgb = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

            yield Frame(data=data_rgb, timestamp=timestamp)

    def sample_frames(
        self,
        target_fps: float = 1.0,
        max_frames: int | None = None,
    ) -> Iterator[Frame]:
        """Sample frames at a target frame rate.

        IMPLEMENTS: v0.2.0 G3 - Extract frames at 1 FPS

        Args:
            target_fps: Target frames per second (default: 1.0)
            max_frames: Maximum frames to extract (None = all)

        Yields:
            Frame objects sampled at target_fps

        Example:
            for frame in video.sample_frames(target_fps=1.0):
                # Process one frame per second
                embed = encoder.encode_single(frame.data)
        """
        if target_fps <= 0:
            raise ValueError(f"target_fps must be positive, got {target_fps}")

        video_fps = self.fps
        if video_fps <= 0:
            logger.warning("Unknown video FPS, sampling every frame")
            video_fps = target_fps

        # Calculate frame interval
        frame_interval = video_fps / target_fps
        next_frame_idx = 0.0
        current_frame_idx = 0
        frames_yielded = 0

        logger.info(
            "Sampling at %.2f FPS (interval: %.1f frames) from %.2f FPS video",
            target_fps,
            frame_interval,
            video_fps,
        )

        while True:
            ret, data = self._capture.read()

            if not ret:
                break

            # Check if this frame should be sampled
            if current_frame_idx >= next_frame_idx:
                timestamp = self._capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                # Convert BGR to RGB
                data_rgb = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

                yield Frame(data=data_rgb, timestamp=timestamp)

                frames_yielded += 1
                next_frame_idx += frame_interval

                if max_frames is not None and frames_yielded >= max_frames:
                    logger.info("Reached max_frames limit: %d", max_frames)
                    break

            current_frame_idx += 1

        logger.info(
            "Sampled %d frames from %d total (%.1f%% of video)",
            frames_yielded,
            current_frame_idx,
            (frames_yielded / max(current_frame_idx, 1)) * 100,
        )

    def close(self) -> None:
        """Release video capture resources."""
        self._capture.release()

    def __enter__(self) -> VideoInput:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()
