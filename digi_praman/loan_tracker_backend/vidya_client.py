# loan_backend/services/vidya_client.py
import httpx
from typing import Any, Dict

VIDYA_BASE_URL = "http://localhost:8001"  # URL where VIDYA service runs

class VidyaAIError(RuntimeError):
    pass

async def score_case(evidence_package: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{VIDYA_BASE_URL}/cases/score"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=evidence_package)
        if resp.status_code != 200:
            raise VidyaAIError(f"VIDYA AI error {resp.status_code}: {resp.text}")
        return resp.json()
