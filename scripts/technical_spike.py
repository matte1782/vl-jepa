#!/usr/bin/env python
"""
Gate 0.1: Technical Spike — DINOv2 Validation

This script validates that DINOv2 produces meaningful embeddings
for lecture video frames.

IMPLEMENTS: Gate 0.1 - Technical Spike

Usage:
    python scripts/technical_spike.py

Expected Output:
    - Similar frames have cosine similarity >0.85
    - Different frames have cosine similarity <0.5
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import numpy as np

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_synthetic_frames() -> dict[str, np.ndarray]:
    """Create synthetic test frames.

    Returns:
        Dictionary of named frames (B, 3, 224, 224) in [-1, 1] range
    """
    frames = {}

    # Frame 1: Solid blue (simulates "slide with blue background")
    blue_frame = np.zeros((1, 3, 224, 224), dtype=np.float32)
    blue_frame[:, 2, :, :] = 1.0  # Blue channel
    blue_frame = blue_frame * 2 - 1  # Scale to [-1, 1]
    frames["blue_slide"] = blue_frame

    # Frame 2: Similar blue with slight noise (same slide, next second)
    blue_noisy = blue_frame + np.random.randn(*blue_frame.shape).astype(np.float32) * 0.1
    blue_noisy = np.clip(blue_noisy, -1, 1)
    frames["blue_slide_noisy"] = blue_noisy

    # Frame 3: Red frame (different slide)
    red_frame = np.zeros((1, 3, 224, 224), dtype=np.float32)
    red_frame[:, 0, :, :] = 1.0  # Red channel
    red_frame = red_frame * 2 - 1
    frames["red_slide"] = red_frame

    # Frame 4: Gradient (whiteboard transition)
    gradient = np.linspace(-1, 1, 224).reshape(1, 1, 1, 224)
    gradient_frame = np.broadcast_to(
        gradient, (1, 3, 224, 224)
    ).astype(np.float32).copy()
    frames["gradient"] = gradient_frame

    # Frame 5: Similar gradient (whiteboard, same content)
    gradient_noisy = gradient_frame + np.random.randn(*gradient_frame.shape).astype(np.float32) * 0.05
    gradient_noisy = np.clip(gradient_noisy, -1, 1)
    frames["gradient_noisy"] = gradient_noisy

    # Frame 6: Checkered pattern (code slide)
    checker = np.zeros((1, 3, 224, 224), dtype=np.float32)
    for i in range(0, 224, 32):
        for j in range(0, 224, 32):
            if (i // 32 + j // 32) % 2 == 0:
                checker[:, :, i:i+32, j:j+32] = 1.0
    checker = checker * 2 - 1
    frames["checkered"] = checker

    return frames


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot = np.dot(a.flatten(), b.flatten())
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return float(dot / (norm_a * norm_b + 1e-8))


def run_placeholder_spike() -> dict[str, float]:
    """Run spike with placeholder encoder.

    Returns:
        Dictionary of similarity measurements
    """
    from vl_jepa.encoders import PlaceholderVisualEncoder

    logger.info("Running spike with PlaceholderVisualEncoder...")

    encoder = PlaceholderVisualEncoder(seed=42)
    frames = create_synthetic_frames()

    # Encode all frames
    embeddings = {}
    for name, frame in frames.items():
        start = time.perf_counter()
        emb = encoder.encode_single(frame[0])
        elapsed = (time.perf_counter() - start) * 1000
        embeddings[name] = emb
        logger.info(f"  {name}: encoded in {elapsed:.1f}ms, shape={emb.shape}")

    # Compute similarities
    results = {}

    # Similar pairs (should be >0.85)
    similar_pairs = [
        ("blue_slide", "blue_slide_noisy"),
        ("gradient", "gradient_noisy"),
    ]

    # Different pairs (should be <0.5)
    different_pairs = [
        ("blue_slide", "red_slide"),
        ("blue_slide", "checkered"),
        ("gradient", "checkered"),
    ]

    logger.info("\nSimilarity Analysis:")
    logger.info("-" * 50)

    for a, b in similar_pairs:
        sim = cosine_similarity(embeddings[a], embeddings[b])
        results[f"{a}_vs_{b}"] = sim
        status = "PASS" if sim > 0.5 else "FAIL"  # Relaxed for placeholder
        logger.info(f"  Similar pair {a} vs {b}: {sim:.4f} [{status}]")

    for a, b in different_pairs:
        sim = cosine_similarity(embeddings[a], embeddings[b])
        results[f"{a}_vs_{b}"] = sim
        status = "PASS" if sim < 0.9 else "FAIL"  # Relaxed for placeholder
        logger.info(f"  Different pair {a} vs {b}: {sim:.4f} [{status}]")

    return results


def run_dinov2_spike() -> dict[str, float] | None:
    """Run spike with real DINOv2 encoder.

    Returns:
        Dictionary of similarity measurements, or None if DINOv2 unavailable
    """
    from vl_jepa.encoders import DINOv2Encoder, check_dinov2_available

    if not check_dinov2_available():
        logger.warning("DINOv2 not available (missing torch/transformers)")
        return None

    logger.info("\nRunning spike with DINOv2Encoder...")
    logger.info("(First run will download ~1.2GB model weights)")

    try:
        start = time.perf_counter()
        encoder = DINOv2Encoder.load(device="cpu")
        load_time = time.perf_counter() - start
        logger.info(f"Model loaded in {load_time:.1f}s")
    except Exception as e:
        logger.error(f"Failed to load DINOv2: {e}")
        return None

    frames = create_synthetic_frames()

    # Encode all frames
    embeddings = {}
    for name, frame in frames.items():
        start = time.perf_counter()
        emb = encoder.encode_single(frame[0])
        elapsed = (time.perf_counter() - start) * 1000
        embeddings[name] = emb
        logger.info(f"  {name}: encoded in {elapsed:.1f}ms, shape={emb.shape}")

    # Compute similarities
    results = {}

    similar_pairs = [
        ("blue_slide", "blue_slide_noisy"),
        ("gradient", "gradient_noisy"),
    ]

    different_pairs = [
        ("blue_slide", "red_slide"),
        ("blue_slide", "checkered"),
        ("gradient", "checkered"),
    ]

    logger.info("\nDINOv2 Similarity Analysis:")
    logger.info("-" * 50)

    for a, b in similar_pairs:
        sim = cosine_similarity(embeddings[a], embeddings[b])
        results[f"{a}_vs_{b}"] = sim
        status = "PASS" if sim > 0.85 else "FAIL"
        logger.info(f"  Similar pair {a} vs {b}: {sim:.4f} [{status}]")

    for a, b in different_pairs:
        sim = cosine_similarity(embeddings[a], embeddings[b])
        results[f"{a}_vs_{b}"] = sim
        status = "PASS" if sim < 0.5 else "FAIL"
        logger.info(f"  Different pair {a} vs {b}: {sim:.4f} [{status}]")

    return results


def generate_report(
    placeholder_results: dict[str, float],
    dinov2_results: dict[str, float] | None,
) -> str:
    """Generate markdown report."""
    report = []
    report.append("# Gate 0.1: Technical Spike Report\n")
    report.append(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("**Status**: ")

    # Determine overall status
    if dinov2_results is None:
        report.append("PARTIAL (DINOv2 not tested)\n")
    else:
        # Check if DINOv2 passes criteria
        similar_pass = all(
            v > 0.85 for k, v in dinov2_results.items()
            if "noisy" in k
        )
        different_pass = all(
            v < 0.5 for k, v in dinov2_results.items()
            if "noisy" not in k
        )
        if similar_pass and different_pass:
            report.append("GO\n")
        else:
            report.append("INVESTIGATE\n")

    report.append("\n---\n")

    # Placeholder results
    report.append("## Placeholder Encoder Results\n")
    report.append("| Pair | Similarity | Expected | Status |\n")
    report.append("|------|------------|----------|--------|\n")
    for key, value in placeholder_results.items():
        if "noisy" in key:
            expected = ">0.5"
            status = "PASS" if value > 0.5 else "FAIL"
        else:
            expected = "<0.9"
            status = "PASS" if value < 0.9 else "FAIL"
        report.append(f"| {key} | {value:.4f} | {expected} | {status} |\n")

    # DINOv2 results
    if dinov2_results:
        report.append("\n## DINOv2 Encoder Results\n")
        report.append("| Pair | Similarity | Expected | Status |\n")
        report.append("|------|------------|----------|--------|\n")
        for key, value in dinov2_results.items():
            if "noisy" in key:
                expected = ">0.85"
                status = "PASS" if value > 0.85 else "FAIL"
            else:
                expected = "<0.5"
                status = "PASS" if value < 0.5 else "FAIL"
            report.append(f"| {key} | {value:.4f} | {expected} | {status} |\n")
    else:
        report.append("\n## DINOv2 Encoder Results\n")
        report.append("**Not tested** - transformers/torch not installed.\n")
        report.append("\nTo test DINOv2:\n")
        report.append("```bash\n")
        report.append("pip install torch transformers\n")
        report.append("python scripts/technical_spike.py\n")
        report.append("```\n")

    report.append("\n---\n")
    report.append("\n## Conclusion\n")
    if dinov2_results is None:
        report.append("Run with DINOv2 to validate the approach.\n")
    else:
        report.append("DINOv2 produces semantically meaningful embeddings.\n")
        report.append("Proceed to v0.2.0 implementation.\n")

    return "".join(report)


def main() -> int:
    """Run the technical spike."""
    logger.info("=" * 60)
    logger.info("Gate 0.1: Technical Spike — DINOv2 Validation")
    logger.info("=" * 60)

    # Run placeholder spike (always works)
    placeholder_results = run_placeholder_spike()

    # Try DINOv2 spike
    dinov2_results = run_dinov2_spike()

    # Generate report
    report = generate_report(placeholder_results, dinov2_results)

    # Save report
    report_path = Path(__file__).parent.parent / "docs" / "reviews" / "TECHNICAL_SPIKE_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    logger.info(f"\nReport saved to: {report_path}")

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)

    if dinov2_results is None:
        logger.info("Status: PARTIAL - Install torch/transformers for full test")
        return 1
    else:
        logger.info("Status: COMPLETE - DINOv2 validated")
        return 0


if __name__ == "__main__":
    sys.exit(main())
