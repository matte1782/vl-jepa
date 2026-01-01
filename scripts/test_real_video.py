#!/usr/bin/env python
"""
Gate 0.1: Test Real Video — Lecture Video Validation

Test the encoder on real lecture videos to validate semantic clustering.

Usage:
    python scripts/test_real_video.py path/to/lecture.mp4
    python scripts/test_real_video.py path/to/lecture.mp4 --sample-rate 10

Arguments:
    video_path: Path to the lecture video file
    --sample-rate: Seconds between frame samples (default: 10)
    --max-frames: Maximum frames to process (default: 50)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def extract_frames(
    video_path: str,
    sample_rate: float = 10.0,
    max_frames: int = 50,
) -> tuple[list[np.ndarray], list[float]]:
    """Extract frames from video at regular intervals.

    Args:
        video_path: Path to video file
        sample_rate: Seconds between samples
        max_frames: Maximum number of frames to extract

    Returns:
        Tuple of (frames list, timestamps list)
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    logger.info(f"Video: {video_path}")
    logger.info(f"Duration: {duration/60:.1f} minutes ({duration:.0f}s)")
    logger.info(f"FPS: {fps:.1f}, Total frames: {total_frames}")
    logger.info(f"Sampling every {sample_rate}s (max {max_frames} frames)")

    frames = []
    timestamps = []
    frame_interval = int(fps * sample_rate)

    frame_idx = 0
    while len(frames) < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if not ret:
            break

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize to 224x224
        frame_resized = cv2.resize(frame_rgb, (224, 224))

        # Convert to float32 [-1, 1] and CHW format
        frame_normalized = frame_resized.astype(np.float32) / 127.5 - 1.0
        frame_chw = np.transpose(frame_normalized, (2, 0, 1))

        frames.append(frame_chw)
        timestamps.append(frame_idx / fps)

        frame_idx += frame_interval

    cap.release()

    logger.info(f"Extracted {len(frames)} frames")
    return frames, timestamps


