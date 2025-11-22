"""Tests for OCR penalty and cross-check logic."""

from __future__ import annotations

from datetime import datetime

import pytest

from app.config import ocr_config
from app.services.ocr_processing import DocumentOCRService
from app.utils.media_loader import MediaLoader


@pytest.fixture
def ocr_service() -> DocumentOCRService:
    # No Google credentials during tests, forcing regex fallback
    return DocumentOCRService(MediaLoader(), ocr_config, credentials_path=None)


def test_ocr_crosscheck_detects_vendor_and_amount_mismatch(ocr_service: DocumentOCRService) -> None:
    parsed = {"vendor": "Agri Corp", "amount": 300000.0, "date": "05/01/2025"}
    penalties, crosscheck = ocr_service._crosscheck(
        parsed,
        declared_vendor="Different Vendor",
        declared_amount=200000.0,
        declared_date=datetime(2025, 1, 5),
        confidence=0.6,
    )

    assert "vendor_mismatch" in penalties
    assert "amount_mismatch" in penalties
    assert "low_confidence" in penalties
    assert crosscheck["vendor_match"] is False
    assert crosscheck["amount_match"] is False


def test_ocr_crosscheck_accepts_close_amount_and_date(ocr_service: DocumentOCRService) -> None:
    parsed = {"vendor": "Trusted Vendor", "amount": 101000.0, "date": "10/01/2025"}
    penalties, crosscheck = ocr_service._crosscheck(
        parsed,
        declared_vendor="Trusted Vendor",
        declared_amount=100000.0,
        declared_date=datetime(2025, 1, 25),
        confidence=0.95,
    )

    assert penalties == {}
    assert crosscheck["vendor_match"] is True
    assert crosscheck["amount_match"] is True
    assert crosscheck["date_match"] is True
