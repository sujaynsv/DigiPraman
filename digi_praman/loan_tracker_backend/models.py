from sqlalchemy import Column, String, DateTime, Numeric, Enum as SQLEnum, CheckConstraint, UniqueConstraint, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from database import Base

# =====================================================
# ENUM Types
# =====================================================

class RoleType(str, enum.Enum):
    BENEFICIARY = "beneficiary"
    OFFICER = "officer"
    ADMIN = "admin"



class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    SCORED = "scored"
    ROUTED = "routed"
    NEEDS_MORE = "needs_more"
    APPROVED = "approved"
    REJECTED = "rejected"
    VIDEO_PENDING = "video_pending"
    VIDEO_DONE = "video_done"

class RequirementType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    DOC = "doc"

class RequirementStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class DecisionType(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_MORE = "request_more"
    VIDEO_REQUIRED = "video_required"

class NotificationChannel(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"

# =====================================================
# ORGANIZATIONS
# =====================================================

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    type = Column(Text)
    config = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    schemes = relationship("Scheme", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_organizations_name', 'name'),
    )

# =====================================================
# SCHEMES (Loan Programs)
# =====================================================

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='RESTRICT'), nullable=False)
    code = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    evidence_template = Column(JSONB)
    default_thresholds = Column(JSONB)
    locale_options = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="schemes")

    __table_args__ = (
        Index('idx_schemes_org_id', '_org_id'),
        Index('idx_schemes_code', 'code', unique=True),
    )

# =====================================================
# USERS
# =====================================================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='RESTRICT'), nullable=False)
    role = Column(String(20), nullable=False)
    name = Column(Text, nullable=False)
    mobile = Column(String(15), unique=True, nullable=False)
    email = Column(Text)
    locale = Column(String(8), default='en')
    status = Column(Text, default='active')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('_org_id', 'email', name='unique_org_email'),
        Index('idx_users_org_id', '_org_id'),
        Index('idx_users_mobile', 'mobile'),
        Index('idx_users_role', 'role'),
    )


from sqlalchemy import Boolean

class OTP(Base):
    __tablename__ = "otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile = Column(String(15), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_otps_mobile", "mobile"),
    )


# =====================================================
# DEVICES
# =====================================================

class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    device_fingerprint = Column(Text, unique=True, nullable=False)
    last_seen = Column(DateTime(timezone=True))
    trust_score = Column(Numeric(3, 2))
    device_metadata = Column(JSONB)  # Changed from metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="devices")

    __table_args__ = (
        CheckConstraint('trust_score >= 0 AND trust_score <= 1', name='check_trust_score_range'),
        Index('idx_devices_user_id', '_user_id'),
        Index('idx_devices_fingerprint', 'device_fingerprint', unique=True),
    )


from sqlalchemy import Column, String, DateTime, Numeric, Enum as SQLEnum, CheckConstraint, UniqueConstraint, ForeignKey, Index, Date, Boolean, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # ← Make sure this line is present
from geoalchemy2 import Geometry
import enum
import uuid
from datetime import datetime


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _org_id = Column(PGUUID(as_uuid=True), ForeignKey('organizations.id', ondelete='RESTRICT'), nullable=False)
    _scheme_id = Column(PGUUID(as_uuid=True), ForeignKey('schemes.id', ondelete='RESTRICT'), nullable=False)
    _beneficiary_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    verification_evidence = relationship("VerificationEvidence", back_populates="loan_application")
    loan_ref_no = Column(Text, unique=True, nullable=False)
    loan_type = Column(Text)
    sanctioned_amount = Column(Numeric(12, 2))
    disbursed_amount = Column(Numeric(12, 2))
    emi_due_date = Column(Date)
    next_emi_date = Column(Date)
    purpose = Column(Text)
    declared_asset = Column(JSON)
    lifecycle_status = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # optional relationships
    beneficiary = relationship("User")
    scheme = relationship("Scheme")



from geoalchemy2 import Geometry

class VerificationEvidence(Base):
    __tablename__ = "verification_evidence"

    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    loan_application_id = Column(PGUUID(as_uuid=True), ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False)
    requirement_type = Column(String(100))
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size_bytes = Column(Numeric)
    capture_location = Column(Geometry('POINT', srid=4326))
    capture_address = Column(Text)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    loan_application = relationship("LoanApplication", back_populates="verification_evidence")
