"""Pydantic schemas for VIDYA AI inputs and outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class GPSCoordinate(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)


class EvidenceImage(BaseModel):
    id: str
    url: Optional[HttpUrl] = None
    file_path: Optional[str] = None
    base64_data: Optional[str] = None
    mime_type: Optional[str] = Field("image/jpeg")
    declared_asset_type: Optional[str] = None
    timestamp: Optional[datetime] = None


class EvidenceDocument(EvidenceImage):
    document_type: Optional[str] = None


class EvidenceVideo(BaseModel):
    id: str
    url: Optional[HttpUrl] = None
    file_path: Optional[str] = None
    base64_data: Optional[str] = None
    duration_seconds: Optional[float] = None
    timestamp: Optional[datetime] = None


class ApplicantHistory(BaseModel):
    previous_rejections: int = 0
    fraudulent_flags: int = 0
    submitted_cases: int = 0


class Metadata(BaseModel):
    case_id: str
    applicant_id: str
    org_id: Optional[str] = None
    scheme_code: Optional[str] = None
    declared_loan_amount: float
    declared_asset_type: Optional[str] = None
    declared_vendor: Optional[str] = None
    declared_invoice_amount: Optional[float] = None
    declared_invoice_date: Optional[datetime] = None
    declared_asset_location: Optional[GPSCoordinate] = None
    submission_location: Optional[GPSCoordinate] = None
    submission_device_id: Optional[str] = None
    submission_timestamp: datetime = Field(default_factory=datetime.utcnow)
    applicant_history: ApplicantHistory = Field(default_factory=ApplicantHistory)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidencePackage(BaseModel):
    case_id: str = Field(..., min_length=1)
    asset_images: List[EvidenceImage] = Field(default_factory=list)
    doc_images: List[EvidenceDocument] = Field(default_factory=list)
    videos: List[EvidenceVideo] = Field(default_factory=list)
    gps_coords: Optional[List[GPSCoordinate]] = None
    timestamps: Optional[List[datetime]] = None
    metadata: Metadata


class ImageQualityResult(BaseModel):
    image_id: str
    quality_score: float
    blur_variance: float
    brightness: float
    contrast: float
    resolution_ok: bool
    flags: List[str] = Field(default_factory=list)
    officer_review_flag: bool = False
    reason_if_fail: Optional[str] = None


class ObjectDetectionResult(BaseModel):
    image_id: str
    detected_objects: List[Dict[str, Any]]
    asset_match: bool
    asset_match_score: float
    match_score: float = Field(0.0, description="Deprecated, use asset_match_score")
    details: Dict[str, Any] = Field(default_factory=dict)


class OCRResult(BaseModel):
    doc_id: str
    raw_text: str
    ocr_confidence: float
    parsed_fields: Dict[str, Any]
    crosscheck_results: Dict[str, Any]
    penalties: Dict[str, float] = Field(default_factory=dict)
    match_score: float = 1.0


class DuplicateResult(BaseModel):
    evidence_id: str
    duplicate_found: bool
    hash_distance: int
    reference_case_id: Optional[str] = None
    penalty_points: float = 0.0


class FraudFeatureVector(BaseModel):
    case_id: str
    features: Dict[str, float]
    explanation_fields: Dict[str, Any]


class FraudScoreResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    fraud_score: float
    model_version: str
    feature_importance: Dict[str, float]
    rule_penalties: Dict[str, float] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    gst_verified: bool
    gst_details: Dict[str, Any]
    bank_match: bool
    bank_details: Dict[str, Any]


class ScoreBreakdown(BaseModel):
    image_quality: List[ImageQualityResult]
    asset_match: List[ObjectDetectionResult]
    ocr: List[OCRResult]
    duplicates: List[DuplicateResult]
    fraud_features: FraudFeatureVector
    xgboost: FraudScoreResult
    verification: Optional[VerificationResult] = None
    forensics: List[Dict[str, Any]] = Field(default_factory=list)


class ScoreResponse(BaseModel):
    case_id: str
    final_risk_score: float
    risk_tier: Literal["auto-approve", "officer-review", "video-verify"]
    routing_decision: str
    # verification_summary: Optional[VerificationResult] = None # Keep this, it's important
    verification_summary: Optional[VerificationResult] = None
    
    # Critical reasons for the decision (Simpler for devs)
    decision_reasons: List[str] = Field(default_factory=list)
    
    # Detailed breakdown (Optional / secondary)
    scores: ScoreBreakdown
    # full_explanation: Dict[str, Any]  <-- REMOVED (Redundant & Huge)


class WeightUpdateRequest(BaseModel):
    weights: Dict[str, float]


class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: Dict[str, bool]