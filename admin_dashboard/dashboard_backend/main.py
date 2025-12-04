from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

import models
import schemas
import crud
from database import engine, get_db

# DON'T call init_db() here - it might be causing issues
# We'll create tables manually if needed

# Create FastAPI app
app = FastAPI(
    title="Admin Dashboard Backend API",
    description="Backend API for Loan Verification Admin Dashboard",
    version="1.0.0"
)

# ============================================
# CORS MIDDLEWARE - MUST BE FIRST!
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
def root():
    return {
        "message": "Admin Dashboard Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health/")
def health_check():
    return {"status": "healthy", "database": "connected"}

# ============================================
# STATS ENDPOINT
# ============================================
# @app.get("/stats/")
# def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        stats = crud.get_stats(db)
        return stats
    except Exception as e:
        print(f"❌ Error in get_stats: {e}")
        # Return zero stats instead of crashing
        return {
            "total_organizations": 0,
            "total_users": 0,
            "total_beneficiaries": 0,
            "total_officers": 0,
            "total_admins": 0,
            "total_schemes": 0,
        }

@app.get("/stats/")
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        return crud.get_stats(db)
    except Exception as e:
        print(f"❌ Error in dashboard stats: {e}")
        return {
            "pending_review": 0,
            "approved": 0,
            "flagged": 0,
            "rejected": 0,
            "pending_review_change": 0,
            "approved_change": 0,
            "flagged_change": 0,
            "rejected_change": 0,
            "risk_distribution": {
                "low": {"count": 0, "percentage": 0},
                "medium": {"count": 0, "percentage": 0},
                "high": {"count": 0, "percentage": 0}
            },
            "recent_applications": []
        }


# ============================================
# ORGANIZATION ENDPOINTS
# ============================================
@app.get("/organizations/")
def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of all organizations"""
    try:
        return crud.get_organizations(db, skip=skip, limit=limit)
    except Exception as e:
        print(f"❌ Error loading organizations: {e}")
        return []

@app.get("/organizations/{org_id}")
def get_organization(org_id: UUID, db: Session = Depends(get_db)):
    """Get organization by ID"""
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.post("/organizations/", status_code=201)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization"""
    try:
        return crud.create_organization(db, org)
    except Exception as e:
        print(f"❌ Error creating organization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# USER ENDPOINTS
# ============================================
@app.get("/users/")
def list_users(
    org_id: Optional[UUID] = Query(None),
    role: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of users with optional filters"""
    try:
        return crud.get_users(db, org_id=org_id, role=role, skip=skip, limit=limit)
    except Exception as e:
        print(f"❌ Error loading users: {e}")
        return []

@app.get("/users/{user_id}")
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        existing_user = crud.get_user_by_mobile(db, user.mobile)
        if existing_user:
            raise HTTPException(status_code=400, detail="Mobile number already registered")
        
        return crud.create_user(db, user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SCHEME ENDPOINTS
# ============================================
@app.get("/schemes/")
def list_schemes(
    org_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of schemes"""
    try:
        return crud.get_schemes(db, org_id=org_id, skip=skip, limit=limit)
    except Exception as e:
        print(f"❌ Error loading schemes: {e}")
        return []

@app.post("/schemes/", status_code=201)
def create_scheme(scheme: schemas.SchemeCreate, db: Session = Depends(get_db)):
    """Create a new scheme"""
    try:
        return crud.create_scheme(db, scheme)
    except Exception as e:
        print(f"❌ Error creating scheme: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# APPLICATION ENDPOINTS
# ============================================

# @app.get("/applications/")
# def list_applications(
#     search: Optional[str] = Query(None),
#     status: Optional[str] = Query("all"),
#     risk_level: Optional[str] = Query("all"),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=200),
#     db: Session = Depends(get_db)
# ):
#     """Get loan applications for the admin UI"""
#     try:
#         return crud.get_applications(
#             db,
#             search=search,
#             status=status,
#             risk_level=risk_level,
#             skip=skip,
#             limit=limit,
#         )
#     except Exception as e:
#         print(f"❌ Error loading applications: {e}")
#         raise HTTPException(status_code=500, detail="Unable to load applications")
    


    # @app.get("/applications/{application_id}")
    # def get_application_detail(application_id: UUID, db: Session = Depends(get_db)):
    #     """Get full details for a single application"""
    #     try:
    #         data = crud.get_application_detail(db, application_id)
    #         if not data:
    #             raise HTTPException(status_code=404, detail="Application not found")
    #         return data
    #     except HTTPException:
    #         raise
    #     except Exception as e:
    #         print(f"❌ Error loading application detail: {e}")
    #         raise HTTPException(status_code=500, detail="Unable to load application detail")

@app.get("/applications/")
def list_applications(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query("all"),
    risk_level: Optional[str] = Query("all"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get loan applications for the admin UI"""
    try:
        return crud.get_applications(
            db,
            search=search,
            status=status,
            risk_level=risk_level,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        print(f"❌ Error loading applications: {e}")
        raise HTTPException(status_code=500, detail="Unable to load applications")


@app.get("/applications/{application_id}")
def get_application_detail(application_id: UUID, db: Session = Depends(get_db)):
    """
    Get full detail for a single loan application.
    """
    try:
        detail = crud.get_application_detail(db, application_id)
        if not detail:
            raise HTTPException(status_code=404, detail="Application not found")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error loading application detail: {e}")
        raise HTTPException(status_code=500, detail="Unable to load application detail")