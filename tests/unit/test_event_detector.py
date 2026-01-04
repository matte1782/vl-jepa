"""
SPEC: S005 - Event Detection
TEST_IDs: T005.1-T005.5
"""

import numpy as np
import pytest

from vl_jepa.detector import EventDetector


class TestEventDetector:
    """Tests for semantic boundary event detection (S005)."""

    # T005.1: Detect boundary on embedding change
    @pytest.mark.unit
    def test_detect_boundary_on_embedding_change(
        self, sample_embedding: np.ndarray
    ) -> None:
        """
        SPEC: S005
        TEST_ID: T005.1
        Given: Two embeddings with cosine distance > threshold
        When: EventDetector.process() is called
        Then: An event is detected
        """
        # Arrange
        embedding1 = sample_embedding
        embedding2 = -sample_embedding  # Opposite direction = max distance

        # Act
        detector = EventDetector(threshold=0.3, min_event_gap=0.0)
        detector.process(embedding1, timestamp=0.0)
        event = detector.process(embedding2, timestamp=1.0)

        # Assert
        assert event is not None
        assert event.confidence > 0

    # T005.2: No event on identical embeddings
    @pytest.mark.unit
    def test_no_event_on_identical_embeddings(
        self, sample_embedding: np.ndarray
    ) -> None:
        """
        SPEC: S005
        TEST_ID: T005.2
        EDGE_CASE: EC024
        Given: Identical consecutive embeddings
        When: EventDetector.process() is called
        Then: No event is detected (distance = 0)
        """
        # Arrange
        embedding = sample_embedding

        # Act
        detector = EventDetector(threshold=0.3)
        detector.process(embedding, timestamp=0.0)
        event = detector.process(embedding, timestamp=1.0)

        # Assert
        assert event is None

    # T005.3: Verify smoothing reduces noise
    @pytest.mark.unit
    def test_verify_smoothing_reduces_noise(self) -> None:
        """
        SPEC: S005
        TEST_ID: T005.3
        Given: Noisy embedding sequence
        When: Smoothing window is applied
        Then: Fewer spurious events detected than without smoothing
        """
        # Arrange - create noisy sequence
        np.random.seed(42)
        base = np.random.randn(768).astype(np.float32)
        base = base / np.linalg.norm(base)

        # Add noise
        noisy_embeddings = []
        for _ in range(20):
            noise = np.random.randn(768).astype(np.float32) * 0.1
            noisy = base + noise
            noisy = noisy / np.linalg.norm(noisy)
            noisy_embeddings.append(noisy)

        # Count events without smoothing
        detector_no_smooth = EventDetector(
            threshold=0.1, min_event_gap=0.0, smoothing_window=1
        )
        events_no_smooth = 0
        for i, emb in enumerate(noisy_embeddings):
            if detector_no_smooth.process(emb, float(i)):
                events_no_smooth += 1

        # Count events with smoothing
        detector_smooth = EventDetector(
            threshold=0.1, min_event_gap=0.0, smoothing_window=5
        )
        events_smooth = 0
        for i, emb in enumerate(noisy_embeddings):
            if detector_smooth.process(emb, float(i)):
                events_smooth += 1

        # Assert - smoothing should reduce events
        assert events_smooth <= events_no_smooth

    # T005.4: Verify min_event_gap enforcement
    @pytest.mark.unit
    def test_verify_min_event_gap_enforcement(self) -> None:
        """
        SPEC: S005
        TEST_ID: T005.4
        INVARIANT: INV007
        EDGE_CASE: EC028
        Given: Events detected within min_event_gap
        When: EventDetector filters events
        Then: Only events separated by >= min_event_gap are emitted
        """
        # Arrange
        np.random.seed(42)
        detector = EventDetector(threshold=0.1, min_event_gap=5.0, smoothing_window=1)

        # Create alternating embeddings that would trigger events
        emb1 = np.random.randn(768).astype(np.float32)
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = -emb1  # Opposite

        # Act
        events = []
        detector.process(emb1, 0.0)

        for t in range(1, 20):
            emb = emb2 if t % 2 == 1 else emb1
            event = detector.process(emb, float(t))
            if event:
                events.append(event.timestamp)

        # Assert - events should be at least 5s apart
        for i in range(1, len(events)):
            gap = events[i] - events[i - 1]
            assert gap >= 5.0, f"Event gap {gap} < min_event_gap 5.0"

    # T005.5: Confidence in [0, 1]
    @pytest.mark.unit
    def test_confidence_in_bounds(self) -> None:
        """
        SPEC: S005
        TEST_ID: T005.5
        INVARIANT: INV008
        Given: Any detected event
        When: Confidence is retrieved
        Then: Confidence is in [0.0, 1.0]
        """
        # Arrange
        np.random.seed(42)
        detector = EventDetector(threshold=0.1, min_event_gap=0.0)

        emb1 = np.random.randn(768).astype(np.float32)
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = -emb1

        # Act
        detector.process(emb1, 0.0)
        event = detector.process(emb2, 1.0)

        # Assert
        assert event is not None
        assert 0.0 <= event.confidence <= 1.0
