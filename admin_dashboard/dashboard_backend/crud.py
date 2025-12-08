# from sqlalchemy.orm import Session
# from sqlalchemy import func, text
# from typing import List, Optional
# from uuid import UUID
# import models
# import schemas

# # =====================================================
# # ORGANIZATION CRUD
# # =====================================================

# def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
#     return db.query(models.Organization).offset(skip).limit(limit).all()

# def get_organization(db: Session, org_id: UUID) -> Optional[models.Organization]:
#     return db.query(models.Organization).filter(models.Organization.id == org_id).first()

# def create_organization(db: Session, org: schemas.OrganizationCreate) -> models.Organization:
#     db_org = models.Organization(**org.dict())
#     db.add(db_org)
#     db.commit()
#     db.refresh(db_org)
#     return db_org

# def update_organization(db: Session, org_id: UUID, org: schemas.OrganizationUpdate) -> Optional[models.Organization]:
#     db_org = get_organization(db, org_id)
#     if not db_org:
#         return None
    
#     update_data = org.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_org, key, value)
    
#     db.commit()
#     db.refresh(db_org)
#     return db_org

# # =====================================================
# # USER CRUD
# # =====================================================

# def get_users(
#     db: Session,
#     org_id: Optional[UUID] = None,
#     role: Optional[str] = None,
#     skip: int = 0,
#     limit: int = 100
# ) -> List[models.User]:
#     query = db.query(models.User)
    
#     if org_id:
#         query = query.filter(models.User._org_id == org_id)
#     if role:
#         query = query.filter(models.User.role == role)
    
#     return query.offset(skip).limit(limit).all()

# def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
#     return db.query(models.User).filter(models.User.id == user_id).first()

# def get_user_by_mobile(db: Session, mobile: str) -> Optional[models.User]:
#     return db.query(models.User).filter(models.User.mobile == mobile).first()

# def create_user(db: Session, user: schemas.UserCreate) -> models.User:
#     db_user = models.User(**user.dict())
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def update_user(db: Session, user_id: UUID, user: schemas.UserUpdate) -> Optional[models.User]:
#     db_user = get_user(db, user_id)
#     if not db_user:
#         return None
    
#     update_data = user.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_user, key, value)
    
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# # =====================================================
# # SCHEME CRUD
# # =====================================================

# def get_schemes(
#     db: Session,
#     org_id: Optional[UUID] = None,
#     skip: int = 0,
#     limit: int = 100
# ) -> List[models.Scheme]:
#     query = db.query(models.Scheme)
    
#     if org_id:
#         query = query.filter(models.Scheme._org_id == org_id)
    
#     return query.offset(skip).limit(limit).all()

# def get_scheme(db: Session, scheme_id: UUID) -> Optional[models.Scheme]:
#     return db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()

# def create_scheme(db: Session, scheme: schemas.SchemeCreate) -> models.Scheme:
#     db_scheme = models.Scheme(**scheme.dict())
#     db.add(db_scheme)
#     db.commit()
#     db.refresh(db_scheme)
#     return db_scheme

# # =====================================================
# # STATS
# # =====================================================

# # def get_stats(db: Session) -> dict:
#     total_orgs = db.query(func.count(models.Organization.id)).scalar()
#     total_users = db.query(func.count(models.User.id)).scalar()
#     total_beneficiaries = db.query(func.count(models.User.id)).filter(
#         models.User.role == models.RoleType.beneficiary
#     ).scalar()
#     total_officers = db.query(func.count(models.User.id)).filter(
#         models.User.role == models.RoleType.officer
#     ).scalar()
#     total_admins = db.query(func.count(models.User.id)).filter(
#         models.User.role == models.RoleType.admin
#     ).scalar()
#     total_schemes = db.query(func.count(models.Scheme.id)).scalar()
    
#     return {
#         "total_organizations": total_orgs,
#         "total_users": total_users,
#         "total_beneficiaries": total_beneficiaries,
#         "total_officers": total_officers,
#         "total_admins": total_admins,
#         "total_schemes": total_schemes,
#     }


# from datetime import datetime, timedelta



# def get_stats(db):
#     # ------------------------------
#     # 1. VERIFICATION STATUS COUNTS
#     # ------------------------------
#     status_counts = dict(db.query(
#         models.VerificationRequest.status,
#         func.count(models.VerificationRequest.id)
#     ).group_by(models.VerificationRequest.status).all())

