"""
Performance Benchmarks for Query Pipeline
TEST_IDs: T011.3

IMPLEMENTS: Week 4 Day 1 - Benchmark Implementation
"""

import numpy as np
import pytest

from vl_jepa.index import EmbeddingIndex
from vl_jepa.multimodal_index import MultimodalIndex, RankingConfig


@pytest.fixture
def populated_index() -> EmbeddingIndex:
    """Create a populated embedding index for query benchmarks."""
    index = EmbeddingIndex(dimension=768)
    embeddings = np.random.randn(1000, 768).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    ids = list(range(1000))
    index.add_batch(embeddings, ids)
    return index


@pytest.fixture
def populated_multimodal_index() -> MultimodalIndex:
    """Create a multimodal index with visual and transcript entries."""
    index = MultimodalIndex(dimension=768)

    # Add 500 visual entries (simulating 500 frames)
    for i in range(500):
        emb = np.random.randn(768).astype(np.float32)
        emb /= np.linalg.norm(emb)
        index.add_visual(emb, timestamp=i * 2.0, frame_index=i)

    # Add 200 transcript entries (simulating 200 text chunks)
    for i in range(200):
        emb = np.random.randn(768).astype(np.float32)
        emb /= np.linalg.norm(emb)
        index.add_transcript(
            emb,
            start_time=i * 5.0,
            end_time=i * 5.0 + 4.5,
            text=f"Transcript chunk {i} with some content.",
        )

    return index


@pytest.mark.benchmark
class TestQueryPipelineBenchmarks:
    """Performance benchmarks for end-to-end query."""

    # T011.3: Query latency <100ms
    def test_query_latency_simple(
        self,
        benchmark,
        populated_index: EmbeddingIndex,
        sample_embedding: np.ndarray,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.3
        BUDGET: <100ms per query
        Given: An index with 1000 embeddings
        When: search(k=10) is called
        Then: Results returned in <100ms
        """
        # Act
        result = benchmark(populated_index.search, sample_embedding, k=10)

        # Assert
        assert len(result) == 10
        assert benchmark.stats["mean"] < 0.100  # 100ms

    def test_multimodal_search_latency(
        self,
        benchmark,
        populated_multimodal_index: MultimodalIndex,
        sample_embedding: np.ndarray,
    ) -> None:
        """
        TEST_ID: T011.4
        BUDGET: <100ms per multimodal query
        Given: A multimodal index with 700 entries (500 visual + 200 transcript)
        When: search(k=10) is called
        Then: Results returned in <100ms
        """
        # Act
        result = benchmark(populated_multimodal_index.search, sample_embedding, k=10)

        # Assert
        assert len(result) <= 10
        assert benchmark.stats["mean"] < 0.100  # 100ms

    def test_multimodal_fusion_search_latency(
        self,
        benchmark,
        populated_multimodal_index: MultimodalIndex,
        sample_embedding: np.ndarray,
    ) -> None:
        """
        TEST_ID: T011.5
        BUDGET: <150ms per multimodal fusion query
        Given: A multimodal index with 700 entries
        When: search_multimodal with weighted fusion is called
        Then: Results returned in <150ms (includes fusion ranking overhead)
        """
        config = RankingConfig(visual_weight=0.3, transcript_weight=0.7)

        # Act
        result = benchmark(
            populated_multimodal_index.search_multimodal,
            sample_embedding,
            k=10,
            config=config,
        )

        # Assert
        assert len(result) <= 10
        assert benchmark.stats["mean"] < 0.150  # 150ms

    def test_timestamp_search_latency(
        self,
        benchmark,
        populated_multimodal_index: MultimodalIndex,
    ) -> None:
        """
        TEST_ID: T011.6
        BUDGET: <50ms per timestamp search
        Given: A multimodal index with 700 entries
        When: search_by_timestamp is called
        Then: Results returned in <50ms
        """
        # Act
        result = benchmark(
            populated_multimodal_index.search_by_timestamp,
            timestamp=100.0,
            tolerance=5.0,
        )

        # Assert
        assert isinstance(result, list)
        assert benchmark.stats["mean"] < 0.050  # 50ms
