"""Feature engineering for fraud modeling."""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Dict, List

import numpy as np
import pandas as pd

from ..config import FraudRuleConfig
from ..schemas import (
    DuplicateResult,
    EvidencePackage,
    FraudFeatureVector,
    ImageQualityResult,
    Metadata,
    ObjectDetectionResult,
    OCRResult,
)
from ..utils.geospatial import gps_deviation
from ..utils.state import LocalStateStore


class FeatureEngineer:
    """Converts raw evidence outputs into ML-ready features."""

    def __init__(self, state_store: LocalStateStore, rules: FraudRuleConfig):
        self.state = state_store
        self.rules = rules

    def build_feature_vector(
        self,
        package: EvidencePackage,
        quality: List[ImageQualityResult],
        detection: List[ObjectDetectionResult],
        ocr_results: List[OCRResult],
        duplicates: List[DuplicateResult],
    ) -> FraudFeatureVector:
        metadata = package.metadata
        features: Dict[str, float] = {}

        features.update(self._quality_features(quality))
        features.update(self._detection_features(detection, metadata))
        features.update(self._ocr_features(ocr_results))
        features.update(self._duplicate_features(duplicates))
        features.update(self._submission_features(package))
        features.update(self._history_features(metadata))

        explanation = {
            "quality_summary": features.get("avg_quality_score"),
            "detection_match": features.get("asset_match_rate"),
            "vendor_match": features.get("vendor_match_rate"),
            "duplicate_ratio": features.get("duplicate_ratio"),
            "gps_deviation_km": features.get("gps_deviation_km"),
        }

        return FraudFeatureVector(case_id=package.case_id, features=features, explanation_fields=explanation)

    def _quality_features(self, results: List[ImageQualityResult]) -> Dict[str, float]:
        if not results:
            return {"avg_quality_score": 0.5}
        df = pd.DataFrame([r.model_dump() for r in results])
        return {
            "avg_quality_score": float(df["quality_score"].mean()),
            "low_quality_ratio": float((df["quality_score"] < 0.5).mean()),
        }

    def _detection_features(self, results: List[ObjectDetectionResult], metadata: Metadata) -> Dict[str, float]:
        if not results:
            return {"asset_match_rate": 0.5}
        match_scores = [r.match_score for r in results]
        match_rate = float(np.mean(match_scores))
        return {
            "asset_match_rate": match_rate,
            "asset_declared": 1.0 if metadata.declared_asset_type else 0.0,
        }

    def _ocr_features(self, results: List[OCRResult]) -> Dict[str, float]:
        if not results:
            return {"avg_ocr_confidence": 0.0, "vendor_match_rate": 0.0, "amount_match_rate": 0.0}
        vendor_matches = [r.crosscheck_results.get("vendor_match", False) for r in results]
        amount_matches = [r.crosscheck_results.get("amount_match", False) for r in results]
        confidences = [r.ocr_confidence for r in results]
        return {
            "avg_ocr_confidence": float(mean(confidences)),
            "vendor_match_rate": float(np.mean(vendor_matches)),
            "amount_match_rate": float(np.mean(amount_matches)),
        }

    def _duplicate_features(self, results: List[DuplicateResult]) -> Dict[str, float]:
        if not results:
            return {"duplicate_ratio": 0.0}
        duplicates = [r.duplicate_found for r in results]
        return {"duplicate_ratio": float(np.mean(duplicates))}

    def _submission_features(self, package: EvidencePackage) -> Dict[str, float]:
        metadata = package.metadata
        gps_delta = gps_deviation(metadata.declared_asset_location, metadata.submission_location)
        device_use = float(
            self.state.record_device_usage(metadata.submission_device_id, metadata.submission_timestamp)
        )
        submission_hours = [t.hour for t in (package.timestamps or [])]
        if not submission_hours:
            submission_hours = [metadata.submission_timestamp.hour]
        hour_std = float(np.std(submission_hours)) if len(submission_hours) > 1 else 0.0
        gps_value = gps_delta if gps_delta is not None else 0.0
        gps_threshold_breach = 1.0 if gps_value > self.rules.gps_threshold_km else 0.0
        hour = metadata.submission_timestamp.hour
        off_hours_flag = (
            1.0
            if hour < self.rules.off_hours_start or hour > self.rules.off_hours_end
            else 0.0
        )
        return {
            "gps_deviation_km": gps_value,
            "gps_over_threshold": gps_threshold_breach,
            "device_usage_count": device_use,
            "submission_hour_std": hour_std,
            "off_hours_flag": off_hours_flag,
            "submission_hour": float(hour),
        }

    def _history_features(self, metadata: Metadata) -> Dict[str, float]:
        history = metadata.applicant_history
        timestamps = self.state.record_case_timestamp(metadata.applicant_id, metadata.submission_timestamp.isoformat())
        rapid_submissions = self._rapid_submission_ratio(timestamps)
        return {
            "historical_rejections": float(history.previous_rejections),
            "historical_flags": float(history.fraudulent_flags),
            "total_cases": float(history.submitted_cases),
            "rapid_submission_ratio": rapid_submissions,
        }

    def _rapid_submission_ratio(self, timestamps: List[str]) -> float:
        if len(timestamps) < 2:
            return 0.0
        parsed_all = []
        for ts in timestamps:
             try:
                 dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                 # FORCE NAIVE
                 parsed_all.append(dt.replace(tzinfo=None))
             except Exception:
                 continue
        
        parsed = sorted(parsed_all)
        if len(parsed) < 2: return 0.0

        intervals = [
            (parsed[idx] - parsed[idx - 1]).total_seconds() / 3600 for idx in range(1, len(parsed))
        ]
        if not intervals:
            return 0.0
        rapid = [1 for interval in intervals if interval < 2]
        return float(len(rapid) / len(intervals))


__all__ = ["FeatureEngineer"]
