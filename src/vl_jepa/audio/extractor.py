"""
SPEC: Audio Extraction from Video

Extract audio track from video files using FFmpeg.

IMPLEMENTS: v0.2.0 G7 - Audio Transcription
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioExtractionError(Exception):
    """Raised when audio extraction fails."""

    pass


def _find_ffmpeg() -> str | None:
    """Find FFmpeg executable path.

    Checks:
    1. System PATH
    2. Winget installation path (Windows)

    Returns:
        Path to ffmpeg executable, or None if not found
    """
    # Check system PATH first
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # Check winget installation path on Windows
    import os
    import sys

    if sys.platform == "win32":
        winget_base = (
            Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
        )
        if winget_base.exists():
            # Find FFmpeg package directory
            for pkg_dir in winget_base.glob("Gyan.FFmpeg*"):
                for bin_dir in pkg_dir.rglob("bin"):
                    ffmpeg_exe = bin_dir / "ffmpeg.exe"
                    if ffmpeg_exe.exists():
                        # Add to PATH for this session
                        os.environ["PATH"] = (
                            str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
                        )
                        logger.info("Found FFmpeg at winget path: %s", bin_dir)
                        return str(ffmpeg_exe)

    return None


def check_ffmpeg_available() -> bool:
    """Check if FFmpeg is available.

    Returns:
        True if ffmpeg command is available
    """
    return _find_ffmpeg() is not None


def get_ffmpeg_path() -> str:
    """Get FFmpeg executable path.

    Returns:
        Path to ffmpeg executable

    Raises:
        AudioExtractionError: If FFmpeg not found
    """
    path = _find_ffmpeg()
    if path is None:
        raise AudioExtractionError(
            "FFmpeg not found. Install FFmpeg:\n"
            "  Windows: winget install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Linux: apt install ffmpeg"
        )
    return path


def extract_audio(
    video_path: str,
    output_path: str | None = None,
    sample_rate: int = 16000,
    mono: bool = True,
) -> str:
    """Extract audio from video file.

    Args:
        video_path: Path to video file
        output_path: Output audio path (auto-generated if None)
        sample_rate: Audio sample rate (16000 for Whisper)
        mono: Convert to mono (required for Whisper)

    Returns:
        Path to extracted audio file

    Raises:
        AudioExtractionError: If extraction fails
        FileNotFoundError: If video file not found
    """
    video = Path(video_path)

    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    ffmpeg = get_ffmpeg_path()

    # Generate output path if not provided
    out_file: Path
    if output_path is None:
        out_file = video.with_suffix(".wav")
    else:
        out_file = Path(output_path)

    logger.info("Extracting audio: %s -> %s", video.name, out_file.name)

    # Build FFmpeg command
    cmd = [
        ffmpeg,
        "-i",
        str(video),
        "-vn",  # No video
        "-acodec",
        "pcm_s16le",  # WAV format
        "-ar",
        str(sample_rate),  # Sample rate
    ]

    if mono:
        cmd.extend(["-ac", "1"])  # Mono

    cmd.extend(
        [
            "-y",  # Overwrite output
            str(out_file),
        ]
    )

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info("Audio extracted: %s", out_file)
        return str(out_file)

    except subprocess.CalledProcessError as e:
        logger.error("FFmpeg failed: %s", e.stderr)
        raise AudioExtractionError(f"FFmpeg failed: {e.stderr}") from e


def extract_audio_segment(
    video_path: str,
    start_time: float,
    end_time: float,
    output_path: str | None = None,
) -> str:
    """Extract a segment of audio from video.

    Args:
        video_path: Path to video file
        start_time: Start time in seconds
        end_time: End time in seconds
        output_path: Output audio path (auto-generated if None)

    Returns:
        Path to extracted audio segment
    """
    video = Path(video_path)

    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    ffmpeg = get_ffmpeg_path()

    # Generate output path
    out_file: str
    if output_path is None:
        # Use with_name since suffix must start with '.'
        out_file = str(video.with_name(f"{video.stem}_{start_time:.0f}_{end_time:.0f}.wav"))
    else:
        out_file = output_path

    duration = end_time - start_time

    cmd = [
        ffmpeg,
        "-i",
        str(video),
        "-ss",
        str(start_time),
        "-t",
        str(duration),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-y",
        out_file,
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return out_file
    except subprocess.CalledProcessError as e:
        raise AudioExtractionError(f"FFmpeg failed: {e.stderr}") from e


def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds
    """
    ffmpeg = get_ffmpeg_path()
    # ffprobe is in the same directory as ffmpeg
    ffprobe = str(
        Path(ffmpeg).parent
        / ("ffprobe.exe" if Path(ffmpeg).suffix == ".exe" else "ffprobe")
    )

    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        raise AudioExtractionError(f"Failed to get duration: {e}") from e
