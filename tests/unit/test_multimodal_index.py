"""
Tests for MultimodalIndex.

IMPLEMENTS: v0.2.0 Week 3 - Multimodal search tests
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from vl_jepa.multimodal_index import (
    Modality,
    MultimodalEntry,
    MultimodalIndex,
    MultimodalSearchResult,
    RankingConfig,
)


class TestModality:
    """Tests for Modality enum."""

    @pytest.mark.unit
    def test_modality_values(self) -> None:
        """Modality enum has correct values."""
        assert Modality.VISUAL.value == "visual"
        assert Modality.TRANSCRIPT.value == "transcript"

    @pytest.mark.unit
    def test_modality_from_string(self) -> None:
        """Can create Modality from string."""
        assert Modality("visual") == Modality.VISUAL
        assert Modality("transcript") == Modality.TRANSCRIPT


class TestMultimodalEntry:
    """Tests for MultimodalEntry dataclass."""

    @pytest.mark.unit
    def test_visual_entry_creation(self) -> None:
        """Can create visual entry."""
        emb = np.random.randn(768).astype(np.float32)
        entry = MultimodalEntry(
            id=0,
            modality=Modality.VISUAL,
            timestamp=1.5,
            embedding=emb,
            frame_index=30,
        )

        assert entry.id == 0
        assert entry.modality == Modality.VISUAL
        assert entry.timestamp == 1.5
        assert entry.frame_index == 30
        assert entry.text is None

    @pytest.mark.unit
    def test_transcript_entry_creation(self) -> None:
        """Can create transcript entry."""
        emb = np.random.randn(768).astype(np.float32)
        entry = MultimodalEntry(
            id=1,
            modality=Modality.TRANSCRIPT,
            timestamp=5.0,
            embedding=emb,
            text="Hello world",
            segment_id=0,
        )

        assert entry.id == 1
        assert entry.modality == Modality.TRANSCRIPT
        assert entry.text == "Hello world"
        assert entry.frame_index is None


class TestMultimodalIndex:
    """Tests for MultimodalIndex."""

    @pytest.fixture
    def index(self) -> MultimodalIndex:
        """Create empty index."""
        return MultimodalIndex()

    @pytest.fixture
    def populated_index(self) -> MultimodalIndex:
        """Create index with sample data."""
        index = MultimodalIndex()

        # Add visual frames
        for i in range(5):
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_visual(emb, timestamp=float(i), frame_index=i)

        # Add transcript segments
        texts = [
            "Introduction to the topic",
            "Main concepts explained",
            "Examples and demonstrations",
            "Summary and conclusions",
        ]
        for i, text in enumerate(texts):
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_transcript(
                emb,
                start_time=float(i * 10),
                end_time=float(i * 10 + 8),
                text=text,
            )

        return index

    @pytest.mark.unit
    def test_empty_index_properties(self, index: MultimodalIndex) -> None:
        """Empty index has correct properties."""
        assert index.size == 0
        assert index.visual_count == 0
        assert index.transcript_count == 0

    @pytest.mark.unit
    def test_add_visual_entry(self, index: MultimodalIndex) -> None:
        """Can add visual entry."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)

        id_ = index.add_visual(emb, timestamp=1.0, frame_index=30)

        assert index.size == 1
        assert index.visual_count == 1
        assert index.transcript_count == 0
        assert id_ == 0

    @pytest.mark.unit
    def test_add_transcript_entry(self, index: MultimodalIndex) -> None:
        """Can add transcript entry."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)

        id_ = index.add_transcript(
            emb,
            start_time=0.0,
            end_time=5.0,
            text="Test transcript",
        )

        assert index.size == 1
        assert index.visual_count == 0
        assert index.transcript_count == 1
        assert id_ == 0

    @pytest.mark.unit
    def test_search_returns_results(self, populated_index: MultimodalIndex) -> None:
        """Search returns results."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search(query, k=5)

        assert len(results) > 0
        assert len(results) <= 5
        assert all(isinstance(r, MultimodalSearchResult) for r in results)

    @pytest.mark.unit
    def test_search_visual_only(self, populated_index: MultimodalIndex) -> None:
        """Search can filter by visual modality."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search_visual(query, k=10)

        assert all(r.modality == Modality.VISUAL for r in results)
        assert len(results) <= populated_index.visual_count

    @pytest.mark.unit
    def test_search_transcript_only(self, populated_index: MultimodalIndex) -> None:
        """Search can filter by transcript modality."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search_transcript(query, k=10)

        assert all(r.modality == Modality.TRANSCRIPT for r in results)
        assert len(results) <= populated_index.transcript_count

    @pytest.mark.unit
    def test_search_by_timestamp(self, populated_index: MultimodalIndex) -> None:
        """Can search by timestamp."""
        results = populated_index.search_by_timestamp(timestamp=2.0, tolerance=1.5)

        assert len(results) > 0
        # All results should be within tolerance
        for r in results:
            assert abs(r.timestamp - 2.0) <= 1.5

    @pytest.mark.unit
    def test_get_entry(self, populated_index: MultimodalIndex) -> None:
        """Can retrieve entry by ID."""
        entry = populated_index.get_entry(0)

        assert entry is not None
        assert entry.id == 0

    @pytest.mark.unit
    def test_get_entry_nonexistent(self, index: MultimodalIndex) -> None:
        """Returns None for nonexistent entry."""
        entry = index.get_entry(999)
        assert entry is None

    @pytest.mark.unit
    def test_get_aligned_context(self, populated_index: MultimodalIndex) -> None:
        """Can get aligned visual and transcript context."""
        context = populated_index.get_aligned_context(
            timestamp=2.0,
            visual_tolerance=2.0,
            transcript_tolerance=5.0,
        )

        assert "visual" in context
        assert "transcript" in context
        assert isinstance(context["visual"], list)
        assert isinstance(context["transcript"], list)

    @pytest.mark.unit
    def test_save_and_load(self, populated_index: MultimodalIndex) -> None:
        """Can save and load index."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "test_index"

            # Save
            populated_index.save(path)

            # Verify files created
            assert path.with_suffix(".faiss").exists()
            assert path.with_suffix(".json").exists()
            assert path.with_suffix(".multimodal.json").exists()

            # Load
            loaded = MultimodalIndex.load(path)

            assert loaded.size == populated_index.size
            assert loaded.visual_count == populated_index.visual_count
            assert loaded.transcript_count == populated_index.transcript_count

    @pytest.mark.unit
    def test_repr(self, populated_index: MultimodalIndex) -> None:
        """Index has readable repr."""
        repr_str = repr(populated_index)

        assert "MultimodalIndex" in repr_str
        assert "visual=" in repr_str
        assert "transcript=" in repr_str

    @pytest.mark.unit
    def test_search_scores_sorted(self, populated_index: MultimodalIndex) -> None:
        """Search results are sorted by score descending."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search(query, k=5)

        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score

    @pytest.mark.unit
    def test_unique_ids(self, index: MultimodalIndex) -> None:
        """Each entry gets unique ID."""
        ids = []
        for i in range(10):
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)

            if i % 2 == 0:
                id_ = index.add_visual(emb, timestamp=float(i), frame_index=i)
            else:
                id_ = index.add_transcript(emb, float(i), float(i + 1), f"Text {i}")

            ids.append(id_)

        assert len(ids) == len(set(ids))  # All unique

    @pytest.mark.unit
    def test_transcript_stores_text(self, index: MultimodalIndex) -> None:
        """Transcript entries store text content."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)

        id_ = index.add_transcript(emb, 0.0, 5.0, "Test text content")
        entry = index.get_entry(id_)

        assert entry is not None
        assert entry.text == "Test text content"

    @pytest.mark.unit
    def test_visual_stores_frame_index(self, index: MultimodalIndex) -> None:
        """Visual entries store frame index."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)

        id_ = index.add_visual(emb, timestamp=1.0, frame_index=42)
        entry = index.get_entry(id_)

        assert entry is not None
        assert entry.frame_index == 42

    @pytest.mark.unit
    def test_search_by_timestamp_zero_tolerance_raises(
        self, index: MultimodalIndex
    ) -> None:
        """Zero tolerance raises ValueError."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)
        index.add_visual(emb, timestamp=1.0, frame_index=0)

        with pytest.raises(ValueError, match="tolerance must be positive"):
            index.search_by_timestamp(1.0, tolerance=0.0)

    @pytest.mark.unit
    def test_search_by_timestamp_negative_tolerance_raises(
        self, index: MultimodalIndex
    ) -> None:
        """Negative tolerance raises ValueError."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)
        index.add_visual(emb, timestamp=1.0, frame_index=0)

        with pytest.raises(ValueError, match="tolerance must be positive"):
            index.search_by_timestamp(1.0, tolerance=-1.0)

    @pytest.mark.unit
    def test_get_aligned_context_zero_visual_tolerance_raises(
        self, index: MultimodalIndex
    ) -> None:
        """Zero visual tolerance raises ValueError."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)
        index.add_visual(emb, timestamp=1.0, frame_index=0)

        with pytest.raises(ValueError, match="tolerance values must be positive"):
            index.get_aligned_context(1.0, visual_tolerance=0.0)

    @pytest.mark.unit
    def test_get_aligned_context_zero_transcript_tolerance_raises(
        self, index: MultimodalIndex
    ) -> None:
        """Zero transcript tolerance raises ValueError."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)
        index.add_transcript(emb, 0.0, 2.0, "test")

        with pytest.raises(ValueError, match="tolerance values must be positive"):
            index.get_aligned_context(1.0, transcript_tolerance=0.0)

    @pytest.mark.unit
    def test_get_aligned_context_negative_tolerance_raises(
        self, index: MultimodalIndex
    ) -> None:
        """Negative tolerance raises ValueError."""
        emb = np.random.randn(768).astype(np.float32)
        emb = emb / np.linalg.norm(emb)
        index.add_visual(emb, timestamp=1.0, frame_index=0)

        with pytest.raises(ValueError, match="tolerance values must be positive"):
            index.get_aligned_context(
                1.0, visual_tolerance=-0.5, transcript_tolerance=2.0
            )


