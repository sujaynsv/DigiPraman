"""Object detection service using YOLOv8 or fallbacks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

try:
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover - ultralytics may be missing
    YOLO = None

from ..config import DetectionConfig
from ..schemas import EvidenceImage, ObjectDetectionResult
from ..utils.media_loader import MediaLoader, MediaLoaderError


class ObjectDetectionService:
    """Wraps YOLO inference for asset validation."""

    def __init__(self, loader: MediaLoader, config: DetectionConfig, model_path: Optional[Path] = None) -> None:
        self.loader = loader
        self.config = config
        self.model = self._load_model(model_path) if model_path else None

    def _load_model(self, model_path: Path | str | None):
        if YOLO and model_path and Path(model_path).exists():
            try:
                return YOLO(str(model_path))
            except Exception:
                return None
        return None

    def analyze(self, images: List[EvidenceImage], declared_asset: Optional[str]) -> List[ObjectDetectionResult]:
        results: List[ObjectDetectionResult] = []
        for image in images:
            try:
                payload = self.loader.load_image_bytes(image)
                results.append(self._run_detection(image, payload, declared_asset))
            except MediaLoaderError as exc:
                results.append(
                    ObjectDetectionResult(
                        image_id=image.id,
                        detected_objects=[],
                        asset_match=False,
                        asset_match_score=0.0,
                        match_score=0.0,
                        details={"error": str(exc)},
                    )
                )
        return results

    def _run_detection(
        self,
        image: EvidenceImage,
        payload: bytes,
        declared_asset: Optional[str],
    ) -> ObjectDetectionResult:
        keywords = self._keywords(declared_asset, image.declared_asset_type)
        if not self.model:
            haystack = (image.declared_asset_type or "").lower()
            match_score = 1.0 if keywords and any(keyword in haystack for keyword in keywords) else 0.0
            return self._result_from_scores(image.id, [], match_score, declared_asset, "fallback")

        detections = self.model.predict(
            source=payload,
            verbose=False,
            conf=self.config.confidence_threshold,
            iou=self.config.iou_threshold,
        )
        detected_objects: List[Dict[str, float | str]] = []
        best_match = 0.0
        matched_label: Optional[str] = None
        for result in detections:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_name = self.model.names.get(int(box.cls[0]), "object")
                conf = float(box.conf[0])
                detected_objects.append(
                    {
                        "label": cls_name,
                        "confidence": round(conf, 3),
                        "bbox": box.xyxy[0].tolist(),
                    }
                )
                if keywords and any(keyword in cls_name.lower() for keyword in keywords):
                    if conf > best_match:
                        best_match = conf
                        matched_label = cls_name

        return self._result_from_scores(
            image.id,
            detected_objects,
            best_match,
            declared_asset,
            "yolov8",
            matched_label,
        )

    def _result_from_scores(
        self,
        image_id: str,
        detected_objects: List[Dict[str, float | str]],
        match_score: float,
        declared_asset: Optional[str],
        mode: str,
        matched_label: Optional[str] = None,
    ) -> ObjectDetectionResult:
        normalized_score = 1.0 if match_score >= self.config.confidence_threshold else 0.0
        details = {"mode": mode, "declared_asset": declared_asset}
        if matched_label:
            details["matched_label"] = matched_label
        return ObjectDetectionResult(
            image_id=image_id,
            detected_objects=detected_objects,
            asset_match=bool(normalized_score),
            asset_match_score=normalized_score,
            match_score=normalized_score,
            details=details,
        )

    def _keywords(self, declared_asset: Optional[str], fallback_asset: Optional[str]) -> List[str]:
        if not declared_asset and not fallback_asset:
            return []
        asset_key = (declared_asset or fallback_asset or "").lower()
        synonyms = self.config.asset_synonyms.get(asset_key, [])
        return list({asset_key, *[syn.lower() for syn in synonyms]})


__all__ = ["ObjectDetectionService"]
