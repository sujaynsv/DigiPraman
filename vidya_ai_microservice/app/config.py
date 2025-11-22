"""Configuration helpers for the VIDYA AI service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings


class WeightConfig(BaseModel):
    """Weights applied to each layer for final risk aggregation."""

    image_quality_weight: float = Field(0.15, ge=0.0)
    asset_match_weight: float = Field(0.20, ge=0.0)
    ocr_match_weight: float = Field(0.20, ge=0.0)
    duplicate_weight: float = Field(0.10, ge=0.0)
    fraud_score_weight: float = Field(0.25, ge=0.0)

    def total(self) -> float:
        return sum(self.model_dump().values()) or 1.0


class ThresholdConfig(BaseModel):
    """Routing thresholds for risk tiers."""

    auto_approve_threshold: int = Field(65, ge=0, le=100)
    officer_review_threshold: int = Field(85, ge=0, le=100)


class QualityConfig(BaseModel):
    blur_variance_threshold: float = 100.0
    brightness_dark_threshold: float = 60.0
    brightness_bright_threshold: float = 220.0
    contrast_threshold: float = 20.0
    min_width: int = 600
    min_height: int = 400
    officer_review_quality_threshold: float = Field(0.8, ge=0.0, le=1.0)


class DetectionConfig(BaseModel):
    confidence_threshold: float = Field(0.45, ge=0.0, le=1.0)
    iou_threshold: float = Field(0.4, ge=0.0, le=1.0)
    asset_synonyms: Dict[str, List[str]] = Field(default_factory=dict)


class OCRConfig(BaseModel):
    provider_confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    amount_tolerance_pct: float = Field(0.25, ge=0.0, le=1.0)
    date_tolerance_days: int = 30
    vendor_penalty: float = 10.0
    amount_penalty: float = 15.0
    date_penalty: float = 10.0
    low_confidence_penalty: float = 5.0


class DuplicateConfig(BaseModel):
    hash_distance_threshold: int = 5
    duplicate_penalty_points: float = 15.0


class FraudRuleConfig(BaseModel):
    gps_threshold_km: float = 25.0
    gps_penalty: float = 15.0
    off_hours_start: int = 7
    off_hours_end: int = 20
    off_hours_penalty: float = 5.0
    device_cases_limit: int = 2
    device_penalty: float = 10.0
    history_penalty: float = 10.0


class Settings(BaseSettings):
    """Application settings loaded from env or defaults."""
    
    model_config = ConfigDict(protected_namespaces=())

    app_name: str = "VIDYA AI Microservice"
    environment: str = Field("development", description="Environment label for logging")
    weight_file: Path = Field(
        default=Path(__file__).resolve().parents[1] / "configs" / "risk_weights.default.json",
        description="Path to JSON file carrying weight overrides.",
    )
    duplicate_state_path: Path = Field(
        default=Path(__file__).resolve().parents[1] / "data" / "duplicates_state.json",
        description="Path for persisting perceptual hash comparisons.",
    )
    device_state_path: Path = Field(
        default=Path(__file__).resolve().parents[1] / "data" / "device_state.json",
        description="Path for persisting device usage counters.",
    )
    google_credentials_path: Optional[Path] = Field(default=None, description="Service account key for Vision API")
    google_api_key: Optional[str] = Field(default=None, description="Direct API key for Google Vision REST usage")
    google_project_id: Optional[str] = Field(default=None)
    yolo_model_path: Optional[Path] = Field(default=None)
    model_registry_path: Path = Field(
        default=Path(__file__).resolve().parents[1] / "models",
        description="Folder containing serialized ML models.",
    )
    enable_mlflow_logging: bool = Field(False, description="Toggle MLflow logging for experiments")

    def load_runtime_config(self) -> Dict[str, Any]:
        if self.weight_file and self.weight_file.exists():
            return self._load_json(self.weight_file)
        return {}

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        import json

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


settings = Settings()
_raw_config = settings.load_runtime_config()

ConfigType = TypeVar("ConfigType", bound=BaseModel)


def _build_config(model: Type[ConfigType], key: str) -> ConfigType:
    return model(**_raw_config.get(key, {}))


weight_config: WeightConfig = _build_config(WeightConfig, "weights")
threshold_config: ThresholdConfig = _build_config(ThresholdConfig, "thresholds")
quality_config: QualityConfig = _build_config(QualityConfig, "quality")
detection_config: DetectionConfig = _build_config(DetectionConfig, "detection")
ocr_config: OCRConfig = _build_config(OCRConfig, "ocr")
duplicate_config: DuplicateConfig = _build_config(DuplicateConfig, "duplicates")
fraud_rule_config: FraudRuleConfig = _build_config(FraudRuleConfig, "fraud_rules")

__all__ = [
    "settings",
    "weight_config",
    "threshold_config",
    "quality_config",
    "detection_config",
    "ocr_config",
    "duplicate_config",
    "fraud_rule_config",
    "WeightConfig",
    "ThresholdConfig",
    "QualityConfig",
    "DetectionConfig",
    "OCRConfig",
    "DuplicateConfig",
    "FraudRuleConfig",
]