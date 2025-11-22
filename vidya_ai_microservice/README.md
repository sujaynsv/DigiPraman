# VIDYA AI Microservice

VIDYA AI is a FastAPI-based microservice that inspects loan utilization evidence, detects fraud signals, and produces transparent risk scores for DigiPraman.

## Capabilities

- **Image Quality Layer**: Laplacian blur, brightness, and resolution analysis via OpenCV.
- **Object Detection Layer**: YOLOv8 integration (Ultralytics) with rule-based fallback.
- **OCR Layer**: Google Cloud Vision text extraction plus invoice parsing.
- **Perceptual Hashing**: `imagehash`-powered duplicate/tamper detection with persistent local state.
- **Feature Engineering**: GPS deviation, device reuse, submission timing, document cross-checks, and applicant history signals.
- **Fraud Scoring**: XGBoost booster loading with heuristic fallback and feature-importance reporting.
- **Aggregation & Routing**: Configurable weights/thresholds produce final risk tiers (auto-approve, officer-review, video-verify) plus JSON explanations.

## Project Layout

```
vidya_ai_microservice/
├── app/
│   ├── main.py                # FastAPI app + endpoints
│   ├── config.py              # Pydantic settings + weight loader
│   ├── schemas.py             # Request/response contracts
│   ├── services/              # Processing layers (quality, OCR, YOLO, hashing, etc.)
│   └── utils/                 # Media loader, geospatial math, state store
├── configs/
│   └── risk_weights.default.json
├── samples/
│   └── sample_request.json
├── requirements.txt
└── README.md
```

## Running Locally

```powershell
cd vidya_ai_microservice
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8082
```

Use `samples/sample_request.json` as a template for `POST /cases/score`.

### Running Tests

```powershell
cd vidya_ai_microservice
pytest --maxfail=1 --disable-warnings -q
```

Add `-m "not slow"` or `-k duplicate` to focus specific layers; use `pytest --cov=app tests/` for coverage snapshots.

## Configuration

All scoring knobs live in `configs/risk_weights.default.json`:

- `weights`: risk aggregation weights (image quality 15%, asset match 20%, OCR 20%, duplicate flags 10%, fraud score 25%).
- `thresholds`: auto-approve (<=65) vs officer review (66–85) vs video verification (>85).
- `quality`: Laplacian blur, brightness, contrast, and resolution thresholds plus the 0.8 officer-review quality flag.
- `detection`: YOLO confidence/IoU thresholds and optional per-asset synonym lists.
- `ocr`: vendor/amount/date penalties, ±25% amount tolerance, 30-day date tolerance, and a low-confidence penalty (0.7 default cutoff). If Google Vision credentials are absent (set `GOOGLE_CREDENTIALS_PATH=/path/to/key.json` **or** `GOOGLE_API_KEY=your-key` in `.env`), the service falls back to regex parsing and downgrades confidence automatically.
- `duplicates`: perceptual hash distance (<5) and 15-point penalty per duplicate.
- `fraud_rules`: GPS (>25 km), off-hours (outside 7am–8pm), device reuse (>2 cases in 7 days), and applicant-history penalties used when the XGBoost model is absent.

You can override the config path via the `WEIGHT_FILE` env var; the `/config/weights` endpoint lets admins hot-patch just the weight vector at runtime.
Store Google Vision credentials in `.env` (`GOOGLE_CREDENTIALS_PATH=`) when available—until then the OCR layer still runs in fallback mode and reports reduced confidence in its explanation payloads.

## Testing Checklist

1. **Low-risk case**: high quality, matching documents ⇒ expect auto-approval.
2. **Medium risk**: subtle mismatches (vendor/amount) ⇒ officer review.
3. **High risk**: duplicate hashes, GPS drift, off-hours submission, device reuse, or prior flags ⇒ video verification.
4. Validate `/config/weights` update flow, the penalty breakdown in `scores.xgboost.rule_penalties`, and other audit payloads in the API response.
