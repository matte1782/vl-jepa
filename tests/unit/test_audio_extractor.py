"""
Tests for audio extraction module.

IMPLEMENTS: v0.2.0 G7 - Audio Extraction Tests
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vl_jepa.audio.extractor import (
    AudioExtractionError,
    _find_ffmpeg,
    check_ffmpeg_available,
    extract_audio,
    extract_audio_segment,
    get_audio_duration,
    get_ffmpeg_path,
)


class TestAudioExtractionError:
    """Tests for AudioExtractionError exception."""

    def test_exception_creation(self) -> None:
        """AudioExtractionError can be created with message."""
        error = AudioExtractionError("Test error")
        assert str(error) == "Test error"

    def test_exception_inherits_from_exception(self) -> None:
        """AudioExtractionError inherits from Exception."""
        error = AudioExtractionError("Test")
        assert isinstance(error, Exception)

    def test_exception_can_be_raised(self) -> None:
        """AudioExtractionError can be raised and caught."""
        with pytest.raises(AudioExtractionError, match="FFmpeg failed"):
            raise AudioExtractionError("FFmpeg failed")


class TestFindFFmpeg:
    """Tests for _find_ffmpeg internal function."""

    @patch("shutil.which")
    def test_find_ffmpeg_in_path(self, mock_which: MagicMock) -> None:
        """Find FFmpeg when in system PATH."""
        mock_which.return_value = "/usr/bin/ffmpeg"
        result = _find_ffmpeg()
        assert result == "/usr/bin/ffmpeg"
        mock_which.assert_called_once_with("ffmpeg")

    @patch("shutil.which")
    def test_find_ffmpeg_not_in_path_not_windows(self, mock_which: MagicMock) -> None:
        """Return None when FFmpeg not in PATH and not Windows."""
        mock_which.return_value = None
        with patch("sys.platform", "linux"):
            result = _find_ffmpeg()
        assert result is None


class TestCheckFFmpegAvailable:
    """Tests for check_ffmpeg_available function."""

    @patch("vl_jepa.audio.extractor._find_ffmpeg")
    def test_returns_true_when_found(self, mock_find: MagicMock) -> None:
        """Return True when FFmpeg is found."""
        mock_find.return_value = "/usr/bin/ffmpeg"
        assert check_ffmpeg_available() is True

    @patch("vl_jepa.audio.extractor._find_ffmpeg")
    def test_returns_false_when_not_found(self, mock_find: MagicMock) -> None:
        """Return False when FFmpeg is not found."""
        mock_find.return_value = None
        assert check_ffmpeg_available() is False


class TestGetFFmpegPath:
    """Tests for get_ffmpeg_path function."""

    @patch("vl_jepa.audio.extractor._find_ffmpeg")
    def test_returns_path_when_found(self, mock_find: MagicMock) -> None:
        """Return path when FFmpeg is found."""
        mock_find.return_value = "/usr/bin/ffmpeg"
        result = get_ffmpeg_path()
        assert result == "/usr/bin/ffmpeg"

    @patch("vl_jepa.audio.extractor._find_ffmpeg")
    def test_raises_when_not_found(self, mock_find: MagicMock) -> None:
        """Raise AudioExtractionError when FFmpeg not found."""
        mock_find.return_value = None
        with pytest.raises(AudioExtractionError, match="FFmpeg not found"):
            get_ffmpeg_path()


class TestExtractAudio:
    """Tests for extract_audio function."""

    def test_video_not_found_raises_error(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError for missing video."""
        fake_video = tmp_path / "nonexistent.mp4"
        with pytest.raises(FileNotFoundError, match="Video not found"):
            extract_audio(str(fake_video))

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_generates_output_path_when_none(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Generate output path when not provided."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()

        result = extract_audio(str(video))
        expected = str(video.with_suffix(".wav"))
        assert result == expected

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_uses_provided_output_path(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Use provided output path."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()
        output = tmp_path / "output.wav"

        result = extract_audio(str(video), output_path=str(output))
        assert result == str(output)

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_builds_correct_ffmpeg_command(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Build correct FFmpeg command with options."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()

        extract_audio(str(video), sample_rate=22050, mono=True)

        # Check command was called
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]

        assert "/usr/bin/ffmpeg" in cmd
        assert "-vn" in cmd  # No video
        assert "-ar" in cmd
        assert "22050" in cmd  # Sample rate
        assert "-ac" in cmd
        assert "1" in cmd  # Mono

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_stereo_output_omits_mono_flag(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Omit mono flag when mono=False."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()

        extract_audio(str(video), mono=False)

        cmd = mock_run.call_args[0][0]
        # -ac should not be in command for stereo
        # Check command structure without -ac 1
        cmd_str = " ".join(cmd)
        assert "-ac" not in cmd_str or "-ac 1" not in cmd_str

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_ffmpeg_failure_raises_error(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Raise AudioExtractionError on FFmpeg failure."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ffmpeg", stderr="Error decoding"
        )

        video = tmp_path / "test.mp4"
        video.touch()

        with pytest.raises(AudioExtractionError, match="FFmpeg failed"):
            extract_audio(str(video))


class TestExtractAudioSegment:
    """Tests for extract_audio_segment function."""

    def test_video_not_found_raises_error(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError for missing video."""
        fake_video = tmp_path / "nonexistent.mp4"
        with pytest.raises(FileNotFoundError, match="Video not found"):
            extract_audio_segment(str(fake_video), 0.0, 10.0)

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_generates_output_path_with_timestamps(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Generate output path with timestamps when not provided."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()

        result = extract_audio_segment(str(video), 10.0, 30.0)
        assert "_10_30.wav" in result

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_uses_provided_output_path(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Use provided output path."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()
        output = tmp_path / "segment.wav"

        result = extract_audio_segment(str(video), 5.0, 15.0, output_path=str(output))
        assert result == str(output)

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_builds_correct_ffmpeg_command(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Build correct FFmpeg command with time options."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        video = tmp_path / "test.mp4"
        video.touch()

        extract_audio_segment(str(video), 10.0, 25.0)

        cmd = mock_run.call_args[0][0]

        assert "-ss" in cmd  # Start time
        assert "10.0" in cmd
        assert "-t" in cmd  # Duration
        assert "15.0" in cmd  # Duration = 25.0 - 10.0

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_ffmpeg_failure_raises_error(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock, tmp_path: Path
    ) -> None:
        """Raise AudioExtractionError on FFmpeg failure."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ffmpeg", stderr="Seek error"
        )

        video = tmp_path / "test.mp4"
        video.touch()

        with pytest.raises(AudioExtractionError, match="FFmpeg failed"):
            extract_audio_segment(str(video), 0.0, 10.0)


class TestGetAudioDuration:
    """Tests for get_audio_duration function."""

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_returns_duration_as_float(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock
    ) -> None:
        """Return duration as float."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(stdout="125.5\n", returncode=0)

        result = get_audio_duration("/path/to/audio.wav")
        assert result == 125.5

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_uses_ffprobe(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock
    ) -> None:
        """Use ffprobe from same directory as ffmpeg."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(stdout="100.0\n", returncode=0)

        get_audio_duration("/path/to/audio.wav")

        cmd = mock_run.call_args[0][0]
        assert "ffprobe" in cmd[0]

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_ffprobe_failure_raises_error(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock
    ) -> None:
        """Raise AudioExtractionError on ffprobe failure."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ffprobe", stderr="No such file"
        )

        with pytest.raises(AudioExtractionError, match="Failed to get duration"):
            get_audio_duration("/path/to/audio.wav")

    @patch("vl_jepa.audio.extractor.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_invalid_output_raises_error(
        self, mock_run: MagicMock, mock_ffmpeg: MagicMock
    ) -> None:
        """Raise AudioExtractionError on invalid ffprobe output."""
        mock_ffmpeg.return_value = "/usr/bin/ffmpeg"
        mock_run.return_value = MagicMock(stdout="not_a_number\n", returncode=0)

        with pytest.raises(AudioExtractionError, match="Failed to get duration"):
            get_audio_duration("/path/to/audio.wav")


class TestExtractAudioIntegration:
    """Integration tests requiring real FFmpeg."""

    @pytest.mark.skipif(
        not check_ffmpeg_available(),
        reason="FFmpeg not installed",
    )
    @pytest.mark.integration
    def test_extract_audio_real_video(self, tmp_path: Path) -> None:
        """Extract audio from real test video if available."""
        test_video = Path("tests/lecture_ex/December19_I.mp4")
        if not test_video.exists():
            pytest.skip("Test video not available")

        output = tmp_path / "extracted.wav"
        result = extract_audio(str(test_video), output_path=str(output))

        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
