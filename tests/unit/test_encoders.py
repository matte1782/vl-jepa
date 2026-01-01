"""
Tests for encoder interfaces and implementations.

IMPLEMENTS: Gate 0.3 - Encoder Interface Tests
"""

import numpy as np
import pytest

from vl_jepa.encoders import (
    VISUAL_EMBEDDING_DIM,
    PlaceholderTextEncoder,
    PlaceholderVisualEncoder,
    TextEncoderProtocol,
    VisualEncoderProtocol,
    validate_text_embedding,
    validate_visual_embedding,
)


class TestVisualEncoderProtocol:
    """Tests for VisualEncoderProtocol compliance."""

    def test_placeholder_implements_protocol(self) -> None:
        """PlaceholderVisualEncoder implements VisualEncoderProtocol."""
        encoder = PlaceholderVisualEncoder()
        assert isinstance(encoder, VisualEncoderProtocol)

    def test_placeholder_has_embedding_dim(self) -> None:
        """Encoder has EMBEDDING_DIM class attribute."""
        assert PlaceholderVisualEncoder.EMBEDDING_DIM == VISUAL_EMBEDDING_DIM

    def test_encode_returns_correct_shape(self) -> None:
        """encode() returns (B, 768) array."""
        encoder = PlaceholderVisualEncoder()
        frames = np.random.randn(4, 3, 224, 224).astype(np.float32)

        embeddings = encoder.encode(frames)

        assert embeddings.shape == (4, VISUAL_EMBEDDING_DIM)

    def test_encode_single_returns_correct_shape(self) -> None:
        """encode_single() returns (768,) array."""
        encoder = PlaceholderVisualEncoder()
        frame = np.random.randn(3, 224, 224).astype(np.float32)

        embedding = encoder.encode_single(frame)

        assert embedding.shape == (VISUAL_EMBEDDING_DIM,)

    def test_embeddings_are_l2_normalized(self) -> None:
        """INV006: Embeddings are L2-normalized."""
        encoder = PlaceholderVisualEncoder()
        frames = np.random.randn(4, 3, 224, 224).astype(np.float32)

        embeddings = encoder.encode(frames)
        norms = np.linalg.norm(embeddings, axis=1)

        np.testing.assert_allclose(norms, 1.0, rtol=1e-4)

    def test_encode_rejects_wrong_dimensions(self) -> None:
        """encode() raises ValueError for wrong input dimensions."""
        encoder = PlaceholderVisualEncoder()
        wrong_dims = np.random.randn(3, 224, 224).astype(np.float32)  # Missing batch

        with pytest.raises(ValueError, match="Expected 4D"):
            encoder.encode(wrong_dims)

    def test_encode_rejects_wrong_channels(self) -> None:
        """encode() raises ValueError for wrong channel count."""
        encoder = PlaceholderVisualEncoder()
        wrong_channels = np.random.randn(2, 4, 224, 224).astype(np.float32)

        with pytest.raises(ValueError, match="Expected.*3,224,224"):
            encoder.encode(wrong_channels)

    def test_deterministic_with_same_seed(self) -> None:
        """Same seed produces same embeddings."""
        enc1 = PlaceholderVisualEncoder(seed=42)
        enc2 = PlaceholderVisualEncoder(seed=42)
        frames = np.random.randn(2, 3, 224, 224).astype(np.float32)

        emb1 = enc1.encode(frames)
        emb2 = enc2.encode(frames)

        np.testing.assert_array_equal(emb1, emb2)


