"""Tests for the object detection layer (fallback logic)."""

from __future__ import annotations

import base64

import numpy as np
import cv2

from app.config import detection_config
from app.schemas import EvidenceImage
from app.services.object_detection import ObjectDetectionService
from app.utils.media_loader import MediaLoader


def _blank_image_base64() -> str:
    frame = np.zeros((64, 64, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def test_detection_matches_declared_asset_when_model_missing() -> None:
    service = ObjectDetectionService(MediaLoader(), detection_config, model_path=None)
    evidence = EvidenceImage(id="tractor-1", base64_data=_blank_image_base64(), declared_asset_type="tractor")

    result = service.analyze([evidence], declared_asset="tractor")[0]

    assert result.asset_match is True
    assert result.asset_match_score == 1.0


def test_detection_flags_mismatch_with_unknown_asset() -> None:
    service = ObjectDetectionService(MediaLoader(), detection_config, model_path=None)
    evidence = EvidenceImage(id="unknown-1", base64_data=_blank_image_base64(), declared_asset_type="bicycle")

    result = service.analyze([evidence], declared_asset="heavy_equipment")[0]

    assert result.asset_match is False
    assert result.asset_match_score == 0.0
