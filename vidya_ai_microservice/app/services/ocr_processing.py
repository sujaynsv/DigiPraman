"""OCR and document parsing via Google Cloud Vision."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from google.cloud import vision  # type: ignore
except Exception:  # pragma: no cover - API optional
    vision = None

from ..config import OCRConfig
from ..schemas import EvidenceDocument, OCRResult
from ..utils.media_loader import MediaLoader, MediaLoaderError


class DocumentOCRService:
    """Handles OCR extraction and business-field parsing."""

    def __init__(self, loader: MediaLoader, config: OCRConfig, credentials_path: Optional[str] = None):
        self.loader = loader
        self.config = config
        self.client = self._init_client(credentials_path) if vision else None

    def _init_client(self, credentials_path: Optional[str]):  # pragma: no cover - network
        if not vision:
            return None
        try:
            if credentials_path:
                return vision.ImageAnnotatorClient.from_service_account_file(credentials_path)
            return vision.ImageAnnotatorClient()
        except Exception:
            # Credentials missing; fall back to regex-only parsing
            return None

    def process_documents(
        self,
        documents: List[EvidenceDocument],
        declared_vendor: Optional[str],
        declared_amount: Optional[float],
        declared_date: Optional[datetime],
    ) -> List[OCRResult]:
        results: List[OCRResult] = []
        for doc in documents:
            try:
                payload = self.loader.load_document_bytes(doc)
                results.append(self._process_single(doc, payload, declared_vendor, declared_amount, declared_date))
            except MediaLoaderError as exc:
                results.append(
                    OCRResult(
                        doc_id=doc.id,
                        raw_text="",
                        ocr_confidence=0.0,
                        parsed_fields={},
                        crosscheck_results={"error": str(exc)},
                        penalties={"load_failure": self.config.amount_penalty},
                        match_score=0.0,
                    )
                )
        return results

    def _process_single(
        self,
        document: EvidenceDocument,
        payload: bytes,
        declared_vendor: Optional[str],
        declared_amount: Optional[float],
        declared_date: Optional[datetime],
    ) -> OCRResult:
        if not self.client:
            # Lightweight regex fallback if GCV unavailable
            text = ""
            confidence = 0.5
        else:  # pragma: no cover - network
            image = vision.Image(content=payload)
            response = self.client.document_text_detection(image=image)
            if response.error.message:
                raise RuntimeError(response.error.message)
            text = response.full_text_annotation.text
            # Use average symbol confidence when available
            confidences = [s.confidence for p in response.full_text_annotation.pages for b in p.blocks for paragraph in b.paragraphs for word in paragraph.words for s in word.symbols]
            confidence = float(sum(confidences) / len(confidences)) if confidences else 0.8

        parsed_fields = self._parse_fields(text)
        penalties, crosscheck = self._crosscheck(parsed_fields, declared_vendor, declared_amount, declared_date, confidence)
        max_penalty = (
            self.config.vendor_penalty
            + self.config.amount_penalty
            + self.config.date_penalty
            + self.config.low_confidence_penalty
        )
        match_score = max(0.0, 1 - (sum(penalties.values()) / max_penalty)) if max_penalty else 1.0

        return OCRResult(
            doc_id=document.id,
            raw_text=text,
            ocr_confidence=round(confidence, 3),
            parsed_fields=parsed_fields,
            crosscheck_results=crosscheck,
            penalties=penalties,
            match_score=round(match_score, 3),
        )

    def _parse_fields(self, text: str) -> Dict[str, Optional[str | float]]:
        vendor = self._extract_vendor(text)
        amount = self._extract_amount(text)
        date = self._extract_date(text)
        return {
            "vendor": vendor,
            "amount": amount,
            "date": date,
        }

    def _extract_vendor(self, text: str) -> Optional[str]:
        match = re.search(r"Vendor\s*:?\s*(.+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_amount(self, text: str) -> Optional[float]:
        match = re.search(r"(INR|Rs\.?|₹)\s*([0-9,]+\.?[0-9]*)", text, re.IGNORECASE)
        if match:
            return float(match.group(2).replace(",", ""))
        match = re.search(r"Total\s*:?\s*([0-9,]+\.?[0-9]*)", text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
        return match.group(1) if match else None

    def _crosscheck(
        self,
        parsed: Dict[str, Optional[str | float]],
        declared_vendor: Optional[str],
        declared_amount: Optional[float],
        declared_date: Optional[datetime],
        confidence: float,
    ) -> tuple[Dict[str, float], Dict[str, Any]]:
        penalties: Dict[str, float] = {}
        vendor_match = False
        parsed_vendor = parsed.get("vendor")
        if parsed_vendor and declared_vendor:
            vendor_match = declared_vendor.lower() in parsed_vendor.lower()
        if declared_vendor and not vendor_match:
            penalties["vendor_mismatch"] = self.config.vendor_penalty

        amount_match = False
        parsed_amount = parsed.get("amount")
        if parsed_amount and declared_amount:
            diff = abs(float(parsed_amount) - declared_amount)
            if declared_amount:
                amount_match = diff <= self.config.amount_tolerance_pct * declared_amount
        if declared_amount and not amount_match:
            penalties["amount_mismatch"] = self.config.amount_penalty

        date_match = True
        parsed_date_value = self._normalize_date(parsed.get("date"))
        if declared_date and parsed_date_value:
            delta_days = abs((parsed_date_value - declared_date).days)
            date_match = delta_days <= self.config.date_tolerance_days
        if declared_date and not date_match:
            penalties["date_mismatch"] = self.config.date_penalty

        if confidence < self.config.provider_confidence_threshold:
            penalties["low_confidence"] = self.config.low_confidence_penalty

        crosscheck = {
            "vendor_match": vendor_match,
            "amount_match": amount_match,
            "date_match": date_match,
            "declared_vendor": declared_vendor,
            "declared_amount": declared_amount,
            "declared_date": declared_date.isoformat() if declared_date else None,
        }

        return penalties, crosscheck

    def _normalize_date(self, value: Optional[str | float]) -> Optional[datetime]:
        if not value or not isinstance(value, str):
            return None
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None


__all__ = ["DocumentOCRService"]
