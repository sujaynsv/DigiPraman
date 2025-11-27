from datetime import datetime, timedelta
import models
import schemas
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

# Debug: Print what's in models
print("Models module:", models)
print("Models attributes:", dir(models))
print("Has Device?", hasattr(models, 'Device'))

# =====================================================
# ORGANIZATION CRUD
# =====================================================

def create_organization(db: Session, org: schemas.OrganizationCreate) -> models.Organization:
    db_org = models.Organization(**org.model_dump())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organization(db: Session, org_id: UUID) -> Optional[models.Organization]:
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
    return db.query(models.Organization).offset(skip).limit(limit).all()

def update_organization(db: Session, org_id: UUID, org_update: schemas.OrganizationUpdate) -> Optional[models.Organization]:
    db_org = get_organization(db, org_id)
    if db_org:
        update_data = org_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_org, key, value)
        db.commit()
        db.refresh(db_org)
    return db_org

def delete_organization(db: Session, org_id: UUID) -> bool:
    db_org = get_organization(db, org_id)
    if db_org:
        db.delete(db_org)
        db.commit()
        return True
    return False

# =====================================================
# SCHEME CRUD
# =====================================================

def create_scheme(db: Session, scheme: schemas.SchemeCreate) -> models.Scheme:
    db_scheme = models.Scheme(**scheme.model_dump())
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return db_scheme

def get_scheme(db: Session, scheme_id: UUID) -> Optional[models.Scheme]:
    return db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()

def get_scheme_by_code(db: Session, code: str) -> Optional[models.Scheme]:
    return db.query(models.Scheme).filter(models.Scheme.code == code).first()

def get_schemes(db: Session, org_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[models.Scheme]:
    query = db.query(models.Scheme)
    if org_id:
        query = query.filter(models.Scheme._org_id == org_id)
    return query.offset(skip).limit(limit).all()

def update_scheme(db: Session, scheme_id: UUID, scheme_update: schemas.SchemeUpdate) -> Optional[models.Scheme]:
    db_scheme = get_scheme(db, scheme_id)
    if db_scheme:
        update_data = scheme_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_scheme, key, value)
        db.commit()
        db.refresh(db_scheme)
    return db_scheme

def delete_scheme(db: Session, scheme_id: UUID) -> bool:
    db_scheme = get_scheme(db, scheme_id)
    if db_scheme:
        db.delete(db_scheme)
        db.commit()
        return True
    return False

# =====================================================
# USER CRUD
# =====================================================

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_mobile(db: Session, mobile: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.mobile == mobile).first()

def get_users(
    db: Session,
    org_id: Optional[UUID] = None,
    role: Optional[models.RoleType] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    query = db.query(models.User)
    
    if org_id:
        query = query.filter(models.User._org_id == org_id)
    if role:
        query = query.filter(models.User.role == role)
    if status:
        query = query.filter(models.User.status == status)
    
    return query.offset(skip).limit(limit).all()

def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# =====================================================
# DEVICE CRUD
# =====================================================

def create_device(db: Session, device: schemas.DeviceCreate) -> models.Device:
    db_device = models.Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_device(db: Session, device_id: UUID) -> Optional[models.Device]:
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def get_device_by_fingerprint(db: Session, fingerprint: str) -> Optional[models.Device]:
    return db.query(models.Device).filter(models.Device.device_fingerprint == fingerprint).first()

def get_devices_by_user(db: Session, user_id: UUID) -> List[models.Device]:
    return db.query(models.Device).filter(models.Device._user_id == user_id).all()

def update_device(db: Session, device_id: UUID, device_update: schemas.DeviceUpdate) -> Optional[models.Device]:
    db_device = get_device(db, device_id)
    if db_device:
        update_data = device_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_device, key, value)
        db.commit()
        db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: UUID) -> bool:
    db_device = get_device(db, device_id)
    if db_device:
        db.delete(db_device)
        db.commit()
        return True
    return False

from twilio.rest import Client
import os

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_sms(to: str, body: str):
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to
    )
    return message.sid

import random

def generate_otp_code() -> str:
    # Generate a 6-digit random OTP as a string
    return f"{random.randint(100000, 999999)}"


from models import OTP
def create_otp(db: Session, mobile: str):
    otp_code = generate_otp_code()
    expires = datetime.utcnow() + timedelta(minutes=5)
    otp = OTP(mobile=mobile, otp_code=otp_code, expires_at=expires)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    # Send SMS with OTP
    send_sms(
        to=mobile, 
        body=f"Your verification code is {otp_code}. It will expire in 5 minutes."
    )
    return otp

from datetime import datetime
from models import OTP
from sqlalchemy.orm import Session

