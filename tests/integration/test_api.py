"""
Integration tests for FastAPI endpoints.

IMPLEMENTS: v0.3.0 G1 - Web UI API testing
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if FastAPI is not installed
fastapi = pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from vl_jepa.api.main import create_app, _jobs, _job_lock
from vl_jepa.api.models import JobStatus, ProcessingStage


@pytest.fixture
def client() -> TestClient:
    """Create test client with fresh app."""
    app = create_app(use_placeholders=True, debug=True)
    return TestClient(app)


@pytest.fixture
def clean_jobs():
    """Clean job storage before and after test."""
    with _job_lock:
        _jobs.clear()
    yield
    with _job_lock:
        _jobs.clear()


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_returns_healthy(self, client: TestClient) -> None:
        """Health endpoint returns status healthy."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_service(self, client: TestClient) -> None:
        """Health endpoint includes service name."""
        response = client.get("/api/health")
        data = response.json()
        assert "service" in data
        assert data["service"] == "lecture-mind"


class TestRootEndpoint:
    """Tests for / endpoint."""

    def test_root_returns_html(self, client: TestClient) -> None:
        """Root endpoint returns HTML page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_root_contains_lecture_mind(self, client: TestClient) -> None:
        """Root page contains Lecture Mind branding."""
        response = client.get("/")
        assert "Lecture Mind" in response.text


class TestUploadEndpoint:
    """Tests for /api/upload endpoint."""

    def test_upload_no_file_returns_422(self, client: TestClient) -> None:
        """Upload without file returns validation error."""
        response = client.post("/api/upload")
        assert response.status_code == 422

    def test_upload_empty_file_accepts_mp4(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Upload with empty mp4 file is accepted (fails later in processing)."""
        # API accepts the upload, processing will fail later
        empty_file = io.BytesIO(b"")
        response = client.post(
            "/api/upload",
            files={"file": ("empty.mp4", empty_file, "video/mp4")},
        )
        # Upload succeeds but file is empty - job is created
        assert response.status_code == 200
        assert "job_id" in response.json()

    def test_upload_invalid_extension_returns_400(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Upload with invalid file extension returns bad request."""
        text_file = io.BytesIO(b"not a video")
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", text_file, "text/plain")},
        )
        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()

    def test_upload_valid_video_returns_job_id(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Upload with valid video returns job ID."""
        # Create minimal MP4-like content (just needs to not be empty)
        fake_video = io.BytesIO(b"\x00" * 1000)
        response = client.post(
            "/api/upload",
            files={"file": ("test.mp4", fake_video, "video/mp4")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "message" in data


class TestStatusEndpoint:
    """Tests for /api/status/{job_id} endpoint."""

    def test_status_unknown_job_returns_404(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Status for unknown job returns 404."""
        response = client.get("/api/status/unknown-job-id")
        assert response.status_code == 404

    def test_status_known_job_returns_progress(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Status for known job returns progress."""
        # Add a test job
        job_id = "test-job-123"
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.PROCESSING,
                "stage": ProcessingStage.TRANSCRIBING,
                "progress": 0.3,
                "message": "Transcribing audio...",
                "result": None,
                "error": None,
            }

        response = client.get(f"/api/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["stage"] == "transcribing"
        assert data["progress"] == 0.3

    def test_status_includes_message(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Status endpoint includes message."""
        job_id = "test-job-msg"
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.PROCESSING,
                "stage": ProcessingStage.ENCODING_FRAMES,
                "progress": 0.5,
                "message": "Encoding video frames...",
                "result": None,
                "error": None,
            }

        response = client.get(f"/api/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Encoding video frames..."


class TestResultsEndpoint:
    """Tests for /api/results/{job_id} endpoint."""

    def test_results_unknown_job_returns_404(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Results for unknown job returns 404."""
        response = client.get("/api/results/unknown-job-id")
        assert response.status_code == 404

    def test_results_incomplete_job_returns_status(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Results for incomplete job returns status without result."""
        job_id = "test-job-incomplete"
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.PROCESSING,
                "stage": ProcessingStage.TRANSCRIBING,
                "progress": 0.5,
                "message": "Processing...",
                "result": None,
                "error": None,
            }

        response = client.get(f"/api/results/{job_id}")
        # Results endpoint returns status even for incomplete jobs
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["result"] is None


class TestSearchEndpoint:
    """Tests for /api/search/{job_id} endpoint."""

    def test_search_unknown_job_returns_404(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Search for unknown job returns 404."""
        response = client.post(
            "/api/search/unknown-job-id",
            json={"query": "test query"},
        )
        assert response.status_code == 404

    def test_search_with_query_returns_results(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Search with query returns search results."""
        from vl_jepa.api.models import (
            ProcessingResult,
            TranscriptChunk,
            VideoMetadata,
        )

        job_id = "test-job-search"
        result = ProcessingResult(
            metadata=VideoMetadata(
                filename="test.mp4",
                duration=60.0,
                width=1920,
                height=1080,
                fps=30.0,
                codec="h264",
            ),
            events=[],
            transcript=[
                TranscriptChunk(
                    text="Hello world",
                    start=0.0,
                    end=5.0,
                    start_formatted="0:00",
                    end_formatted="0:05",
                )
            ],
            processing_time=1.5,
        )
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.COMPLETED,
                "stage": ProcessingStage.COMPLETED,
                "progress": 1.0,
                "message": "Done",
                "result": result,
                "error": None,
                "index": None,
                "text_encoder": None,
            }

        response = client.post(
            f"/api/search/{job_id}",
            json={"query": "hello"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "hello"
        assert len(data["results"]) == 1
        assert "Hello world" in data["results"][0]["text"]


class TestExportEndpoint:
    """Tests for /api/export/{job_id}/{format} endpoint."""

    def test_export_unknown_job_returns_404(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Export for unknown job returns 404."""
        response = client.get("/api/export/unknown-job-id/markdown")
        assert response.status_code == 404

    def test_export_invalid_format_returns_422(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Export with invalid format returns validation error."""
        from vl_jepa.api.models import (
            ProcessingResult,
            VideoMetadata,
        )

        job_id = "test-job-export"
        result = ProcessingResult(
            metadata=VideoMetadata(
                filename="test.mp4",
                duration=60.0,
                width=1920,
                height=1080,
                fps=30.0,
                codec="h264",
            ),
            events=[],
            transcript=[],
            processing_time=1.5,
        )
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.COMPLETED,
                "stage": ProcessingStage.COMPLETED,
                "progress": 1.0,
                "message": "Done",
                "result": result,
                "error": None,
            }

        response = client.get(f"/api/export/{job_id}/invalid_format")
        # FastAPI returns 422 for enum validation errors
        assert response.status_code == 422

    def test_export_markdown_returns_content(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Export markdown returns content."""
        from vl_jepa.api.models import (
            ProcessingResult,
            VideoMetadata,
        )

        job_id = "test-job-export-md"
        result = ProcessingResult(
            metadata=VideoMetadata(
                filename="test.mp4",
                duration=60.0,
                width=1920,
                height=1080,
                fps=30.0,
                codec="h264",
            ),
            events=[],
            transcript=[],
            processing_time=1.5,
        )
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.COMPLETED,
                "stage": ProcessingStage.COMPLETED,
                "progress": 1.0,
                "message": "Done",
                "result": result,
                "error": None,
            }

        response = client.get(f"/api/export/{job_id}/markdown")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "markdown"
        assert "content" in data
        assert "filename" in data


class TestDeleteEndpoint:
    """Tests for /api/job/{job_id} DELETE endpoint."""

    def test_delete_unknown_job_returns_404(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Delete unknown job returns 404."""
        response = client.delete("/api/job/unknown-job-id")
        assert response.status_code == 404

    def test_delete_known_job_removes_it(
        self, client: TestClient, clean_jobs
    ) -> None:
        """Delete known job removes it from storage."""
        job_id = "test-job-delete"
        with _job_lock:
            _jobs[job_id] = {
                "status": JobStatus.COMPLETED,
                "stage": ProcessingStage.COMPLETED,
                "progress": 1.0,
                "message": "Done",
                "result": None,
                "error": None,
            }

        response = client.delete(f"/api/job/{job_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Job deleted"

        # Verify job is gone
        with _job_lock:
            assert job_id not in _jobs


class TestAppCreation:
    """Tests for app factory function."""

    def test_create_app_returns_fastapi(self) -> None:
        """create_app returns FastAPI instance."""
        from fastapi import FastAPI
        app = create_app()
        assert isinstance(app, FastAPI)

    def test_create_app_with_placeholders_flag(self) -> None:
        """create_app stores placeholder flag in state."""
        app = create_app(use_placeholders=True)
        assert app.state.use_placeholders is True

        app2 = create_app(use_placeholders=False)
        assert app2.state.use_placeholders is False

    def test_create_app_with_debug_flag(self) -> None:
        """create_app stores debug flag in state."""
        app = create_app(debug=True)
        assert app.state.debug is True

    def test_create_app_has_cors_middleware(self) -> None:
        """create_app adds CORS middleware."""
        app = create_app()
        # Check middleware is registered
        middleware_names = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_names

    def test_create_app_has_docs(self) -> None:
        """create_app enables API docs."""
        app = create_app()
        assert app.docs_url == "/api/docs"
        assert app.redoc_url == "/api/redoc"


class TestModelsValidation:
    """Tests for Pydantic models."""

    def test_job_status_enum_values(self) -> None:
        """JobStatus enum has expected values."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.PROCESSING == "processing"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"

    def test_processing_stage_enum_values(self) -> None:
        """ProcessingStage enum has expected values."""
        assert ProcessingStage.LOADING == "loading"
        assert ProcessingStage.EXTRACTING_AUDIO == "extracting_audio"
        assert ProcessingStage.TRANSCRIBING == "transcribing"
        assert ProcessingStage.SAMPLING_FRAMES == "sampling_frames"
        assert ProcessingStage.ENCODING_FRAMES == "encoding_frames"
        assert ProcessingStage.ENCODING_TEXT == "encoding_text"
        assert ProcessingStage.DETECTING_EVENTS == "detecting_events"
        assert ProcessingStage.BUILDING_INDEX == "building_index"
        assert ProcessingStage.COMPLETED == "completed"

    def test_export_format_enum_values(self) -> None:
        """ExportFormat enum has expected values."""
        from vl_jepa.api.models import ExportFormat
        assert ExportFormat.MARKDOWN == "markdown"
        assert ExportFormat.JSON == "json"
        assert ExportFormat.SRT == "srt"
