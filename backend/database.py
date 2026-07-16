import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ---- Database URL ----
# Set this as an environment variable in production (e.g. on Render/Railway, they provide it automatically)
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:hamzacr7@localhost:5432/xray_triage_db"  # local dev fallback
)

# Some hosts (like Render/Heroku) give URLs starting with "postgres://" instead of "postgresql://"
# SQLAlchemy 1.4+ requires "postgresql://" — this fixes that automatically if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ---- Dependency for FastAPI routes ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()