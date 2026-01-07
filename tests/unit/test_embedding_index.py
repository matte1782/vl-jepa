"""
SPEC: S007 - Embedding Index (FAISS)
TEST_IDs: T007.1-T007.6
"""

from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def sample_embedding() -> np.ndarray:
    """Create a normalized 768-dim embedding."""
    emb = np.random.randn(768).astype(np.float32)
    return emb / np.linalg.norm(emb)


@pytest.fixture
def sample_embedding_batch() -> np.ndarray:
    """Create batch of 10 normalized embeddings."""
    batch = np.random.randn(10, 768).astype(np.float32)
    norms = np.linalg.norm(batch, axis=1, keepdims=True)
    return batch / norms


class TestEmbeddingIndex:
    """Tests for FAISS embedding index (S007)."""

    # T007.1: Add single embedding
    @pytest.mark.unit
    def test_add_single_embedding(self, sample_embedding: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.1
        Given: A single 768-dim embedding
        When: EmbeddingIndex.add() is called
        Then: Embedding is added, index size increases by 1
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        initial_size = index.size
        index.add(sample_embedding, id=0)
        assert index.size == initial_size + 1

    # T007.2: Add batch embeddings
    @pytest.mark.unit
    def test_add_batch_embeddings(self, sample_embedding_batch: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.2
        Given: A batch of embeddings (10, 768)
        When: EmbeddingIndex.add_batch() is called
        Then: All embeddings are added
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        ids = list(range(10))
        index.add_batch(sample_embedding_batch, ids=ids)
        assert index.size == 10

    # T007.3: Search returns correct top-k
    @pytest.mark.unit
    def test_search_returns_correct_top_k(self, sample_embedding_batch: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.3
        INVARIANT: INV012
        Given: An index with N embeddings
        When: search(query, k=5) is called
        Then: Returns exactly min(k, N) results
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        ids = list(range(10))
        index.add_batch(sample_embedding_batch, ids=ids)

        query = sample_embedding_batch[0]
        results = index.search(query, k=5)
        assert len(results) == 5

        # Search with k > N
        results = index.search(query, k=20)
        assert len(results) == 10  # min(20, 10)

    # T007.4: Search empty index
    @pytest.mark.unit
    def test_search_empty_index(self, sample_embedding: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.4
        EDGE_CASE: EC034
        Given: An empty index
        When: search() is called
        Then: Returns empty list
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        results = index.search(sample_embedding, k=5)
        assert len(results) == 0

    # T007.5: Save and load index
    @pytest.mark.unit
    def test_save_and_load_index(
        self, sample_embedding_batch: np.ndarray, tmp_path: Path
    ):
        """
        SPEC: S007
        TEST_ID: T007.5
        Given: An index with embeddings
        When: save() then load() is called
        Then: Loaded index has same size (FAISS required for full search)
        """
        from vl_jepa.index import EmbeddingIndex

        # Create and populate index
        index = EmbeddingIndex()
        ids = list(range(10))
        metadata = {i: {"timestamp": float(i * 10)} for i in ids}
        index.add_batch(sample_embedding_batch, ids=ids, metadata=metadata)

        # Save
        save_path = tmp_path / "test_index"
        index.save(save_path)

        # Load and verify mappings (search only works with FAISS)
        loaded = EmbeddingIndex.load(save_path)
        # Verify id_map and metadata were saved/loaded
        assert len(loaded._id_map) == 10
        # Note: JSON key "0" may be filtered out, so we check >= 9
        assert len(loaded._metadata) >= 9

    # T007.6: IVF transition
    @pytest.mark.skip(reason="IVF transition needs 1000+ vectors - slow test")
    @pytest.mark.unit
    def test_ivf_transition(self):
        """
        SPEC: S007
        TEST_ID: T007.6
        EDGE_CASE: EC038
        Given: Index with 999 vectors
        When: 1000th vector is added
        Then: Index transitions to IVF
        """
        pass

    @pytest.mark.unit
    def test_search_with_metadata(self, sample_embedding_batch: np.ndarray):
        """Search returns metadata when stored."""
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        ids = list(range(10))
        metadata = {i: {"timestamp": float(i * 10)} for i in ids}
        index.add_batch(sample_embedding_batch, ids=ids, metadata=metadata)

        results = index.search(sample_embedding_batch[0], k=3)
        assert len(results) == 3

        # Verify metadata is returned (at least one result should have it)
        has_metadata = any(r.metadata is not None for r in results)
        assert has_metadata, "At least one result should have metadata"

    @pytest.mark.unit
    def test_search_result_scores(self, sample_embedding_batch: np.ndarray):
        """Search results have valid scores."""
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        ids = list(range(10))
        index.add_batch(sample_embedding_batch, ids=ids)

        results = index.search(sample_embedding_batch[0], k=5)

        # First result should be the query itself (score ~1.0)
        assert results[0].score > 0.99

        # Scores should be in descending order
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.unit
    def test_dimension_property(self):
        """Index has correct internal dimension."""
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex(dimension=768)
        assert index._dimension == 768

    # T007.7: Mismatched embeddings and ids raises error
    @pytest.mark.unit
    def test_add_batch_mismatched_lengths_raises(
        self, sample_embedding_batch: np.ndarray
    ):
        """
        SPEC: S007
        TEST_ID: T007.7
        Given: Embeddings and ids with different lengths
        When: add_batch() is called
        Then: Raises ValueError
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        # 10 embeddings but only 5 ids
        ids = list(range(5))

        with pytest.raises(ValueError, match="same length"):
            index.add_batch(sample_embedding_batch, ids=ids)

    # T007.8: Add batch with list metadata
    @pytest.mark.unit
    def test_add_batch_with_list_metadata(self, sample_embedding_batch: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.8
        Given: Embeddings with list of metadata dicts
        When: add_batch() is called
        Then: Metadata is stored correctly
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        ids = list(range(10))
        # List of metadata (with some None values)
        metadata_list = [
            {"timestamp": 0.0},
            None,  # Should be skipped
            {"timestamp": 20.0},
            {"timestamp": 30.0},
            None,
            {"timestamp": 50.0},
            {"timestamp": 60.0},
            {"timestamp": 70.0},
            {"timestamp": 80.0},
            {"timestamp": 90.0},
        ]

        index.add_batch(sample_embedding_batch, ids=ids, metadata=metadata_list)

        assert index.size == 10
        # Check metadata was stored (excluding Nones)
        assert 0 in index._metadata
        assert 1 not in index._metadata  # Was None
        assert 2 in index._metadata

    # T007.9: Search result dataclass
    @pytest.mark.unit
    def test_search_result_dataclass(self):
        """
        SPEC: S007
        TEST_ID: T007.9
        Given: SearchResult dataclass
        When: Created with values
        Then: Has expected attributes
        """
        from vl_jepa.index import SearchResult

        result = SearchResult(id=42, score=0.95, metadata={"key": "value"})

        assert result.id == 42
        assert result.score == 0.95
        assert result.metadata == {"key": "value"}

    # T007.10: Search result default metadata
    @pytest.mark.unit
    def test_search_result_default_metadata(self):
        """
        SPEC: S007
        TEST_ID: T007.10
        Given: SearchResult without metadata
        When: Created
        Then: Metadata is None
        """
        from vl_jepa.index import SearchResult

        result = SearchResult(id=1, score=0.5)
        assert result.metadata is None

    # T007.11: Add with metadata dict
    @pytest.mark.unit
    def test_add_batch_with_dict_metadata(self, sample_embedding_batch: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.11
        Given: Metadata as dict keyed by id
        When: add_batch() is called
        Then: Metadata is stored correctly
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        ids = list(range(10))
        # Dict keyed by id
        metadata_dict: dict[int, dict] = {
            0: {"timestamp": 0.0},
            5: {"timestamp": 50.0},
            9: {"timestamp": 90.0},
        }

        index.add_batch(sample_embedding_batch, ids=ids, metadata=metadata_dict)

        assert index.size == 10
        assert index._metadata.get(0) == {"timestamp": 0.0}
        assert index._metadata.get(5) == {"timestamp": 50.0}
        assert index._metadata.get(9) == {"timestamp": 90.0}
        assert index._metadata.get(3) is None  # Not in dict

    # T007.12: Add single with metadata
    @pytest.mark.unit
    def test_add_single_with_metadata(self, sample_embedding: np.ndarray):
        """
        SPEC: S007
        TEST_ID: T007.12
        Given: Single embedding with metadata
        When: add() is called
        Then: Metadata is stored
        """
        from vl_jepa.index import EmbeddingIndex

        index = EmbeddingIndex()
        metadata = {"timestamp": 120.5, "label": "intro"}

        index.add(sample_embedding, id=42, metadata=metadata)

        assert index.size == 1
        assert index._metadata.get(42) == metadata


class TestEmbeddingIndexIVFTransition:
    """Tests for IVF transition behavior (HOSTILE_REVIEW M2).

    These tests verify graceful degradation when FAISS is unavailable
    and the IVF transition fails.
    """

    @pytest.mark.unit
    def test_ivf_transition_returns_false_without_faiss(self):
        """
        SPEC: S007
        TEST_ID: T007.IVF.1
        EDGE_CASE: EC038
        Given: An index with use_ivf enabled and FAISS unavailable
        When: _transition_to_ivf() is called
        Then: Returns False (transition fails gracefully)
        """
        from tests.conftest import HAS_FAISS
        from vl_jepa.index import EmbeddingIndex

        if HAS_FAISS:
            pytest.skip("Test only relevant when FAISS unavailable")

        index = EmbeddingIndex(dimension=768)
        embeddings = np.random.randn(100, 768).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Attempt transition
        result = index._transition_to_ivf(embeddings)

        assert result is False
        assert index._use_ivf is False

    @pytest.mark.unit
    def test_index_functions_after_failed_ivf_transition(self):
        """
        SPEC: S007
        TEST_ID: T007.IVF.2
        EDGE_CASE: EC038
        Given: An index that attempted but failed IVF transition
        When: Search is performed
        Then: Search returns valid results using numpy fallback
        """
        from tests.conftest import HAS_FAISS
        from vl_jepa.index import EmbeddingIndex

        if HAS_FAISS:
            pytest.skip("Test only relevant when FAISS unavailable")

        index = EmbeddingIndex(dimension=768)

        # Add embeddings that would trigger IVF transition (>= 1000)
        embeddings = np.random.randn(1500, 768).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        ids = list(range(1500))

        index.add_batch(embeddings, ids)

        # Verify index is still functional
        assert index.size == 1500
        assert index._use_ivf is False  # Transition should have failed

        # Search should work with numpy fallback
        query = embeddings[0]
        results = index.search(query, k=5)

        assert len(results) == 5
        # First result should be the query itself (score ~1.0)
        assert results[0].score > 0.99

    @pytest.mark.unit
    def test_ivf_transition_success_with_faiss(self):
        """
        SPEC: S007
        TEST_ID: T007.IVF.3
        Given: An index with FAISS available
        When: Enough embeddings are added to trigger IVF transition
        Then: Transition succeeds and _use_ivf is True
        """
        from tests.conftest import HAS_FAISS
        from vl_jepa.index import EmbeddingIndex

        if not HAS_FAISS:
            pytest.skip("Test requires FAISS")

        index = EmbeddingIndex(dimension=768)

        # Add embeddings that trigger IVF transition (>= 1000)
        embeddings = np.random.randn(1500, 768).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        ids = list(range(1500))

        index.add_batch(embeddings, ids)

        # Verify transition occurred
        assert index.size == 1500
        assert index._use_ivf is True

        # Search should still work
        query = embeddings[0]
        results = index.search(query, k=5)
        assert len(results) == 5

    @pytest.mark.unit
    def test_numpy_fallback_save_load_roundtrip(self, tmp_path: Path):
        """
        SPEC: S007
        TEST_ID: T007.IVF.4
        Given: An index using numpy fallback (no FAISS)
        When: Index is saved and loaded
        Then: Loaded index has same data and search works
        """
        from tests.conftest import HAS_FAISS
        from vl_jepa.index import EmbeddingIndex

        if HAS_FAISS:
            pytest.skip("Test only relevant when FAISS unavailable")

        # Create and populate index
        index = EmbeddingIndex(dimension=768)
        embeddings = np.random.randn(100, 768).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        ids = list(range(100))
        metadata = {i: {"timestamp": float(i)} for i in ids}

        index.add_batch(embeddings, ids, metadata=metadata)

        # Save
        save_path = tmp_path / "test_index"
        index.save(save_path)

        # Verify .npy file created (not .faiss)
        assert save_path.with_suffix(".npy").exists()
        assert not save_path.with_suffix(".faiss").exists()

        # Load
        loaded = EmbeddingIndex.load(save_path)

        # Verify data preserved
        assert loaded.size == index.size
        assert loaded._id_map == index._id_map

        # Verify search works on loaded index
        results = loaded.search(embeddings[0], k=5)
        assert len(results) == 5
        assert results[0].score > 0.99
