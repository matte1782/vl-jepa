#!/usr/bin/env python
"""
Whisper Integration Test

IMPLEMENTS: v0.2.0 Week 2 Day 4 - Whisper validation

This script verifies:
1. Whisper model loads correctly
2. Audio extraction from video works
3. Transcription produces text output
4. Timestamps are valid

Run: python scripts/test_whisper.py
"""

from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_whisper_load() -> bool:
    """Test that Whisper model loads correctly."""
    logger.info("\n=== Testing Whisper Model Load ===")

    try:
        from faster_whisper import WhisperModel

        logger.info("Loading Whisper 'base' model...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Whisper loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load Whisper: {e}")
        return False


def test_audio_extraction(video_path: str) -> str | None:
    """Test audio extraction from video."""
    logger.info("\n=== Testing Audio Extraction ===")
    logger.info(f"Video: {video_path}")

    try:
        from vl_jepa.audio import extract_audio, check_ffmpeg_available

        if not check_ffmpeg_available():
            logger.error("FFmpeg not available")
            return None

        # Extract to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        audio_path = extract_audio(video_path, output_path)
        logger.info(f"Audio extracted: {audio_path}")

        # Verify file exists and has content
        size = Path(audio_path).stat().st_size
        logger.info(f"Audio file size: {size / 1024:.1f} KB")

        if size < 1000:
            logger.error("Audio file too small")
            return None

        return audio_path
    except Exception as e:
        logger.error(f"Audio extraction failed: {e}")
        return None


def test_transcription(audio_path: str, max_duration: float = 30.0) -> bool:
    """Test transcription of audio file."""
    logger.info("\n=== Testing Transcription ===")
    logger.info(f"Audio: {audio_path}")
    logger.info(f"Max duration: {max_duration}s")

    try:
        from vl_jepa.audio import WhisperTranscriber

        # Load transcriber
        transcriber = WhisperTranscriber.load(model_size="base", device="cpu")

        # Transcribe
        segments = transcriber.transcribe(audio_path)

        logger.info(f"Transcribed {len(segments)} segments")

        if len(segments) == 0:
            logger.error("No segments produced")
            return False

        # Show first few segments
        logger.info("\nFirst 5 segments:")
        for i, seg in enumerate(segments[:5]):
            logger.info(f"  [{seg.start:.1f}s - {seg.end:.1f}s] {seg.text[:60]}...")

        # Validate segments
        from vl_jepa.audio import validate_segments

        try:
            validate_segments(segments)
            logger.info("\nSegment validation: PASS")
        except ValueError as e:
            logger.error(f"\nSegment validation FAILED: {e}")
            return False

        # Check total text length
        total_text = " ".join(s.text for s in segments)
        logger.info(f"\nTotal text length: {len(total_text)} chars")
        logger.info(f"Total segments: {len(segments)}")

        if len(total_text) < 10:
            logger.error("Transcription too short")
            return False

        return True

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_whisper_transcriber_class() -> bool:
    """Test WhisperTranscriber from our module."""
    logger.info("\n=== Testing WhisperTranscriber Class ===")

    try:
        from vl_jepa.audio import WhisperTranscriber, check_whisper_available

        if not check_whisper_available():
            logger.error("Whisper not available")
            return False

        logger.info("WhisperTranscriber available: OK")

        # Check it can be instantiated
        transcriber = WhisperTranscriber.load(model_size="base")
        logger.info(f"Model size: base")
        logger.info("WhisperTranscriber: OK")
        return True

    except Exception as e:
        logger.error(f"WhisperTranscriber test failed: {e}")
        return False


def main() -> int:
    """Run Whisper integration tests."""
    logger.info("=" * 60)
    logger.info("Whisper Integration Test")
    logger.info("=" * 60)

    results = []

    # Test 1: Whisper load
    passed = test_whisper_load()
    results.append(("Whisper model load", passed))

    # Test 2: WhisperTranscriber class
    passed = test_whisper_transcriber_class()
    results.append(("WhisperTranscriber class", passed))

    # Test 3: Audio extraction + transcription (if video available)
    project_root = Path(__file__).parent.parent
    video_path = project_root / "tests" / "lecture_ex" / "December19_I.mp4"

    if video_path.exists():
        # Extract audio
        audio_path = test_audio_extraction(str(video_path))
        results.append(("Audio extraction", audio_path is not None))

        if audio_path:
            # Transcribe
            passed = test_transcription(audio_path)
            results.append(("Transcription", passed))

            # Cleanup
            try:
                Path(audio_path).unlink()
            except Exception:
                pass
    else:
        logger.warning(f"\nTest video not found: {video_path}")
        logger.warning("Skipping audio extraction and transcription tests.")
        logger.warning("Place a video at the above path to run full tests.")

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
        logger.info("\nAll tests PASSED - Whisper integration OK")
        return 0
    else:
        logger.error("\nSome tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
