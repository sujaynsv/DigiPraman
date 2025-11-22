"""XGBoost-based fraud scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np

try:
    import xgboost as xgb  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency
    xgb = None

from ..config import FraudRuleConfig
from ..schemas import FraudFeatureVector, FraudScoreResult


class FraudScoringService:
    """Wraps a trained XGBoost model with graceful fallback."""

    def __init__(self, model_dir: Path, rules: FraudRuleConfig):
        self.model_dir = model_dir
        self.rules = rules
        self.model, self.version = self._load_latest_model()

    def _load_latest_model(self) -> Tuple[object | None, str]:
        if not xgb:
            return None, "baseline"
        if not self.model_dir.exists():
            return None, "baseline"
        candidates = sorted(self.model_dir.glob("*.json"))
        if not candidates:
            return None, "baseline"
        latest = candidates[-1]
        booster = xgb.Booster()
        booster.load_model(str(latest))
        return booster, latest.stem

    def score(self, feature_vector: FraudFeatureVector) -> FraudScoreResult:
        features = feature_vector.features
        penalties = self._rule_penalties(features)
        penalty_total = sum(penalties.values())

        if self.model and xgb:
            dmatrix = xgb.DMatrix(np.array([list(features.values())]), feature_names=list(features.keys()))
            prob = float(self.model.predict(dmatrix)[0])
            base_score = prob * 100
            importance = {feat: float(weight) for feat, weight in zip(features.keys(), self.model.get_score().values())}
            fraud_points = float(np.clip(base_score + penalty_total, 0, 100))
            return FraudScoreResult(
                fraud_score=round(fraud_points, 2),
                model_version=self.version,
                feature_importance=importance,
                rule_penalties=penalties,
            )

        fraud_score = float(np.clip(penalty_total, 0, 100))
        importance = {feature: value for feature, value in penalties.items()}
        return FraudScoreResult(
            fraud_score=fraud_score,
            model_version=self.version,
            feature_importance=importance,
            rule_penalties=penalties,
        )

    def _rule_penalties(self, features: Dict[str, float]) -> Dict[str, float]:
        penalties: Dict[str, float] = {}
        if features.get("gps_deviation_km", 0.0) > self.rules.gps_threshold_km:
            penalties["gps_deviation"] = self.rules.gps_penalty
        if features.get("off_hours_flag", 0.0) >= 1.0:
            penalties["off_hours_submission"] = self.rules.off_hours_penalty
        if features.get("device_usage_count", 0.0) > self.rules.device_cases_limit:
            penalties["device_reuse"] = self.rules.device_penalty
        history_total = features.get("historical_rejections", 0.0) + features.get("historical_flags", 0.0)
        if history_total > 0:
            penalties["history_flags"] = self.rules.history_penalty
        return penalties


__all__ = ["FraudScoringService"]
