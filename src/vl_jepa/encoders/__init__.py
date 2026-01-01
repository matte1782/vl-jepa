"""
Encoder implementations for Lecture Mind.

IMPLEMENTS: Gate 0.3 - Encoder Interface Design

This package provides:
- Protocol definitions for visual and text encoders
- Placeholder implementations for testing
- DINOv2 implementation for production use

Example:
    from vl_jepa.encoders import DINOv2Encoder, PlaceholderVisualEncoder

    # For testing
    encoder = PlaceholderVisualEncoder()

    # For production
    encoder = DINOv2Encoder.load(device="cuda")

    embeddings = encoder.encode(frames)
"""

from .base import (
    TEXT_EMBEDDING_DIM,
    VISUAL_EMBEDDING_DIM,
    TextEncoderProtocol,
    VisualEncoderProtocol,
    validate_text_embedding,
    validate_visual_embedding,
)
from .placeholder import PlaceholderTextEncoder, PlaceholderVisualEncoder

# DINOv2 is optional - requires transformers
try:
    from .dinov2 import DINOv2Encoder, DINOv2LoadError, check_dinov2_available
except ImportError:
    DINOv2Encoder = None  # type: ignore[misc, assignment]
    DINOv2LoadError = None  # type: ignore[misc, assignment]

    def check_dinov2_available() -> bool:
        return False


__all__ = [
    # Protocols
    "VisualEncoderProtocol",
    "TextEncoderProtocol",
    # Constants
    "VISUAL_EMBEDDING_DIM",
    "TEXT_EMBEDDING_DIM",
    # Validation
    "validate_visual_embedding",
    "validate_text_embedding",
    # Placeholders
    "PlaceholderVisualEncoder",
    "PlaceholderTextEncoder",
    # DINOv2
    "DINOv2Encoder",
    "DINOv2LoadError",
    "check_dinov2_available",
]