class TestTextEncoderProtocol:
    """Tests for TextEncoderProtocol compliance."""

    def test_placeholder_implements_protocol(self) -> None:
        """PlaceholderTextEncoder implements TextEncoderProtocol."""
        encoder = PlaceholderTextEncoder()
        assert isinstance(encoder, TextEncoderProtocol)

    def test_placeholder_has_visual_dim(self) -> None:
        """Encoder has VISUAL_DIM class attribute."""
        assert PlaceholderTextEncoder.VISUAL_DIM == VISUAL_EMBEDDING_DIM

    def test_encode_returns_correct_shape(self) -> None:
        """encode() returns (768,) array."""
        encoder = PlaceholderTextEncoder()

        embedding = encoder.encode("What is machine learning?")

        assert embedding.shape == (VISUAL_EMBEDDING_DIM,)

    def test_encode_batch_returns_correct_shape(self) -> None:
        """encode_batch() returns (N, 768) array."""
        encoder = PlaceholderTextEncoder()
        texts = ["Hello", "World", "Test"]

        embeddings = encoder.encode_batch(texts)

        assert embeddings.shape == (3, VISUAL_EMBEDDING_DIM)

    def test_embeddings_are_l2_normalized(self) -> None:
        """INV010: Embeddings are L2-normalized."""
        encoder = PlaceholderTextEncoder()

        embedding = encoder.encode("Test query")
        norm = np.linalg.norm(embedding)

        np.testing.assert_allclose(norm, 1.0, rtol=1e-4)

    def test_encode_rejects_empty_text(self) -> None:
        """encode() raises ValueError for empty text."""
        encoder = PlaceholderTextEncoder()

        with pytest.raises(ValueError, match="cannot be empty"):
            encoder.encode("")

    def test_encode_rejects_whitespace_only(self) -> None:
        """encode() raises ValueError for whitespace-only text."""
        encoder = PlaceholderTextEncoder()

        with pytest.raises(ValueError, match="cannot be empty"):
            encoder.encode("   \t\n  ")

    def test_same_text_produces_same_embedding(self) -> None:
        """Same text produces same embedding (deterministic)."""
        encoder = PlaceholderTextEncoder()
        text = "What is gradient descent?"

        emb1 = encoder.encode(text)
        emb2 = encoder.encode(text)

        np.testing.assert_array_equal(emb1, emb2)

    def test_different_text_produces_different_embedding(self) -> None:
        """Different text produces different embedding."""
        encoder = PlaceholderTextEncoder()

        emb1 = encoder.encode("What is supervised learning?")
        emb2 = encoder.encode("How does backpropagation work?")

        assert not np.allclose(emb1, emb2)


class TestValidation:
    """Tests for embedding validation functions."""

    def test_validate_visual_batch_accepts_valid(self) -> None:
        """validate_visual_embedding accepts valid batch embedding."""
        embedding = np.random.randn(4, VISUAL_EMBEDDING_DIM).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)

        # Should not raise
        validate_visual_embedding(embedding, batch=True)

    def test_validate_visual_single_accepts_valid(self) -> None:
        """validate_visual_embedding accepts valid single embedding."""
        embedding = np.random.randn(VISUAL_EMBEDDING_DIM).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)

        # Should not raise
        validate_visual_embedding(embedding, batch=False)

    def test_validate_visual_rejects_wrong_dim(self) -> None:
        """validate_visual_embedding rejects wrong dimensions."""
        embedding = np.random.randn(4, 512).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)

        with pytest.raises(ValueError, match="Expected dim 768"):
            validate_visual_embedding(embedding, batch=True)

    def test_validate_visual_rejects_unnormalized(self) -> None:
        """validate_visual_embedding rejects unnormalized embeddings."""
        embedding = np.random.randn(4, VISUAL_EMBEDDING_DIM).astype(np.float32)
        # Not normalized

        with pytest.raises(ValueError, match="not L2-normalized"):
            validate_visual_embedding(embedding, batch=True)

    def test_validate_text_accepts_valid(self) -> None:
        """validate_text_embedding accepts valid embedding."""
        embedding = np.random.randn(VISUAL_EMBEDDING_DIM).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)

        # Should not raise
        validate_text_embedding(embedding)

    def test_validate_text_rejects_2d(self) -> None:
        """validate_text_embedding rejects 2D array."""
        embedding = np.random.randn(1, VISUAL_EMBEDDING_DIM).astype(np.float32)

        with pytest.raises(ValueError, match="Expected 1D"):
            validate_text_embedding(embedding)
