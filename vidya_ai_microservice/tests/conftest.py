"""Shared pytest fixtures for VIDYA AI tests."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import pytest

from app.config import threshold_config, weight_config
from app.schemas import (
    DuplicateResult,
    FraudScoreResult,
    ImageQualityResult,
    ObjectDetectionResult,
    OCRResult,
)
from app.services.aggregation import RiskAggregator


@pytest.fixture(scope="session")
def aggregator() -> RiskAggregator:
    """Provide a single risk aggregator with default weights/thresholds."""

    return RiskAggregator(weight_config, threshold_config)


def _quality(result_id: str, score: float) -> ImageQualityResult:
    return ImageQualityResult(
        image_id=result_id,
        quality_score=score,
        blur_variance=150.0,
        brightness=180.0,
        contrast=45.0,
        resolution_ok=True,
        flags=[],
        officer_review_flag=score < 0.8,
    )


def _detection(result_id: str, score: float) -> ObjectDetectionResult:
    return ObjectDetectionResult(
        image_id=result_id,
        detected_objects=[],
        asset_match=score >= 1.0,
        asset_match_score=score,
        match_score=score,
        details={"mode": "test"},
    )


def _ocr(result_id: str, penalty_total: float) -> OCRResult:
    penalties: Dict[str, float] = {"test_penalty": penalty_total} if penalty_total else {}
    return OCRResult(
        doc_id=result_id,
        raw_text="",
        ocr_confidence=0.95,
        parsed_fields={},
        crosscheck_results={},
        penalties=penalties,
        match_score=1.0 if penalty_total == 0 else max(0.0, 1 - penalty_total / 100),
    )


def _duplicate(result_id: str, penalty: float) -> DuplicateResult:
    return DuplicateResult(
        evidence_id=result_id,
        duplicate_found=penalty > 0,
        hash_distance=0,
        reference_case_id=None,
        penalty_points=penalty,
    )


def _fraud(score: float, penalties: Dict[str, float] | None = None) -> FraudScoreResult:
    return FraudScoreResult(
        fraud_score=score,
        model_version="rules",
        feature_importance={},
        rule_penalties=penalties or {},
    )


@pytest.fixture
def low_risk_case() -> Dict[str, List]:
    return {
        "quality": [_quality("img-low", 0.95)],
        "detection": [_detection("img-low", 1.0)],
        "ocr": [_ocr("doc-low", 0.0)],
        "duplicates": [],
        "fraud_score": _fraud(20.0),
    }


@pytest.fixture
def medium_risk_case() -> Dict[str, List]:
    return {
        "quality": [_quality("img-med", 0.6)],
        "detection": [_detection("img-med", 0.3)],
        "ocr": [_ocr("doc-med", 40.0)],
        "duplicates": [_duplicate("dup-med", 60.0)],
        "fraud_score": _fraud(100.0, {"device_reuse": 10.0}),
    }


@pytest.fixture
def high_risk_case() -> Dict[str, List]:
    return {
        "quality": [_quality("img-high", 0.4)],
        "detection": [_detection("img-high", 0.0)],
        "ocr": [_ocr("doc-high", 80.0)],
        "duplicates": [_duplicate("dup-high", 100.0)],
        "fraud_score": _fraud(100.0, {"gps_deviation": 15.0, "history_flags": 10.0}),
    }
*** End of File**