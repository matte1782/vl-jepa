"""
SPEC: Whisper Audio Transcriber

Whisper-based transcription using faster-whisper (CTranslate2).

IMPLEMENTS: v0.2.0 G7 - Audio Transcription
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from .base import TranscriptSegment

if TYPE_CHECKING:
    from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class WhisperLoadError(Exception):
    """Raised when Whisper model loading fails."""

    pass


class WhisperTranscriber:
    """Whisper transcriber using faster-whisper.

    IMPLEMENTS: v0.2.0 G7
    INVARIANTS: INV_AUDIO_001, INV_AUDIO_002, INV_AUDIO_003

    Uses faster-whisper (CTranslate2) for efficient CPU/GPU inference.
    Supports 99 languages with automatic detection.

    Example:
        transcriber = WhisperTranscriber.load("base")
        segments = transcriber.transcribe("lecture.mp3")

        for seg in segments:
            print(f"[{seg.start:.1f}s] {seg.text}")
    """

    # Available model sizes (speed vs accuracy tradeoff)
    MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v3"]

    def __init__(
        self,
        model: WhisperModel,
        model_size: str = "base",
    ) -> None:
        """Initialize transcriber with loaded model.

        Args:
            model: Loaded faster-whisper model
            model_size: Model size name for logging
        """
        self._model = model
        self._model_size = model_size
        logger.info("WhisperTranscriber initialized with %s model", model_size)

    @classmethod
    def load(
        cls,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
    ) -> WhisperTranscriber:
        """Load Whisper model.

        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
            device: Device to use ("auto", "cpu", "cuda")
            compute_type: Compute type ("auto", "int8", "float16", "float32")

        Returns:
            Initialized WhisperTranscriber

        Raises:
            WhisperLoadError: If model cannot be loaded
        """
        try:
            from faster_whisper import WhisperModel

            logger.info("Loading Whisper %s model...", model_size)

            # Auto-detect best settings
            if device == "auto":
                import torch

                device = "cuda" if torch.cuda.is_available() else "cpu"

            if compute_type == "auto":
                compute_type = "int8" if device == "cpu" else "float16"

            model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )

            logger.info(
                "Whisper loaded: size=%s, device=%s, compute=%s",
                model_size,
                device,
                compute_type,
            )

            return cls(model, model_size)

        except ImportError as e:
            raise WhisperLoadError(
                "faster-whisper not installed. Install with: pip install faster-whisper"
            ) from e
        except Exception as e:
            raise WhisperLoadError(f"Failed to load Whisper: {e}") from e

    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> list[TranscriptSegment]:
        """Transcribe audio file to segments.

        Args:
            audio_path: Path to audio file (wav, mp3, m4a, etc.)
            language: Language code (None for auto-detect)

        Returns:
            List of TranscriptSegment with timestamps
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info("Transcribing %s...", path.name)

        # Run transcription
        segments_iter, info = self._model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,  # Voice Activity Detection
            vad_parameters={"min_silence_duration_ms": 500},
        )

        detected_language = info.language
        logger.info(
            "Detected language: %s (prob=%.2f)",
            detected_language,
            info.language_probability,
        )

        # Convert to TranscriptSegment
        import math

        segments = []
        for seg in segments_iter:
            # Convert log probability to confidence [0, 1]
            # avg_logprob is negative, exp() converts to probability
            if hasattr(seg, "avg_logprob") and seg.avg_logprob is not None:
                confidence = min(1.0, max(0.0, math.exp(seg.avg_logprob)))
            else:
                confidence = 0.9

            segment = TranscriptSegment(
                text=seg.text.strip(),
                start=seg.start,
                end=seg.end,
                confidence=confidence,
                language=detected_language,
            )
            segments.append(segment)

        logger.info(
            "Transcribed %d segments (%.1f minutes)", len(segments), info.duration / 60
        )

        return segments

    def transcribe_with_words(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> tuple[list[TranscriptSegment], list[TranscriptSegment]]:
        """Transcribe with word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detect)

        Returns:
            Tuple of (sentence_segments, word_segments)
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info("Transcribing with word timestamps: %s", path.name)

        # Run transcription with word timestamps
        segments_iter, info = self._model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
        )

        detected_language = info.language

        sentences = []
        words = []

        for seg in segments_iter:
            # Sentence segment
            sentence = TranscriptSegment(
                text=seg.text.strip(),
                start=seg.start,
                end=seg.end,
                confidence=0.9,
                language=detected_language,
            )
            sentences.append(sentence)

            # Word segments
            if hasattr(seg, "words") and seg.words:
                for word in seg.words:
                    word_seg = TranscriptSegment(
                        text=word.word.strip(),
                        start=word.start,
                        end=word.end,
                        confidence=word.probability
                        if hasattr(word, "probability")
                        else 0.9,
                        language=detected_language,
                    )
                    words.append(word_seg)

        logger.info(
            "Transcribed %d sentences, %d words",
            len(sentences),
            len(words),
        )

        return sentences, words


def check_whisper_available() -> bool:
    """Check if Whisper can be loaded.

    Returns:
        True if faster-whisper is available
    """
    import importlib.util

    return importlib.util.find_spec("faster_whisper") is not None