def verify_otp(db: Session, mobile: str, otp_code: str) -> bool:
    otp = (
        db.query(OTP)
        .filter(
            OTP.mobile == mobile,
            OTP.verified == False,
            OTP.expires_at > datetime.utcnow()
        )
        .order_by(OTP.created_at.desc())
        .first()
    )
    if otp and otp.otp_code == otp_code:
        otp.verified = True
        db.commit()
        return True
    return False

def get_loans_for_mobile(
    db: Session,
    mobile: str,
    skip: int = 0,
    limit: int = 20
) -> List[models.LoanApplication]:
    return (
        db.query(models.LoanApplication)
        .join(models.User, models.LoanApplication._beneficiary_id == models.User.id)
        .filter(models.User.mobile == mobile)
        .order_by(models.LoanApplication.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_user_by_mobile(db: Session, mobile: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.mobile == mobile).first()


from typing import Tuple
def get_loan_summary_for_mobile(
    db: Session, mobile: str, skip: int = 0, limit: int = 20
) -> tuple:
    """
    Return (user, loans, active_count, pending_count)
    """
    user = db.query(models.User).filter(models.User.mobile == mobile).first()
    if not user:
        return (None, [], 0, 0)

    q = (
        db.query(models.LoanApplication)
        .filter(models.LoanApplication._beneficiary_id == user.id)
        .order_by(models.LoanApplication.created_at.desc())
    )

    loans = q.offset(skip).limit(limit).all()

    active_count = (
        db.query(models.LoanApplication)
        .filter(
            models.LoanApplication._beneficiary_id == user.id,
            models.LoanApplication.lifecycle_status.in_(["active", "disbursed"])
        )
        .count()
    )

    pending_count = (
        db.query(models.LoanApplication)
        .filter(
            models.LoanApplication._beneficiary_id == user.id,
            models.LoanApplication.lifecycle_status.in_(
                ["verification_required", "verification_pending"]
            ),
        )
        .count()
    )

    return (user, loans, active_count, pending_count)



from sqlalchemy import text
from typing import List, Optional

def create_verification_evidence(
    db: Session,
    loan_application_id: UUID,
    evidence_data: schemas.EvidenceCreate
) -> models.VerificationEvidence:
    """Store verification evidence with optional GPS location"""
    
    # Prepare geometry if lat/lon provided
    geom_text = None
    if evidence_data.latitude and evidence_data.longitude:
        # PostGIS uses (longitude, latitude) order!
        geom_text = f"SRID=4326;POINT({evidence_data.longitude} {evidence_data.latitude})"
    
    evidence = models.VerificationEvidence(
        loan_application_id=loan_application_id,
        evidence_type=evidence_data.evidence_type,
        requirement_type=evidence_data.requirement_type,
        file_name=evidence_data.file_name,
        file_path=evidence_data.file_path,
        file_type=evidence_data.file_type,
        file_size_bytes=evidence_data.file_size_bytes,
        capture_address=evidence_data.capture_address,
    )
    
    db.add(evidence)
    db.flush()  # Get the ID before setting geometry
    
    # Set geometry using PostGIS function
    if geom_text:
        db.execute(
            text("""
                UPDATE verification_evidence 
                SET capture_location = ST_GeomFromText(:geom_text)
                WHERE id = :evidence_id
            """),
            {"geom_text": geom_text, "evidence_id": evidence.id}
        )
    
    db.commit()
    db.refresh(evidence)
    return evidence

def get_verification_evidence_with_location(
    db: Session,
    loan_application_id: UUID
) -> List[dict]:
    """Retrieve evidence with lat/lon extracted from PostGIS geometry"""
    
    query = text("""
        SELECT 
            id,
            loan_application_id,
            evidence_type,
            requirement_type,
            file_name,
            file_path,
            file_type,
            file_size_bytes,
            ST_Y(capture_location::geometry) AS latitude,
            ST_X(capture_location::geometry) AS longitude,
            capture_address,
            captured_at
        FROM verification_evidence
        WHERE loan_application_id = :loan_id
        ORDER BY captured_at DESC
    """)
    
    result = db.execute(query, {"loan_id": loan_application_id})
    return [dict(row._mapping) for row in result]

def get_verification_status(
    db: Session,
    loan_ref_no: str
) -> Optional[schemas.VerificationStatus]:
    """Check completion status of verification steps"""
    
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        return None
    
    evidence_list = get_verification_evidence_with_location(db, loan.id)
    
    asset_photos = [e for e in evidence_list if e['evidence_type'] == 'asset_photo']
    documents = [e for e in evidence_list if e['evidence_type'] == 'document']
    
    # Require at least 2 asset photos and 1 document
    asset_photos_complete = len(asset_photos) >= 2
    documents_complete = len(documents) >= 1
    
    return schemas.VerificationStatus(
        loan_ref_no=loan_ref_no,
        asset_photos_count=len(asset_photos),
        documents_count=len(documents),
        asset_photos_complete=asset_photos_complete,
        documents_complete=documents_complete,
        can_submit=asset_photos_complete and documents_complete
    )


from sqlalchemy import text

def list_verification_evidence_for_loan(
    db: Session,
    loan_ref_no: str,
) -> list[dict]:
    loan = (
        db.query(models.LoanApplication)
        .filter(models.LoanApplication.loan_ref_no == loan_ref_no)
        .first()
    )
    if not loan:
        return []

    q = text("""
        SELECT 
            id,
            evidence_type,
            requirement_type,
            file_name,
            file_type,
            file_size_bytes,
            captured_at,
            ST_Y(capture_location::geometry) AS latitude,
            ST_X(capture_location::geometry) AS longitude,
            capture_address
        FROM verification_evidence
        WHERE loan_application_id = :loan_id
        ORDER BY captured_at DESC
    """)
    rows = db.execute(q, {"loan_id": loan.id})
    return [dict(row._mapping) for row in rows]


from sqlalchemy import text
from typing import List, Optional

from datetime import timezone

def get_evidence_with_preview(db: Session, evidence_id: UUID) -> Optional[dict]:
    """Get evidence with full file_path for preview"""
    query = text("""
        SELECT 
            id,
            evidence_type,
            requirement_type,
            file_name,
            file_type,
            file_size_bytes,
            file_path,
            ST_Y(capture_location::geometry) AS latitude,
            ST_X(capture_location::geometry) AS longitude,
            capture_address,
            captured_at
        FROM verification_evidence
        WHERE id = :evidence_id
    """)
    
    result = db.execute(query, {"evidence_id": evidence_id})
    row = result.fetchone()
    return dict(row._mapping) if row else None

def list_evidence_with_previews(db: Session, loan_ref_no: str) -> list[dict]:
    """List all evidence with file data for previews"""
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        return []
    
    query = text("""
        SELECT 
            id,
            evidence_type,
            requirement_type,
            file_name,
            file_type,
            file_size_bytes,
            file_path AS file_data,
            ST_Y(capture_location::geometry) AS latitude,
            ST_X(capture_location::geometry) AS longitude,
            capture_address,
            captured_at
        FROM verification_evidence
        WHERE loan_application_id = :loan_id
        ORDER BY captured_at DESC
    """)
    
    result = db.execute(query, {"loan_id": loan.id})
    return [dict(row._mapping) for row in result]

def submit_verification_final(db: Session, loan_ref_no: str) -> models.LoanApplication:
    """Final submission - moves from documents_uploaded to submitted"""
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        raise ValueError("Loan not found")
    
    loan.verification_stage = models.VerificationStage.submitted
    loan.submitted_at = datetime.now(timezone.utc)
    loan.lifecycle_status = "verification_submitted"
    
    # Create tracking event
    event = models.VerificationTrackingEvent(
        loan_application_id=loan.id,
        stage=models.VerificationStage.submitted,
        description="Application submitted for verification"
    )
    db.add(event)
    db.commit()
    db.refresh(loan)
    
    return loan

def get_application_tracking(db: Session, loan_ref_no: str) -> Optional[dict]:
    """Get tracking status and events for an application"""
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        return None
    
    events = db.query(models.VerificationTrackingEvent).filter(
        models.VerificationTrackingEvent.loan_application_id == loan.id
    ).order_by(models.VerificationTrackingEvent.created_at.desc()).all()
    
    video_call = db.query(models.VideoCallRequest).filter(
        models.VideoCallRequest.loan_application_id == loan.id,
        models.VideoCallRequest.status == 'pending'
    ).first()
    
    return {
        "loan_ref_no": loan.loan_ref_no,
        "current_stage": loan.verification_stage,
        "submitted_at": loan.submitted_at,
        "reviewed_at": loan.reviewed_at,
        "video_call_requested": video_call is not None,
        "video_call_scheduled_for": video_call.scheduled_for if video_call else None,
        "events": events
    }

def get_pending_video_calls(db: Session, user_mobile: str) -> list:
    """Get pending video call requests for a user"""
    user = db.query(models.User).filter(models.User.mobile == user_mobile).first()
    if not user:
        return []
    
    loans = db.query(models.LoanApplication).filter(
        models.LoanApplication._beneficiary_id == user.id
    ).all()
    
    loan_ids = [loan.id for loan in loans]
    
    calls = db.query(models.VideoCallRequest).filter(
        models.VideoCallRequest.loan_application_id.in_(loan_ids),
        models.VideoCallRequest.status == 'pending'
    ).all()
    
    return calls


def get_video_call_for_loan(db: Session, loan_ref_no: str):
    """Get the pending video call request for a loan"""
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        return None
    
    video_call = db.query(models.VideoCallRequest).filter(
        models.VideoCallRequest.loan_application_id == loan.id,
        models.VideoCallRequest.status == 'pending'
    ).first()
    
    return video_call
