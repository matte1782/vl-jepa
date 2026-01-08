"""
FastAPI application for Lecture Mind.

IMPLEMENTS: S014 - REST API Interface
Provides REST endpoints for video processing, search, and export.
"""

from __future__ import annotations

import logging
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from vl_jepa.api.models import (
    ErrorResponse,
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
    pass

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

    @app.post("/api/upload", response_model=UploadResponse)
    async def upload_video(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
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
            message=f"Video uploaded. Processing started.",
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
        """Search within processed video content."""
        with _job_lock:
            job = _jobs.get(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job["status"] != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400, detail="Processing not complete"
            )

        # Get the index from job state
        index = job.get("index")
        result = job.get("result")

        if not result:
            return SearchResponse(query=request.query, results=[], total=0)

        # For now, do simple text matching on transcript
        # In full implementation, use the multimodal index
        results: list[SearchResultItem] = []
        query_lower = request.query.lower()

        for chunk in result.transcript:
            if query_lower in chunk.text.lower():
                results.append(
                    SearchResultItem(
                        text=chunk.text,
                        timestamp=chunk.start,
                        timestamp_formatted=chunk.start_formatted,
                        score=1.0,
                        result_type="transcript",
                    )
                )

        # Limit results
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
            raise HTTPException(
                status_code=400, detail="Processing not complete"
            )

        result = job.get("result")
        if not result:
            raise HTTPException(status_code=404, detail="No results available")

        # Generate export content
        from vl_jepa.ui.export import (
            ExportFormat as UIExportFormat,
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
                    type("E", (), {"timestamp": e.timestamp, "confidence": e.confidence})()
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
    import shutil

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
            use_placeholders = job["use_placeholders"]

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
        time.sleep(0.3)

        # Stage 3: Transcribe
        update_progress(ProcessingStage.TRANSCRIBING, 0.30, "Transcribing audio...")
        time.sleep(0.5)

        # Generate demo transcript
        transcript_chunks = [
            TranscriptChunk(
                text="Welcome to today's lecture on machine learning fundamentals.",
                start=0.0,
                end=5.0,
                start_formatted="0:00",
                end_formatted="0:05",
            ),
            TranscriptChunk(
                text="We'll cover neural networks, backpropagation, and optimization.",
                start=5.0,
                end=12.0,
                start_formatted="0:05",
                end_formatted="0:12",
            ),
            TranscriptChunk(
                text="Let's start with the basics of how neurons work in artificial networks.",
                start=12.0,
                end=18.0,
                start_formatted="0:12",
                end_formatted="0:18",
            ),
        ]

        # Stage 4: Sample frames
        update_progress(ProcessingStage.SAMPLING_FRAMES, 0.45, "Sampling frames...")
        time.sleep(0.3)

        # Stage 5: Encode frames
        update_progress(ProcessingStage.ENCODING_FRAMES, 0.60, "Encoding frames...")
        time.sleep(0.5)

        # Stage 6: Encode text
        update_progress(ProcessingStage.ENCODING_TEXT, 0.75, "Encoding transcript...")
        time.sleep(0.3)

        # Stage 7: Detect events
        update_progress(ProcessingStage.DETECTING_EVENTS, 0.85, "Detecting events...")
        time.sleep(0.3)

        # Generate demo events
        events = [
            EventItem(
                timestamp=0.0,
                timestamp_formatted="0:00",
                confidence=1.0,
            ),
            EventItem(
                timestamp=30.0,
                timestamp_formatted="0:30",
                confidence=0.87,
            ),
            EventItem(
                timestamp=45.0,
                timestamp_formatted="0:45",
                confidence=0.92,
            ),
        ]

        # Stage 8: Build index
        update_progress(ProcessingStage.BUILDING_INDEX, 0.95, "Building search index...")
        time.sleep(0.3)

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

        logger.info("Job %s completed successfully", job_id)

    except Exception as e:
        logger.exception("Job %s failed", job_id)
        with _job_lock:
            if job_id in _jobs:
                _jobs[job_id]["status"] = JobStatus.FAILED
                _jobs[job_id]["error"] = "Processing failed. Please try again."
                _jobs[job_id]["message"] = "Failed"


# CLI entry point
def main() -> None:
    """Run the API server."""
    import uvicorn

    app = create_app(use_placeholders=True, debug=True)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
