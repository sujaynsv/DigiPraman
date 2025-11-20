from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
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

def get_users(
    db: Session,
    org_id: Optional[UUID] = None,
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
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

def get_schemes(
    db: Session,
    org_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Scheme]:
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
# STATS
# =====================================================

def get_stats(db: Session) -> dict:
    total_orgs = db.query(func.count(models.Organization.id)).scalar()
    total_users = db.query(func.count(models.User.id)).scalar()
    total_beneficiaries = db.query(func.count(models.User.id)).filter(
        models.User.role == models.RoleType.beneficiary
    ).scalar()
    total_officers = db.query(func.count(models.User.id)).filter(
        models.User.role == models.RoleType.officer
    ).scalar()
    total_admins = db.query(func.count(models.User.id)).filter(
        models.User.role == models.RoleType.admin
    ).scalar()
    total_schemes = db.query(func.count(models.Scheme.id)).scalar()
    
    return {
        "total_organizations": total_orgs,
        "total_users": total_users,
        "total_beneficiaries": total_beneficiaries,
        "total_officers": total_officers,
        "total_admins": total_admins,
        "total_schemes": total_schemes,
    }
