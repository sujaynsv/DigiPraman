# DigiPraman - VIDYA AI Microservice Setup Guide

Follow these steps to set up and run the project from scratch.

## 1. Prerequisites
- Python 3.10+
- Git

## 2. Clone & Install Dependencies
```bash
git clone <repo_url>
cd "DigiPraman/vidya_ai_microservice"

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Generate AI Models
The project requires a local XGBoost model to function. Run the training script to generate it:
```bash
# Ensure you are in the vidya_ai_microservice directory
python scripts/train_model.py
```
*This will create `models/baseline.json`.*

## 4. Configure Environment
You need a Google Cloud Vision API Key for OCR.
- **Option A (Temporary):** Set it in your terminal session.
  ```powershell
  $env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
  ```
- **Option B (Permanent):** Create a `.env` file in `vidya_ai_microservice/` (same level as `app/`):
  ```env
  GOOGLE_API_KEY=YOUR_API_KEY_HERE
  ```

## 5. Run the Service
You need two terminals running simultaneously.

**Terminal 1: Media Server** (Hosts sample images)
```bash
cd data
python -m http.server 9000
```

**Terminal 2: API Server** (The main app)
```bash
# Make sure .venv is activated
uvicorn app.main:app --reload
```

## 6. Test the API
Open a third terminal to send a test request:
```bash
curl -X POST "http://127.0.0.1:8000/cases/score" \
     -H "Content-Type: application/json" \
     -d "@samples/sample_request.json"
```
