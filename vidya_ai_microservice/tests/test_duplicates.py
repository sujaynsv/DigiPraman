"""Tests for perceptual hashing and duplicate detection."""

from __future__ import annotations

import base64
from io import BytesIO

from PIL import Image

from app.config import duplicate_config
from app.schemas import EvidenceImage
from app.services.hashing import DuplicateDetector
from app.utils.media_loader import MediaLoader
from app.utils.state import LocalStateStore


def _make_base64_image(color: int) -> str:
    image = Image.new("RGB", (64, 64), color=(color, color, color))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def test_duplicate_detection_flags_reused_image(tmp_path) -> None:
    state = LocalStateStore(tmp_path / "duplicates.json")
    detector = DuplicateDetector(MediaLoader(), state, duplicate_config)

    img_a = EvidenceImage(id="img-a", base64_data=_make_base64_image(120))
    img_b = EvidenceImage(id="img-b", base64_data=_make_base64_image(120))

    first_result = detector.evaluate_images([img_a], applicant_id="app-1", case_id="case-1")[0]
    assert first_result.duplicate_found is False

    second_result = detector.evaluate_images([img_b], applicant_id="app-1", case_id="case-2")[0]
    assert second_result.duplicate_found is True
    assert second_result.penalty_points == duplicate_config.duplicate_penalty_points
*** End of File**