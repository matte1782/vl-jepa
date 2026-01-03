#!/usr/bin/env python
"""
Text Encoder Integration Test

IMPLEMENTS: v0.2.0 Week 3 Day 2 - Text encoding validation

This script verifies:
1. sentence-transformers model loads correctly
2. Embeddings have correct shape (768-dim)
3. Embeddings are L2 normalized
4. Semantic similarity works (related > unrelated)
5. Integration with real lecture transcript

Run: python scripts/test_text_encoder.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_model_load() -> bool:
    """Test that sentence-transformers model loads correctly."""
    logger.info("\n=== Testing Model Load ===")

    try:
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder.load()
        logger.info("TextEncoder loaded successfully")
        logger.info(f"  TEXT_DIM: {encoder.TEXT_DIM}")
        logger.info(f"  VISUAL_DIM: {encoder.VISUAL_DIM}")
        logger.info(f"  Model: {encoder._model}")

        return encoder._model is not None

    except Exception as e:
        logger.error(f"Model load failed: {e}")
        return False


def test_embedding_shape() -> bool:
    """Test that embeddings have correct shape."""
    logger.info("\n=== Testing Embedding Shape ===")

    try:
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder.load()
        embedding = encoder.encode("This is a test sentence")

        logger.info(f"Embedding shape: {embedding.shape}")
        logger.info(f"Expected: (768,)")

        passed = embedding.shape == (768,)
        logger.info(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed

    except Exception as e:
        logger.error(f"Shape test failed: {e}")
        return False


def test_l2_normalization() -> bool:
    """Test that embeddings are L2 normalized."""
    logger.info("\n=== Testing L2 Normalization ===")

    try:
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder.load()

        texts = [
            "Short text",
            "A longer text with more words and content",
            "Machine learning is a field of artificial intelligence",
        ]

        all_normalized = True
        for text in texts:
            embedding = encoder.encode(text)
            norm = np.linalg.norm(embedding)
            is_normalized = abs(norm - 1.0) < 1e-5

            logger.info(f"  '{text[:30]}...' -> norm={norm:.6f}")

            if not is_normalized:
                all_normalized = False

        logger.info(f"Result: {'PASS' if all_normalized else 'FAIL'}")
        return all_normalized

    except Exception as e:
        logger.error(f"Normalization test failed: {e}")
        return False


def test_semantic_similarity() -> bool:
    """Test that semantic similarity works correctly."""
    logger.info("\n=== Testing Semantic Similarity ===")

    try:
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder.load()

        # Test pairs
        pairs = [
            ("gradient descent optimization", "gradient descent algorithm", "related"),
            ("neural network architecture", "deep learning model", "related"),
            ("gradient descent", "cats playing with yarn", "unrelated"),
            ("machine learning", "ancient Roman history", "unrelated"),
        ]

        results = []
        for text1, text2, expected in pairs:
            emb1 = encoder.encode(text1)
            emb2 = encoder.encode(text2)
            similarity = float(np.dot(emb1, emb2))

            # Related texts should have similarity > 0.5
            # Unrelated texts should have similarity < 0.5
            if expected == "related":
                passed = similarity > 0.5
            else:
                passed = similarity < 0.5

            results.append(passed)
            status = "PASS" if passed else "FAIL"
            logger.info(
                f"  {status}: '{text1[:20]}' vs '{text2[:20]}' = {similarity:.4f} ({expected})"
            )

        all_passed = all(results)
        logger.info(f"\nResult: {'PASS' if all_passed else 'FAIL'}")
        return all_passed

    except Exception as e:
        logger.error(f"Similarity test failed: {e}")
        return False


def test_batch_encoding() -> bool:
    """Test batch encoding functionality."""
    logger.info("\n=== Testing Batch Encoding ===")

    try:
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder.load()

        texts = [
            "What is machine learning?",
            "Explain the concept of backpropagation",
            "How do convolutional neural networks work?",
            "What is the difference between supervised and unsupervised learning?",
            "Describe the attention mechanism in transformers",
        ]

        embeddings = encoder.encode_batch(texts)

        logger.info(f"Input texts: {len(texts)}")
        logger.info(f"Output shape: {embeddings.shape}")
        logger.info(f"Expected: ({len(texts)}, 768)")

        shape_ok = embeddings.shape == (len(texts), 768)

        # Check all are normalized
        norms = np.linalg.norm(embeddings, axis=1)
        norms_ok = np.allclose(norms, 1.0, atol=1e-5)
        logger.info(f"All norms ~1.0: {norms_ok}")

        passed = shape_ok and norms_ok
        logger.info(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed

    except Exception as e:
        logger.error(f"Batch encoding test failed: {e}")
        return False


def test_with_lecture_transcript() -> bool:
    """Test with real lecture transcript segments."""
    logger.info("\n=== Testing with Lecture Transcript ===")

    try:
        from vl_jepa.text import TextEncoder
        from vl_jepa.audio import WhisperTranscriber, extract_audio

        # Check if lecture video exists
        project_root = Path(__file__).parent.parent
        video_path = project_root / "tests" / "lecture_ex" / "December19_I.mp4"

        if not video_path.exists():
            logger.warning(f"Lecture video not found: {video_path}")
            logger.warning("Skipping lecture transcript test")
            return True  # Skip but don't fail

        # Extract a short segment of audio
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_path = f.name

        logger.info(f"Extracting audio from: {video_path.name}")
        extract_audio(str(video_path), audio_path)

        # Transcribe first 30 seconds
        logger.info("Transcribing audio (first segments)...")
        transcriber = WhisperTranscriber.load(model_size="base", device="cpu")
        segments = transcriber.transcribe(audio_path)

        # Take first 5 segments
        sample_segments = segments[:5]
        logger.info(f"Got {len(sample_segments)} sample segments")

        # Encode segments
        encoder = TextEncoder.load()
        for seg in sample_segments:
            if seg.text.strip():
                emb = encoder.encode(seg.text)
                logger.info(
                    f"  [{seg.start:.1f}s] '{seg.text[:40]}...' -> shape={emb.shape}"
                )

        # Test semantic search simulation
        query = "What is the main topic of this lecture?"
        query_emb = encoder.encode(query)

        similarities = []
        for seg in sample_segments:
            if seg.text.strip():
                seg_emb = encoder.encode(seg.text)
                sim = float(np.dot(query_emb, seg_emb))
                similarities.append((sim, seg.text[:50]))

        similarities.sort(reverse=True)
        logger.info(f"\nTop matches for query '{query}':")
        for sim, text in similarities[:3]:
            logger.info(f"  {sim:.4f}: {text}...")

        # Cleanup
        try:
            Path(audio_path).unlink()
        except Exception:
            pass

        return True

    except Exception as e:
        logger.error(f"Lecture transcript test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    """Run text encoder integration tests."""
    logger.info("=" * 60)
    logger.info("Text Encoder Integration Test")
    logger.info("=" * 60)

    results = []

    # Test 1: Model load
    passed = test_model_load()
    results.append(("Model load", passed))

    # Test 2: Embedding shape
    passed = test_embedding_shape()
    results.append(("Embedding shape (768,)", passed))

    # Test 3: L2 normalization
    passed = test_l2_normalization()
    results.append(("L2 normalization", passed))

    # Test 4: Semantic similarity
    passed = test_semantic_similarity()
    results.append(("Semantic similarity", passed))

    # Test 5: Batch encoding
    passed = test_batch_encoding()
    results.append(("Batch encoding", passed))

    # Test 6: Lecture transcript (optional)
    passed = test_with_lecture_transcript()
    results.append(("Lecture transcript", passed))

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
        logger.info("\nAll tests PASSED - Text encoder integration OK")
        return 0
    else:
        logger.error("\nSome tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