#     pending = status_counts.get(models.VerificationStatus.pending, 0)
#     approved = status_counts.get(models.VerificationStatus.approved, 0)
#     rejected = status_counts.get(models.VerificationStatus.rejected, 0)
#     flagged = status_counts.get(models.VerificationStatus.needs_more, 0)

#     # ------------------------------
#     # 2. WEEKLY COMPARISON
#     # ------------------------------
#     last_week = datetime.utcnow() - timedelta(days=7)

#     def weekly_count(status):
#         return db.query(func.count(models.VerificationRequest.id)) \
#             .filter(
#                 models.VerificationRequest.status == status,
#                 models.VerificationRequest.created_at >= last_week
#             ).scalar()

#     pending_last_week = weekly_count(models.VerificationStatus.pending)
#     approved_last_week = weekly_count(models.VerificationStatus.approved)
#     rejected_last_week = weekly_count(models.VerificationStatus.rejected)
#     flagged_last_week = weekly_count(models.VerificationStatus.needs_more)

#     def percentage_change(current, previous):
#         if previous == 0:
#             return 0
#         return round(((current - previous) / previous) * 100, 1)

#     # ------------------------------
#     # 3. RISK DISTRIBUTION
#     # ------------------------------
#     risk_counts = dict(
#         db.query(
#             models.RiskAnalysis.risk_tier,
#             func.count(models.RiskAnalysis.id)
#         ).group_by(models.RiskAnalysis.risk_tier).all()
#     )

#     total_risks = sum(risk_counts.values()) or 1

#     risk_distribution = {
#         "low": {
#             "count": risk_counts.get("Low", 0),
#             "percentage": round((risk_counts.get("Low", 0) / total_risks) * 100, 1)
#         },
#         "medium": {
#             "count": risk_counts.get("Medium", 0),
#             "percentage": round((risk_counts.get("Medium", 0) / total_risks) * 100, 1)
#         },
#         "high": {
#             "count": risk_counts.get("High", 0),
#             "percentage": round((risk_counts.get("High", 0) / total_risks) * 100, 1)
#         },
#     }

#     # ------------------------------
#     # 4. RECENT APPLICATIONS
#     # ------------------------------
#     recent_apps = db.execute(text("""
#         SELECT 
#             la.id,
#             la.loan_ref_no,
#             u.name AS applicant_name,
#             la.sanctioned_amount AS loan_amount,
#             COALESCE(ra.risk_tier, 'Medium') AS risk_tier
#         FROM loan_applications la
#         JOIN users u ON u.id = la._beneficiary_id
#         LEFT JOIN verification_requests vr ON vr._loan_id = la.id
#         LEFT JOIN risk_analyses ra ON ra._verification_id = vr.id
#         ORDER BY la.created_at DESC
#         LIMIT 5
#     """)).mappings().all()

#     recent_applications = [
#         {
#             "application_id": str(row["id"]),
#             "loan_ref_no": row["loan_ref_no"],
#             "applicant_name": row["applicant_name"],
#             "loan_amount": float(row["loan_amount"] or 0),
#             "risk_tier": row["risk_tier"]
#         }
#         for row in recent_apps
#     ]

#     # ------------------------------
#     # 5. FINAL RESPONSE
#     # ------------------------------
#     return {
#         "pending_review": pending,
#         "approved": approved,
#         "rejected": rejected,
#         "flagged": flagged,

#         "pending_review_change": percentage_change(pending, pending_last_week),
#         "approved_change": percentage_change(approved, approved_last_week),
#         "rejected_change": percentage_change(rejected, rejected_last_week),
#         "flagged_change": percentage_change(flagged, flagged_last_week),

#         "risk_distribution": risk_distribution,
#         "recent_applications": recent_applications
#     }



# # =====================================================
# # APPLICATIONS
# # =====================================================

# _STATUS_ALIASES = {
#     "auto-approved": "auto_approved",
#     "video-required": "video_required",
# }

# _RISK_BUCKET_SQL = """
# CASE
#     WHEN ra.risk_tier IS NOT NULL THEN LOWER(ra.risk_tier)
#     WHEN ra.risk_score IS NULL THEN 'medium'
#     WHEN ra.risk_score < 40 THEN 'low'
#     WHEN ra.risk_score <= 70 THEN 'medium'
#     ELSE 'high'
# END
# """


