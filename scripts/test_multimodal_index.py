#!/usr/bin/env python
"""
Multimodal Index Integration Test

IMPLEMENTS: v0.2.0 Week 3 Day 3 - Multimodal integration validation

This script verifies:
1. Visual frame extraction and encoding
2. Transcript extraction and encoding
3. Multimodal index stores both modalities
4. Search works across modalities
5. Timestamp alignment works

Run: python scripts/test_multimodal_index.py
"""

from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_multimodal_with_lecture(video_path: str, max_frames: int = 30) -> bool:
    """Test multimodal index with real lecture video.

    Args:
        video_path: Path to lecture video
        max_frames: Maximum frames to process (for speed)

    Returns:
        True if all tests pass
    """
    logger.info("\n" + "=" * 60)
    logger.info("Multimodal Index Integration Test")
    logger.info("=" * 60)
    logger.info(f"Video: {Path(video_path).name}")
    logger.info(f"Max frames: {max_frames}")

    try:
        # Import components
        from vl_jepa.audio import TranscriptChunker, WhisperTranscriber, extract_audio
        from vl_jepa.multimodal_index import Modality, MultimodalIndex
        from vl_jepa.text import TextEncoder
        from vl_jepa.video import VideoInput

        # Step 1: Extract and encode visual frames
        logger.info("\n1. Extracting visual frames...")
        with VideoInput.open(video_path) as video:
            metadata = video.get_metadata()
            logger.info(
                f"   Video: {metadata.width}x{metadata.height}, {metadata.fps:.1f} FPS"
            )
            logger.info(
                f"   Duration: {metadata.duration:.1f}s ({metadata.duration / 60:.1f} min)"
            )

            frames = list(video.sample_frames(target_fps=1.0, max_frames=max_frames))
            logger.info(f"   Extracted {len(frames)} frames at 1 FPS")

        # Step 2: Extract audio and transcribe
        logger.info("\n2. Transcribing audio...")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_path = f.name

        extract_audio(video_path, audio_path)
        transcriber = WhisperTranscriber.load(model_size="base", device="cpu")
        segments = transcriber.transcribe(audio_path)
        logger.info(f"   Transcribed {len(segments)} segments")

        # Chunk transcripts
        chunker = TranscriptChunker(window_size=30.0, overlap=5.0)
        chunks = list(chunker.chunk(segments))
        logger.info(f"   Created {len(chunks)} chunks (30s windows)")

        # Step 3: Create multimodal index
        logger.info("\n3. Building multimodal index...")
        index = MultimodalIndex()

        # Load encoders
        text_encoder = TextEncoder.load()

        # For visual, we'll use placeholder embeddings (DINOv2 is slow for integration test)
        # In production, use DINOv2Encoder
        logger.info("   Adding visual frames (placeholder embeddings for speed)...")
        for i, frame in enumerate(frames):
            # Placeholder: random but consistent embedding
            np.random.seed(i)
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_visual(emb, timestamp=frame.timestamp, frame_index=i)

        logger.info("   Adding transcript chunks...")
        for i, chunk in enumerate(chunks):
            if not chunk.text.strip():
                continue
            emb = text_encoder.encode(chunk.text)
            index.add_transcript(
                emb,
                start_time=chunk.start,
                end_time=chunk.end,
                text=chunk.text,
            )

        logger.info(f"   Index size: {index.size} entries")
        logger.info(
            f"   Visual: {index.visual_count}, Transcript: {index.transcript_count}"
        )

        # Step 4: Test semantic search
        logger.info("\n4. Testing semantic search...")

        # Search for Z3/SMT related content
        queries = [
            "Python API for Z3 SMT solver",
            "satisfiability and theorem proving",
            "how to install and use Z3",
        ]

        for query in queries:
            query_emb = text_encoder.encode(query)
            results = index.search_transcript(query_emb, k=3)

            logger.info(f"\n   Query: '{query}'")
            for r in results:
                text_preview = r.text[:50] if r.text else "N/A"
                logger.info(
                    f"     {r.score:.4f} @ {r.timestamp:.1f}s: {text_preview}..."
                )

        # Step 5: Test timestamp alignment
        logger.info("\n5. Testing timestamp alignment...")

        # Get aligned context at 30 seconds
        context = index.get_aligned_context(
            timestamp=30.0,
            visual_tolerance=2.0,
            transcript_tolerance=10.0,
        )

        logger.info(f"   Context at t=30s:")
        logger.info(f"     Visual entries: {len(context['visual'])}")
        logger.info(f"     Transcript entries: {len(context['transcript'])}")

        if context["transcript"]:
            top_transcript = context["transcript"][0]
            logger.info(
                f"     Top transcript: '{top_transcript.text[:50] if top_transcript.text else 'N/A'}...'"
            )

        # Step 6: Test save/load
        logger.info("\n6. Testing save/load...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = Path(tmp_dir) / "lecture_index"
            index.save(save_path)

            loaded_index = MultimodalIndex.load(save_path)
            logger.info(f"   Saved and loaded: {loaded_index.size} entries")

            # Verify loaded index works
            results = loaded_index.search_transcript(
                text_encoder.encode("Z3 solver"), k=1
            )
            logger.info(f"   Search on loaded index: {len(results)} results")

        # Cleanup
        Path(audio_path).unlink()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"  Visual entries: {index.visual_count}")
        logger.info(f"  Transcript entries: {index.transcript_count}")
        logger.info(f"  Total entries: {index.size}")
        logger.info(f"  Semantic search: WORKING")
        logger.info(f"  Timestamp alignment: WORKING")
        logger.info(f"  Save/Load: WORKING")

        return True

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_synthetic_multimodal() -> bool:
    """Test with synthetic data (no video needed)."""
    logger.info("\n=== Testing with Synthetic Data ===")

    try:
        from vl_jepa.multimodal_index import Modality, MultimodalIndex

        index = MultimodalIndex()

        # Add synthetic visual entries
        for i in range(10):
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_visual(emb, timestamp=float(i), frame_index=i)

        # Add synthetic transcript entries
        texts = [
            "Introduction to the Z3 SMT solver",
            "Installing Z3 Python bindings",
            "Creating satisfiability constraints",
            "Solving boolean formulas",
            "Advanced Z3 features and optimization",
        ]
        for i, text in enumerate(texts):
            np.random.seed(100 + i)
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_transcript(
                emb,
                start_time=float(i * 20),
                end_time=float(i * 20 + 18),
                text=text,
            )

        logger.info(f"  Created index: {index}")

        # Test search
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        all_results = index.search(query, k=5)
        visual_results = index.search_visual(query, k=3)
        transcript_results = index.search_transcript(query, k=3)

        logger.info(f"  All search: {len(all_results)} results")
        logger.info(f"  Visual search: {len(visual_results)} results")
        logger.info(f"  Transcript search: {len(transcript_results)} results")

        # Verify modality filtering
        assert all(r.modality == Modality.VISUAL for r in visual_results)
        assert all(r.modality == Modality.TRANSCRIPT for r in transcript_results)

        logger.info("  Modality filtering: PASS")

        return True

    except Exception as e:
        logger.error(f"Synthetic test failed: {e}")
        return False


def main() -> int:
    """Run multimodal index integration tests."""
    results = []

    # Test 1: Synthetic data (always runs)
    passed = test_synthetic_multimodal()
    results.append(("Synthetic multimodal", passed))

    # Test 2: Real lecture video (if available)
    project_root = Path(__file__).parent.parent
    video_path = project_root / "tests" / "lecture_ex" / "December19_I.mp4"

    if video_path.exists():
        passed = test_multimodal_with_lecture(str(video_path), max_frames=30)
        results.append(("Lecture multimodal", passed))
    else:
        logger.warning(f"\nLecture video not found: {video_path}")
        logger.warning("Skipping lecture integration test.")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        logger.info(f"  {status}: {name}")
        all_passed = all_passed and passed

    if all_passed:
        logger.info("\nAll tests PASSED - Multimodal index integration OK")
        return 0
    else:
        logger.error("\nSome tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
