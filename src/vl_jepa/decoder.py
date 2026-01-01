"""
SPEC: S008 - Summary Generation (Y-Decoder)

Gemma-2B based Y-decoder for generating event summaries.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EventContext:
    """Context for summary generation."""

    previous_summary: str | None = None
    ocr_text: str | None = None
    timestamp: float = 0.0


class YDecoder:
    """Y-Decoder for generating event summaries.

    IMPLEMENTS: S008
    INVARIANTS: INV013, INV014

    Uses Gemma-2B or similar small LLM to generate concise
    summaries from event context.

    Example:
        decoder = YDecoder.load()
        context = EventContext(
            previous_summary="Introduction to ML",
            ocr_text="Supervised Learning",
            timestamp=120.5
        )
        summary = decoder.generate(context)
    """

    MAX_OUTPUT_TOKENS: int = 150
    TIMEOUT_SECONDS: float = 5.0

    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        device: str = "cpu",
    ) -> None:
        """Initialize decoder.

        Args:
            model: Language model
            tokenizer: Tokenizer
            device: Device to run on
        """
        self._model = model
        self._tokenizer = tokenizer
        self._device = device

    @classmethod
    def load(
        cls,
        model_name: str = "google/gemma-2b",
        device: str | None = None,
    ) -> YDecoder:
        """Load decoder model.

        Args:
            model_name: HuggingFace model name
            device: Device to load to (auto-detect if None)

        Returns:
            Initialized YDecoder
        """
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map=device,
            )

            logger.info(f"Loaded decoder: {model_name} on {device}")

            return cls(model, tokenizer, device)

        except ImportError:
            logger.warning("transformers not installed, using placeholder decoder")
            return cls(None, None, "cpu")

        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using placeholder")
            return cls(None, None, "cpu")

    def generate(self, context: dict[str, Any] | EventContext) -> str:
        """Generate summary from context.

        INVARIANT: INV013 - Output <= 150 tokens
        INVARIANT: INV014 - Timeout handling

        Args:
            context: Event context (dict or EventContext)

        Returns:
            Generated summary text
        """
        # Convert dict to EventContext if needed
        if isinstance(context, dict):
            context = EventContext(
                previous_summary=context.get("previous_summary"),
                ocr_text=context.get("ocr_text"),
                timestamp=context.get("timestamp", 0.0),
            )

        # Build prompt
        prompt = self._build_prompt(context)

        # Generate
        if self._model is not None:
            return self._generate_with_model(prompt)
        else:
            return self._generate_placeholder(context)

    def _build_prompt(self, context: EventContext) -> str:
        """Build generation prompt from context."""
        parts = ["Generate a brief lecture summary."]

        if context.previous_summary:
            parts.append(f"Previous: {context.previous_summary}")

        if context.ocr_text:
            parts.append(f"Current slide text: {context.ocr_text}")
        else:
            parts.append("Note: No text detected on slide")

        parts.append(f"Timestamp: {context.timestamp:.1f}s")
        parts.append("Summary:")

        return "\n".join(parts)

    def _generate_with_model(self, prompt: str) -> str:
        """Generate using actual model.

        INVARIANT: INV013 - Max 150 tokens
        INVARIANT: INV014 - Timeout handling (cross-platform)
        """
        import concurrent.futures

        import torch

        def _do_generate() -> str:
            """Inner generation function for timeout wrapper."""
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)

            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=self.MAX_OUTPUT_TOKENS,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self._tokenizer.eos_token_id,
                )

            # Decode and extract summary
            full_text: str = self._tokenizer.decode(
                outputs[0], skip_special_tokens=True
            )
            return full_text[len(prompt) :].strip()

        # Cross-platform timeout using ThreadPoolExecutor
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(_do_generate)
                return future.result(timeout=self.TIMEOUT_SECONDS)

        except concurrent.futures.TimeoutError:
            logger.warning("Generation timeout, returning placeholder")
            return "[Summary generation timed out]"

    def _generate_placeholder(self, context: EventContext) -> str:
        """Generate placeholder summary for testing."""
        if context.ocr_text:
            return f"Topic: {context.ocr_text[:100]}"
        elif context.previous_summary:
            return f"Continuing: {context.previous_summary[:50]}..."
        else:
            return f"Lecture segment at {context.timestamp:.1f}s"
