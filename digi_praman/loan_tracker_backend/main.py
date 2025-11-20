from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

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
