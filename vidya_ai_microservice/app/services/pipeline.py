"""VIDYA AI end-to-end orchestration pipeline."""

from __future__ import annotations

from typing import Dict

from ..config import (
    DetectionConfig,
    DuplicateConfig,
    FraudRuleConfig,
    OCRConfig,
    QualityConfig,
    ThresholdConfig,
    WeightConfig,
    settings,
)
from ..schemas import EvidencePackage, ScoreBreakdown, ScoreResponse
from ..utils.media_loader import MediaLoader
from ..utils.state import LocalStateStore
from .aggregation import RiskAggregator
from .feature_engineering import FeatureEngineer
from .fraud_model import FraudScoringService
from .hashing import DuplicateDetector
from .object_detection import ObjectDetectionService
from .ocr_processing import DocumentOCRService
from .quality import ImageQualityAnalyzer


class VidyaAIPipeline:
    """Coordinates all processing layers and builds audit trail."""

    def __init__(
        self,
        weights: WeightConfig,
        thresholds: ThresholdConfig,
        quality_cfg: QualityConfig,
        detection_cfg: DetectionConfig,
        ocr_cfg: OCRConfig,
        duplicate_cfg: DuplicateConfig,
        fraud_rules: FraudRuleConfig,
    ):
        self.loader = MediaLoader()
        self.duplicate_state = LocalStateStore(settings.duplicate_state_path)
        self.device_state = self.duplicate_state  # reuse same store for simplicity

        self.quality = ImageQualityAnalyzer(loader=self.loader, config=quality_cfg)
        self.detector = ObjectDetectionService(
            loader=self.loader,
            config=detection_cfg,
            model_path=settings.yolo_model_path,
        )
        self.ocr = DocumentOCRService(
            loader=self.loader,
            config=ocr_cfg,
            credentials_path=settings.google_credentials_path,
        )
        self.duplicates = DuplicateDetector(
            loader=self.loader,
            state_store=self.duplicate_state,
            config=duplicate_cfg,
        )
        self.features = FeatureEngineer(state_store=self.device_state, rules=fraud_rules)
        self.fraud = FraudScoringService(model_dir=settings.model_registry_path, rules=fraud_rules)
        self.aggregator = RiskAggregator(weights, thresholds)

    def update_weights(self, new_weights: WeightConfig) -> None:
        self.aggregator.update_weights(new_weights)

    def current_weights(self) -> WeightConfig:
        return self.aggregator.weights

    def score_case(self, payload: EvidencePackage) -> ScoreResponse:
        quality_asset = self.quality.analyze_batch(payload.asset_images)
        quality_docs = self.quality.analyze_batch(payload.doc_images)
        quality_results = quality_asset + quality_docs

        detection_results = self.detector.analyze(payload.asset_images, payload.metadata.declared_asset_type)
        ocr_results = self.ocr.process_documents(
            payload.doc_images,
            payload.metadata.declared_vendor,
            payload.metadata.declared_invoice_amount,
            payload.metadata.declared_invoice_date,
        )
        duplicate_asset = self.duplicates.evaluate_images(payload.asset_images, payload.metadata.applicant_id, payload.case_id)
        duplicate_docs = self.duplicates.evaluate_documents(payload.doc_images, payload.metadata.applicant_id, payload.case_id)
        duplicate_results = duplicate_asset + duplicate_docs

        feature_vector = self.features.build_feature_vector(
            package=payload,
            quality=quality_results,
            detection=detection_results,
            ocr_results=ocr_results,
            duplicates=duplicate_results,
        )
        fraud_score = self.fraud.score(feature_vector)

        aggregate = self.aggregator.aggregate(
            quality=quality_results,
            detection=detection_results,
            ocr_results=ocr_results,
            duplicates=duplicate_results,
            fraud_score=fraud_score,
        )

        breakdown = ScoreBreakdown(
            image_quality=quality_results,
            asset_match=detection_results,
            ocr=ocr_results,
            duplicates=duplicate_results,
            fraud_features=feature_vector,
            xgboost=fraud_score,
        )

        explanation: Dict[str, object] = {
            "image_quality": [result.model_dump() for result in quality_results],
            "object_detection": [result.model_dump() for result in detection_results],
            "ocr": [result.model_dump() for result in ocr_results],
            "duplicates": [result.model_dump() for result in duplicate_results],
            "fraud_features": feature_vector.model_dump(),
            "fraud_score": fraud_score.model_dump(),
            "aggregation_components": aggregate["components"],
        }

        return ScoreResponse(
            case_id=payload.case_id,
            scores=breakdown,
            final_risk_score=aggregate["final_risk_score"],
            risk_tier=aggregate["risk_tier"],
            routing_decision=aggregate["routing_decision"],
            full_explanation=explanation,
        )


__all__ = ["VidyaAIPipeline"]
