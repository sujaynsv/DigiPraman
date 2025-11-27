from datetime import datetime, timezone
from wsgiref import headers
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import os
import base64
import requests
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("TRANSLATE_API_KEY")


# Use absolute imports with your package structure
import models
import schemas
import crud
from database import engine, get_db, init_db

# Or if running as a script (not a package), keep relative imports:
import models
import schemas
import crud
from database import engine, get_db, init_db

# Initialize database
init_db()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Loan Verification System API",
    description="FastAPI backend for loan verification system with PostgreSQL",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROOT ENDPOINT
# =====================================================

@app.get("/")
def read_root():
    return {
        "message": "Loan Verification System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# =====================================================
# ORGANIZATION ENDPOINTS
# =====================================================

@app.post("/organizations/", response_model=schemas.OrganizationResponse, status_code=201)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization"""
    return crud.create_organization(db=db, org=org)

@app.get("/organizations/", response_model=List[schemas.OrganizationResponse])
def list_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all organizations"""
    return crud.get_organizations(db=db, skip=skip, limit=limit)

@app.get("/organizations/{org_id}", response_model=schemas.OrganizationResponse)
def get_organization(org_id: UUID, db: Session = Depends(get_db)):
    """Get organization by ID"""
    org = crud.get_organization(db=db, org_id=org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.patch("/organizations/{org_id}", response_model=schemas.OrganizationResponse)
def update_organization(org_id: UUID, org_update: schemas.OrganizationUpdate, db: Session = Depends(get_db)):
    """Update organization"""
    org = crud.update_organization(db=db, org_id=org_id, org_update=org_update)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.delete("/organizations/{org_id}", status_code=204)
def delete_organization(org_id: UUID, db: Session = Depends(get_db)):
    """Delete organization"""
    success = crud.delete_organization(db=db, org_id=org_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
    return None

# =====================================================
# SCHEME ENDPOINTS
# =====================================================

@app.post("/schemes/", response_model=schemas.SchemeResponse, status_code=201)
def create_scheme(scheme: schemas.SchemeCreate, db: Session = Depends(get_db)):
    """Create a new scheme"""
    # Check if organization exists
    org = crud.get_organization(db=db, org_id=scheme._org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if scheme code already exists
    existing = crud.get_scheme_by_code(db=db, code=scheme.code)
    if existing:
        raise HTTPException(status_code=400, detail="Scheme code already exists")
    
    return crud.create_scheme(db=db, scheme=scheme)

@app.get("/schemes/", response_model=List[schemas.SchemeResponse])
def list_schemes(
    org_id: Optional[UUID] = Query(None, description="Filter by organization ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all schemes, optionally filtered by organization"""
    return crud.get_schemes(db=db, org_id=org_id, skip=skip, limit=limit)

@app.get("/schemes/{scheme_id}", response_model=schemas.SchemeResponse)
def get_scheme(scheme_id: UUID, db: Session = Depends(get_db)):
    """Get scheme by ID"""
    scheme = crud.get_scheme(db=db, scheme_id=scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@app.get("/schemes/code/{code}", response_model=schemas.SchemeResponse)
def get_scheme_by_code(code: str, db: Session = Depends(get_db)):
    """Get scheme by code"""
    scheme = crud.get_scheme_by_code(db=db, code=code)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@app.patch("/schemes/{scheme_id}", response_model=schemas.SchemeResponse)
def update_scheme(scheme_id: UUID, scheme_update: schemas.SchemeUpdate, db: Session = Depends(get_db)):
    """Update scheme"""
    scheme = crud.update_scheme(db=db, scheme_id=scheme_id, scheme_update=scheme_update)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@app.delete("/schemes/{scheme_id}", status_code=204)
def delete_scheme(scheme_id: UUID, db: Session = Depends(get_db)):
    """Delete scheme"""
    success = crud.delete_scheme(db=db, scheme_id=scheme_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return None

# =====================================================
# USER ENDPOINTS
# =====================================================

@app.post("/users/", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if organization exists
    org = crud.get_organization(db=db, org_id=user._org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if mobile already exists
    existing = crud.get_user_by_mobile(db=db, mobile=user.mobile)
    if existing:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.UserResponse])
def list_users(
    org_id: Optional[UUID] = Query(None, description="Filter by organization ID"),
    role: Optional[models.RoleType] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users with optional filters"""
    return crud.get_users(db=db, org_id=org_id, role=role, status=status, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/mobile/{mobile}", response_model=schemas.UserResponse)
def get_user_by_mobile(mobile: str, db: Session = Depends(get_db)):
    """Get user by mobile number"""
    user = crud.get_user_by_mobile(db=db, mobile=mobile)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: UUID, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    """Delete user"""
    success = crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# =====================================================
# DEVICE ENDPOINTS
# =====================================================

@app.post("/devices/", response_model=schemas.DeviceResponse, status_code=201)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    """Create a new device"""
    # Check if user exists
    user = crud.get_user(db=db, user_id=device._user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if device fingerprint already exists
    existing = crud.get_device_by_fingerprint(db=db, fingerprint=device.device_fingerprint)
    if existing:
        raise HTTPException(status_code=400, detail="Device fingerprint already exists")
    
    return crud.create_device(db=db, device=device)

@app.get("/devices/user/{user_id}", response_model=List[schemas.DeviceResponse])
def list_user_devices(user_id: UUID, db: Session = Depends(get_db)):
    """List all devices for a user"""
    return crud.get_devices_by_user(db=db, user_id=user_id)

@app.get("/devices/{device_id}", response_model=schemas.DeviceResponse)
def get_device(device_id: UUID, db: Session = Depends(get_db)):
    """Get device by ID"""
    device = crud.get_device(db=db, device_id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.patch("/devices/{device_id}", response_model=schemas.DeviceResponse)
def update_device(device_id: UUID, device_update: schemas.DeviceUpdate, db: Session = Depends(get_db)):
    """Update device"""
    device = crud.update_device(db=db, device_id=device_id, device_update=device_update)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: UUID, db: Session = Depends(get_db)):
    """Delete device"""
    success = crud.delete_device(db=db, device_id=device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return None

# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import Body, HTTPException
from schemas import OTPRequest, OTPVerifyRequest
@app.post("/auth/send-otp")
def send_otp(request: schemas.OTPRequest, db: Session = Depends(get_db)):
    otp = crud.create_otp(db, mobile=request.mobile)
    return {"message": f"OTP sent to {request.mobile}"}

from models import Organization
def get_default_org_id_somehow(db: Session) -> UUID:
    org = db.query(models.Organization).filter(Organization.name == "Default Org").first()
    if not org:
        raise HTTPException(status_code=400, detail="Default organization not found")
    return org.id

from models import OTP

@app.post("/auth/verify-otp")
def verify_otp_only(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    otp = (
        db.query(OTP)
        .filter(
            OTP.mobile == request.mobile,
            OTP.otp_code == request.otp,
            OTP.verified == False
        )
        .order_by(OTP.created_at.desc())
        .first()
    )
    if otp:
        otp.verified = True
        db.commit()
        return {"status": "verified"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # return {"status": "verified"}


from typing import List
from fastapi import Query

@app.get("/loans", response_model=List[schemas.LoanApplicationResponse])
def list_loans_for_user(
    mobile: str = Query(..., description="User mobile number"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    loans = crud.get_loans_for_mobile(db, mobile=mobile, skip=skip, limit=limit)
    return loans


from typing import List
from fastapi import Query, HTTPException

@app.get("/loans/summary", response_model=schemas.LoanSummaryResponse)
def get_loans_summary(
    mobile: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    user, loans, active_count, pending_count = crud.get_loan_summary_for_mobile(
        db, mobile, skip, limit
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    loans_data = []
    for loan in loans:
        # DEBUG: Print what we're getting
        print(f"DEBUG: loan_ref_no={loan.loan_ref_no}, verification_stage={loan.verification_stage}, type={type(loan.verification_stage)}")
        
        loans_data.append({
            "id": str(loan.id),
            "loan_ref_no": loan.loan_ref_no,
            "purpose": loan.purpose,
            "sanctioned_amount": float(loan.sanctioned_amount) if loan.sanctioned_amount else None,
            "next_emi_date": str(loan.next_emi_date) if loan.next_emi_date else None,
            "lifecycle_status": loan.lifecycle_status,
            "verification_stage": loan.verification_stage.value if loan.verification_stage else "not_started",  # THIS LINE MUST BE HERE
        })


    return schemas.LoanSummaryResponse(
        user_name=user.name or "User",
        active_loans_count=active_count,
        pending_verification_count=pending_count,
        loans=loans_data,
    )


from fastapi.responses import StreamingResponse
from io import BytesIO

@app.post("/tts")
def text_to_speech(
    text: str = Query(..., description="Text to read"),
    language_code: str = Query("en-IN", description="BCP-47 language code, e.g. en-IN, hi-IN"),
):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="TTS API key not configured")

    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"

    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": language_code,
            "ssmlGender": "NEUTRAL",
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 1.0,
        },
    }

    r = requests.post(url, json=payload)

    # # Log exact error from Google
    # print("TTS status:", r.status_code)
    # print("TTS body:", r.text)

    if r.status_code != 200:
      raise HTTPException(status_code=500, detail=f"TTS failed: {r.text}")

    data = r.json()
    audio_content_b64 = data.get("audioContent")
    if not audio_content_b64:
      raise HTTPException(status_code=500, detail=f"No audio content from TTS: {r.text}")

    audio_bytes = base64.b64decode(audio_content_b64)
    return StreamingResponse(
        BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=tts.mp3"},
    )


import base64
from fastapi import UploadFile, File, Form

# File upload endpoint
@app.post("/loans/{loan_ref_no:path}/evidence/upload")
async def upload_verification_evidence(
    loan_ref_no: str,
    evidence_type: str = Form(...),  # 'asset_photo' or 'document'
    requirement_type: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    capture_address: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Store file (for now, base64 encode and store in DB; production should use S3)
    file_b64 = base64.b64encode(file_content).decode('utf-8')
    file_path = f"data:{file.content_type};base64,{file_b64}"
    
    evidence_data = schemas.EvidenceCreate(
        evidence_type=evidence_type,
        requirement_type=requirement_type,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size_bytes=file_size,
        latitude=latitude,
        longitude=longitude,
        capture_address=capture_address
    )
    
    evidence = crud.create_verification_evidence(db, loan.id, evidence_data)
    
    return {"id": str(evidence.id), "message": "Evidence uploaded successfully"}

# Get verification status
@app.get("/loans/{loan_ref_no:path}/verification/status", response_model=schemas.VerificationStatus)
def get_verification_status_endpoint(
    loan_ref_no: str,
    db: Session = Depends(get_db)
):
    status = crud.get_verification_status(db, loan_ref_no)
    if not status:
        raise HTTPException(status_code=404, detail="Loan not found")
    return status

# Submit verification
@app.post("/loans/{loan_ref_no:path}/verification/submit")
def submit_verification(
    loan_ref_no: str,
    db: Session = Depends(get_db)
):
    status = crud.get_verification_status(db, loan_ref_no)
    if not status or not status.can_submit:
        raise HTTPException(status_code=400, detail="Cannot submit: requirements not met")
    
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    loan.verification_submitted_at = datetime.now(timezone.utc)
    loan.lifecycle_status = "verification_pending"
    db.commit()
    
    return {"message": "Verification submitted successfully"}


@app.get(
    "/loans/{loan_ref_no:path}/evidence",
    response_model=list[schemas.EvidenceListItem],
)
def list_verification_evidence(
    loan_ref_no: str,
    db: Session = Depends(get_db),
):
    items = crud.list_verification_evidence_for_loan(db, loan_ref_no)
    return items


from datetime import datetime, timezone

# Get evidence with preview (for download/display)
@app.get("/loans/{loan_ref_no:path}/evidence/{evidence_id}/preview")
def get_evidence_preview(
    loan_ref_no: str,
    evidence_id: UUID,
    db: Session = Depends(get_db)
):
    evidence = crud.get_evidence_with_preview(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return evidence

# List evidence with full data for review page
@app.get("/loans/{loan_ref_no:path}/evidence/full", response_model=List[schemas.EvidenceWithPreview])
def list_evidence_full(
    loan_ref_no: str,
    db: Session = Depends(get_db)
):
    items = crud.list_evidence_with_previews(db, loan_ref_no)
    return items

# Submit verification (final step from review page)
@app.post("/loans/{loan_ref_no:path}/verification/submit-final")
def submit_verification_final(
    loan_ref_no: str,
    db: Session = Depends(get_db)
):
    try:
        loan = crud.submit_verification_final(db, loan_ref_no)
        return {"message": "Application submitted successfully", "stage": loan.verification_stage}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get application tracking
@app.get("/loans/{loan_ref_no:path}/tracking", response_model=schemas.ApplicationTrackingResponse)
def get_application_tracking(
    loan_ref_no: str,
    db: Session = Depends(get_db)
):
    tracking = crud.get_application_tracking(db, loan_ref_no)
    if not tracking:
        raise HTTPException(status_code=404, detail="Loan not found")
    return tracking

# Get pending video calls for user
@app.get("/video-calls/pending")
def get_pending_video_calls(
    mobile: str,
    db: Session = Depends(get_db)
):
    calls = crud.get_pending_video_calls(db, mobile)
    return calls

# Update when uploading evidence (mark as documents_uploaded)
@app.post("/loans/{loan_ref_no:path}/evidence/upload")
async def upload_verification_evidence(
    loan_ref_no: str,
    evidence_type: str = Form(...),
    requirement_type: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    capture_address: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    loan = db.query(models.LoanApplication).filter(
        models.LoanApplication.loan_ref_no == loan_ref_no
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    file_content = await file.read()
    file_size = len(file_content)
    file_b64 = base64.b64encode(file_content).decode('utf-8')
    file_path = f"data:{file.content_type};base64,{file_b64}"
    
    evidence_data = schemas.EvidenceCreate(
        evidence_type=evidence_type,
        requirement_type=requirement_type,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size_bytes=file_size,
        latitude=latitude,
        longitude=longitude,
        capture_address=capture_address
    )
    
    evidence = crud.create_verification_evidence(db, loan.id, evidence_data)
    
    # Update stage if first upload
    if loan.verification_stage == models.VerificationStage.not_started:
        loan.verification_stage = models.VerificationStage.documents_uploaded
        db.commit()
    
    return {"id": str(evidence.id), "message": "Evidence uploaded successfully"}


@app.post("/video-call/start/{loan_ref_no:path}")
def start_video_call(
    loan_ref_no: str,
    db: Session = Depends(get_db)
):
    """Generate Jitsi meeting room name"""
    try:
        loan = db.query(models.LoanApplication).filter(
            models.LoanApplication.loan_ref_no == loan_ref_no
        ).first()
        
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Create unique room name from loan ref
        room_name = f"loan_{loan_ref_no.replace('/', '_')}".lower()
        
        # Jitsi URL with camera configuration
        jitsi_url = f"https://meet.jit.si/{room_name}?config.constraints={{mediaSource:{{audio:true,video:{{width:{{ideal:1280}},height:{{ideal:720}}}}}}}}&interfaceConfig.DEFAULT_REMOTE_DISPLAY_NAME_KEY='on'"
        
        # Update loan verification stage
        loan.verification_stage = models.VerificationStage.video_verification_requested
        db.commit()
        
        return {
            "room_url": jitsi_url,
            "room_name": room_name
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