# def _status_slug(value: Optional[str]) -> str:
#     if not value:
#         return "pending"
#     return value.replace("_", "-").lower()


# def _status_label(slug: str) -> str:
#     words = slug.replace("-", " ").split()
#     if not words:
#         return "Pending"
#     return "-".join(word.capitalize() for word in words)


# def get_applications(
#     db: Session,
#     search: Optional[str] = None,
#     status: Optional[str] = None,
#     risk_level: Optional[str] = None,
#     skip: int = 0,
#     limit: int = 100,
# ):
#     params = {
#         "skip": max(skip, 0),
#         "limit": max(min(limit, 200), 1),
#     }
#     filters = []

#     normalized_search = (search or "").strip()
#     if normalized_search:
#         params["search"] = f"%{normalized_search.lower()}%"
#         filters.append(
#             "(LOWER(COALESCE(la.loan_ref_no, '')) LIKE :search OR "
#             "LOWER(COALESCE(la.purpose, '')) LIKE :search OR "
#             "LOWER(COALESCE(u.name, '')) LIKE :search OR "
#             "LOWER(COALESCE(CAST(u.id AS TEXT), '')) LIKE :search)"
#         )

#     normalized_status = (status or "all").lower()
#     if normalized_status != "all":
#         mapped = _STATUS_ALIASES.get(normalized_status, normalized_status)
#         params["status"] = mapped
#         filters.append(
#             "LOWER(COALESCE(la.lifecycle_status, vr.status::text, 'pending')) = :status"
#         )

#     normalized_risk = (risk_level or "all").lower()
#     if normalized_risk != "all":
#         params["risk_level"] = normalized_risk
#         filters.append(f"({_RISK_BUCKET_SQL}) = :risk_level")

#     base_sql = """
#         FROM loan_applications la
#         JOIN users u ON u.id = la._beneficiary_id
#         LEFT JOIN verification_requests vr ON vr._loan_id = la.id
#         LEFT JOIN risk_analyses ra ON ra._verification_id = vr.id
#     """

#     where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

#     total_query = text(f"SELECT COUNT(*) {base_sql} {where_clause}")
#     total = db.execute(total_query, params).scalar() or 0

#     rows_query = text(
#         f"""
#         SELECT
#             la.id,
#             la.loan_ref_no AS application_id,
#             la.lifecycle_status,
#             la.loan_type,
#             la.sanctioned_amount AS loan_amount,
#             la.created_at,
#             u.name AS beneficiary_name,
#             u.id AS beneficiary_identifier,
#             vr.status::text AS verification_status,
#             vr.submitted_at,
#             {_RISK_BUCKET_SQL} AS computed_risk_level,
#             ra.risk_score,
#             ra.risk_tier
#         {base_sql}
#         {where_clause}
#         ORDER BY la.created_at DESC
#         OFFSET :skip
#         LIMIT :limit
#         """
#     )

#     rows = db.execute(rows_query, params).mappings().all()

#     items = []
#     for row in rows:
#         risk_score = float(row["risk_score"]) if row["risk_score"] is not None else None
#         risk_level_value = row["computed_risk_level"] or "medium"

#         status_source = row["lifecycle_status"] or row["verification_status"] or "pending"
#         status_slug = _status_slug(status_source)

#         submitted_at = row["submitted_at"] or row["created_at"]

#         items.append(
#             {
#                 "id": str(row["id"]),
#                 "application_id": row["application_id"],
#                 "beneficiary_name": row["beneficiary_name"] or "Unknown",
#                 "beneficiary_identifier": str(row["beneficiary_identifier"]),
#                 "loan_type": row["loan_type"],
#                 "loan_amount": float(row["loan_amount"])
#                 if row["loan_amount"] is not None
#                 else None,
#                 "risk_score": risk_score,
#                 "risk_level": risk_level_value,
#                 "status": status_slug,
#                 "status_label": _status_label(status_slug),
#                 "submitted_at": submitted_at.isoformat() if submitted_at else None,
#             }
#         )

#     return {"items": items, "total": total}



from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import models
import schemas

# =====================================================
# ORGANIZATION CRUD
# =====================================================

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
    return db.query(models.Organization).offset(skip).limit(limit).all()

