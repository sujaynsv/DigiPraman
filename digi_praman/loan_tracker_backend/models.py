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
    role = Column(SQLEnum(RoleType), nullable=False)
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
