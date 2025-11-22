"""Image quality checks using OpenCV."""

from __future__ import annotations

from statistics import mean
from typing import List

import numpy as np

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - OpenCV may be unavailable in CI
    cv2 = None

from ..config import QualityConfig
from ..schemas import EvidenceImage, ImageQualityResult
from ..utils.media_loader import MediaLoader, MediaLoaderError


class ImageQualityAnalyzer:
    """Evaluates blur, lighting, and resolution for evidence images."""

    def __init__(self, loader: MediaLoader, config: QualityConfig) -> None:
        self.loader = loader
        self.config = config

    def analyze_batch(self, images: List[EvidenceImage]) -> List[ImageQualityResult]:
        results: List[ImageQualityResult] = []
        for image in images:
            try:
                payload = self.loader.load_image_bytes(image)
                results.append(self._analyze_single(image, payload))
            except MediaLoaderError as exc:
                results.append(
                    ImageQualityResult(
                        image_id=image.id,
                        quality_score=0.0,
                        blur_variance=0.0,
                        brightness=0.0,
                        contrast=0.0,
                        resolution_ok=False,
                        reason_if_fail=str(exc),
                    )
                )
        return results

    def _analyze_single(self, evidence: EvidenceImage, payload: bytes) -> ImageQualityResult:
        if not cv2:
            # Basic fallback when OpenCV is missing
            return ImageQualityResult(
                image_id=evidence.id,
                quality_score=0.5,
                blur_variance=0.0,
                brightness=0.0,
                contrast=0.0,
                resolution_ok=True,
                flags=["opencv_missing"],
                officer_review_flag=True,
                reason_if_fail="OpenCV not installed; defaulting to neutral score",
            )

        array = np.frombuffer(payload, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise MediaLoaderError(f"Failed to decode image {evidence.id}")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(np.mean(gray))
        contrast_value = float(np.std(gray))
        height, width = gray.shape
        resolution_ok = width >= self.config.min_width and height >= self.config.min_height

        flags: List[str] = []

        blur_score = 1.0
        if blur_variance < self.config.blur_variance_threshold:
            blur_score = max(0.0, blur_variance / self.config.blur_variance_threshold)
            flags.append("blurry")

        brightness_score = self._normalize_brightness(brightness, flags)

        contrast_score = 1.0
        if contrast_value < self.config.contrast_threshold:
            contrast_score = max(0.0, contrast_value / self.config.contrast_threshold)
            flags.append("low_contrast")

        resolution_score = 1.0 if resolution_ok else 0.0
        if not resolution_ok:
            flags.append("low_resolution")

        quality_score = mean([blur_score, brightness_score, contrast_score, resolution_score])
        officer_flag = quality_score < self.config.officer_review_quality_threshold
        reason = ", ".join(flags) if flags else None

        return ImageQualityResult(
            image_id=evidence.id,
            quality_score=round(quality_score, 3),
            blur_variance=round(blur_variance, 2),
            brightness=round(brightness, 2),
            contrast=round(contrast_value, 2),
            resolution_ok=resolution_ok,
            flags=flags,
            officer_review_flag=officer_flag,
            reason_if_fail=reason,
        )

    def _normalize_brightness(self, brightness: float, flags: List[str]) -> float:
        low = self.config.brightness_dark_threshold
        high = self.config.brightness_bright_threshold
        if brightness <= low:
            flags.append("too_dark")
            return max(0.0, brightness / max(low, 1.0))
        if brightness >= high:
            flags.append("too_bright")
            return max(0.0, 1 - ((brightness - high) / max(255 - high, 1)))
        return 1.0


__all__ = ["ImageQualityAnalyzer"]
