"""Tests for fraud scoring and rule penalties."""

from __future__ import annotations

from pathlib import Path

from app.config import fraud_rule_config
from app.schemas import FraudFeatureVector
from app.services.fraud_model import FraudScoringService


def test_fraud_rules_apply_penalties(tmp_path) -> None:
    service = FraudScoringService(model_dir=tmp_path, rules=fraud_rule_config)
    features = {
        "gps_deviation_km": fraud_rule_config.gps_threshold_km + 10,
        "off_hours_flag": 1.0,
        "device_usage_count": fraud_rule_config.device_cases_limit + 2,
        "historical_rejections": 1.0,
        "historical_flags": 0.0,
    }
    vector = FraudFeatureVector(case_id="case-penalty", features=features, explanation_fields={})

    result = service.score(vector)

    assert result.fraud_score >= 40.0
    assert "gps_deviation" in result.rule_penalties
    assert "device_reuse" in result.rule_penalties
    assert "history_flags" in result.rule_penalties
*** End of File**