"""End-to-end routing expectations from aggregator inputs."""

from __future__ import annotations

from app.services.aggregation import RiskAggregator


def test_low_risk_auto_approve(aggregator: RiskAggregator, low_risk_case):
    result = aggregator.aggregate(**low_risk_case)
    assert result["risk_tier"] == "auto-approve"
    assert result["final_risk_score"] < 30


def test_medium_risk_officer_review(aggregator: RiskAggregator, medium_risk_case):
    result = aggregator.aggregate(**medium_risk_case)
    assert result["risk_tier"] == "officer-review"
    assert 30 <= result["final_risk_score"] < 70


def test_high_risk_video_verify(aggregator: RiskAggregator, high_risk_case):
    result = aggregator.aggregate(**high_risk_case)
    assert result["risk_tier"] == "video-verify"
    assert result["final_risk_score"] >= 70
*** End of File**