def analyze_similarities(
    embeddings: np.ndarray,
    timestamps: list[float],
) -> dict[str, float]:
    """Analyze similarity patterns in embeddings.

    Args:
        embeddings: Array of embeddings (N, 768)
        timestamps: List of timestamps

    Returns:
        Analysis results
    """
    n = len(embeddings)
    if n < 2:
        return {"error": "Need at least 2 frames"}

    # Compute all pairwise similarities
    # Since embeddings are L2-normalized, dot product = cosine similarity
    similarities = embeddings @ embeddings.T

    # Adjacent frame similarities (should be high for stable content)
    adjacent_sims = [similarities[i, i + 1] for i in range(n - 1)]

    # Non-adjacent similarities (random pairs)
    non_adjacent_sims = []
    for i in range(n):
        for j in range(i + 2, min(i + 10, n)):  # Skip 2-10 frames ahead
            non_adjacent_sims.append(similarities[i, j])

    # Find potential transitions (low adjacent similarity)
    transition_threshold = 0.7
    transitions = []
    for i, sim in enumerate(adjacent_sims):
        if sim < transition_threshold:
            transitions.append({
                "from_time": timestamps[i],
                "to_time": timestamps[i + 1],
                "similarity": float(sim),
            })

    results = {
        "num_frames": n,
        "adjacent_mean": float(np.mean(adjacent_sims)),
        "adjacent_std": float(np.std(adjacent_sims)),
        "adjacent_min": float(np.min(adjacent_sims)),
        "adjacent_max": float(np.max(adjacent_sims)),
        "non_adjacent_mean": float(np.mean(non_adjacent_sims)) if non_adjacent_sims else 0.0,
        "num_transitions": len(transitions),
        "transitions": transitions[:10],  # First 10 transitions
    }

    return results


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def run_video_test(
    video_path: str,
    sample_rate: float = 10.0,
    max_frames: int = 50,
) -> dict:
    """Run the full video test.

    Args:
        video_path: Path to video file
        sample_rate: Seconds between samples
        max_frames: Maximum frames to process

    Returns:
        Test results
    """
    from vl_jepa.encoders import PlaceholderVisualEncoder, check_dinov2_available

    # Extract frames
    logger.info("=" * 60)
    logger.info("Extracting frames...")
    frames, timestamps = extract_frames(video_path, sample_rate, max_frames)

    if len(frames) < 2:
        logger.error("Not enough frames extracted")
        return {"error": "Not enough frames"}

    # Try DINOv2 first, fall back to placeholder
    if check_dinov2_available():
        try:
            from vl_jepa.encoders import DINOv2Encoder
            logger.info("Using DINOv2Encoder...")
            encoder = DINOv2Encoder.load(device="cpu")
            encoder_name = "DINOv2"
        except Exception as e:
            logger.warning(f"DINOv2 failed: {e}, using placeholder")
            encoder = PlaceholderVisualEncoder(seed=42)
            encoder_name = "Placeholder"
    else:
        logger.info("Using PlaceholderVisualEncoder...")
        encoder = PlaceholderVisualEncoder(seed=42)
        encoder_name = "Placeholder"

    # Encode all frames
    logger.info("Encoding frames...")
    start_time = time.perf_counter()

    frames_array = np.stack(frames, axis=0)
    embeddings = encoder.encode(frames_array)

    encode_time = time.perf_counter() - start_time
    logger.info(f"Encoded {len(frames)} frames in {encode_time:.2f}s")
    logger.info(f"Average: {encode_time/len(frames)*1000:.1f}ms per frame")

    # Analyze similarities
    logger.info("Analyzing similarities...")
    results = analyze_similarities(embeddings, timestamps)
    results["encoder"] = encoder_name
    results["encode_time_s"] = encode_time
    results["video_path"] = video_path

    # Print results
    logger.info("=" * 60)
    logger.info("RESULTS")
    logger.info("=" * 60)
    logger.info(f"Encoder: {encoder_name}")
    logger.info(f"Frames analyzed: {results['num_frames']}")
    logger.info(f"")
    logger.info(f"Adjacent frame similarity (consecutive frames):")
    logger.info(f"  Mean: {results['adjacent_mean']:.4f}")
    logger.info(f"  Std:  {results['adjacent_std']:.4f}")
    logger.info(f"  Min:  {results['adjacent_min']:.4f}")
    logger.info(f"  Max:  {results['adjacent_max']:.4f}")
    logger.info(f"")
    logger.info(f"Non-adjacent similarity: {results['non_adjacent_mean']:.4f}")
    logger.info(f"")
    logger.info(f"Detected transitions: {results['num_transitions']}")

    if results["transitions"]:
        logger.info(f"")
        logger.info("Potential slide/scene changes:")
        for t in results["transitions"]:
            logger.info(
                f"  {format_time(t['from_time'])} -> {format_time(t['to_time'])}: "
                f"similarity={t['similarity']:.3f}"
            )

    # Validation
    logger.info("")
    logger.info("=" * 60)
    logger.info("VALIDATION")
    logger.info("=" * 60)

    if encoder_name == "Placeholder":
        # Placeholder has different thresholds
        adjacent_pass = results["adjacent_mean"] > 0.5
        logger.info(f"Adjacent similarity > 0.5: {'PASS' if adjacent_pass else 'FAIL'}")
        logger.info("")
        logger.info("NOTE: Using placeholder encoder. For accurate results:")
        logger.info("  pip install torch transformers")
        logger.info("  python scripts/test_real_video.py <video>")
    else:
        # DINOv2 thresholds
        adjacent_pass = results["adjacent_mean"] > 0.85
        variance_pass = results["adjacent_std"] < 0.15
        logger.info(f"Adjacent similarity > 0.85: {'PASS' if adjacent_pass else 'FAIL'}")
        logger.info(f"Similarity variance < 0.15: {'PASS' if variance_pass else 'FAIL'}")

        if adjacent_pass and variance_pass:
            logger.info("")
            logger.info("VERDICT: GO - DINOv2 produces meaningful embeddings for lectures")
        else:
            logger.info("")
            logger.info("VERDICT: INVESTIGATE - Results need review")

    return results


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test encoder on real lecture video"
    )
    parser.add_argument("video_path", help="Path to lecture video file")
    parser.add_argument(
        "--sample-rate",
        type=float,
        default=10.0,
        help="Seconds between frame samples (default: 10)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=50,
        help="Maximum frames to process (default: 50)",
    )

    args = parser.parse_args()

    if not Path(args.video_path).exists():
        logger.error(f"Video not found: {args.video_path}")
        return 1

    try:
        run_video_test(args.video_path, args.sample_rate, args.max_frames)
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
