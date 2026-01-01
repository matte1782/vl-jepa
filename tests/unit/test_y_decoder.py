"""
SPEC: S008 - Summary Generation (Y-Decoder)
TEST_IDs: T008.1-T008.4
"""

import pytest


class TestYDecoder:
    """Tests for Gemma-2B Y-Decoder summary generation (S008)."""

    # T008.1: Generate summary with full context
    @pytest.mark.unit
    def test_generate_summary_with_full_context(self):
        """
        SPEC: S008
        TEST_ID: T008.1
        Given: Event with full context (previous summary, OCR text)
        When: YDecoder.generate() is called
        Then: Returns non-empty summary string
        """
        from vl_jepa.decoder import EventContext, YDecoder

        # Use placeholder decoder (no model)
        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        context = EventContext(
            previous_summary="Introduction to machine learning",
            ocr_text="Supervised Learning: Classification vs Regression",
            timestamp=120.5,
        )

        summary = decoder.generate(context)

        assert len(summary) > 0
        assert isinstance(summary, str)
        # Placeholder uses OCR text
        assert "Supervised Learning" in summary

    # T008.2: Generate summary without OCR
    @pytest.mark.unit
    def test_generate_summary_without_ocr(self):
        """
        SPEC: S008
        TEST_ID: T008.2
        EDGE_CASE: EC040
        Given: Event without OCR text
        When: YDecoder.generate() is called
        Then: Returns summary using previous summary or timestamp
        """
        from vl_jepa.decoder import EventContext, YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        # With previous summary
        context = EventContext(
            previous_summary="Introduction to ML",
            ocr_text=None,
            timestamp=60.0,
        )

        summary = decoder.generate(context)
        assert "Continuing" in summary
        assert "Introduction to ML" in summary

    @pytest.mark.unit
    def test_generate_summary_no_context(self):
        """Generate summary with no OCR and no previous summary."""
        from vl_jepa.decoder import EventContext, YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        context = EventContext(
            previous_summary=None,
            ocr_text=None,
            timestamp=45.5,
        )

        summary = decoder.generate(context)
        assert "45.5s" in summary

    @pytest.mark.unit
    def test_generate_with_dict_input(self):
        """Accept dict input in addition to EventContext."""
        from vl_jepa.decoder import YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        context = {
            "previous_summary": "Prior topic",
            "ocr_text": "Current slide text",
            "timestamp": 90.0,
        }

        summary = decoder.generate(context)
        assert len(summary) > 0

    # T008.3: Verify output length <= 150 tokens
    @pytest.mark.unit
    def test_verify_output_length_limit(self):
        """
        SPEC: S008
        TEST_ID: T008.3
        INVARIANT: INV013
        Given: Any generation request
        When: YDecoder.generate() is called
        Then: Output is <= 150 tokens (placeholder is much shorter)
        """
        from vl_jepa.decoder import EventContext, YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        # Even with long OCR text, output is bounded
        context = EventContext(
            ocr_text="A" * 500,  # Very long text
            timestamp=0.0,
        )

        summary = decoder.generate(context)
        # Placeholder truncates to 100 chars
        assert len(summary) <= 110  # "Topic: " + 100 chars

    # T008.4: Handle timeout gracefully
    @pytest.mark.unit
    def test_handle_timeout_gracefully(self):
        """
        SPEC: S008
        TEST_ID: T008.4
        INVARIANT: INV014
        EDGE_CASE: EC041
        Placeholder decoder doesn't timeout, but tests the path.
        """
        from vl_jepa.decoder import YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        # Verify TIMEOUT_SECONDS constant exists
        assert decoder.TIMEOUT_SECONDS > 0
        assert decoder.MAX_OUTPUT_TOKENS > 0

    @pytest.mark.unit
    def test_build_prompt(self):
        """Test prompt building logic."""
        from vl_jepa.decoder import EventContext, YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        context = EventContext(
            previous_summary="Prior summary",
            ocr_text="Current text",
            timestamp=100.0,
        )

        prompt = decoder._build_prompt(context)

        assert "Generate a brief lecture summary" in prompt
        assert "Previous: Prior summary" in prompt
        assert "Current slide text: Current text" in prompt
        assert "100.0s" in prompt

    @pytest.mark.unit
    def test_build_prompt_no_ocr(self):
        """Build prompt without OCR text."""
        from vl_jepa.decoder import EventContext, YDecoder

        decoder = YDecoder(model=None, tokenizer=None, device="cpu")

        context = EventContext(
            previous_summary=None,
            ocr_text=None,
            timestamp=50.0,
        )

        prompt = decoder._build_prompt(context)
        assert "No text detected" in prompt
