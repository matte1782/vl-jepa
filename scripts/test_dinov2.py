#!/usr/bin/env python
"""
DINOv2 Integration Test

IMPLEMENTS: v0.2.0 Week 2 Day 3 - DINOv2 validation

This script verifies:
1. DINOv2 model loads correctly
2. Embeddings are generated from frames
3. Similar frames have high cosine similarity (>= 0.85)
4. Different frames have lower similarity

Run: python scripts/test_dinov2.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class DINOv2Encoder:
    """DINOv2 ViT-L/14 encoder for frame embeddings.

    Uses facebook/dinov2 from torch.hub for semantic frame embeddings.
    Output dimension: 1024 (ViT-L/14)
    """

    EMBEDDING_DIM: int = 1024
    INPUT_SIZE: int = 224

    def __init__(self, model: torch.nn.Module, device: str = "cpu") -> None:
        self._model = model
        self._device = device
        # Set to inference mode
        self._model.train(False)

    @classmethod
    def load(cls, device: str | None = None) -> "DINOv2Encoder":
        """Load DINOv2 model from torch.hub.

        Args:
            device: Device to use ("cpu" or "cuda")

        Returns:
            Initialized DINOv2Encoder
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Loading DINOv2 ViT-L/14 on {device}...")

        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vitl14")
        model = model.to(device)
        model.train(False)  # Set to inference mode

        logger.info(f"DINOv2 loaded: {model.embed_dim}D embeddings")

        return cls(model, device)

    def preprocess(self, frame: np.ndarray) -> torch.Tensor:
        """Preprocess frame for DINOv2.

        Args:
            frame: BGR or RGB frame, any size

        Returns:
            Tensor of shape (1, 3, 224, 224), normalized
        """
        # Resize to 224x224
        frame_resized = cv2.resize(frame, (self.INPUT_SIZE, self.INPUT_SIZE))

        # Convert BGR to RGB if needed (OpenCV loads as BGR)
        if len(frame_resized.shape) == 3 and frame_resized.shape[2] == 3:
            # Assume BGR, convert to RGB
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = frame_resized

        # Convert to float and normalize to [0, 1]
        frame_float = frame_rgb.astype(np.float32) / 255.0

        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        frame_norm = (frame_float - mean) / std

        # Convert to tensor: (H, W, C) -> (C, H, W) -> (1, C, H, W)
        tensor = torch.from_numpy(frame_norm).permute(2, 0, 1).unsqueeze(0)

        return tensor.to(self._device)

    def encode(self, frame: np.ndarray) -> np.ndarray:
        """Encode a single frame to embedding.

        Args:
            frame: BGR or RGB frame

        Returns:
            L2-normalized embedding of shape (1024,)
        """
        tensor = self.preprocess(frame)

        with torch.no_grad():
            embedding = self._model(tensor)

            # L2 normalize
            embedding = F.normalize(embedding, p=2, dim=1)

        return embedding.cpu().numpy().squeeze()

    def encode_batch(self, frames: list[np.ndarray]) -> np.ndarray:
        """Encode multiple frames.

        Args:
            frames: List of BGR/RGB frames

        Returns:
            Embeddings of shape (N, 1024)
        """
        tensors = [self.preprocess(f) for f in frames]
        batch = torch.cat(tensors, dim=0)

        with torch.no_grad():
            embeddings = self._model(batch)
            embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings.cpu().numpy()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def test_similar_frames(encoder: DINOv2Encoder, video_path: str) -> tuple[float, bool]:
    """Test that similar (adjacent) frames have high cosine similarity.

    PASS criteria: cosine >= 0.85 for adjacent frames
    """
    logger.info(f"\n=== Testing Similar Frame Similarity ===")
    logger.info(f"Video: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return 0.0, False

    # Read two adjacent frames (should be very similar)
    ret1, frame1 = cap.read()
    ret2, frame2 = cap.read()
    cap.release()

    if not ret1 or not ret2:
        logger.error("Cannot read frames from video")
        return 0.0, False

    logger.info(f"Frame 1 shape: {frame1.shape}")
    logger.info(f"Frame 2 shape: {frame2.shape}")

    # Encode frames
    emb1 = encoder.encode(frame1)
    emb2 = encoder.encode(frame2)

    logger.info(f"Embedding 1 shape: {emb1.shape}")
    logger.info(f"Embedding 2 shape: {emb2.shape}")

    # Compute similarity
    similarity = cosine_similarity(emb1, emb2)
    passed = similarity >= 0.85

    logger.info(f"Cosine similarity (adjacent frames): {similarity:.4f}")
    logger.info(f"PASS threshold: >= 0.85")
    logger.info(f"Result: {'PASS' if passed else 'FAIL'}")

    return similarity, passed


def test_different_frames(encoder: DINOv2Encoder, video_path: str) -> tuple[float, float, bool]:
    """Test that distant frames have lower similarity than adjacent frames.

    PASS criteria: distant_similarity < adjacent_similarity
    """
    logger.info(f"\n=== Testing Different Frame Similarity ===")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0, 0.0, False

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get frame at start
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret1, frame_start = cap.read()

    # Get frame 30 seconds later (or at end if video is shorter)
    target_frame = min(int(fps * 30), total_frames - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret2, frame_later = cap.read()

    # Get adjacent frame for comparison
    cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
    ret3, frame_adjacent = cap.read()

    cap.release()

    if not all([ret1, ret2, ret3]):
        logger.error("Cannot read frames")
        return 0.0, 0.0, False

    # Encode
    emb_start = encoder.encode(frame_start)
    emb_later = encoder.encode(frame_later)
    emb_adjacent = encoder.encode(frame_adjacent)

    # Compare
    sim_adjacent = cosine_similarity(emb_start, emb_adjacent)
    sim_distant = cosine_similarity(emb_start, emb_later)

    passed = sim_distant < sim_adjacent

    logger.info(f"Adjacent frames similarity: {sim_adjacent:.4f}")
    logger.info(f"Distant frames similarity: {sim_distant:.4f}")
    logger.info(f"Expected: distant < adjacent")
    logger.info(f"Result: {'PASS' if passed else 'FAIL'}")

    return sim_adjacent, sim_distant, passed


def test_with_synthetic_frames(encoder: DINOv2Encoder) -> tuple[float, float, bool]:
    """Test with synthetic frames (no video needed).

    Creates similar frames (slight color shift) and different frames.
    """
    logger.info(f"\n=== Testing with Synthetic Frames ===")

    # Create base frame (red square on blue background)
    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
    frame1[:, :] = [255, 0, 0]  # Blue background (BGR)
    frame1[100:200, 100:200] = [0, 0, 255]  # Red square

    # Similar frame (slightly brighter)
    frame2 = np.clip(frame1.astype(np.int32) + 10, 0, 255).astype(np.uint8)

    # Different frame (green square on red background)
    frame3 = np.zeros((480, 640, 3), dtype=np.uint8)
    frame3[:, :] = [0, 0, 255]  # Red background
    frame3[200:400, 300:500] = [0, 255, 0]  # Green square

    # Encode
    emb1 = encoder.encode(frame1)
    emb2 = encoder.encode(frame2)
    emb3 = encoder.encode(frame3)

    # Compare
    sim_similar = cosine_similarity(emb1, emb2)
    sim_different = cosine_similarity(emb1, emb3)

    passed = sim_similar > sim_different

    logger.info(f"Similar frames (color shift) similarity: {sim_similar:.4f}")
    logger.info(f"Different frames similarity: {sim_different:.4f}")
    logger.info(f"Expected: similar > different")
    logger.info(f"Result: {'PASS' if passed else 'FAIL'}")

    return sim_similar, sim_different, passed


def main() -> int:
    """Run DINOv2 integration tests."""
    logger.info("=" * 60)
    logger.info("DINOv2 Integration Test")
    logger.info("=" * 60)

    # Load encoder
    try:
        encoder = DINOv2Encoder.load()
    except Exception as e:
        logger.error(f"Failed to load DINOv2: {e}")
        return 1

    # Check for test video
    project_root = Path(__file__).parent.parent
    video_path = project_root / "tests" / "lecture_ex" / "December19_I.mp4"

    all_passed = True
    results = []

    # Test 1: Synthetic frames (always runs)
    sim_sim, sim_diff, passed = test_with_synthetic_frames(encoder)
    results.append(("Synthetic frames", passed))
    all_passed = all_passed and passed

    # Test 2: Real video (if available)
    if video_path.exists():
        sim, passed = test_similar_frames(encoder, str(video_path))
        results.append(("Similar frames >= 0.85", passed))
        all_passed = all_passed and passed

        adj, dist, passed = test_different_frames(encoder, str(video_path))
        results.append(("Distant < Adjacent", passed))
        all_passed = all_passed and passed
    else:
        logger.warning(f"\nTest video not found: {video_path}")
        logger.warning("Skipping real video tests. Place a video at:")
        logger.warning(f"  {video_path}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        logger.info(f"  {status}: {name}")

    if all_passed:
        logger.info("\nAll tests PASSED - DINOv2 integration OK")
        logger.info("\nDECISION GATE: GO - Continue with DINOv2")
        return 0
    else:
        logger.error("\nSome tests FAILED")
        logger.error("\nDECISION GATE: INVESTIGATE")
        return 1


if __name__ == "__main__":
    sys.exit(main())
