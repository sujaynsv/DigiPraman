from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from models import RoleType, VerificationStatus, RequirementType, RequirementStatus, DecisionType, NotificationChannel
from decimal import Decimal

# =====================================================
# ORGANIZATION SCHEMAS
# =====================================================

class OrganizationBase(BaseModel):
    name: str
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# SCHEME SCHEMAS
# =====================================================

class SchemeBase(BaseModel):
    code: str
    name: str
    evidence_template: Optional[Dict[str, Any]] = None
    default_thresholds: Optional[Dict[str, Any]] = None
    locale_options: Optional[Dict[str, Any]] = None

class SchemeCreate(SchemeBase):
    _org_id: UUID

class SchemeUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    evidence_template: Optional[Dict[str, Any]] = None
    default_thresholds: Optional[Dict[str, Any]] = None
    locale_options: Optional[Dict[str, Any]] = None

class SchemeResponse(SchemeBase):
    id: UUID
    _org_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# USER SCHEMAS
# =====================================================

class UserBase(BaseModel):
    name: str
    mobile: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    role: RoleType
    locale: Optional[str] = "en"
    status: Optional[str] = "active"

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('Mobile number must have at least 10 digits')
        return v

class UserCreate(UserBase):
    _org_id: UUID

class UserUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleType] = None
    locale: Optional[str] = None
    status: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    _org_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# DEVICE SCHEMAS
# =====================================================

class DeviceBase(BaseModel):
    device_fingerprint: str
    trust_score: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=2)
    device_metadata: Optional[Dict[str, Any]] = None  # Changed from 'metadata'

class DeviceCreate(DeviceBase):
    _user_id: UUID

class DeviceUpdate(BaseModel):
    device_fingerprint: Optional[str] = None
    last_seen: Optional[datetime] = None
    trust_score: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=2)
    device_metadata: Optional[Dict[str, Any]] = None  # Changed from 'metadata'

class DeviceResponse(DeviceBase):
    id: UUID
    _user_id: UUID
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# QUERY PARAMETERS
# =====================================================

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

class UserFilterParams(PaginationParams):
    org_id: Optional[UUID] = None
    role: Optional[RoleType] = None
    status: Optional[str] = None
