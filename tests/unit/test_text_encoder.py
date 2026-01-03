"""
SPEC: S006 - Text Encoding with Projection
TEST_IDs: T006.1-T006.5
"""

import numpy as np
import pytest


class TestTextEncoder:
    """Tests for MiniLM text encoder with projection (S006)."""

    # T006.1: Verify output shape (768,)
    @pytest.mark.unit
    def test_verify_output_shape(self):
        """
        SPEC: S006
        TEST_ID: T006.1
        INVARIANT: INV009
        Given: A text query string
        When: TextEncoder.encode() is called
        Then: Output shape is (768,)
        """
        from vl_jepa.text import TextEncoder

        # Use placeholder encoder (no model)
        encoder = TextEncoder(model=None)
        embedding = encoder.encode("What is gradient descent?")

        assert embedding.shape == (768,)

    # T006.2: Verify L2 normalization
    @pytest.mark.unit
    def test_verify_l2_normalization(self):
        """
        SPEC: S006
        TEST_ID: T006.2
        INVARIANT: INV010
        Given: A projected text embedding
        When: L2 norm is computed
        Then: Norm is approximately 1.0
        """
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder(model=None)
        embedding = encoder.encode("Test query")

        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-5

    # T006.3: Handle long query truncation
    @pytest.mark.unit
    def test_handle_long_query_truncation(self):
        """
        SPEC: S006
        TEST_ID: T006.3
        EDGE_CASE: EC030
        Given: A query with >256 tokens
        When: TextEncoder.encode() is called
        Then: Query is truncated, valid embedding returned
        """
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder(model=None)
        long_query = " ".join(["word"] * 500)  # Very long query

        embedding = encoder.encode(long_query)

        # Should still return valid embedding
        assert embedding.shape == (768,)
        assert abs(np.linalg.norm(embedding) - 1.0) < 1e-5

    # T006.4: Reject empty query
    @pytest.mark.unit
    def test_reject_empty_query(self):
        """
        SPEC: S006
        TEST_ID: T006.4
        EDGE_CASE: EC029
        Given: An empty query string
        When: TextEncoder.encode() is called
        Then: Raises ValueError
        """
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder(model=None)
        with pytest.raises(ValueError):
            encoder.encode("")

    # T006.5: Batch encoding works
    @pytest.mark.unit
    def test_batch_encoding_works(self):
        """
        SPEC: S006
        TEST_ID: T006.5
        Given: A list of query strings
        When: TextEncoder.encode_batch() is called
        Then: Returns array of shape (N, 768)
        """
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder(model=None)
        queries = [
            "What is machine learning?",
            "Explain backpropagation",
            "How do neural networks work?",
        ]

        embeddings = encoder.encode_batch(queries)

        assert embeddings.shape == (3, 768)
        # Each should be normalized
        for i in range(3):
            norm = np.linalg.norm(embeddings[i])
            assert abs(norm - 1.0) < 1e-5

    @pytest.mark.unit
    def test_output_dimensions(self):
        """Output dimension constants are correct."""
        from vl_jepa.text import TextEncoder

        assert TextEncoder.TEXT_DIM == 384
        assert TextEncoder.VISUAL_DIM == 768

    @pytest.mark.unit
    def test_whitespace_query_raises(self):
        """Whitespace-only query raises ValueError."""
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder(model=None)
        with pytest.raises(ValueError):
            encoder.encode("   ")

    @pytest.mark.unit
    def test_default_projection_shape(self):
        """Default projection matrix has correct shape."""
        from vl_jepa.text import TextEncoder

        encoder = TextEncoder(model=None)
        assert encoder._projection.shape == (384, 768)

    @pytest.mark.unit
    def test_custom_projection(self):
        """Custom projection matrix can be provided."""
        from vl_jepa.text import TextEncoder

        custom_proj = np.random.randn(384, 768).astype(np.float32)
        encoder = TextEncoder(model=None, projection=custom_proj)

        assert np.array_equal(encoder._projection, custom_proj)


class TestTextEncoderRealModel:
    """Tests for TextEncoder with real sentence-transformers model."""

    @pytest.fixture
    def encoder(self):
        """Load real text encoder, skip if model not available."""
        from vl_jepa.text import TextEncoder

        enc = TextEncoder.load()
        if enc._model is None:
            pytest.skip("sentence-transformers model not available")
        return enc

    @pytest.mark.unit
    def test_real_model_output_shape(self, encoder):
        """Real model produces 768-dim embeddings."""
        embedding = encoder.encode("Test sentence for embedding")
        assert embedding.shape == (768,)

    @pytest.mark.unit
    def test_real_model_l2_normalized(self, encoder):
        """Real model embeddings are L2 normalized."""
        embedding = encoder.encode("Another test sentence")
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-5

    @pytest.mark.unit
    def test_real_model_semantic_similarity(self, encoder):
        """Related texts have higher similarity than unrelated texts."""
        emb1 = encoder.encode("machine learning algorithms")
        emb2 = encoder.encode("deep learning neural networks")
        emb3 = encoder.encode("cooking recipes for dinner")

        sim_related = np.dot(emb1, emb2)
        sim_unrelated = np.dot(emb1, emb3)

        assert sim_related > sim_unrelated
        assert sim_related > 0.5  # Related texts should be similar
        assert sim_unrelated < 0.5  # Unrelated texts should be dissimilar

    @pytest.mark.unit
    def test_real_model_dtype(self, encoder):
        """Embeddings are float32."""
        embedding = encoder.encode("Test dtype")
        assert embedding.dtype == np.float32

    @pytest.mark.unit
    def test_real_model_deterministic(self, encoder):
        """Same input produces same output."""
        text = "Deterministic test input"
        emb1 = encoder.encode(text)
        emb2 = encoder.encode(text)

        assert np.allclose(emb1, emb2, atol=1e-6)
