"""
VL-JEPA Lecture Summarizer - Shared Test Fixtures

This module provides shared fixtures for all test categories:
- Unit tests
- Property tests
- Integration tests
- Benchmark tests
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


import numpy as np  # noqa: E402
import pytest  # noqa: E402

# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def test_videos_dir(test_data_dir: Path) -> Path:
    """Return path to test videos directory."""
    return test_data_dir / "videos"


@pytest.fixture
def test_models_dir(test_data_dir: Path) -> Path:
    """Return path to test models directory."""
    return test_data_dir / "models"


# =============================================================================
# Mock Data Fixtures
# =============================================================================


@pytest.fixture
def sample_frame() -> np.ndarray:
    """Return a sample normalized frame (224, 224, 3) in [-1, 1]."""
    return np.random.uniform(-1.0, 1.0, (224, 224, 3)).astype(np.float32)


@pytest.fixture
def sample_frame_batch() -> np.ndarray:
    """Return a batch of normalized frames (4, 3, 224, 224)."""
    return np.random.uniform(-1.0, 1.0, (4, 3, 224, 224)).astype(np.float32)


@pytest.fixture
def sample_embedding() -> np.ndarray:
    """Return a sample L2-normalized 768-dim embedding."""
    emb = np.random.randn(768).astype(np.float32)
    return emb / np.linalg.norm(emb)


@pytest.fixture
def sample_embedding_batch() -> np.ndarray:
    """Return a batch of L2-normalized embeddings (10, 768)."""
    emb = np.random.randn(10, 768).astype(np.float32)
    return emb / np.linalg.norm(emb, axis=1, keepdims=True)


@pytest.fixture
def sample_text_embedding() -> np.ndarray:
    """Return a sample L2-normalized 384-dim text embedding."""
    emb = np.random.randn(384).astype(np.float32)
    return emb / np.linalg.norm(emb)


# =============================================================================
# Mock Model Fixtures
# =============================================================================


@pytest.fixture
def mock_visual_encoder():
    """Return a mock visual encoder that produces 768-dim embeddings."""

    class MockVisualEncoder:
        def encode(self, frames: np.ndarray) -> np.ndarray:
            batch_size = frames.shape[0]
            emb = np.random.randn(batch_size, 768).astype(np.float32)
            return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    return MockVisualEncoder()


@pytest.fixture
def mock_text_encoder():
    """Return a mock text encoder that produces 768-dim projected embeddings."""

    class MockTextEncoder:
        def encode(self, text: str) -> np.ndarray:
            emb = np.random.randn(768).astype(np.float32)
            return emb / np.linalg.norm(emb)

    return MockTextEncoder()


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================


@pytest.fixture
def temp_lecture_dir(tmp_path: Path) -> Path:
    """Return a temporary lecture data directory."""
    lecture_dir = tmp_path / "lecture_001"
    lecture_dir.mkdir()
    return lecture_dir


@pytest.fixture
def temp_db_path(temp_lecture_dir: Path) -> Path:
    """Return path for temporary SQLite database."""
    return temp_lecture_dir / "metadata.db"


# =============================================================================
# Pytest Markers
# =============================================================================


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "property: Property-based tests with Hypothesis")
    config.addinivalue_line(
        "markers", "integration: Integration tests (may require network/GPU)"
    )
    config.addinivalue_line("markers", "benchmark: Performance benchmark tests")
    config.addinivalue_line(
        "markers", "slow: Slow tests that may be skipped in quick runs"
    )
    config.addinivalue_line("markers", "gpu: Tests that require GPU")
    config.addinivalue_line("markers", "network: Tests that require network access")