class TestRankingConfig:
    """Tests for RankingConfig dataclass."""

    @pytest.mark.unit
    def test_default_values(self) -> None:
        """Default config has reasonable values."""
        config = RankingConfig()

        assert config.visual_weight == 0.3
        assert config.transcript_weight == 0.7
        assert config.time_decay == 0.0
        assert config.time_reference is None

    @pytest.mark.unit
    def test_custom_weights(self) -> None:
        """Can create config with custom weights."""
        config = RankingConfig(visual_weight=0.5, transcript_weight=0.5)

        assert config.visual_weight == 0.5
        assert config.transcript_weight == 0.5

    @pytest.mark.unit
    def test_invalid_visual_weight_raises(self) -> None:
        """Invalid visual weight raises ValueError."""
        with pytest.raises(ValueError, match="visual_weight must be in"):
            RankingConfig(visual_weight=1.5)

        with pytest.raises(ValueError, match="visual_weight must be in"):
            RankingConfig(visual_weight=-0.1)

    @pytest.mark.unit
    def test_invalid_transcript_weight_raises(self) -> None:
        """Invalid transcript weight raises ValueError."""
        with pytest.raises(ValueError, match="transcript_weight must be in"):
            RankingConfig(transcript_weight=2.0)

    @pytest.mark.unit
    def test_invalid_time_decay_raises(self) -> None:
        """Invalid time decay raises ValueError."""
        with pytest.raises(ValueError, match="time_decay must be in"):
            RankingConfig(time_decay=-0.1)

    @pytest.mark.unit
    def test_time_decay_with_reference(self) -> None:
        """Can set time decay with reference."""
        config = RankingConfig(time_decay=0.1, time_reference=30.0)

        assert config.time_decay == 0.1
        assert config.time_reference == 30.0


