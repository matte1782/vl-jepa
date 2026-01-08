"""
Pydantic models for API requests and responses.

IMPLEMENTS: S014 - REST API Interface
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Processing job status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStage(str, Enum):
    """Processing pipeline stages."""

    LOADING = "loading"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    SAMPLING_FRAMES = "sampling_frames"
    ENCODING_FRAMES = "encoding_frames"
    ENCODING_TEXT = "encoding_text"
    DETECTING_EVENTS = "detecting_events"
    BUILDING_INDEX = "building_index"
    COMPLETED = "completed"


class ExportFormat(str, Enum):
    """Export format options."""

    MARKDOWN = "markdown"
    JSON = "json"
    SRT = "srt"


# Request Models
class SearchRequest(BaseModel):
    """Search query request."""

    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


# Response Models
class VideoMetadata(BaseModel):
    """Video file metadata."""

    filename: str
    duration: float
    width: int
    height: int
    fps: float
    codec: str


class UploadResponse(BaseModel):
    """Response after video upload."""

    job_id: str
    message: str


class ProgressResponse(BaseModel):
    """Processing progress response."""

    job_id: str
    status: JobStatus
    stage: ProcessingStage | None = None
    progress: float = Field(ge=0.0, le=1.0)
    message: str
    error: str | None = None


class EventItem(BaseModel):
    """Detected event in video."""

    timestamp: float
    timestamp_formatted: str
    confidence: float


class TranscriptChunk(BaseModel):
    """Transcript segment."""

    text: str
    start: float
    end: float
    start_formatted: str
    end_formatted: str


class ProcessingResult(BaseModel):
    """Complete processing result."""

    metadata: VideoMetadata
    events: list[EventItem]
    transcript: list[TranscriptChunk]
    processing_time: float


class ResultsResponse(BaseModel):
    """Response with processing results."""

    job_id: str
    status: JobStatus
    result: ProcessingResult | None = None
    error: str | None = None


class SearchResultItem(BaseModel):
    """Single search result."""

    text: str
    timestamp: float
    timestamp_formatted: str
    score: float
    result_type: str  # "visual" or "transcript"


class SearchResponse(BaseModel):
    """Search results response."""

    query: str
    results: list[SearchResultItem]
    total: int


class ExportResponse(BaseModel):
    """Export result."""

    format: ExportFormat
    content: str
    filename: str


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
