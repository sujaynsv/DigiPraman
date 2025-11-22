"""Tests for the image quality layer."""

from __future__ import annotations

import base64

import numpy as np
import cv2

from app.config import quality_config
from app.schemas import EvidenceImage
from app.services.quality import ImageQualityAnalyzer
from app.utils.media_loader import MediaLoader


def _make_base64_image(brightness: int) -> str:
    """Create an in-memory JPEG with uniform brightness for testing."""

    height = max(quality_config.min_height, 10)
    width = max(quality_config.min_width, 10)
    frame = np.full((height, width, 3), brightness, dtype=np.uint8)
    success, buffer = cv2.imencode(".jpg", frame)
    assert success, "Failed to encode test image"
    return base64.b64encode(buffer).decode("utf-8")


def test_quality_passes_for_clear_image() -> None:
    analyzer = ImageQualityAnalyzer(MediaLoader(), quality_config)
    evidence = EvidenceImage(id="img-clear", base64_data=_make_base64_image(180))

    result = analyzer.analyze_batch([evidence])[0]

    assert result.quality_score >= 0.9
    assert not result.flags
    assert not result.officer_review_flag


def test_quality_flags_dark_low_contrast_image() -> None:
    analyzer = ImageQualityAnalyzer(MediaLoader(), quality_config)
    evidence = EvidenceImage(id="img-dark", base64_data=_make_base64_image(20))

    result = analyzer.analyze_batch([evidence])[0]

    assert "too_dark" in result.flags or "low_contrast" in result.flags
    assert result.officer_review_flag
    assert result.quality_score < 0.8