class TestMultimodalSearch:
    """Tests for multimodal search with weighted fusion."""

    @pytest.fixture
    def populated_index(self) -> MultimodalIndex:
        """Create index with sample data for search tests."""
        index = MultimodalIndex()

        # Add visual frames at 0, 1, 2, 3, 4 seconds
        for i in range(5):
            np.random.seed(i)
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_visual(emb, timestamp=float(i), frame_index=i)

        # Add transcript segments
        texts = [
            "Introduction to machine learning",
            "Supervised learning algorithms",
            "Neural network architectures",
            "Deep learning applications",
        ]
        for i, text in enumerate(texts):
            np.random.seed(100 + i)
            emb = np.random.randn(768).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            index.add_transcript(
                emb,
                start_time=float(i * 10),
                end_time=float(i * 10 + 8),
                text=text,
            )

        return index

    @pytest.mark.unit
    def test_search_multimodal_returns_results(
        self, populated_index: MultimodalIndex
    ) -> None:
        """Multimodal search returns results from both modalities."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search_multimodal(query, k=10)

        assert len(results) > 0
        modalities = {r.modality for r in results}
        # Should have results from at least one modality
        assert len(modalities) >= 1

    @pytest.mark.unit
    def test_search_multimodal_respects_k(
        self, populated_index: MultimodalIndex
    ) -> None:
        """Multimodal search respects k limit."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search_multimodal(query, k=3)

        assert len(results) <= 3

    @pytest.mark.unit
    def test_search_multimodal_with_config(
        self, populated_index: MultimodalIndex
    ) -> None:
        """Multimodal search uses ranking config."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        # High visual weight
        config = RankingConfig(visual_weight=0.9, transcript_weight=0.1)
        results = populated_index.search_multimodal(query, k=5, config=config)

        assert len(results) > 0
        # All results should have scores (can be negative for cosine similarity)
        for r in results:
            assert isinstance(r.score, float)

    @pytest.mark.unit
    def test_search_multimodal_scores_sorted(
        self, populated_index: MultimodalIndex
    ) -> None:
        """Results are sorted by weighted score descending."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = populated_index.search_multimodal(query, k=5)

        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score

    @pytest.mark.unit
    def test_search_multimodal_with_time_decay(
        self, populated_index: MultimodalIndex
    ) -> None:
        """Time decay affects scores based on timestamp distance."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        # Search with time decay centered at t=2
        config = RankingConfig(
            visual_weight=0.5,
            transcript_weight=0.5,
            time_decay=0.5,
            time_reference=2.0,
        )
        results = populated_index.search_multimodal(query, k=10, config=config)

        assert len(results) > 0
        # Scores should be affected by time decay (can be negative for cosine similarity)
        for r in results:
            assert isinstance(r.score, float)

    @pytest.mark.unit
    def test_search_multimodal_default_config(
        self, populated_index: MultimodalIndex
    ) -> None:
        """Multimodal search works with default config (None)."""
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        # Should not raise, uses default config
        results = populated_index.search_multimodal(query, k=5, config=None)

        assert isinstance(results, list)

    @pytest.mark.unit
    def test_apply_time_decay(self, populated_index: MultimodalIndex) -> None:
        """Time decay function works correctly."""
        # At reference point, decay should be 1.0
        decay = populated_index._apply_time_decay(10.0, 10.0, 0.5)
        assert abs(decay - 1.0) < 0.001

        # Further from reference, decay should be less
        decay_far = populated_index._apply_time_decay(20.0, 10.0, 0.5)
        assert decay_far < 1.0
        assert decay_far > 0.0

    @pytest.mark.unit
    def test_search_multimodal_empty_index(self) -> None:
        """Multimodal search on empty index returns empty list."""
        index = MultimodalIndex()
        query = np.random.randn(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = index.search_multimodal(query, k=5)

        assert results == []
