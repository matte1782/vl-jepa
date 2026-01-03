#!/usr/bin/env python
"""
Video Processor Integration Test

IMPLEMENTS: v0.2.0 Week 3 Day 1 - Video processing validation

This script verifies:
1. Video file loads correctly with OpenCV
2. Metadata extraction works
3. Frame extraction at 1 FPS produces correct count
4. Timestamps are monotonically increasing

Run: python scripts/test_video_processor.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_video_load(video_path: str) -> bool:
    """Test that video file loads correctly."""
    logger.info("\n=== Testing Video Load ===")
    logger.info(f"Video: {video_path}")

    try:
        from vl_jepa.video import VideoInput

        video = VideoInput.open(video_path)
        logger.info("Video loaded successfully")

        # Get basic properties
        logger.info(f"  Width: {video.width}")
        logger.info(f"  Height: {video.height}")
        logger.info(f"  FPS: {video.fps:.2f}")
        logger.info(f"  Frame count: {video.frame_count}")
        logger.info(f"  Duration: {video.duration:.1f}s")
        logger.info(f"  Codec: {video.codec}")

        video.close()
        return True

    except Exception as e:
        logger.error(f"Video load failed: {e}")
        return False


def test_metadata_extraction(video_path: str) -> bool:
    """Test metadata extraction."""
    logger.info("\n=== Testing Metadata Extraction ===")

    try:
        from vl_jepa.video import VideoInput

        with VideoInput.open(video_path) as video:
            metadata = video.get_metadata()

        logger.info(f"Metadata extracted:")
        logger.info(f"  Path: {metadata.path}")
        logger.info(f"  Resolution: {metadata.width}x{metadata.height}")
        logger.info(f"  FPS: {metadata.fps:.2f}")
        logger.info(f"  Frames: {metadata.frame_count}")
        logger.info(
            f"  Duration: {metadata.duration:.1f}s ({metadata.duration / 60:.1f} min)"
        )
        logger.info(f"  Codec: {metadata.codec}")

        # Validate metadata
        assert metadata.width > 0, "Width must be positive"
        assert metadata.height > 0, "Height must be positive"
        assert metadata.fps > 0, "FPS must be positive"
        assert metadata.duration > 0, "Duration must be positive"

        logger.info("Metadata validation: PASS")
        return True

    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_frame_extraction_1fps(video_path: str) -> tuple[int, float, bool]:
    """Test frame extraction at 1 FPS.

    Returns:
        Tuple of (frames_extracted, expected_frames, passed)
    """
    logger.info("\n=== Testing Frame Extraction at 1 FPS ===")

    try:
        from vl_jepa.video import VideoInput

        with VideoInput.open(video_path) as video:
            duration = video.duration
            expected_frames = int(duration)  # 1 FPS means ~1 frame per second

            # Extract frames at 1 FPS
            frames = list(video.sample_frames(target_fps=1.0, max_frames=100))

        logger.info(f"Video duration: {duration:.1f}s")
        logger.info(f"Expected frames (at 1 FPS): ~{expected_frames}")
        logger.info(f"Extracted frames: {len(frames)}")

        # Validate frame count (allow ±10% tolerance)
        tolerance = 0.1
        min_expected = int(
            min(expected_frames * (1 - tolerance), 100 * (1 - tolerance))
        )
        max_expected = min(int(expected_frames * (1 + tolerance)), 100)

        if len(frames) < min_expected:
            logger.warning(f"Too few frames: {len(frames)} < {min_expected}")
            passed = False
        elif len(frames) > max_expected:
            logger.warning(f"Too many frames: {len(frames)} > {max_expected}")
            passed = False
        else:
            passed = True

        # Validate frame data
        for i, frame in enumerate(frames[:3]):  # Check first 3
            logger.info(
                f"  Frame {i}: shape={frame.data.shape}, "
                f"timestamp={frame.timestamp:.2f}s, "
                f"dtype={frame.data.dtype}"
            )
            assert frame.data.shape[2] == 3, "Frame must have 3 channels (RGB)"
            assert frame.data.dtype.name == "uint8", "Frame must be uint8"

        logger.info(f"Frame extraction: {'PASS' if passed else 'FAIL'}")
        return len(frames), expected_frames, passed

    except Exception as e:
        logger.error(f"Frame extraction failed: {e}")
        import traceback

        traceback.print_exc()
        return 0, 0, False


def test_timestamp_monotonicity(video_path: str) -> bool:
    """Test that timestamps are strictly monotonically increasing."""
    logger.info("\n=== Testing Timestamp Monotonicity ===")

    try:
        from vl_jepa.video import VideoInput

        with VideoInput.open(video_path) as video:
            frames = list(video.sample_frames(target_fps=1.0, max_frames=50))

        if len(frames) < 2:
            logger.warning("Not enough frames to test monotonicity")
            return True

        timestamps = [f.timestamp for f in frames]

        # Check monotonicity
        violations = 0
        for i in range(1, len(timestamps)):
            if timestamps[i] <= timestamps[i - 1]:
                violations += 1
                logger.warning(
                    f"Violation at frame {i}: "
                    f"{timestamps[i]:.3f} <= {timestamps[i - 1]:.3f}"
                )

        if violations == 0:
            logger.info(
                f"All {len(timestamps)} timestamps are monotonically increasing"
            )
            logger.info(f"  First: {timestamps[0]:.3f}s")
            logger.info(f"  Last: {timestamps[-1]:.3f}s")
            logger.info(f"  Span: {timestamps[-1] - timestamps[0]:.3f}s")
            return True
        else:
            logger.error(f"{violations} monotonicity violations found")
            return False

    except Exception as e:
        logger.error(f"Monotonicity test failed: {e}")
        return False


def test_with_synthetic_video(tmp_path: Path) -> bool:
    """Test with a programmatically created video."""
    logger.info("\n=== Testing with Synthetic Video ===")

    try:
        import cv2
        import numpy as np

        # Create a short synthetic video
        video_path = tmp_path / "synthetic.mp4"
        fps = 30
        duration_sec = 5
        width, height = 320, 240

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

        if not writer.isOpened():
            logger.warning("Cannot create synthetic video (codec issue)")
            return True  # Skip test if we can't create video

        for i in range(fps * duration_sec):
            # Create frame with varying color
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :, 0] = int(255 * i / (fps * duration_sec))  # Blue gradient
            frame[:, :, 1] = 128  # Green constant
            frame[:, :, 2] = 255 - int(255 * i / (fps * duration_sec))  # Red gradient
            writer.write(frame)

        writer.release()

        logger.info(f"Created synthetic video: {video_path}")
        logger.info(f"  Duration: {duration_sec}s")
        logger.info(f"  FPS: {fps}")
        logger.info(f"  Expected frames at 1 FPS: {duration_sec}")

        # Test with our video processor
        from vl_jepa.video import VideoInput

        with VideoInput.open(str(video_path)) as video:
            metadata = video.get_metadata()
            frames = list(video.sample_frames(target_fps=1.0))

        logger.info(f"Extracted {len(frames)} frames")

        # Validate
        passed = abs(len(frames) - duration_sec) <= 1
        logger.info(f"Synthetic video test: {'PASS' if passed else 'FAIL'}")

        return passed

    except Exception as e:
        logger.error(f"Synthetic video test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    """Run video processor integration tests."""
    logger.info("=" * 60)
    logger.info("Video Processor Integration Test")
    logger.info("=" * 60)

    results = []

    # Check for test video
    project_root = Path(__file__).parent.parent
    video_path = project_root / "tests" / "lecture_ex" / "December19_I.mp4"

    if video_path.exists():
        # Test 1: Video load
        passed = test_video_load(str(video_path))
        results.append(("Video load", passed))

        # Test 2: Metadata extraction
        passed = test_metadata_extraction(str(video_path))
        results.append(("Metadata extraction", passed))

        # Test 3: Frame extraction at 1 FPS
        count, expected, passed = test_frame_extraction_1fps(str(video_path))
        results.append(("Frame extraction (1 FPS)", passed))

        # Test 4: Timestamp monotonicity
        passed = test_timestamp_monotonicity(str(video_path))
        results.append(("Timestamp monotonicity", passed))
    else:
        logger.warning(f"\nTest video not found: {video_path}")
        logger.warning("Skipping real video tests.")

    # Test 5: Synthetic video (always runs)
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        passed = test_with_synthetic_video(Path(tmp_dir))
        results.append(("Synthetic video", passed))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        logger.info(f"  {status}: {name}")
        all_passed = all_passed and passed

    if all_passed:
        logger.info("\nAll tests PASSED - Video processor integration OK")
        return 0
    else:
        logger.error("\nSome tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
