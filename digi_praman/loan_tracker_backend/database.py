from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with pool settings for production
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create extensions and enums
def init_db():
    with engine.connect() as conn:
        # Enable extensions
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "postgis"'))
        
        # Create enum types (will be ignored if they already exist)
        enums = [
            "CREATE TYPE role_type AS ENUM ('beneficiary', 'officer', 'admin')",
            "CREATE TYPE verification_status AS ENUM ('pending', 'submitted', 'scored', 'routed', 'needs_more', 'approved', 'rejected', 'video_pending', 'video_done')",
            "CREATE TYPE requirement_type AS ENUM ('photo', 'video', 'doc')",
            "CREATE TYPE requirement_status AS ENUM ('not_started', 'in_progress', 'completed')",
            "CREATE TYPE decision_type AS ENUM ('approve', 'reject', 'request_more', 'video_required')",
            "CREATE TYPE notification_channel AS ENUM ('sms', 'email', 'whatsapp', 'push')"
        ]
        
        for enum_sql in enums:
            try:
                conn.execute(text(enum_sql))
            except Exception:
                pass  # Enum already exists
        
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
