"""Tests for weighted risk aggregation and routing."""

from __future__ import annotations

from app.schemas import DuplicateResult, FraudScoreResult, ImageQualityResult, ObjectDetectionResult, OCRResult
from app.services.aggregation import RiskAggregator


def test_risk_aggregation_balances_components(aggregator: RiskAggregator) -> None:
    quality = [ImageQualityResult(
        image_id="img",
        quality_score=0.8,
        blur_variance=120.0,
        brightness=150.0,
        contrast=30.0,
        resolution_ok=True,
        flags=[],
        officer_review_flag=False,
    )]
    detection = [ObjectDetectionResult(
        image_id="img",
        detected_objects=[],
        asset_match=True,
        asset_match_score=1.0,
        match_score=1.0,
        details={},
    )]
    ocr = [OCRResult(
        doc_id="doc",
        raw_text="",
        ocr_confidence=0.9,
        parsed_fields={},
        crosscheck_results={},
        penalties={"amount_mismatch": 10.0},
        match_score=0.9,
    )]
    duplicates = [DuplicateResult(
        evidence_id="dup",
        duplicate_found=False,
        hash_distance=0,
        reference_case_id=None,
        penalty_points=0.0,
    )]
    fraud = FraudScoreResult(
        fraud_score=50.0,
        model_version="rules",
        feature_importance={},
        rule_penalties={},
    )

    result = aggregator.aggregate(quality, detection, ocr, duplicates, fraud)

    assert 0 <= result["final_risk_score"] <= 100
    assert result["risk_tier"] in {"auto-approve", "officer-review", "video-verify"}
*** End of File**