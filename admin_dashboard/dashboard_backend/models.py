import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
    Numeric,
)
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
    applications = relationship(
        "LoanApplication",
        back_populates="beneficiary",
        cascade="all, delete-orphan",
    )

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
    applications = relationship("LoanApplication", back_populates="scheme")

    __table_args__ = (
        UniqueConstraint('_org_id', 'code', name='unique_org_scheme_code'),
        Index('idx_schemes_org_id', '_org_id'),
    )


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False)
    _scheme_id = Column(PGUUID(as_uuid=True), ForeignKey("schemes.id", ondelete="RESTRICT"), nullable=False)
    _beneficiary_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    loan_ref_no = Column(String, nullable=False, unique=True)
    loan_type = Column(String)
    sanctioned_amount = Column(Numeric(12, 2))
    disbursed_amount = Column(Numeric(12, 2))
    emi_due_date = Column(Date)
    next_emi_date = Column(Date)
    purpose = Column(String)
    declared_asset = Column(JSON)
    lifecycle_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    beneficiary = relationship("User", back_populates="applications", foreign_keys=[_beneficiary_id])
    scheme = relationship("Scheme", back_populates="applications")
    verification_requests = relationship(
        "VerificationRequest",
        back_populates="loan",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index('idx_loans_org', '_org_id'),
        Index('idx_loans_scheme', '_scheme_id'),
        Index('idx_loans_beneficiary', '_beneficiary_id'),
    )


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _loan_id = Column(PGUUID(as_uuid=True), ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False)
    initiated_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(
        SQLEnum(VerificationStatus, name='verification_status', create_type=False),
        nullable=False,
        default=VerificationStatus.pending,
    )
    current_tier = Column(String)
    thresholds_ref = Column(JSON)
    due_date = Column(Date)
    submitted_at = Column(DateTime)
    scored_at = Column(DateTime)
    routed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    loan = relationship("LoanApplication", back_populates="verification_requests")
    risk_analysis = relationship("RiskAnalysis", back_populates="verification", uselist=False)


class RiskAnalysis(Base):
    __tablename__ = "risk_analyses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _verification_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("verification_requests.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    version = Column(String)
    scores = Column(JSON)
    risk_score = Column(Numeric(5, 2))
    risk_tier = Column(String)
    recommended_action = Column(String)
    flags = Column(JSON)
    explanation = Column(JSON)
    model_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    verification = relationship("VerificationRequest", back_populates="risk_analysis")