def get_organization(db: Session, org_id: UUID) -> Optional[models.Organization]:
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def create_organization(db: Session, org: schemas.OrganizationCreate) -> models.Organization:
    db_org = models.Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def update_organization(db: Session, org_id: UUID, org: schemas.OrganizationUpdate) -> Optional[models.Organization]:
    db_org = get_organization(db, org_id)
    if not db_org:
        return None
    
    update_data = org.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_org, key, value)

    db.commit()
    db.refresh(db_org)
    return db_org


# =====================================================
# USER CRUD
# =====================================================

def get_users(db: Session, org_id: Optional[UUID] = None, role: Optional[str] = None,
              skip: int = 0, limit: int = 100) -> List[models.User]:
    query = db.query(models.User)

    if org_id:
        query = query.filter(models.User._org_id == org_id)
    if role:
        query = query.filter(models.User.role == role)

    return query.offset(skip).limit(limit).all()


def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_mobile(db: Session, mobile: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.mobile == mobile).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: UUID, user: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


# =====================================================
# SCHEME CRUD
# =====================================================

def get_schemes(db: Session, org_id: Optional[UUID] = None,
                skip: int = 0, limit: int = 100) -> List[models.Scheme]:

    query = db.query(models.Scheme)

    if org_id:
        query = query.filter(models.Scheme._org_id == org_id)

    return query.offset(skip).limit(limit).all()

def get_scheme(db: Session, scheme_id: UUID) -> Optional[models.Scheme]:
    return db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()

def create_scheme(db: Session, scheme: schemas.SchemeCreate) -> models.Scheme:
    db_scheme = models.Scheme(**scheme.dict())
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return db_scheme


# =====================================================
# DASHBOARD STATS
# =====================================================

def get_stats(db: Session):

    # ------------------------------
    # 1. STATUS COUNTS FROM DB
    # ------------------------------

    loan_pending = db.query(func.count(models.LoanApplication.id)) \
        .filter(models.LoanApplication.lifecycle_status.in_([
            "verification_pending",
            "verification_required"
        ])).scalar() or 0

    approved_loans = db.query(func.count(models.LoanApplication.id)) \
        .filter(models.LoanApplication.lifecycle_status == "approved").scalar() or 0

    rejected_loans = db.query(func.count(models.LoanApplication.id)) \
        .filter(models.LoanApplication.lifecycle_status == "rejected").scalar() or 0

    flagged = db.query(func.count(models.VerificationRequest.id)) \
        .filter(models.VerificationRequest.status == models.VerificationStatus.needs_more).scalar() or 0


    # ------------------------------
    # 2. WEEKLY CHANGE CALCULATION
    # ------------------------------

    last_week = datetime.utcnow() - timedelta(days=7)

    def weekly_count(status_list):
        return db.query(func.count(models.LoanApplication.id)) \
            .filter(
                models.LoanApplication.lifecycle_status.in_(status_list),
                models.LoanApplication.created_at >= last_week
            ).scalar() or 0

    pending_last_week = weekly_count(["verification_pending", "verification_required"])
    approved_last_week = weekly_count(["approved"])
    rejected_last_week = weekly_count(["rejected"])

    def percentage_change(current, previous):
        if previous == 0:
            return 0
        return round(((current - previous) / previous) * 100, 1)

    # ------------------------------
    # 3. RISK DISTRIBUTION
    # ------------------------------

    risk_counts = dict(
        db.query(
            func.lower(models.RiskAnalysis.risk_tier),
            func.count(models.RiskAnalysis.id)
        ).group_by(func.lower(models.RiskAnalysis.risk_tier)).all()
    )

    total_risks = sum(risk_counts.values()) or 1

    risk_distribution = {
        "low": {
            "count": risk_counts.get("low", 0),
            "percentage": round((risk_counts.get("low", 0) / total_risks) * 100, 1)
        },
        "medium": {
            "count": risk_counts.get("medium", 0),
            "percentage": round((risk_counts.get("medium", 0) / total_risks) * 100, 1)
        },
        "high": {
            "count": risk_counts.get("high", 0),
            "percentage": round((risk_counts.get("high", 0) / total_risks) * 100, 1)
        },
    }


    # ------------------------------
    # 4. RECENT APPLICATIONS
    # ------------------------------

    recent_apps = db.execute(text("""
        SELECT 
            la.id,
            la.loan_ref_no,
            u.name AS applicant_name,
            la.sanctioned_amount AS loan_amount,
            la.lifecycle_status,
            COALESCE(ra.risk_tier, 'medium') AS risk_tier
        FROM loan_applications la
        JOIN users u ON u.id = la._beneficiary_id
        LEFT JOIN verification_requests vr ON vr._loan_id = la.id
        LEFT JOIN risk_analyses ra ON ra._verification_id = vr.id
        ORDER BY la.created_at DESC
        LIMIT 5
    """)).mappings().all()


    recent_applications = []
    for row in recent_apps:
        recent_applications.append({
            "application_id": str(row["id"]),
            "loan_ref_no": row["loan_ref_no"],
            "applicant_name": row["applicant_name"],
            "loan_amount": float(row["loan_amount"] or 0),
            "risk_tier": str(row["risk_tier"]).capitalize(),
            "status": row["lifecycle_status"]
        })


    # ------------------------------
    # 5. FINAL RESPONSE FOR DASHBOARD
    # ------------------------------

    return {
        "verification_pending": loan_pending,
        "verification_pending_change": percentage_change(loan_pending, pending_last_week),

        "approved": approved_loans,
        "approved_change": percentage_change(approved_loans, approved_last_week),

        "rejected": rejected_loans,
        "rejected_change": percentage_change(rejected_loans, rejected_last_week),

        "flagged": flagged,
        "flagged_change": 0,  # You can later improve this

        "risk_distribution": risk_distribution,
        "recent_applications": recent_applications
    }


