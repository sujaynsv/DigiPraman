"""Risk aggregation and routing logic."""

from __future__ import annotations

from statistics import mean
from typing import Dict, List

from ..config import ThresholdConfig, WeightConfig
from ..schemas import (
    DuplicateResult,
    FraudScoreResult,
    ImageQualityResult,
    ObjectDetectionResult,
    OCRResult,
)


class RiskAggregator:
    """Combines layer scores into a final risk score and routing decision."""

    def __init__(self, weights: WeightConfig, thresholds: ThresholdConfig):
        self.weights = weights
        self.thresholds = thresholds

    def update_weights(self, weights: WeightConfig) -> None:
        self.weights = weights

    def aggregate(
        self,
        quality: List[ImageQualityResult],
        detection: List[ObjectDetectionResult],
        ocr_results: List[OCRResult],
        duplicates: List[DuplicateResult],
        fraud_score: FraudScoreResult,
    ) -> Dict[str, float | str]:
        components = self._components(quality, detection, ocr_results, duplicates, fraud_score)
        total_weight = self.weights.total()
        weighted_sum = (
            self.weights.image_quality_weight * components["image_quality"]
            + self.weights.asset_match_weight * components["asset_match"]
            + self.weights.ocr_match_weight * components["ocr"]
            + self.weights.duplicate_weight * components["duplicates"]
            + self.weights.fraud_score_weight * components["fraud"]
        )
        final_score = round(weighted_sum / total_weight, 2)
        risk_tier = self._risk_tier(final_score)

        return {
            "final_risk_score": final_score,
            "risk_tier": risk_tier,
            "routing_decision": self._routing_decision(risk_tier),
            "components": components,
        }

    def _components(
        self,
        quality: List[ImageQualityResult],
        detection: List[ObjectDetectionResult],
        ocr_results: List[OCRResult],
        duplicates: List[DuplicateResult],
        fraud_score: FraudScoreResult,
    ) -> Dict[str, float]:
        avg_quality = mean([item.quality_score for item in quality]) if quality else 1.0
        quality_risk = round((1 - avg_quality) * 100, 2)

        detection_scores = [item.asset_match_score for item in detection]
        avg_detection = mean(detection_scores) if detection_scores else 1.0
        detection_risk = round((1 - avg_detection) * 100, 2)

        ocr_penalties = [sum(result.penalties.values()) for result in ocr_results]
        ocr_risk = round(mean(ocr_penalties), 2) if ocr_penalties else 0.0

        duplicate_penalty = sum(result.penalty_points for result in duplicates)
        duplicate_risk = round(min(duplicate_penalty, 100), 2)

        fraud_risk = round(fraud_score.fraud_score, 2)

        return {
            "image_quality": quality_risk,
            "asset_match": detection_risk,
            "ocr": ocr_risk,
            "duplicates": duplicate_risk,
            "fraud": fraud_risk,
        }

    def _risk_tier(self, final_score: float) -> str:
        if final_score <= self.thresholds.auto_approve_threshold:
            return "auto-approve"
        if final_score <= self.thresholds.officer_review_threshold:
            return "officer-review"
        return "video-verify"

    def _routing_decision(self, risk_tier: str) -> str:
        mapping = {
            "auto-approve": "auto_approve",
            "officer-review": "officer_review",
            "video-verify": "video_verification_required",
        }
        return mapping[risk_tier]


__all__ = ["RiskAggregator"]
