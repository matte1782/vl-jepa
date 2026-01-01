"""
SPEC: S001 - Video File Ingestion
SPEC: S002 - Stream Ingestion

Video input handling for files and live streams.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

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

    def close(self) -> None:
        """Release video capture resources."""
        self._capture.release()

    def __enter__(self) -> VideoInput:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()
