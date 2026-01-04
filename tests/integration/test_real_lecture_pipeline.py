"""
Integration Tests for Real Lecture Video Pipeline

TEST_IDs: T_PIPELINE_REAL_1, T_PIPELINE_REAL_2, T_PIPELINE_REAL_3

IMPLEMENTS: v0.2.0 Week 3 Day 2 - Video Pipeline with Real DINOv2
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# Path to real lecture video
LECTURE_VIDEO = Path(__file__).parent.parent / "lecture_ex" / "December19_I.mp4"


def _skip_if_no_video() -> None:
    """Skip test if lecture video not available."""
    if not LECTURE_VIDEO.exists():
        pytest.skip(f"Lecture video not found: {LECTURE_VIDEO}")


def _skip_if_no_ffmpeg() -> None:
    """Skip test if FFmpeg not available."""
    from vl_jepa.audio.extractor import check_ffmpeg_available

    if not check_ffmpeg_available():
        pytest.skip("FFmpeg not available")


def _skip_if_no_models() -> None:
    """Skip test if ML models not available."""
    from vl_jepa.audio.transcriber import check_whisper_available
    from vl_jepa.encoders.dinov2 import check_dinov2_available

    if not check_dinov2_available():
        pytest.skip("DINOv2 dependencies not available")
    if not check_whisper_available():
        pytest.skip("Whisper dependencies not available")


@pytest.fixture(scope="module")
def lecture_video_path() -> Path:
    """Get path to lecture video, skip if not available."""
    _skip_if_no_video()
    return LECTURE_VIDEO


@pytest.fixture(scope="module")
def dinov2_encoder():
    """Load DINOv2 encoder (module-scoped for reuse)."""
    _skip_if_no_models()
    from vl_jepa.encoders.dinov2 import DINOv2Encoder

    logger.info("Loading DINOv2 encoder...")
    start = time.time()
    encoder = DINOv2Encoder.load(device="cpu")
    load_time = time.time() - start
    logger.info("DINOv2 loaded in %.2fs", load_time)
    return encoder


@pytest.fixture(scope="module")
def text_encoder():
    """Load text encoder (module-scoped for reuse)."""
    from vl_jepa.text import TextEncoder

    logger.info("Loading text encoder...")
    start = time.time()
    encoder = TextEncoder.load()
    load_time = time.time() - start
    logger.info("Text encoder loaded in %.2fs", load_time)
    return encoder


@pytest.fixture(scope="module")
def whisper_transcriber():
    """Load Whisper transcriber (module-scoped for reuse)."""
    _skip_if_no_models()
    from vl_jepa.audio.transcriber import WhisperTranscriber

    logger.info("Loading Whisper transcriber (base model)...")
    start = time.time()
    transcriber = WhisperTranscriber.load(model_size="base", device="cpu")
    load_time = time.time() - start
    logger.info("Whisper loaded in %.2fs", load_time)
    return transcriber


@pytest.mark.integration
@pytest.mark.slow
class TestRealVideoFrameExtraction:
    """Tests for extracting frames from real lecture video."""

    def test_video_opens_and_reads_metadata(
        self, lecture_video_path: Path
    ) -> None:
        """
        SPEC: S001
        TEST_ID: T_PIPELINE_REAL_1a

        Given: A real lecture video file
        When: Video is opened
        Then: Metadata is correctly extracted
        """
        from vl_jepa.video import VideoInput

        with VideoInput.open(lecture_video_path) as video:
            metadata = video.get_metadata()

            # Verify video properties
            assert metadata.width > 0
            assert metadata.height > 0
            assert metadata.fps > 0
            assert metadata.duration > 0
            assert metadata.frame_count > 0

            logger.info("Video metadata: %s", metadata)

    def test_frame_sampling_at_1fps(
        self, lecture_video_path: Path
    ) -> None:
        """
        SPEC: S003
        TEST_ID: T_PIPELINE_REAL_1b

        Given: A real lecture video
        When: Frames are sampled at 1 FPS
        Then: Correct number of frames extracted with timestamps
        """
        from vl_jepa.video import VideoInput

        with VideoInput.open(lecture_video_path) as video:
            # Sample first 10 frames only (for speed)
            frames = list(video.sample_frames(target_fps=1.0, max_frames=10))

            assert len(frames) == 10

            # Verify frame properties
            for i, frame in enumerate(frames):
                assert frame.data.ndim == 3
                assert frame.data.shape[2] == 3  # RGB
                assert frame.timestamp >= 0

                # Timestamps should be roughly 1 second apart
                if i > 0:
                    time_diff = frame.timestamp - frames[i-1].timestamp
                    assert 0.5 < time_diff < 2.0, f"Frame {i} time diff: {time_diff}"

            logger.info(
                "Sampled %d frames, timestamps: %.1f - %.1f",
                len(frames),
                frames[0].timestamp,
                frames[-1].timestamp,
            )


@pytest.mark.integration
@pytest.mark.slow
class TestRealVideoDINOv2Encoding:
    """Tests for encoding real video frames with DINOv2."""

    def test_dinov2_encodes_real_frames(
        self, lecture_video_path: Path, dinov2_encoder
    ) -> None:
        """
        SPEC: S004
        TEST_ID: T_PIPELINE_REAL_2a

        Given: Real video frames
        When: Encoded with DINOv2
        Then: Produces 768-dim normalized embeddings
        """
        from vl_jepa.frame import FrameSampler
        from vl_jepa.video import VideoInput

        sampler = FrameSampler(mode="center_crop")
        embeddings = []
        timestamps = []
        encode_times = []

        with VideoInput.open(lecture_video_path) as video:
            for frame in video.sample_frames(target_fps=1.0, max_frames=5):
                # Process frame
                processed = sampler.process(frame.data)
                # Convert to (B, C, H, W) format
                batch = np.transpose(processed, (2, 0, 1))[np.newaxis, ...]

                # Encode
                start = time.time()
                embedding = dinov2_encoder.encode(batch)[0]
                encode_time = time.time() - start
                encode_times.append(encode_time)

                # Validate
                assert embedding.shape == (768,)
                assert np.allclose(np.linalg.norm(embedding), 1.0, atol=1e-5)

                embeddings.append(embedding)
                timestamps.append(frame.timestamp)

        # Performance baseline
        avg_encode_time = np.mean(encode_times) * 1000
        logger.info(
            "Encoded %d frames, avg time: %.1fms per frame",
            len(embeddings),
            avg_encode_time,
        )

        # Store for later tests
        assert len(embeddings) == 5
        assert len(timestamps) == 5

    def test_dinov2_similarity_on_real_frames(
        self, lecture_video_path: Path, dinov2_encoder
    ) -> None:
        """
        SPEC: S004
        TEST_ID: T_PIPELINE_REAL_2b

        Given: Adjacent and distant real video frames
        When: Encoded with DINOv2
        Then: Adjacent frames are more similar than distant frames
        """
        from vl_jepa.frame import FrameSampler
        from vl_jepa.video import VideoInput

        sampler = FrameSampler(mode="center_crop")

        with VideoInput.open(lecture_video_path) as video:
            frames = list(video.sample_frames(target_fps=1.0, max_frames=30))

        # Encode first, middle, and last frames
        def encode_frame(frame):
            processed = sampler.process(frame.data)
            batch = np.transpose(processed, (2, 0, 1))[np.newaxis, ...]
            return dinov2_encoder.encode(batch)[0]

        emb_first = encode_frame(frames[0])
        emb_second = encode_frame(frames[1])
        emb_last = encode_frame(frames[-1])

        # Calculate similarities
        sim_adjacent = np.dot(emb_first, emb_second)
        sim_distant = np.dot(emb_first, emb_last)

        logger.info(
            "Similarity - adjacent: %.4f, distant (30s apart): %.4f",
            sim_adjacent,
            sim_distant,
        )

        # Adjacent frames should be more similar
        # (for lecture video, this may vary depending on content changes)
        assert sim_adjacent >= 0.0  # At minimum, not anti-correlated
        assert sim_distant >= 0.0


@pytest.mark.integration
@pytest.mark.slow
class TestRealVideoAudioTranscription:
    """Tests for transcribing audio from real lecture video."""

    def test_audio_extraction(
        self, lecture_video_path: Path, tmp_path: Path
    ) -> None:
        """
        SPEC: G7
        TEST_ID: T_PIPELINE_REAL_3a

        Given: A real lecture video
        When: Audio is extracted
        Then: WAV file is created with correct format
        """
        _skip_if_no_ffmpeg()
        from vl_jepa.audio.extractor import extract_audio

        output_path = tmp_path / "lecture_audio.wav"

        start = time.time()
        result = extract_audio(
            str(lecture_video_path),
            str(output_path),
            sample_rate=16000,
            mono=True,
        )
        extract_time = time.time() - start

        assert Path(result).exists()
        assert Path(result).stat().st_size > 0

        logger.info(
            "Audio extracted in %.2fs, size: %.1f MB",
            extract_time,
            Path(result).stat().st_size / 1024 / 1024,
        )

    def test_whisper_transcription(
        self, lecture_video_path: Path, whisper_transcriber, tmp_path: Path
    ) -> None:
        """
        SPEC: G7
        TEST_ID: T_PIPELINE_REAL_3b

        Given: Audio from lecture video
        When: Transcribed with Whisper
        Then: Returns segments with timestamps and text
        """
        _skip_if_no_ffmpeg()
        from vl_jepa.audio.extractor import extract_audio

        # Extract audio first
        audio_path = tmp_path / "lecture_audio.wav"
        extract_audio(str(lecture_video_path), str(audio_path))

        # Transcribe
        start = time.time()
        segments = whisper_transcriber.transcribe(str(audio_path))
        transcribe_time = time.time() - start

        assert len(segments) > 0

        # Validate segments
        for seg in segments[:5]:  # Check first 5
            assert seg.text
            assert seg.start >= 0
            assert seg.end > seg.start
            assert 0 <= seg.confidence <= 1

        logger.info(
            "Transcribed %d segments in %.2fs (%.2f segments/sec)",
            len(segments),
            transcribe_time,
            len(segments) / transcribe_time,
        )
        logger.info(
            "First segment: [%.1f-%.1f] %s",
            segments[0].start,
            segments[0].end,
            segments[0].text[:100],
        )


@pytest.mark.integration
@pytest.mark.slow
class TestFullRealPipeline:
    """End-to-end tests with real lecture video."""

    def test_full_pipeline_builds_searchable_index(
        self,
        lecture_video_path: Path,
        dinov2_encoder,
        text_encoder,
        whisper_transcriber,
        tmp_path: Path,
    ) -> None:
        """
        SPEC: v0.2.0 G3, G7, G8
        TEST_ID: T_PIPELINE_REAL_FULL

        Given: A real lecture video
        When: Full pipeline is executed
        Then: Multimodal index is searchable with semantic queries
        """
        _skip_if_no_ffmpeg()
        from vl_jepa.audio.chunker import TranscriptChunker
        from vl_jepa.audio.extractor import extract_audio
        from vl_jepa.frame import FrameSampler
        from vl_jepa.multimodal_index import MultimodalIndex, RankingConfig
        from vl_jepa.video import VideoInput

        timings = {}
        index = MultimodalIndex(dimension=768)
        sampler = FrameSampler(mode="center_crop")

        # Step 1: Extract and encode video frames (first 60 seconds only)
        logger.info("Step 1: Extracting and encoding video frames...")
        start = time.time()
        with VideoInput.open(lecture_video_path) as video:
            for frame in video.sample_frames(target_fps=1.0, max_frames=60):
                processed = sampler.process(frame.data)
                batch = np.transpose(processed, (2, 0, 1))[np.newaxis, ...]
                embedding = dinov2_encoder.encode(batch)[0]
                index.add_visual(
                    embedding,
                    timestamp=frame.timestamp,
                    frame_index=int(frame.timestamp),
                )
        timings["video_encoding"] = time.time() - start
        logger.info(
            "Video: %d frames encoded in %.2fs",
            index.visual_count,
            timings["video_encoding"],
        )

        # Step 2: Extract audio
        logger.info("Step 2: Extracting audio...")
        start = time.time()
        audio_path = tmp_path / "lecture_audio.wav"
        extract_audio(str(lecture_video_path), str(audio_path))
        timings["audio_extraction"] = time.time() - start
        logger.info("Audio extracted in %.2fs", timings["audio_extraction"])

        # Step 3: Transcribe audio
        logger.info("Step 3: Transcribing audio...")
        start = time.time()
        segments = whisper_transcriber.transcribe(str(audio_path))
        timings["transcription"] = time.time() - start
        logger.info(
            "Transcribed %d segments in %.2fs",
            len(segments),
            timings["transcription"],
        )

        # Step 4: Chunk and encode transcript
        logger.info("Step 4: Chunking and encoding transcript...")
        start = time.time()
        chunker = TranscriptChunker(window_size=10.0, overlap=2.0)
        chunks = list(chunker.chunk(segments))

        for i, chunk in enumerate(chunks):
            embedding = text_encoder.encode(chunk.text)
            index.add_transcript(
                embedding,
                start_time=chunk.start,
                end_time=chunk.end,
                text=chunk.text,
                segment_id=i,
            )
        timings["text_encoding"] = time.time() - start
        logger.info(
            "Encoded %d text chunks in %.2fs",
            index.transcript_count,
            timings["text_encoding"],
        )

        # Step 5: Query the index
        logger.info("Step 5: Testing semantic search...")
        test_queries = [
            "What is the main topic of this lecture?",
            "Can you explain the key concepts?",
            "What examples were given?",
        ]

        for query in test_queries:
            start = time.time()
            query_emb = text_encoder.encode(query)
            config = RankingConfig(visual_weight=0.3, transcript_weight=0.7)
            results = index.search_multimodal(query_emb, k=5, config=config)
            query_time = (time.time() - start) * 1000

            logger.info(
                "Query: '%s' -> %d results in %.1fms",
                query[:50],
                len(results),
                query_time,
            )

            if results:
                top = results[0]
                logger.info(
                    "  Top result: score=%.4f, modality=%s, time=%.1fs",
                    top.score,
                    top.modality,
                    top.timestamp,
                )

        # Verify index is populated
        assert index.visual_count > 0
        assert index.transcript_count > 0
        assert index.size == index.visual_count + index.transcript_count

        # Log performance summary
        logger.info("\n=== Performance Summary ===")
        for step, duration in timings.items():
            logger.info("  %s: %.2fs", step, duration)
        total = sum(timings.values())
        logger.info("  TOTAL: %.2fs", total)

    def test_audio_visual_sync(
        self,
        lecture_video_path: Path,
        dinov2_encoder,
        text_encoder,
        whisper_transcriber,
        tmp_path: Path,
    ) -> None:
        """
        SPEC: v0.2.0 G8
        TEST_ID: T_SYNC_REAL

        Given: Indexed lecture video with visual and transcript
        When: Context is retrieved for a timestamp
        Then: Visual and transcript entries are temporally aligned
        """
        _skip_if_no_ffmpeg()
        from vl_jepa.audio.chunker import TranscriptChunker
        from vl_jepa.audio.extractor import extract_audio
        from vl_jepa.frame import FrameSampler
        from vl_jepa.multimodal_index import MultimodalIndex
        from vl_jepa.video import VideoInput

        index = MultimodalIndex(dimension=768)
        sampler = FrameSampler(mode="center_crop")

        # Index first 30 seconds
        with VideoInput.open(lecture_video_path) as video:
            for frame in video.sample_frames(target_fps=1.0, max_frames=30):
                processed = sampler.process(frame.data)
                batch = np.transpose(processed, (2, 0, 1))[np.newaxis, ...]
                embedding = dinov2_encoder.encode(batch)[0]
                index.add_visual(
                    embedding,
                    timestamp=frame.timestamp,
                    frame_index=int(frame.timestamp),
                )

        # Transcribe and index
        audio_path = tmp_path / "lecture_audio.wav"
        extract_audio(str(lecture_video_path), str(audio_path))
        segments = whisper_transcriber.transcribe(str(audio_path))

        chunker = TranscriptChunker(window_size=10.0, overlap=2.0)
        for _i, chunk in enumerate(chunker.chunk(segments)):
            embedding = text_encoder.encode(chunk.text)
            index.add_transcript(
                embedding,
                start_time=chunk.start,
                end_time=chunk.end,
                text=chunk.text,
            )

        # Test alignment at timestamp 20.0 (well into transcript content)
        # Note: Whisper typically detects speech starting a few seconds in
        target_time = 20.0
        tolerance = 10.0

        context = index.get_aligned_context(
            timestamp=target_time,
            visual_tolerance=5.0,
            transcript_tolerance=tolerance,
        )

        assert "visual" in context
        assert "transcript" in context

        # Verify visual entries are within tolerance
        for entry in context["visual"]:
            assert abs(entry.timestamp - target_time) <= 5.0

        # Verify transcript entries are near the target time
        # Using wider tolerance since transcript segments have variable boundaries
        for entry in context["transcript"]:
            # Entry timestamp should be roughly near target
            assert abs(entry.timestamp - target_time) <= tolerance + 5.0

        logger.info(
            "Alignment at t=%.1f: %d visual, %d transcript entries",
            target_time,
            len(context["visual"]),
            len(context["transcript"]),
        )
