import models
import schemas
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

# Debug: Print what's in models
print("Models module:", models)
print("Models attributes:", dir(models))
print("Has Device?", hasattr(models, 'Device'))

# =====================================================
# ORGANIZATION CRUD
# =====================================================

def create_organization(db: Session, org: schemas.OrganizationCreate) -> models.Organization:
    db_org = models.Organization(**org.model_dump())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organization(db: Session, org_id: UUID) -> Optional[models.Organization]:
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
    return db.query(models.Organization).offset(skip).limit(limit).all()

def update_organization(db: Session, org_id: UUID, org_update: schemas.OrganizationUpdate) -> Optional[models.Organization]:
    db_org = get_organization(db, org_id)
    if db_org:
        update_data = org_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_org, key, value)
        db.commit()
        db.refresh(db_org)
    return db_org

def delete_organization(db: Session, org_id: UUID) -> bool:
    db_org = get_organization(db, org_id)
    if db_org:
        db.delete(db_org)
        db.commit()
        return True
    return False

# =====================================================
# SCHEME CRUD
# =====================================================

def create_scheme(db: Session, scheme: schemas.SchemeCreate) -> models.Scheme:
    db_scheme = models.Scheme(**scheme.model_dump())
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return db_scheme

def get_scheme(db: Session, scheme_id: UUID) -> Optional[models.Scheme]:
    return db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()

def get_scheme_by_code(db: Session, code: str) -> Optional[models.Scheme]:
    return db.query(models.Scheme).filter(models.Scheme.code == code).first()

def get_schemes(db: Session, org_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[models.Scheme]:
    query = db.query(models.Scheme)
    if org_id:
        query = query.filter(models.Scheme._org_id == org_id)
    return query.offset(skip).limit(limit).all()

def update_scheme(db: Session, scheme_id: UUID, scheme_update: schemas.SchemeUpdate) -> Optional[models.Scheme]:
    db_scheme = get_scheme(db, scheme_id)
    if db_scheme:
        update_data = scheme_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_scheme, key, value)
        db.commit()
        db.refresh(db_scheme)
    return db_scheme

def delete_scheme(db: Session, scheme_id: UUID) -> bool:
    db_scheme = get_scheme(db, scheme_id)
    if db_scheme:
        db.delete(db_scheme)
        db.commit()
        return True
    return False

# =====================================================
# USER CRUD
# =====================================================

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_mobile(db: Session, mobile: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.mobile == mobile).first()

def get_users(
    db: Session,
    org_id: Optional[UUID] = None,
    role: Optional[models.RoleType] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    query = db.query(models.User)
    
    if org_id:
        query = query.filter(models.User._org_id == org_id)
    if role:
        query = query.filter(models.User.role == role)
    if status:
        query = query.filter(models.User.status == status)
    
    return query.offset(skip).limit(limit).all()

def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# =====================================================
# DEVICE CRUD
# =====================================================

def create_device(db: Session, device: schemas.DeviceCreate) -> models.Device:
    db_device = models.Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_device(db: Session, device_id: UUID) -> Optional[models.Device]:
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def get_device_by_fingerprint(db: Session, fingerprint: str) -> Optional[models.Device]:
    return db.query(models.Device).filter(models.Device.device_fingerprint == fingerprint).first()

def get_devices_by_user(db: Session, user_id: UUID) -> List[models.Device]:
    return db.query(models.Device).filter(models.Device._user_id == user_id).all()

def update_device(db: Session, device_id: UUID, device_update: schemas.DeviceUpdate) -> Optional[models.Device]:
    db_device = get_device(db, device_id)
    if db_device:
        update_data = device_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_device, key, value)
        db.commit()
        db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: UUID) -> bool:
    db_device = get_device(db, device_id)
    if db_device:
        db.delete(db_device)
        db.commit()
        return True
    return False