# =====================================================
# APPLICATIONS SECTION (UNCHANGED)
# =====================================================

_STATUS_ALIASES = {
    "auto-approved": "auto_approved",
    "video-required": "video_required",
}

_RISK_BUCKET_SQL = """
CASE
    WHEN ra.risk_tier IS NOT NULL THEN LOWER(ra.risk_tier)
    WHEN ra.risk_score IS NULL THEN 'medium'
    WHEN ra.risk_score < 40 THEN 'low'
    WHEN ra.risk_score <= 70 THEN 'medium'
    ELSE 'high'
END
"""

def _status_slug(value: Optional[str]) -> str:
    if not value:
        return "pending"
    return value.replace("_", "-").lower()

def _status_label(slug: str) -> str:
    words = slug.replace("-", " ").split()
    if not words:
        return "Pending"
    return "-".join(word.capitalize() for word in words)


def get_applications(db: Session, search: Optional[str] = None,
                     status: Optional[str] = None, risk_level: Optional[str] = None,
                     skip: int = 0, limit: int = 100):

    params = {
        "skip": max(skip, 0),
        "limit": max(min(limit, 200), 1),
    }

    filters = []

    if search:
        params["search"] = f"%{search.lower()}%"
        filters.append(
            "(LOWER(la.loan_ref_no) LIKE :search OR LOWER(u.name) LIKE :search)"
        )

    base_sql = """
        FROM loan_applications la
        JOIN users u ON u.id = la._beneficiary_id
        LEFT JOIN verification_requests vr ON vr._loan_id = la.id
        LEFT JOIN risk_analyses ra ON ra._verification_id = vr.id
    """

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    rows_query = text(f"""
        SELECT
            la.id,
            la.loan_ref_no AS application_id,
            la.lifecycle_status,
            la.loan_type,
            la.sanctioned_amount AS loan_amount,
            la.created_at,
            u.name AS beneficiary_name,
            {_RISK_BUCKET_SQL} AS computed_risk_level
        {base_sql}
        {where_clause}
        ORDER BY la.created_at DESC
        OFFSET :skip
        LIMIT :limit
    """)

    rows = db.execute(rows_query, params).mappings().all()

    items = []
    for row in rows:

        status_source = row["lifecycle_status"] or "pending"
        status_slug = _status_slug(status_source)

        items.append({
            "id": str(row["id"]),
            "application_id": row["application_id"],
            "beneficiary_name": row["beneficiary_name"],
            "loan_type": row["loan_type"],
            "loan_amount": float(row["loan_amount"] or 0),
            "risk_level": row["computed_risk_level"],
            "status": status_slug,
            "status_label": _status_label(status_slug),
            "submitted_at": row["created_at"].isoformat(),
        })

    return {"items": items}
