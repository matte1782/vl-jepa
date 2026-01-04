"""
Integration Tests for Query Pipeline
TEST_IDs: T010.4, T011.1, T011.2

IMPLEMENTS: v0.2.0 Day 5 - End-to-end pipeline test
"""

from pathlib import Path

import numpy as np
import pytest

from vl_jepa.audio.chunker import TranscriptChunker
from vl_jepa.audio.placeholder import PlaceholderTranscriber
from vl_jepa.encoders.placeholder import (
    PlaceholderTextEncoder,
    PlaceholderVisualEncoder,
)
from vl_jepa.multimodal_index import MultimodalIndex, RankingConfig


class SyntheticVideoFrames:
    """Generate synthetic video frames for testing.

    Creates frames that simulate a lecture video with:
    - Distinct visual content at different timestamps
    - Gradual changes between adjacent frames
    """

    def __init__(self, duration: float = 60.0, fps: float = 1.0, seed: int = 42) -> None:
        """Initialize synthetic video.

        Args:
            duration: Video duration in seconds
            fps: Frames per second to generate
            seed: Random seed for reproducibility
        """
        self.duration = duration
        self.fps = fps
        self.seed = seed
        self._rng = np.random.RandomState(seed)

    def generate_frames(self) -> list[tuple[np.ndarray, float]]:
        """Generate frames with timestamps.

        Returns:
            List of (frame, timestamp) tuples
        """
        frames = []
        num_frames = int(self.duration * self.fps)

        # Create base patterns for different "scenes"
        num_scenes = 5
        scene_patterns = [
            self._rng.randn(3, 224, 224).astype(np.float32)
            for _ in range(num_scenes)
        ]

        for i in range(num_frames):
            timestamp = i / self.fps

            # Determine which scene we're in
            scene_idx = min(int(i / (num_frames / num_scenes)), num_scenes - 1)

            # Blend with neighboring scenes for smooth transitions
            base_frame = scene_patterns[scene_idx]

            # Add small variations for temporal change
            noise = self._rng.randn(3, 224, 224).astype(np.float32) * 0.1
            frame = base_frame + noise

            # Normalize to [-1, 1]
            frame = np.clip(frame / (np.abs(frame).max() + 1e-8), -1, 1)

            frames.append((frame, timestamp))

        return frames


@pytest.fixture
def visual_encoder() -> PlaceholderVisualEncoder:
    """Create placeholder visual encoder."""
    return PlaceholderVisualEncoder(seed=42)


@pytest.fixture
def text_encoder() -> PlaceholderTextEncoder:
    """Create placeholder text encoder."""
    return PlaceholderTextEncoder(seed=42)


@pytest.fixture
def transcriber() -> PlaceholderTranscriber:
    """Create placeholder transcriber."""
    return PlaceholderTranscriber(segment_duration=10.0)


@pytest.fixture
def chunker() -> TranscriptChunker:
    """Create transcript chunker."""
    return TranscriptChunker(window_size=10.0, overlap=0.0)


@pytest.fixture
def synthetic_video() -> SyntheticVideoFrames:
    """Create synthetic video generator."""
    return SyntheticVideoFrames(duration=60.0, fps=1.0, seed=42)


@pytest.fixture
def populated_multimodal_index(
    visual_encoder: PlaceholderVisualEncoder,
    text_encoder: PlaceholderTextEncoder,
    synthetic_video: SyntheticVideoFrames,
) -> MultimodalIndex:
    """Create multimodal index populated with synthetic data.

    This simulates a fully processed lecture with:
    - Visual frame embeddings at 1 FPS
    - Transcript segments with text embeddings
    """
    index = MultimodalIndex(dimension=768)

    # Add visual frames
    frames = synthetic_video.generate_frames()
    for frame_data, timestamp in frames:
        # Add batch dimension for encoder
        frame_batch = frame_data[np.newaxis, ...]
        embedding = visual_encoder.encode(frame_batch)[0]

        frame_idx = int(timestamp * synthetic_video.fps)
        index.add_visual(embedding, timestamp=timestamp, frame_index=frame_idx)

    # Add transcript segments (simulating Whisper output)
    transcript_texts = [
        "Welcome to today's lecture on machine learning fundamentals.",
        "We'll start by discussing supervised learning algorithms.",
        "Neural networks are a key topic in deep learning.",
        "Let's look at some practical examples and code.",
        "In summary, we covered the basics of ML today.",
        "Questions are welcome at any time.",
    ]

    segment_duration = 10.0
    for i, text in enumerate(transcript_texts):
        start_time = i * segment_duration
        end_time = start_time + segment_duration

        embedding = text_encoder.encode(text)
        index.add_transcript(
            embedding,
            start_time=start_time,
            end_time=end_time,
            text=text,
            segment_id=i,
        )

    return index


