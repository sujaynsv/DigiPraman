"""FastAPI application entrypoint for VIDYA AI."""

from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import get_version
from .config import (
    WeightConfig,
    detection_config,
    duplicate_config,
    fraud_rule_config,
    ocr_config,
    quality_config,
    threshold_config,
    weight_config,
)
from .schemas import EvidencePackage, HealthResponse, ScoreResponse, WeightUpdateRequest
from .services import VidyaAIPipeline


def create_app() -> FastAPI:
    app = FastAPI(
        title="VIDYA AI Risk Scoring Service",
        version=get_version(),
        description="Microservice for loan evidence verification, fraud detection, and routing.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    pipeline = VidyaAIPipeline(
        weights=weight_config,
        thresholds=threshold_config,
        quality_cfg=quality_config,
        detection_cfg=detection_config,
        ocr_cfg=ocr_config,
        duplicate_cfg=duplicate_config,
        fraud_rules=fraud_rule_config,
    )

    @lru_cache
    def get_pipeline() -> VidyaAIPipeline:
        return pipeline

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        dependencies = {
            "opencv": _is_module_available("cv2"),
            "ultralytics": _is_module_available("ultralytics"),
            "google_cloud_vision": _is_module_available("google.cloud.vision"),
            "xgboost": _is_module_available("xgboost"),
        }
        return HealthResponse(status="ok", version=get_version(), dependencies=dependencies)

    @app.post("/cases/score", response_model=ScoreResponse)
    async def score_case(payload: EvidencePackage, service: VidyaAIPipeline = Depends(get_pipeline)) -> ScoreResponse:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, service.score_case, payload)
        except Exception as exc:  # pragma: no cover - runtime safeguard
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/config/weights")
    async def get_weights(service: VidyaAIPipeline = Depends(get_pipeline)) -> Dict[str, float]:
        return service.current_weights().model_dump()

    @app.patch("/config/weights", response_model=Dict[str, float])
    async def update_weights(payload: WeightUpdateRequest, service: VidyaAIPipeline = Depends(get_pipeline)) -> Dict[str, float]:
        new_weights = WeightConfig(**payload.weights)
        service.update_weights(new_weights)
        return new_weights.model_dump()

    return app


def _is_module_available(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False






app = create_app()

__all__ = ["app", "create_app"]


