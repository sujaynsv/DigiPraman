from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "ok", "message": "Backend running"}

@router.get("/db")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "DB connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
