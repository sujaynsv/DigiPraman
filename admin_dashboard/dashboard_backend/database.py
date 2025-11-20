from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database (create tables if not exist)
def init_db():
    """
    Create tables in database.
    Note: Tables should already exist from Flutter backend.
    This is just to ensure they exist.
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables verified")
