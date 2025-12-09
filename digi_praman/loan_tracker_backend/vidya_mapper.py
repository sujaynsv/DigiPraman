from datetime import datetime
from typing import Any, Dict, List
from vidya_schemas import (
    EvidencePackage,
    EvidenceImage,
    EvidenceDocument,
    EvidenceVideo,
    Metadata,
    ApplicantHistory,
)
from models import LoanApplication, VerificationEvidence
import json

def build_evidence_package(
    loan: LoanApplication,
    evidences: List[VerificationEvidence],
) -> Dict[str, Any]:
    asset_images = []
    doc_images = []
    videos = []

    for ev in evidences:
        # Extract base64 from data URL
        base64_data = None
        if ev.file_path and ev.file_path.startswith('data:') and ',' in ev.file_path:
            base64_data = ev.file_path.split(',')[1]
        
        # Convert datetime to ISO string
        timestamp = ev.captured_at.isoformat() if ev.captured_at else datetime.utcnow().isoformat()
        
        common = {
            "id": str(ev.id),
            "url": None,
            "file_path": None,
            "base64_data": base64_data,
            "timestamp": timestamp,  # ✅ ISO string, not datetime object
        }

        if ev.evidence_type == "asset_photo":
            asset_images.append(EvidenceImage(declared_asset_type=loan.purpose or "unknown", **common))
        elif ev.evidence_type == "document":
            doc_images.append(EvidenceDocument(document_type=ev.requirement_type or "unknown", **common))

    # Convert datetime to ISO string for metadata
    # submission_timestamp = datetime.utcnow().isoformat()
    
    metadata = Metadata(
        case_id=str(loan.id),
        applicant_id=str(loan.id),
        org_id=None,
        scheme_code=None,
        declared_loan_amount=float(getattr(loan, 'sanctioned_amount', 0) or 0.0),
        declared_asset_type=getattr(loan, 'purpose', None),
        declared_vendor=None,
        declared_invoice_amount=None,
        declared_invoice_date=None,
        declared_asset_location=None,
        submission_location=None,
        submission_device_id=None,
        # submission_timestamp=submission_timestamp,  # ✅ ISO string
        applicant_history=ApplicantHistory(),
        custom_metadata={},
    )

    pkg = EvidencePackage(
        case_id=str(loan.id),
        asset_images=asset_images,
        doc_images=doc_images,
        videos=[],
        gps_coords=None,
        timestamps=None,
        metadata=metadata,
    )
    
    # ✅ Convert to JSON-serializable dict (handles datetime conversion)
    return pkg.model_dump(mode='json')  # or pkg.dict(by_alias=True, exclude_unset=True)
