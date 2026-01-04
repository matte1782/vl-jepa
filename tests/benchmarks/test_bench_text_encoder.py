"""
Performance Benchmarks for Text Encoder
TEST_IDs: T006.8

IMPLEMENTS: Week 4 Day 1 - Benchmark Implementation
"""

import pytest

from vl_jepa.encoders.placeholder import PlaceholderTextEncoder
from vl_jepa.text import TextEncoder


def _has_sentence_transformers() -> bool:
    """Check if sentence-transformers is available."""
    try:
        import sentence_transformers  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.fixture
def placeholder_encoder() -> PlaceholderTextEncoder:
    """Return a placeholder text encoder for fast benchmarks."""
    return PlaceholderTextEncoder(seed=42)


@pytest.fixture
def sample_queries() -> list[str]:
    """Return sample queries for batch benchmarks."""
    return [
        "What is gradient descent?",
        "Explain the concept of neural networks.",
        "How does backpropagation work?",
        "What is the difference between supervised and unsupervised learning?",
        "Explain the attention mechanism in transformers.",
    ]


@pytest.mark.benchmark
class TestTextEncoderBenchmarks:
    """Performance benchmarks for text encoding."""

    def test_placeholder_encode_latency(
        self,
        benchmark,
        placeholder_encoder: PlaceholderTextEncoder,
    ) -> None:
        """
        TEST_ID: T006.7
        BUDGET: <10ms per query (placeholder)
        Given: A typical query string
        When: PlaceholderTextEncoder.encode() is called
        Then: Encoding completes in <10ms
        """
        query = "What is gradient descent?"

        # Act
        result = benchmark(placeholder_encoder.encode, query)

        # Assert
        assert result.shape == (768,)
        assert benchmark.stats["mean"] < 0.010  # 10ms

    # T006.8: Encode latency <50ms
    @pytest.mark.skipif(
        not _has_sentence_transformers(), reason="Requires sentence-transformers"
    )
    def test_encode_latency(self, benchmark) -> None:
        """
        SPEC: S006
        TEST_ID: T006.8
        BUDGET: <50ms per query
        Given: A typical query string
        When: TextEncoder.encode() is called
        Then: Encoding completes in <50ms
        """
        # Arrange
        encoder = TextEncoder.load()
        query = "What is gradient descent?"

        # Act
        result = benchmark(encoder.encode, query)

        # Assert
        assert result.shape == (768,)
        assert benchmark.stats["mean"] < 0.050  # 50ms

    @pytest.mark.skipif(
        not _has_sentence_transformers(), reason="Requires sentence-transformers"
    )
    def test_encode_batch_latency(self, benchmark, sample_queries: list[str]) -> None:
        """
        TEST_ID: T006.9
        BUDGET: <200ms for 5 queries
        Given: A batch of 5 query strings
        When: TextEncoder.encode_batch() is called
        Then: Encoding completes in <200ms (40ms per query amortized)
        """
        # Arrange
        encoder = TextEncoder.load()

        # Act
        result = benchmark(encoder.encode_batch, sample_queries)

        # Assert
        assert result.shape == (5, 768)
        assert benchmark.stats["mean"] < 0.200  # 200ms

    def test_placeholder_batch_latency(
        self,
        benchmark,
        placeholder_encoder: PlaceholderTextEncoder,
        sample_queries: list[str],
    ) -> None:
        """
        TEST_ID: T006.10
        BUDGET: <50ms for 5 queries (placeholder)
        Given: A batch of 5 query strings
        When: PlaceholderTextEncoder.encode_batch() is called
        Then: Encoding completes in <50ms
        """
        # Act
        result = benchmark(placeholder_encoder.encode_batch, sample_queries)

        # Assert
        assert result.shape == (5, 768)
        assert benchmark.stats["mean"] < 0.050  # 50ms