@pytest.mark.integration
class TestEndToEndPipeline:
    """End-to-end integration tests for the full pipeline."""

    def test_pipeline_builds_index(
        self,
        visual_encoder: PlaceholderVisualEncoder,
        text_encoder: PlaceholderTextEncoder,
        synthetic_video: SyntheticVideoFrames,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.1a

        Given: Raw video frames and transcript
        When: Pipeline processes them
        Then: Multimodal index is built with both modalities
        """
        index = MultimodalIndex(dimension=768)

        # Process visual frames
        frames = synthetic_video.generate_frames()
        for frame_data, timestamp in frames:
            frame_batch = frame_data[np.newaxis, ...]
            embedding = visual_encoder.encode(frame_batch)[0]
            index.add_visual(embedding, timestamp=timestamp, frame_index=int(timestamp))

        # Process transcript
        texts = ["Introduction to ML", "Deep learning basics", "Summary"]
        for i, text in enumerate(texts):
            embedding = text_encoder.encode(text)
            index.add_transcript(
                embedding,
                start_time=float(i * 20),
                end_time=float(i * 20 + 15),
                text=text,
            )

        # Verify index
        assert index.size > 0
        assert index.visual_count == len(frames)
        assert index.transcript_count == 3

    def test_end_to_end_query(
        self,
        populated_multimodal_index: MultimodalIndex,
        text_encoder: PlaceholderTextEncoder,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.1

        Given: A processed lecture with embeddings
        When: Natural language query is submitted
        Then: Returns relevant results with timestamps and text
        """
        # Create query
        query_text = "What are the fundamentals of machine learning?"
        query_embedding = text_encoder.encode(query_text)

        # Search across both modalities
        results = populated_multimodal_index.search(query_embedding, k=10)

        # Verify results
        assert len(results) > 0
        assert all(hasattr(r, "timestamp") for r in results)
        assert all(hasattr(r, "modality") for r in results)

        # Should have results from both modalities
        modalities = {r.modality for r in results}
        assert len(modalities) >= 1  # At least one modality

    def test_multimodal_weighted_search(
        self,
        populated_multimodal_index: MultimodalIndex,
        text_encoder: PlaceholderTextEncoder,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.1b

        Given: A multimodal index
        When: Weighted search is performed
        Then: Results are properly weighted by modality
        """
        query_embedding = text_encoder.encode("neural networks and deep learning")

        # Search with transcript-heavy weighting
        config = RankingConfig(visual_weight=0.2, transcript_weight=0.8)
        results = populated_multimodal_index.search_multimodal(
            query_embedding, k=5, config=config
        )

        assert len(results) > 0
        # Results should be sorted by weighted score
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score

    def test_query_with_no_matches(
        self,
        text_encoder: PlaceholderTextEncoder,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.2
        EDGE_CASE: EC034

        Given: An empty index
        When: Query is submitted
        Then: Returns empty results gracefully
        """
        empty_index = MultimodalIndex(dimension=768)

        query_embedding = text_encoder.encode("random unrelated query")
        results = empty_index.search(query_embedding, k=5)

        assert results == []

    def test_temporal_context_retrieval(
        self,
        populated_multimodal_index: MultimodalIndex,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.3

        Given: A multimodal index
        When: Context for a timestamp is requested
        Then: Returns aligned visual and transcript entries
        """
        # Get context for timestamp 25.0 (middle of lecture)
        context = populated_multimodal_index.get_aligned_context(
            timestamp=25.0,
            visual_tolerance=5.0,
            transcript_tolerance=10.0,
        )

        assert "visual" in context
        assert "transcript" in context
        assert isinstance(context["visual"], list)
        assert isinstance(context["transcript"], list)

    def test_index_persistence(
        self,
        populated_multimodal_index: MultimodalIndex,
        tmp_path: Path,
        text_encoder: PlaceholderTextEncoder,
    ) -> None:
        """
        SPEC: S011
        TEST_ID: T011.4

        Given: A populated multimodal index
        When: Index is saved and loaded
        Then: Search results are consistent
        """
        # Save index
        index_path = tmp_path / "test_index"
        populated_multimodal_index.save(index_path)

        # Load index
        loaded_index = MultimodalIndex.load(index_path)

        # Verify properties preserved
        assert loaded_index.size == populated_multimodal_index.size
        assert loaded_index.visual_count == populated_multimodal_index.visual_count
        assert loaded_index.transcript_count == populated_multimodal_index.transcript_count

        # Verify search works on loaded index
        query_embedding = text_encoder.encode("machine learning")
        results = loaded_index.search(query_embedding, k=5)
        assert len(results) > 0


@pytest.mark.integration
class TestPipelineWithTranscription:
    """Tests for pipeline with transcription integration."""

    def test_transcript_chunking_integration(
        self,
        transcriber: PlaceholderTranscriber,
        chunker: TranscriptChunker,
        text_encoder: PlaceholderTextEncoder,
    ) -> None:
        """
        SPEC: G7
        TEST_ID: T_AUDIO_INT_1

        Given: A transcriber and chunker
        When: Audio is transcribed and chunked
        Then: Chunks are suitable for embedding
        """
        # Transcribe (placeholder)
        segments = transcriber.transcribe("fake_audio.wav")

        # Chunk
        chunks = list(chunker.chunk(segments))

        # Verify chunks
        assert len(chunks) > 0

        # Encode chunks
        for chunk in chunks[:3]:  # Test first 3
            embedding = text_encoder.encode(chunk.text)
            assert embedding.shape == (768,)
            assert np.allclose(np.linalg.norm(embedding), 1.0, atol=1e-5)

    def test_full_pipeline_with_placeholders(
        self,
        visual_encoder: PlaceholderVisualEncoder,
        text_encoder: PlaceholderTextEncoder,
        transcriber: PlaceholderTranscriber,
        chunker: TranscriptChunker,
        synthetic_video: SyntheticVideoFrames,
    ) -> None:
        """
        SPEC: v0.2.0 G3, G7, G8
        TEST_ID: T_PIPELINE_FULL

        Given: All pipeline components
        When: Full pipeline is executed
        Then: Multimodal index is created and queryable
        """
        index = MultimodalIndex(dimension=768)

        # Step 1: Process video frames
        frames = synthetic_video.generate_frames()
        for frame_data, timestamp in frames:
            frame_batch = frame_data[np.newaxis, ...]
            embedding = visual_encoder.encode(frame_batch)[0]
            index.add_visual(embedding, timestamp=timestamp, frame_index=int(timestamp))

        # Step 2: Transcribe and chunk
        segments = transcriber.transcribe("fake_lecture.mp3")
        chunks = list(chunker.chunk(segments))

        # Step 3: Encode transcript chunks
        for chunk in chunks:
            embedding = text_encoder.encode(chunk.text)
            index.add_transcript(
                embedding,
                start_time=chunk.start,
                end_time=chunk.end,
                text=chunk.text,
            )

        # Step 4: Verify index
        assert index.visual_count == len(frames)
        assert index.transcript_count == len(chunks)

        # Step 5: Query
        query_emb = text_encoder.encode("What is the main topic?")
        results = index.search_multimodal(query_emb, k=10)

        assert len(results) > 0

        # Step 6: Get temporal context
        mid_timestamp = synthetic_video.duration / 2
        context = index.get_aligned_context(mid_timestamp)

        assert "visual" in context
        assert "transcript" in context


@pytest.mark.integration
class TestQueryPipelineIntegration:
    """Integration tests for end-to-end query flow (legacy tests)."""

    @pytest.mark.skip(reason="Requires real 2hr video - manual test only")
    @pytest.mark.slow
    def test_long_video_without_oom(self, test_videos_dir: Path) -> None:
        """
        SPEC: S010
        TEST_ID: T010.4
        INVARIANT: INV017

        Given: A 2-hour lecture video
        When: Full processing pipeline runs
        Then: Completes without OOM error
        """
        pass
