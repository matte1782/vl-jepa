"""
Video processing pipeline for Gradio UI.

IMPLEMENTS: S013 - Gradio Web Interface (Processing Pipeline)
IMPLEMENTS: v0.3.0 G2 - Progress Indication

Provides:
- ProcessingPipeline: Orchestrates video processing with progress callbacks
- ProcessingProgress: Progress update dataclass
- ProcessingResult: Processing output dataclass
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Configuration constants
MAX_VIDEO_SIZE_BYTES: int = 500 * 1024 * 1024  # 500MB max video file size
DEFAULT_TARGET_FPS: float = 1.0  # Default frames per second for sampling


class ProcessingStage(str, Enum):
    """
    Processing pipeline stages.

    Each stage represents a distinct phase in video processing.
    """

    LOADING = "loading"
    AUDIO_EXTRACTION = "audio_extraction"
    TRANSCRIPTION = "transcription"
    FRAME_SAMPLING = "frame_sampling"
    VISUAL_ENCODING = "visual_encoding"
    TEXT_ENCODING = "text_encoding"
    EVENT_DETECTION = "event_detection"
    INDEX_BUILDING = "index_building"


# Stage order for progress calculation
STAGE_ORDER = [
    ProcessingStage.LOADING,
    ProcessingStage.AUDIO_EXTRACTION,
    ProcessingStage.TRANSCRIPTION,
    ProcessingStage.FRAME_SAMPLING,
    ProcessingStage.VISUAL_ENCODING,
    ProcessingStage.TEXT_ENCODING,
    ProcessingStage.EVENT_DETECTION,
    ProcessingStage.INDEX_BUILDING,
]

STAGE_WEIGHTS = {
    ProcessingStage.LOADING: 0.05,
    ProcessingStage.AUDIO_EXTRACTION: 0.10,
    ProcessingStage.TRANSCRIPTION: 0.20,
    ProcessingStage.FRAME_SAMPLING: 0.10,
    ProcessingStage.VISUAL_ENCODING: 0.25,
    ProcessingStage.TEXT_ENCODING: 0.10,
    ProcessingStage.EVENT_DETECTION: 0.10,
    ProcessingStage.INDEX_BUILDING: 0.10,
}

STAGE_MESSAGES = {
    ProcessingStage.LOADING: "Loading video...",
    ProcessingStage.AUDIO_EXTRACTION: "Extracting audio track...",
    ProcessingStage.TRANSCRIPTION: "Transcribing speech...",
    ProcessingStage.FRAME_SAMPLING: "Sampling video frames...",
    ProcessingStage.VISUAL_ENCODING: "Encoding visual features...",
    ProcessingStage.TEXT_ENCODING: "Encoding transcript...",
    ProcessingStage.EVENT_DETECTION: "Detecting events...",
    ProcessingStage.INDEX_BUILDING: "Building search index...",
}


@dataclass
class ProcessingProgress:
    """
    Progress update for UI display.

    IMPLEMENTS: S013.P1 - Progress Updates

    Attributes:
        stage: Current processing stage.
        progress: Overall progress (0.0 to 1.0).
        message: Human-readable status message.
        current_step: Current step number.
        total_steps: Total number of steps.
    """

    stage: str
    progress: float
    message: str
    current_step: int = 0
    total_steps: int = 8


@dataclass
class TranscriptChunkResult:
    """Transcript chunk for result."""

    text: str
    start: float
    end: float


@dataclass
class EventResult:
    """Event for result."""

    timestamp: float
    confidence: float


@dataclass
class VideoMetadataResult:
    """Video metadata for result."""

    path: str
    duration: float
    width: int
    height: int
    fps: float
    frame_count: int
    codec: str


@dataclass
class ProcessingResult:
    """
    Complete processing result for UI.

    IMPLEMENTS: S013.P2 - Processing Output

    Attributes:
        video_path: Path to processed video.
        duration: Video duration in seconds.
        frame_count: Number of frames processed.
        events: Detected events.
        transcript_chunks: Transcript segments.
        processing_time: Total processing time.
        multimodal_index: Built search index.
        metadata: Video metadata.
        error: Error message if processing failed.
    """

    video_path: Path
    duration: float
    frame_count: int
    events: list[EventResult] = field(default_factory=list)
    transcript_chunks: list[TranscriptChunkResult] = field(default_factory=list)
    processing_time: float = 0.0
    multimodal_index: Any | None = None
    metadata: VideoMetadataResult | None = None
    error: str | None = None

    @property
    def has_error(self) -> bool:
        """Check if processing encountered an error."""
        return self.error is not None


class ProcessingPipeline:
    """
    Video processing pipeline with progress callbacks.

    IMPLEMENTS: S013.P3 - Processing Pipeline

    Orchestrates:
    1. Video loading and validation
    2. Audio extraction (FFmpeg)
    3. Audio transcription (Whisper)
    4. Frame sampling (1 FPS)
    5. Frame encoding (Visual encoder)
    6. Transcript embedding (Text encoder)
    7. Event detection
    8. Index building
    """

    def __init__(
        self,
        visual_encoder: Any | None = None,
        text_encoder: Any | None = None,
        use_placeholders: bool = False,
        progress_callback: Callable[[ProcessingProgress], None] | None = None,
        target_fps: float = 1.0,
    ) -> None:
        """
        Initialize ProcessingPipeline.

        Args:
            visual_encoder: Visual encoder instance.
            text_encoder: Text encoder instance.
            use_placeholders: Use placeholder encoders for testing.
            progress_callback: Callback for progress updates.
            target_fps: Target frames per second to sample.
        """
        self._progress_callback = progress_callback
        self._target_fps = target_fps

        if use_placeholders:
            self._init_placeholders()
        else:
            self._visual_encoder = visual_encoder
            self._text_encoder = text_encoder

    def _init_placeholders(self) -> None:
        """Initialize placeholder encoders for testing."""
        try:
            from vl_jepa.encoders.placeholder import (
                PlaceholderTextEncoder,
                PlaceholderVisualEncoder,
            )

            self._visual_encoder = PlaceholderVisualEncoder(seed=42)
            self._text_encoder = PlaceholderTextEncoder(seed=42)
            logger.info("Using placeholder encoders")
        except ImportError:
            logger.warning("Placeholder encoders not available")
            self._visual_encoder = None
            self._text_encoder = None

    def _emit_progress(
        self,
        stage: ProcessingStage,
        substep: float = 0.0,
        message: str | None = None,
    ) -> None:
        """
        Emit progress update to callback.

        Args:
            stage: Current processing stage.
            substep: Progress within stage (0.0 to 1.0).
            message: Optional custom message.
        """
        if self._progress_callback is None:
            return

        progress = self._calculate_progress(stage, substep)
        msg = message or STAGE_MESSAGES.get(stage, "Processing...")
        step_index = STAGE_ORDER.index(stage) + 1

        update = ProcessingProgress(
            stage=stage.value,
            progress=progress,
            message=msg,
            current_step=step_index,
            total_steps=len(STAGE_ORDER),
        )

        self._progress_callback(update)

    def _calculate_progress(
        self,
        stage: ProcessingStage,
        substep: float = 0.0,
    ) -> float:
        """
        Calculate overall progress.

        Args:
            stage: Current stage.
            substep: Progress within stage (0.0 to 1.0).

        Returns:
            Overall progress (0.0 to 1.0).
        """
        stage_index = STAGE_ORDER.index(stage)

        # Sum weights of completed stages
        completed_weight = sum(STAGE_WEIGHTS[s] for s in STAGE_ORDER[:stage_index])

        # Add partial weight of current stage
        current_weight = STAGE_WEIGHTS[stage] * substep

        return min(completed_weight + current_weight, 1.0)

    def process_video(
        self,
        video_path: Path,
        max_size: int | None = None,
    ) -> ProcessingResult:
        """
        Process a video file.

        IMPLEMENTS: S013.P4 - Video Processing

        Args:
            video_path: Path to video file.
            max_size: Optional maximum file size in bytes (default: MAX_VIDEO_SIZE_BYTES).

        Returns:
            ProcessingResult with all extracted data.
        """
        start_time = time.time()
        effective_max_size = max_size if max_size is not None else MAX_VIDEO_SIZE_BYTES

        # Initialize result
        result = ProcessingResult(
            video_path=video_path,
            duration=0.0,
            frame_count=0,
        )

        # Stage 1: Load video
        self._emit_progress(ProcessingStage.LOADING)
        try:
            if not video_path.exists():
                result.error = "Video file not found"
                logger.error(f"Video file not found: {video_path}")
                return result

            # Validate file size
            file_size = video_path.stat().st_size
            if file_size > effective_max_size:
                result.error = "Video file exceeds maximum allowed size"
                logger.error(
                    f"Video file too large: {file_size} bytes "
                    f"(max: {effective_max_size} bytes)"
                )
                return result

            metadata = self._load_video(video_path)
            result.duration = metadata.duration
            result.metadata = VideoMetadataResult(
                path=str(video_path),
                duration=metadata.duration,
                width=metadata.width,
                height=metadata.height,
                fps=metadata.fps,
                frame_count=metadata.frame_count,
                codec=metadata.codec,
            )
        except Exception:
            result.error = "Failed to load video. Please check the file format."
            logger.exception("Video loading failed")
            return result

        # Stage 2: Extract audio
        self._emit_progress(ProcessingStage.AUDIO_EXTRACTION)
        audio_path = None
        try:
            audio_path = self._extract_audio(video_path)
        except Exception as e:
            logger.warning(f"Audio extraction failed: {e}")
            # Continue without audio

        # Stage 3: Transcribe
        self._emit_progress(ProcessingStage.TRANSCRIPTION)
        transcript_chunks: list[TranscriptChunkResult] = []
        if audio_path:
            try:
                transcript_chunks = self._transcribe(audio_path)
            except Exception as e:
                logger.warning(f"Transcription failed: {e}")

        result.transcript_chunks = transcript_chunks

        # Stage 4: Sample frames
        self._emit_progress(ProcessingStage.FRAME_SAMPLING)
        try:
            frames = self._sample_frames(video_path)
            result.frame_count = len(frames)
        except Exception:
            result.error = "Failed to sample video frames. Please try again."
            logger.exception("Frame sampling failed")
            return result

        # Stage 5: Encode frames
        self._emit_progress(ProcessingStage.VISUAL_ENCODING)
        visual_embeddings: list[np.ndarray] = []
        timestamps: list[float] = []
        try:
            visual_embeddings, timestamps = self._encode_frames(frames)
        except Exception:
            result.error = "Failed to encode video frames. Please try again."
            logger.exception("Visual encoding failed")
            return result

        # Stage 6: Encode transcript
        self._emit_progress(ProcessingStage.TEXT_ENCODING)
        text_embeddings: list[np.ndarray] = []
        if transcript_chunks and self._text_encoder:
            try:
                text_embeddings = self._encode_transcript(transcript_chunks)
            except Exception as e:
                logger.warning(f"Text encoding failed: {e}")

        # Stage 7: Detect events
        self._emit_progress(ProcessingStage.EVENT_DETECTION)
        try:
            events = self._detect_events(visual_embeddings, timestamps)
            result.events = [
                EventResult(timestamp=e.timestamp, confidence=e.confidence)
                for e in events
            ]
        except Exception as e:
            logger.warning(f"Event detection failed: {e}")

        # Stage 8: Build index
        self._emit_progress(ProcessingStage.INDEX_BUILDING)
        try:
            result.multimodal_index = self._build_index(
                visual_embeddings,
                timestamps,
                text_embeddings,
                transcript_chunks,
            )
        except Exception as e:
            logger.warning(f"Index building failed: {e}")

        # Complete
        result.processing_time = time.time() - start_time
        self._emit_progress(
            ProcessingStage.INDEX_BUILDING, substep=1.0, message="Complete!"
        )

        return result

    def _load_video(self, video_path: Path) -> Any:
        """Load video and get metadata."""
        from vl_jepa.video import VideoInput

        with VideoInput.open(video_path) as video:
            return video.get_metadata()

    def _extract_audio(self, video_path: Path) -> Path | None:
        """Extract audio from video."""
        try:
            from vl_jepa.audio import extract_audio

            audio_str = extract_audio(str(video_path))
            return Path(audio_str)
        except ImportError:
            logger.warning("Audio extraction not available")
            return None

    def _transcribe(self, audio_path: Path) -> list[TranscriptChunkResult]:
        """Transcribe audio file."""
        try:
            from vl_jepa.audio import PlaceholderTranscriber

            transcriber = PlaceholderTranscriber()
            segments = transcriber.transcribe(str(audio_path))

            return [
                TranscriptChunkResult(
                    text=seg.text,
                    start=seg.start,
                    end=seg.end,
                )
                for seg in segments
            ]
        except ImportError:
            logger.warning("Transcriber not available")
            return []

    def _sample_frames(
        self,
        video_path: Path,
    ) -> list[tuple[np.ndarray, float]]:
        """Sample frames from video at target FPS."""
        from vl_jepa.frame import FrameSampler
        from vl_jepa.video import VideoInput

        sampler = FrameSampler(mode="center_crop")
        frames: list[tuple[np.ndarray, float]] = []

        with VideoInput.open(video_path) as video:
            for frame in video.sample_frames(target_fps=self._target_fps):
                processed = sampler.process(frame.data)
                frames.append((processed, frame.timestamp))

                # Emit substep progress
                if video.duration > 0:
                    substep = frame.timestamp / video.duration
                    self._emit_progress(
                        ProcessingStage.FRAME_SAMPLING,
                        substep=substep,
                        message=f"Sampling frame at {frame.timestamp:.1f}s...",
                    )

        return frames

    def _encode_frames(
        self,
        frames: list[tuple[np.ndarray, float]],
    ) -> tuple[list[np.ndarray], list[float]]:
        """Encode frames with visual encoder."""
        if not frames or not self._visual_encoder:
            return [], []

        embeddings: list[np.ndarray] = []
        timestamps: list[float] = []

        for i, (frame, timestamp) in enumerate(frames):
            # Convert to batch format (1, 3, 224, 224)
            frame_batch = frame.transpose(2, 0, 1)[np.newaxis, ...]

            embedding = self._visual_encoder.encode(frame_batch)[0]
            embeddings.append(embedding)
            timestamps.append(timestamp)

            # Emit substep progress
            substep = (i + 1) / len(frames)
            self._emit_progress(
                ProcessingStage.VISUAL_ENCODING,
                substep=substep,
                message=f"Encoding frame {i + 1}/{len(frames)}...",
            )

        return embeddings, timestamps

    def _encode_transcript(
        self,
        chunks: list[TranscriptChunkResult],
    ) -> list[np.ndarray]:
        """Encode transcript chunks with text encoder."""
        if not chunks or not self._text_encoder:
            return []

        embeddings: list[np.ndarray] = []

        for i, chunk in enumerate(chunks):
            embedding = self._text_encoder.encode(chunk.text)
            embeddings.append(embedding)

            # Emit substep progress
            substep = (i + 1) / len(chunks)
            self._emit_progress(
                ProcessingStage.TEXT_ENCODING,
                substep=substep,
                message=f"Encoding transcript {i + 1}/{len(chunks)}...",
            )

        return embeddings

    def _detect_events(
        self,
        embeddings: list[np.ndarray],
        timestamps: list[float],
    ) -> list[Any]:
        """Detect events from embeddings."""
        if not embeddings:
            return []

        try:
            from vl_jepa.detector import EventDetector

            detector = EventDetector(
                threshold=0.3,
                min_event_gap=30.0,
            )

            events: list[Any] = []
            for embedding, timestamp in zip(embeddings, timestamps, strict=False):
                event = detector.process(embedding, timestamp)
                if event:
                    events.append(event)

            return events
        except ImportError:
            logger.warning("EventDetector not available")
            return []

    def _build_index(
        self,
        visual_embeddings: list[np.ndarray],
        timestamps: list[float],
        text_embeddings: list[np.ndarray],
        transcript_chunks: list[TranscriptChunkResult],
    ) -> Any:
        """Build multimodal search index."""
        try:
            from vl_jepa.multimodal_index import MultimodalIndex

            index = MultimodalIndex(dimension=768)

            # Add visual embeddings
            for i, (embedding, timestamp) in enumerate(
                zip(visual_embeddings, timestamps, strict=False)
            ):
                index.add_visual(
                    embedding=embedding,
                    timestamp=timestamp,
                    frame_index=i,
                )

            # Add transcript embeddings
            for i, (embedding, chunk) in enumerate(
                zip(text_embeddings, transcript_chunks, strict=False)
            ):
                index.add_transcript(
                    embedding=embedding,
                    start_time=chunk.start,
                    end_time=chunk.end,
                    text=chunk.text,
                    segment_id=i,
                )

            return index
        except ImportError:
            logger.warning("MultimodalIndex not available")
            return None
