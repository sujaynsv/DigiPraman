import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from database import Base

# Enums
class RoleType(str, enum.Enum):
    beneficiary = "beneficiary"
    officer = "officer"
    admin = "admin"

class VerificationStatus(str, enum.Enum):
    pending = "pending"
    submitted = "submitted"
    scored = "scored"
    routed = "routed"
    needs_more = "needs_more"
    approved = "approved"
    rejected = "rejected"
    video_pending = "video_pending"
    video_done = "video_done"

# Organization Model
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    type = Column(String)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    schemes = relationship("Scheme", back_populates="organization")

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # ✅ Use existing role_type enum from database, don't create new one
    role = Column(SQLEnum(RoleType, name='role_type', create_type=False), nullable=False)
    
    name = Column(String, nullable=False)
    mobile = Column(String(15), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    locale = Column(String(8), default="en")
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

    __table_args__ = (
        UniqueConstraint('_org_id', 'email', name='unique_org_email'),
        Index('idx_users_org_id', '_org_id'),
        Index('idx_users_mobile', 'mobile'),
    )

# Scheme Model
class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    evidence_template = Column(JSON)
    default_thresholds = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="schemes")

    __table_args__ = (
        UniqueConstraint('_org_id', 'code', name='unique_org_scheme_code'),
        Index('idx_schemes_org_id', '_org_id'),
    )
