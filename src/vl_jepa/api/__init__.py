"""
FastAPI backend for Lecture Mind.

IMPLEMENTS: S014 - REST API Interface
Provides a modern web API with static frontend.
"""

from vl_jepa.api.main import app, create_app

__all__ = ["app", "create_app"]
