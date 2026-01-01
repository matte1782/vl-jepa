"""
SPEC: S003 - Frame Sampling and Normalization
TEST_IDs: T003.1-T003.5
"""

import numpy as np
import pytest

from vl_jepa.frame import FrameSampler


class TestFrameSampler:
    """Tests for frame sampling and normalization (S003)."""

    # T003.1: Verify output shape 224x224x3
    @pytest.mark.unit
    def test_verify_output_shape(self) -> None:
        """
        SPEC: S003
        TEST_ID: T003.1
        INVARIANT: INV003
        Given: A frame of any valid resolution
        When: FrameSampler.process() is called
        Then: Output shape is exactly (224, 224, 3)
        """
        # Arrange
        input_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)

        # Act
        sampler = FrameSampler()
        output = sampler.process(input_frame)

        # Assert
        assert output.shape == (224, 224, 3)

    # T003.2: Verify normalization range
    @pytest.mark.unit
    def test_verify_normalization_range(self) -> None:
        """
        SPEC: S003
        TEST_ID: T003.2
        INVARIANT: INV004
        Given: A frame with pixel values [0, 255]
        When: FrameSampler.process() is called
        Then: Output values are in [-1.0, 1.0]
        """
        # Arrange
        input_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Act
        sampler = FrameSampler()
        output = sampler.process(input_frame)

        # Assert
        assert output.min() >= -1.0
        assert output.max() <= 1.0
        assert output.dtype == np.float32

    # T003.3: Test center_crop mode
    @pytest.mark.unit
    def test_center_crop_mode(self) -> None:
        """
        SPEC: S003
        TEST_ID: T003.3
        EDGE_CASE: EC011
        Given: A non-square frame (1920x1080)
        When: FrameSampler with mode='center_crop' processes it
        Then: Center 1080x1080 is cropped, then resized to 224x224
        """
        # Arrange
        input_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)

        # Act
        sampler = FrameSampler(mode="center_crop")
        output = sampler.process(input_frame)

        # Assert
        assert output.shape == (224, 224, 3)

    # T003.4: Test resize mode
    @pytest.mark.unit
    def test_resize_mode(self) -> None:
        """
        SPEC: S003
        TEST_ID: T003.4
        Given: A non-square frame (1920x1080)
        When: FrameSampler with mode='resize' processes it
        Then: Frame is stretched to 224x224 (may distort aspect ratio)
        """
        # Arrange
        input_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)

        # Act
        sampler = FrameSampler(mode="resize")
        output = sampler.process(input_frame)

        # Assert
        assert output.shape == (224, 224, 3)

    # T003.5: Test pad mode
    @pytest.mark.unit
    def test_pad_mode(self) -> None:
        """
        SPEC: S003
        TEST_ID: T003.5
        Given: A non-square frame (1920x1080)
        When: FrameSampler with mode='pad' processes it
        Then: Frame is padded to square, then resized to 224x224
        """
        # Arrange
        input_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)

        # Act
        sampler = FrameSampler(mode="pad")
        output = sampler.process(input_frame)

        # Assert
        assert output.shape == (224, 224, 3)
