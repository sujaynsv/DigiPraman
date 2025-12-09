from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 1. Set your DB URL correctly
# Example for PostgreSQL – replace with real values
DATABASE_URL = "postgresql://shared_db_146p_user:0PKiG1dDo5zBW2aiCf0SCvvove3FGOka@dpg-d4go20ali9vc73do6ir0-a.oregon-postgres.render.com/shared_db_146p"

# 2. Create engine and session factory
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Dependency for FastAPI
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
