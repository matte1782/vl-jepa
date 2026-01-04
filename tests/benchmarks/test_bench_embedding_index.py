"""
Performance Benchmarks for Embedding Index
TEST_IDs: T007.9, T007.10

IMPLEMENTS: Week 4 Day 1 - Benchmark Implementation
"""

import numpy as np
import pytest

from vl_jepa.index import EmbeddingIndex


@pytest.fixture
def index_10k() -> EmbeddingIndex:
    """Create an index with 10,000 L2-normalized embeddings."""
    index = EmbeddingIndex(dimension=768)
    embeddings = np.random.randn(10000, 768).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    ids = list(range(10000))
    index.add_batch(embeddings, ids)
    return index


@pytest.fixture
def index_100k() -> EmbeddingIndex:
    """Create an index with 100,000 L2-normalized embeddings."""
    index = EmbeddingIndex(dimension=768)
    embeddings = np.random.randn(100000, 768).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    ids = list(range(100000))
    index.add_batch(embeddings, ids)
    return index


@pytest.mark.benchmark
class TestEmbeddingIndexBenchmarks:
    """Performance benchmarks for FAISS index operations."""

    # T007.9: Search 10k vectors <10ms
    def test_search_10k_vectors(
        self,
        benchmark,
        index_10k: EmbeddingIndex,
        sample_embedding: np.ndarray,
    ) -> None:
        """
        SPEC: S007
        TEST_ID: T007.9
        BUDGET: <10ms for 10k vectors
        Given: An index with 10,000 vectors
        When: search(k=10) is called
        Then: Search completes in <10ms
        """
        # Act
        result = benchmark(index_10k.search, sample_embedding, k=10)

        # Assert
        assert len(result) == 10
        assert benchmark.stats["mean"] < 0.010  # 10ms

    # T007.10: Search 100k vectors <100ms
    @pytest.mark.slow
    def test_search_100k_vectors(
        self,
        benchmark,
        index_100k: EmbeddingIndex,
        sample_embedding: np.ndarray,
    ) -> None:
        """
        SPEC: S007
        TEST_ID: T007.10
        BUDGET: <100ms for 100k vectors
        Given: An index with 100,000 vectors
        When: search(k=10) is called
        Then: Search completes in <100ms
        """
        # Act
        result = benchmark(index_100k.search, sample_embedding, k=10)

        # Assert
        assert len(result) == 10
        assert benchmark.stats["mean"] < 0.100  # 100ms

    def test_add_batch_performance(self, benchmark) -> None:
        """
        TEST_ID: T007.11
        BUDGET: Add 1000 vectors <100ms
        Given: An empty index
        When: add_batch with 1000 vectors is called
        Then: Adding completes in <100ms
        """
        # Arrange
        embeddings = np.random.randn(1000, 768).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        ids = list(range(1000))

        def add_batch() -> None:
            index = EmbeddingIndex(dimension=768)
            index.add_batch(embeddings, ids)

        # Act
        benchmark(add_batch)

        # Assert
        assert benchmark.stats["mean"] < 0.100  # 100ms
