from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from models import RoleType, VerificationStatus
from typing import List


# =====================================================
# ORGANIZATION SCHEMAS
# =====================================================

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# =====================================================
# USER SCHEMAS
# =====================================================

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    role: RoleType
    locale: Optional[str] = "en"
    status: Optional[str] = "active"

class UserCreate(UserBase):
    _org_id: UUID

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    locale: Optional[str] = None
    status: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    _org_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# =====================================================
# SCHEME SCHEMAS
# =====================================================

class SchemeBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    evidence_template: Optional[Dict[str, Any]] = None
    default_thresholds: Optional[Dict[str, Any]] = None

class SchemeCreate(SchemeBase):
    _org_id: UUID

class SchemeUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    evidence_template: Optional[Dict[str, Any]] = None
    default_thresholds: Optional[Dict[str, Any]] = None

class SchemeResponse(SchemeBase):
    id: UUID
    _org_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# =====================================================
# STATS SCHEMAS
# =====================================================

class RiskBucket(BaseModel):
    count: int
    percentage: float


class RiskDistribution(BaseModel):
    low: RiskBucket
    medium: RiskBucket
    high: RiskBucket


class RecentApplication(BaseModel):
    application_id: str
    loan_ref_no: str
    applicant_name: str
    loan_amount: float
    risk_tier: str


class StatsResponse(BaseModel):
    pending_review: int
    approved: int
    flagged: int
    rejected: int

    pending_review_change: float
    approved_change: float
    flagged_change: float
    rejected_change: float

    risk_distribution: RiskDistribution
    recent_applications: List[RecentApplication]



# class StatsResponse(BaseModel):
#     total_organizations: int
#     total_users: int
#     total_beneficiaries: int
#     total_officers: int
#     total_admins: int
#     total_schemes: int
