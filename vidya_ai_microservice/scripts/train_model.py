import xgboost as xgb
import pandas as pd
import numpy as np
from pathlib import Path
import json

def train_baseline_model():
    # Exact features from FeatureEngineer in feature_engineering.py
    features = [
        "avg_quality_score",
        "low_quality_ratio",
        "asset_match_rate",
        "asset_declared",
        "avg_ocr_confidence",
        "vendor_match_rate",
        "amount_match_rate",
        "duplicate_ratio",
        "gps_deviation_km",
        "gps_over_threshold",
        "device_usage_count",
        "submission_hour_std",
        "off_hours_flag",
        "submission_hour",
        "historical_rejections",
        "historical_flags",
        "total_cases",
        "rapid_submission_ratio"
    ]
    
    # Generate synthetic data (100 samples)
    np.random.seed(42)
    X = pd.DataFrame(np.random.rand(100, len(features)), columns=features)
    
    # Logic: High GPS deviation OR high device usage -> Fraud (1)
    y = ((X["gps_deviation_km"] > 0.7) | (X["device_usage_count"] > 0.8)).astype(int)
    
    # Train XGBoost model
    model = xgb.XGBClassifier(objective="binary:logistic", eval_metric="logloss")
    model.fit(X, y)
    
    # Save model
    output_dir = Path(__file__).resolve().parents[1] / "models"
    output_dir.mkdir(exist_ok=True)
    
    model_path = output_dir / "baseline.json"
    model.save_model(model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_baseline_model()
