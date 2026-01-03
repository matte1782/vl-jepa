"""
Audio processing module for Lecture Mind.

IMPLEMENTS: v0.2.0 G7 - Audio Transcription

This package provides:
- Audio extraction from video files
- Whisper-based transcription with timestamps
- Transcript chunking for embedding

Example:
    from vl_jepa.audio import Transcriber, extract_audio

    # Extract audio from video
    audio_path = extract_audio("lecture.mp4")

    # Transcribe with timestamps
    transcriber = Transcriber.load()
    segments = transcriber.transcribe(audio_path)

    for seg in segments:
        print(f"[{seg.start:.1f}s] {seg.text}")
"""

from .base import (
    TranscriberProtocol,
    TranscriptSegment,
    validate_segments,
)

# Chunker for splitting transcripts into time windows
from .chunker import (
    TranscriptChunk,
    TranscriptChunker,
    chunk_transcript,
)

# Extractor always available (uses FFmpeg)
from .extractor import (
    AudioExtractionError,
    check_ffmpeg_available,
    extract_audio,
    extract_audio_segment,
    get_audio_duration,
    get_ffmpeg_path,
)

# Placeholder transcriber always available
from .placeholder import PlaceholderTranscriber

# Whisper is optional - requires faster-whisper
try:
    from .transcriber import (
        WhisperLoadError,
        WhisperTranscriber,
        check_whisper_available,
    )
except ImportError:
    WhisperTranscriber = None  # type: ignore[misc, assignment]
    WhisperLoadError = None  # type: ignore[misc, assignment]

    def check_whisper_available() -> bool:
        return False


__all__ = [
    # Protocol
    "TranscriberProtocol",
    "TranscriptSegment",
    "validate_segments",
    # Chunker
    "TranscriptChunk",
    "TranscriptChunker",
    "chunk_transcript",
    # Extraction
    "extract_audio",
    "extract_audio_segment",
    "get_audio_duration",
    "get_ffmpeg_path",
    "check_ffmpeg_available",
    "AudioExtractionError",
    # Placeholder
    "PlaceholderTranscriber",
    # Whisper
    "WhisperTranscriber",
    "WhisperLoadError",
    "check_whisper_available",
]
