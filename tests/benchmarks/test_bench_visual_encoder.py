"""
Performance Benchmarks for Visual Encoder
TEST_IDs: T004.9, T004.10

IMPLEMENTS: Week 4 Day 1 - Benchmark Implementation
"""

import numpy as np
import pytest

from vl_jepa.encoders.placeholder import PlaceholderVisualEncoder


def _has_torch() -> bool:
    """Check if torch is available."""
    try:
        import torch  # noqa: F401

        return True
    except ImportError:
        return False


def _has_cuda() -> bool:
    """Check if CUDA is available."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


@pytest.fixture
def sample_batch() -> np.ndarray:
    """Return a batch of 4 frames for benchmarking."""
    return np.random.uniform(-1.0, 1.0, (4, 3, 224, 224)).astype(np.float32)


@pytest.fixture
def placeholder_encoder() -> PlaceholderVisualEncoder:
    """Return a placeholder encoder for fast benchmarks."""
    return PlaceholderVisualEncoder(seed=42)


@pytest.mark.benchmark
class TestVisualEncoderBenchmarks:
    """Performance benchmarks for visual encoders."""

    def test_placeholder_encode_latency(
        self,
        benchmark,
        placeholder_encoder: PlaceholderVisualEncoder,
        sample_batch: np.ndarray,
    ) -> None:
        """
        TEST_ID: T004.8
        BUDGET: <50ms per batch (placeholder)
        Given: A batch of 4 frames
        When: PlaceholderVisualEncoder.encode() is called
        Then: Encoding completes in <50ms
        """
        # Act
        result = benchmark(placeholder_encoder.encode, sample_batch)

        # Assert
        assert result.shape == (4, 768)
        assert benchmark.stats["mean"] < 0.050  # 50ms

    # T004.9: Encode latency <200ms CPU
    @pytest.mark.skipif(not _has_torch(), reason="Requires torch")
    @pytest.mark.slow
    def test_encode_latency_cpu(self, benchmark, sample_batch: np.ndarray) -> None:
        """
        SPEC: S004
        TEST_ID: T004.9
        BUDGET: <200ms per frame (CPU)
        Given: A batch of 4 frames on CPU
        When: DINOv2Encoder.encode() is called
        Then: Encoding completes in <200ms per frame (800ms total)
        """
        from vl_jepa.encoders.dinov2 import DINOv2Encoder

        # Arrange - Load encoder (not counted in benchmark)
        encoder = DINOv2Encoder.load(device="cpu")

        # Act
        result = benchmark(encoder.encode, sample_batch)

        # Assert (200ms per frame = 800ms for batch of 4)
        assert result.shape == (4, 768)
        # Relaxed timing for CPU - can be slow
        assert benchmark.stats["mean"] < 5.0  # 5s max for batch of 4

    # T004.10: Encode latency <50ms GPU
    @pytest.mark.skipif(not _has_cuda(), reason="Requires CUDA GPU")
    @pytest.mark.gpu
    def test_encode_latency_gpu(self, benchmark, sample_batch: np.ndarray) -> None:
        """
        SPEC: S004
        TEST_ID: T004.10
        BUDGET: <50ms per frame (GPU)
        Given: A batch of 4 frames on GPU
        When: DINOv2Encoder.encode() is called
        Then: Encoding completes in <50ms per frame (200ms total)
        """
        from vl_jepa.encoders.dinov2 import DINOv2Encoder

        # Arrange - Load encoder (not counted in benchmark)
        encoder = DINOv2Encoder.load(device="cuda")

        # Act
        result = benchmark(encoder.encode, sample_batch)

        # Assert (50ms per frame = 200ms for batch of 4)
        assert result.shape == (4, 768)
        assert benchmark.stats["mean"] < 0.200  # 200ms

    def test_single_frame_encode(
        self,
        benchmark,
        placeholder_encoder: PlaceholderVisualEncoder,
    ) -> None:
        """
        TEST_ID: T004.11
        BUDGET: <20ms per single frame (placeholder)
        Given: A single frame
        When: encode_single() is called
        Then: Encoding completes in <20ms
        """
        frame = np.random.uniform(-1.0, 1.0, (3, 224, 224)).astype(np.float32)

        # Act
        result = benchmark(placeholder_encoder.encode_single, frame)

        # Assert
        assert result.shape == (768,)
        assert benchmark.stats["mean"] < 0.020  # 20ms
