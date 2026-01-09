"""
FastAPI application for Lecture Mind.

IMPLEMENTS: S014 - REST API Interface
Provides REST endpoints for video processing, search, and export.
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Configure logging early for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
_startup_logger = logging.getLogger("vl_jepa.api.startup")
_startup_logger.info("Starting Lecture Mind API module import...")
_startup_logger.info(f"Python version: {sys.version}")
_startup_logger.info(f"Working directory: {os.getcwd()}")
_startup_logger.info(
    f"PORT env variable: {os.environ.get('PORT', 'not set (will use 8000)')}"
)

try:
    import numpy as np

    _startup_logger.info(f"NumPy version: {np.__version__}")
except ImportError as e:
    _startup_logger.error(f"Failed to import numpy: {e}")
    raise

try:
    from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles

    _startup_logger.info("FastAPI imports successful")
except ImportError as e:
    _startup_logger.error(f"Failed to import fastapi: {e}")
    raise

from vl_jepa.api.models import (
    EventItem,
    ExportFormat,
    ExportResponse,
    JobStatus,
    ProcessingResult,
    ProcessingStage,
    ProgressResponse,
    ResultsResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    TranscriptChunk,
    UploadResponse,
    VideoMetadata,
)

if TYPE_CHECKING:
    from vl_jepa.multimodal_index import MultimodalIndex

logger = logging.getLogger(__name__)

# In-memory job storage (for demo - use Redis/DB in production)
_jobs: dict[str, dict[str, Any]] = {}
_job_lock = threading.Lock()

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"


def create_app(
    use_placeholders: bool = True,
    debug: bool = False,
) -> FastAPI:
    """
    Create FastAPI application.

    Args:
        use_placeholders: Use placeholder encoders for fast demo.
        debug: Enable debug mode.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Lecture Mind API",
        description="AI-powered lecture analysis with visual and transcript search",
        version="0.3.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store config in app state
    app.state.use_placeholders = use_placeholders
    app.state.debug = debug

    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Register routes
    _register_routes(app)

    return app


