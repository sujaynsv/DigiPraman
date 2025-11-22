"""Perceptual hashing and duplicate detection."""

from __future__ import annotations

from typing import List, Optional

from io import BytesIO

from PIL import Image

try:
    import imagehash  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency
    imagehash = None

from ..config import DuplicateConfig
from ..schemas import DuplicateResult, EvidenceDocument, EvidenceImage
from ..utils.media_loader import MediaLoader, MediaLoaderError
from ..utils.state import LocalStateStore


class DuplicateDetector:
    """Detects duplicate media using perceptual hashing."""

    def __init__(self, loader: MediaLoader, state_store: LocalStateStore, config: DuplicateConfig):
        self.loader = loader
        self.state = state_store
        self.config = config

    def evaluate_images(self, images: List[EvidenceImage], applicant_id: str, case_id: str) -> List[DuplicateResult]:
        return [self._evaluate_single(image, applicant_id, case_id) for image in images]

    def evaluate_documents(self, documents: List[EvidenceDocument], applicant_id: str, case_id: str) -> List[DuplicateResult]:
        return [self._evaluate_single(doc, applicant_id, case_id) for doc in documents]

    def _evaluate_single(self, evidence: EvidenceImage | EvidenceDocument, applicant_id: str, case_id: str) -> DuplicateResult:
        try:
            payload = self.loader.load_image_bytes(evidence)  # Works for doc as subclass
            hash_value = self._hash_bytes(payload)
        except MediaLoaderError as exc:
            return DuplicateResult(
                evidence_id=evidence.id,
                duplicate_found=False,
                hash_distance=0,
                reference_case_id=str(exc),
            )

        duplicates = self.state.list_hashes(applicant_id)
        duplicate_found = False
        closest_case: Optional[str] = None
        min_distance = 64
        for record in duplicates.values():
            distance = self._hash_distance(hash_value, record.get("hash", ""))
            if distance <= self.config.hash_distance_threshold and distance < min_distance:
                duplicate_found = True
                min_distance = distance
                closest_case = record.get("case_id")

        self.state.record_hash(applicant_id, evidence.id, hash_value, case_id)

        return DuplicateResult(
            evidence_id=evidence.id,
            duplicate_found=duplicate_found,
            hash_distance=min_distance if duplicate_found else 0,
            reference_case_id=closest_case,
            penalty_points=self.config.duplicate_penalty_points if duplicate_found else 0.0,
        )

    def _hash_bytes(self, payload: bytes) -> str:
        if imagehash is None:
            raise MediaLoaderError("imagehash dependency missing")
        image = Image.open(BytesIO(payload))
        return str(imagehash.phash(image))

    def _hash_distance(self, hash_a: str, hash_b: str) -> int:
        if imagehash is None:
            return 64
        if not hash_a or not hash_b:
            return 64
        return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)


__all__ = ["DuplicateDetector"]
