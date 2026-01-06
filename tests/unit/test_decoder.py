"""
SPEC: S008 - Summary Generation (Y-Decoder)
TEST_IDs: T008.1-T008.10
"""

import pytest

from vl_jepa.decoder import EventContext, YDecoder


class TestEventContext:
    """Tests for EventContext dataclass."""

    @pytest.mark.unit
    def test_event_context_defaults(self) -> None:
        """
        SPEC: S008
        TEST_ID: T008.1
        Given: EventContext created with no arguments
        When: Accessed
        Then: Has expected defaults
        """
        # Act
        context = EventContext()

        # Assert
        assert context.previous_summary is None
        assert context.ocr_text is None
        assert context.timestamp == 0.0

    @pytest.mark.unit
    def test_event_context_with_values(self) -> None:
        """
        SPEC: S008
        TEST_ID: T008.2
        Given: EventContext created with values
        When: Accessed
        Then: Has expected values
        """
        # Act
        context = EventContext(
            previous_summary="Introduction",
            ocr_text="Machine Learning",
            timestamp=120.5,
        )

        # Assert
        assert context.previous_summary == "Introduction"
        assert context.ocr_text == "Machine Learning"
        assert context.timestamp == 120.5


class TestYDecoder:
    """Tests for YDecoder class (S008)."""

    @pytest.fixture
    def placeholder_decoder(self) -> YDecoder:
        """Return a placeholder decoder (no real model)."""
        return YDecoder(model=None, tokenizer=None, device="cpu")

    # T008.3: Decoder with placeholder generates summary
    @pytest.mark.unit
    def test_placeholder_decoder_generates_summary(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.3
        Given: Placeholder decoder (no model)
        When: generate is called with ocr_text
        Then: Returns placeholder summary with topic
        """
        # Arrange
        context = EventContext(ocr_text="Gradient Descent", timestamp=60.0)

        # Act
        summary = placeholder_decoder.generate(context)

        # Assert
        assert "Gradient Descent" in summary
        assert summary.startswith("Topic:")

    # T008.4: Placeholder with previous summary
    @pytest.mark.unit
    def test_placeholder_decoder_with_previous_summary(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.4
        Given: Placeholder decoder with previous_summary but no ocr_text
        When: generate is called
        Then: Returns continuation summary
        """
        # Arrange
        context = EventContext(
            previous_summary="Introduction to Neural Networks",
            timestamp=180.0,
        )

        # Act
        summary = placeholder_decoder.generate(context)

        # Assert
        assert "Continuing:" in summary
        assert "Introduction to Neural" in summary

    # T008.5: Placeholder with only timestamp
    @pytest.mark.unit
    def test_placeholder_decoder_with_only_timestamp(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.5
        Given: Placeholder decoder with only timestamp
        When: generate is called
        Then: Returns timestamp-based summary
        """
        # Arrange
        context = EventContext(timestamp=300.0)

        # Act
        summary = placeholder_decoder.generate(context)

        # Assert
        assert "300.0s" in summary
        assert "Lecture segment" in summary

    # T008.6: Generate accepts dict input
    @pytest.mark.unit
    def test_generate_accepts_dict_input(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.6
        Given: Placeholder decoder
        When: generate is called with dict
        Then: Works correctly
        """
        # Arrange
        context_dict = {
            "previous_summary": "Intro",
            "ocr_text": "Deep Learning",
            "timestamp": 240.0,
        }

        # Act
        summary = placeholder_decoder.generate(context_dict)

        # Assert
        assert isinstance(summary, str)
        assert "Deep Learning" in summary

    # T008.7: Generate accepts dict with missing keys
    @pytest.mark.unit
    def test_generate_dict_with_missing_keys(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.7
        Given: Dict with missing keys
        When: generate is called
        Then: Uses defaults for missing keys
        """
        # Arrange
        context_dict = {"ocr_text": "Backpropagation"}

        # Act
        summary = placeholder_decoder.generate(context_dict)

        # Assert
        assert isinstance(summary, str)
        assert "Backpropagation" in summary

    # T008.8: Build prompt includes all components
    @pytest.mark.unit
    def test_build_prompt_includes_all_components(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.8
        Given: EventContext with all fields
        When: _build_prompt is called
        Then: Prompt includes all components
        """
        # Arrange
        context = EventContext(
            previous_summary="Previous topic",
            ocr_text="Current slide text",
            timestamp=120.0,
        )

        # Act
        prompt = placeholder_decoder._build_prompt(context)

        # Assert
        assert "Generate a brief lecture summary" in prompt
        assert "Previous: Previous topic" in prompt
        assert "Current slide text: Current slide text" in prompt
        assert "120.0s" in prompt
        assert "Summary:" in prompt

    # T008.9: Build prompt without OCR text
    @pytest.mark.unit
    def test_build_prompt_without_ocr_text(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.9
        Given: EventContext without ocr_text
        When: _build_prompt is called
        Then: Includes note about no text detected
        """
        # Arrange
        context = EventContext(timestamp=60.0)

        # Act
        prompt = placeholder_decoder._build_prompt(context)

        # Assert
        assert "No text detected on slide" in prompt

    # T008.10: YDecoder.load returns placeholder when no model
    @pytest.mark.unit
    def test_load_returns_placeholder_on_import_error(self) -> None:
        """
        SPEC: S008
        TEST_ID: T008.10
        Given: Transformers may or may not be installed
        When: YDecoder.load is called
        Then: Returns working decoder (either real or placeholder)
        """
        # Act - this should not raise, even without transformers
        decoder = YDecoder.load()

        # Assert - should be a valid decoder
        assert isinstance(decoder, YDecoder)
        assert decoder._device in ["cpu", "cuda"]

        # Should be able to generate
        context = EventContext(ocr_text="Test", timestamp=0.0)
        summary = decoder.generate(context)
        assert isinstance(summary, str)
        assert len(summary) > 0

    # T008.11: OCR text truncated in placeholder
    @pytest.mark.unit
    def test_placeholder_truncates_long_ocr_text(
        self, placeholder_decoder: YDecoder
    ) -> None:
        """
        SPEC: S008
        TEST_ID: T008.11
        Given: Very long OCR text
        When: placeholder generates
        Then: Text is truncated to 100 chars
        """
        # Arrange
        long_text = "A" * 200
        context = EventContext(ocr_text=long_text, timestamp=0.0)

        # Act
        summary = placeholder_decoder.generate(context)

        # Assert - should be truncated
        # Topic: + 100 chars = ~107 chars total max
        assert len(summary) <= 110

    # T008.12: Constants have expected values
    @pytest.mark.unit
    def test_decoder_constants(self) -> None:
        """
        SPEC: S008
        TEST_ID: T008.12
        INVARIANT: INV013, INV014
        Given: YDecoder class
        When: Constants accessed
        Then: Have expected values for invariants
        """
        # Assert
        assert YDecoder.MAX_OUTPUT_TOKENS == 150  # INV013
        assert YDecoder.TIMEOUT_SECONDS == 5.0  # INV014