def _register_routes(app: FastAPI) -> None:
    """Register all API routes."""

    @app.get("/", response_class=HTMLResponse)
    async def serve_frontend() -> HTMLResponse:
        """Serve the main frontend page."""
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
        return HTMLResponse(
            content="<h1>Lecture Mind</h1><p>Frontend not found. Visit /api/docs for API.</p>"
        )

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint for deployment monitoring."""
        return {"status": "healthy", "service": "lecture-mind"}

    @app.post("/api/upload", response_model=UploadResponse)
    async def upload_video(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),  # noqa: B008 - FastAPI pattern
    ) -> UploadResponse:
        """
        Upload a video file for processing.

        Returns a job_id to track processing status.
        """
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        allowed_extensions = {".mp4", ".webm", ".avi", ".mov", ".mkv"}
        ext = Path(file.filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Allowed: {', '.join(allowed_extensions)}",
            )

        # Generate job ID
        job_id = str(uuid.uuid4())[:8]

        # Save uploaded file
        temp_dir = Path(tempfile.mkdtemp())
        video_path = temp_dir / file.filename
        with open(video_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Initialize job
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.PENDING,
                "stage": None,
                "progress": 0.0,
                "message": "Queued for processing",
                "video_path": str(video_path),
                "temp_dir": str(temp_dir),
                "result": None,
                "error": None,
                "use_placeholders": app.state.use_placeholders,
            }

        # Start processing in background
        background_tasks.add_task(_process_video, job_id)

        return UploadResponse(
            job_id=job_id,
            message="Video uploaded. Processing started.",
        )

    @app.get("/api/status/{job_id}", response_model=ProgressResponse)
    async def get_status(job_id: str) -> ProgressResponse:
        """Get processing status for a job."""
        with _job_lock:
            job = _jobs.get(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return ProgressResponse(
            job_id=job_id,
            status=job["status"],
            stage=job.get("stage"),
            progress=job["progress"],
            message=job["message"],
            error=job.get("error"),
        )

    @app.get("/api/results/{job_id}", response_model=ResultsResponse)
    async def get_results(job_id: str) -> ResultsResponse:
        """Get processing results for a completed job."""
        with _job_lock:
            job = _jobs.get(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return ResultsResponse(
            job_id=job_id,
            status=job["status"],
            result=job.get("result"),
            error=job.get("error"),
        )

    @app.post("/api/search/{job_id}", response_model=SearchResponse)
    async def search(job_id: str, request: SearchRequest) -> SearchResponse:
        """Search within processed video content using semantic search."""
        with _job_lock:
            job = _jobs.get(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job["status"] != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Processing not complete")

        # Get the index and text encoder from job state
        index: MultimodalIndex | None = job.get("index")
        text_encoder = job.get("text_encoder")
        result = job.get("result")

        if not result:
            return SearchResponse(query=request.query, results=[], total=0)

        results: list[SearchResultItem] = []

        # Use semantic search if index is available
        if index is not None and text_encoder is not None and index.size > 0:
            try:
                # Encode query
                query_embedding = text_encoder.encode(request.query)

                # Search transcript modality
                from vl_jepa.multimodal_index import Modality

                search_results = index.search(
                    query_embedding,
                    k=request.top_k,
                    modality=Modality.TRANSCRIPT,
                )

                for sr in search_results:
                    results.append(
                        SearchResultItem(
                            text=sr.text or "",
                            timestamp=sr.timestamp,
                            timestamp_formatted=_format_timestamp(sr.timestamp),
                            score=float(sr.score),
                            result_type="transcript",
                        )
                    )
                logger.info(
                    "Semantic search for '%s' found %d results",
                    request.query,
                    len(results),
                )
            except Exception as e:
                logger.warning("Semantic search failed: %s, falling back to text", e)
                # Fall through to text matching

        # Fallback to text matching if semantic search not available or failed
        if not results:
            query_lower = request.query.lower()
            for chunk in result.transcript:
                if query_lower in chunk.text.lower():
                    results.append(
                        SearchResultItem(
                            text=chunk.text,
                            timestamp=chunk.start,
                            timestamp_formatted=chunk.start_formatted,
                            score=0.5,  # Lower score for text match
                            result_type="transcript",
                        )
                    )
            results = results[: request.top_k]

        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
        )

    @app.get("/api/export/{job_id}/{format}")
    async def export(job_id: str, format: ExportFormat) -> ExportResponse:
        """Export results in specified format."""
        with _job_lock:
            job = _jobs.get(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job["status"] != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Processing not complete")

        result = job.get("result")
        if not result:
            raise HTTPException(status_code=404, detail="No results available")

        # Generate export content
        from vl_jepa.ui.export import (
            export_json,
            export_markdown,
            export_srt,
        )

        # Create a mock result object for export functions
        class MockResult:
            def __init__(self, r: ProcessingResult) -> None:
                self.metadata = type(
                    "M",
                    (),
                    {
                        "path": r.metadata.filename,
                        "width": r.metadata.width,
                        "height": r.metadata.height,
                        "fps": r.metadata.fps,
                        "frame_count": int(r.metadata.duration * r.metadata.fps),
                        "duration": r.metadata.duration,
                        "codec": r.metadata.codec,
                    },
                )()
                self.events = [
                    type(
                        "E", (), {"timestamp": e.timestamp, "confidence": e.confidence}
                    )()
                    for e in r.events
                ]
                self.transcript_chunks = [
                    type("T", (), {"text": t.text, "start": t.start, "end": t.end})()
                    for t in r.transcript
                ]
                self.processing_time = r.processing_time
                self.frame_count = int(r.metadata.duration * r.metadata.fps)
                self.error = None

        mock = MockResult(result)

        if format == ExportFormat.MARKDOWN:
            content = export_markdown(mock)
            filename = "lecture_summary.md"
        elif format == ExportFormat.JSON:
            content = export_json(mock)
            filename = "lecture_data.json"
        elif format == ExportFormat.SRT:
            content = export_srt(mock)
            filename = "lecture_subtitles.srt"
        else:
            raise HTTPException(status_code=400, detail="Invalid format")

        return ExportResponse(
            format=format,
            content=content,
            filename=filename,
        )

    @app.delete("/api/job/{job_id}")
    async def delete_job(job_id: str) -> dict[str, str]:
        """Delete a job and clean up resources."""
        with _job_lock:
            job = _jobs.pop(job_id, None)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Clean up temp files
        temp_dir = job.get("temp_dir")
        if temp_dir:
            import shutil

            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

        return {"message": "Job deleted"}


def _format_timestamp(seconds: float) -> str:
    """Format seconds to MM:SS."""
    import math

    if not math.isfinite(seconds) or seconds < 0:
        return "0:00"
    total = int(seconds)
    mins = total // 60
    secs = total % 60
    return f"{mins}:{secs:02d}"


def _process_video(job_id: str) -> None:
    """Process video in background thread."""

    def update_progress(
        stage: ProcessingStage,
        progress: float,
        message: str,
    ) -> None:
        with _job_lock:
            if job_id in _jobs:
                _jobs[job_id]["stage"] = stage
                _jobs[job_id]["progress"] = progress
                _jobs[job_id]["message"] = message
                _jobs[job_id]["status"] = JobStatus.PROCESSING

    try:
        with _job_lock:
            job = _jobs.get(job_id)
            if not job:
                return
            video_path = Path(job["video_path"])

        # Stage 1: Loading video
        update_progress(ProcessingStage.LOADING, 0.05, "Loading video...")
        time.sleep(0.3)  # Simulate work

        # Get video metadata
        try:
            from vl_jepa.video import VideoInput

            video = VideoInput.open(video_path)
            metadata = VideoMetadata(
                filename=video_path.name,
                duration=video.duration,
                width=video.width,
                height=video.height,
                fps=video.fps,
                codec=video.codec,
            )
            video.close()
        except Exception:
            # Fallback for demo
            metadata = VideoMetadata(
                filename=video_path.name,
                duration=60.0,
                width=1920,
                height=1080,
                fps=30.0,
                codec="h264",
            )

        # Stage 2: Extract audio
        update_progress(ProcessingStage.EXTRACTING_AUDIO, 0.15, "Extracting audio...")

        audio_path = None
        transcript_chunks = []

        try:
            from vl_jepa.audio.extractor import check_ffmpeg_available, extract_audio

            if check_ffmpeg_available():
                audio_path = extract_audio(str(video_path))
                logger.info("Audio extracted to: %s", audio_path)
            else:
                logger.warning("FFmpeg not available, skipping audio extraction")
        except Exception as e:
            logger.warning("Audio extraction failed: %s", e)

        # Stage 3: Transcribe with real Whisper
        update_progress(
            ProcessingStage.TRANSCRIBING, 0.30, "Transcribing audio with Whisper..."
        )

        if audio_path:
            try:
                from vl_jepa.audio.transcriber import (
                    WhisperTranscriber,
                    check_whisper_available,
                )

                if check_whisper_available():
                    # Use base model for balance of speed/accuracy
                    transcriber = WhisperTranscriber.load("base", device="auto")
                    segments = transcriber.transcribe(audio_path)

                    # Convert to API format
                    for seg in segments:
                        transcript_chunks.append(
                            TranscriptChunk(
                                text=seg.text,
                                start=seg.start,
                                end=seg.end,
                                start_formatted=_format_timestamp(seg.start),
                                end_formatted=_format_timestamp(seg.end),
                            )
                        )
                    logger.info("Transcribed %d segments", len(transcript_chunks))
                else:
                    logger.warning("Whisper not available")
            except Exception as e:
                logger.warning("Transcription failed: %s", e)

        # Fallback to demo transcript if real transcription failed
        if not transcript_chunks:
            logger.info("Using demo transcript (real transcription not available)")
            transcript_chunks = [
                TranscriptChunk(
                    text="[Demo mode - Install faster-whisper for real transcription]",
                    start=0.0,
                    end=5.0,
                    start_formatted="0:00",
                    end_formatted="0:05",
                ),
                TranscriptChunk(
                    text="Run: pip install faster-whisper",
                    start=5.0,
                    end=10.0,
                    start_formatted="0:05",
                    end_formatted="0:10",
                ),
            ]

        # Stage 4: Sample frames
        update_progress(ProcessingStage.SAMPLING_FRAMES, 0.45, "Sampling frames...")

        # Sample frames from video (1 FPS for event detection)
        frames = []
        frame_timestamps = []
        try:
            from vl_jepa.video import VideoInput

            video = VideoInput.open(video_path)
            sampled = list(video.sample_frames(target_fps=1.0))
            frames = [f.data for f in sampled]
            frame_timestamps = [f.timestamp for f in sampled]
            video.close()
            logger.info("Sampled %d frames at 1 FPS", len(frames))
        except Exception as e:
            logger.warning("Frame sampling failed: %s", e)

        # Stage 5: Encode frames
        update_progress(ProcessingStage.ENCODING_FRAMES, 0.55, "Encoding frames...")

        # Initialize visual encoder
        frame_embeddings = []
        try:
            from vl_jepa.encoders.placeholder import PlaceholderVisualEncoder

            visual_encoder = PlaceholderVisualEncoder()

            # Encode frames (resize to 224x224 and normalize)
            import cv2

            for frame in frames:
                # frame is typically (H, W, 3) BGR uint8
                resized = cv2.resize(frame, (224, 224))
                # Convert BGR to RGB and normalize to [-1, 1]
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                normalized = (rgb.astype(np.float32) / 127.5) - 1.0
                # Transpose to (C, H, W)
                chw = normalized.transpose(2, 0, 1)
                embedding = visual_encoder.encode_single(chw)
                frame_embeddings.append(embedding)
            logger.info("Encoded %d frames", len(frame_embeddings))
        except Exception as e:
            logger.warning("Frame encoding failed: %s", e)

        # Stage 6: Encode text
        update_progress(ProcessingStage.ENCODING_TEXT, 0.65, "Encoding transcript...")

        # Initialize text encoder and multimodal index
        text_encoder: Any = None
        multimodal_index: MultimodalIndex | None = None
        try:
            # Try real MiniLM encoder first
            try:
                from vl_jepa.text import TextEncoder

                text_encoder = TextEncoder.load()
                logger.info("Loaded real TextEncoder (MiniLM)")
            except Exception:
                from vl_jepa.encoders.placeholder import PlaceholderTextEncoder

                text_encoder = PlaceholderTextEncoder()
                logger.info("Using PlaceholderTextEncoder")

            # Build multimodal index
            from vl_jepa.multimodal_index import MultimodalIndex

            multimodal_index = MultimodalIndex()

            # Add transcript embeddings
            for i, chunk in enumerate(transcript_chunks):
                text_embedding = text_encoder.encode(chunk.text)
                multimodal_index.add_transcript(
                    embedding=text_embedding,
                    start_time=chunk.start,
                    end_time=chunk.end,
                    text=chunk.text,
                    segment_id=i,
                )
            logger.info("Added %d transcript chunks to index", len(transcript_chunks))

        except Exception as e:
            logger.warning("Text encoding/indexing failed: %s", e)

        # Stage 7: Detect events
        update_progress(ProcessingStage.DETECTING_EVENTS, 0.80, "Detecting events...")

        events = []
        try:
            from vl_jepa.detector import EventDetector

            # Initialize event detector
            detector = EventDetector(
                threshold=0.25,  # Slightly lower for more sensitivity
                min_event_gap=30.0,  # Minimum 30s between events
                smoothing_window=3,
            )

            # Always add start event
            events.append(
                EventItem(
                    timestamp=0.0,
                    timestamp_formatted="0:00",
                    confidence=1.0,
                )
            )

            # Process frame embeddings to detect events
            for embedding, timestamp in zip(
                frame_embeddings, frame_timestamps, strict=False
            ):
                event = detector.process(embedding, timestamp)
                if event:
                    events.append(
                        EventItem(
                            timestamp=event.timestamp,
                            timestamp_formatted=_format_timestamp(event.timestamp),
                            confidence=event.confidence,
                        )
                    )

            logger.info("Detected %d events (including start)", len(events))

            # If no events detected beyond start, try transcript-based detection
            if len(events) < 2 and len(transcript_chunks) > 2:
                logger.info("Using transcript-based event detection as fallback")
                # Create events based on transcript gaps or topic changes
                prev_end = 0.0
                for chunk in transcript_chunks:
                    # Large gap suggests topic change
                    if chunk.start - prev_end > 20.0:
                        events.append(
                            EventItem(
                                timestamp=chunk.start,
                                timestamp_formatted=_format_timestamp(chunk.start),
                                confidence=0.7,
                            )
                        )
                    prev_end = chunk.end

                # Ensure events are sorted and deduplicated
                events = sorted(events, key=lambda e: e.timestamp)
                seen = set()
                unique_events = []
                for evt in events:
                    key = round(evt.timestamp / 10) * 10  # 10s buckets
                    if key not in seen:
                        seen.add(key)
                        unique_events.append(evt)
                events = unique_events[:10]  # Limit to 10 events

        except Exception as e:
            logger.warning("Event detection failed: %s, using single start event", e)
            events = [
                EventItem(
                    timestamp=0.0,
                    timestamp_formatted="0:00",
                    confidence=1.0,
                )
            ]

        # Stage 8: Build index
        update_progress(
            ProcessingStage.BUILDING_INDEX, 0.95, "Building search index..."
        )

        # Create result
        result = ProcessingResult(
            metadata=metadata,
            events=events,
            transcript=transcript_chunks,
            processing_time=3.5,
        )

        # Complete
        with _job_lock:
            if job_id in _jobs:
                _jobs[job_id]["status"] = JobStatus.COMPLETED
                _jobs[job_id]["stage"] = ProcessingStage.COMPLETED
                _jobs[job_id]["progress"] = 1.0
                _jobs[job_id]["message"] = "Processing complete"
                _jobs[job_id]["result"] = result
                _jobs[job_id]["index"] = multimodal_index
                _jobs[job_id]["text_encoder"] = text_encoder

        logger.info(
            "Job %s completed: %d events, %d transcript chunks, index size %d",
            job_id,
            len(events),
            len(transcript_chunks),
            multimodal_index.size if multimodal_index else 0,
        )

    except Exception:
        logger.exception("Job %s failed", job_id)
        with _job_lock:
            if job_id in _jobs:
                _jobs[job_id]["status"] = JobStatus.FAILED
                _jobs[job_id]["error"] = "Processing failed. Please try again."
                _jobs[job_id]["message"] = "Failed"


# Module-level app instance for uvicorn (used by Render deployment)
_startup_logger.info("Creating FastAPI application...")
try:
    app = create_app(use_placeholders=True, debug=False)
    _startup_logger.info("FastAPI application created successfully!")
except Exception as e:
    _startup_logger.error(f"Failed to create FastAPI application: {e}")
    raise


# CLI entry point
def main() -> None:
    """Run the API server."""
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
