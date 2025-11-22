"""Utilities for loading binary media from various sources."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import requests

from ..schemas import EvidenceDocument, EvidenceImage, EvidenceVideo


class MediaLoaderError(RuntimeError):
    """Raised when media cannot be loaded."""


class MediaLoader:
    """Helper to fetch media bytes from URLs, disk, or embedded payloads."""

    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def _load_from_base64(self, encoded: str) -> bytes:
        return base64.b64decode(encoded.encode("utf-8"))

    def _load_from_file(self, file_path: str) -> bytes:
        path = Path(file_path)
        if not path.exists():
            raise MediaLoaderError(f"File not found: {file_path}")
        return path.read_bytes()

    def _load_from_url(self, url: str) -> bytes:
        response = requests.get(url, timeout=self.timeout_seconds)
        if not response.ok:
            raise MediaLoaderError(f"Failed to download media: {url}")
        return response.content

    def load_image_bytes(self, evidence: EvidenceImage) -> bytes:
        return self._resolve_payload(evidence)

    def load_document_bytes(self, evidence: EvidenceDocument) -> bytes:
        return self._resolve_payload(evidence)

    def load_video_bytes(self, evidence: EvidenceVideo) -> bytes:
        return self._resolve_payload(evidence)

    def _resolve_payload(self, evidence: EvidenceImage | EvidenceDocument | EvidenceVideo) -> bytes:
        if evidence.base64_data:
            return self._load_from_base64(evidence.base64_data)
        if evidence.file_path:
            return self._load_from_file(evidence.file_path)
        if evidence.url:
            return self._load_from_url(str(evidence.url))
        raise MediaLoaderError(f"No media payload available for {evidence.id}")


__all__ = ["MediaLoader", "MediaLoaderError"]
