"""
AeroGuard Database Engine & Session Management
----------------------------------------------
Provides connection pooling and session lifecycle management for SQLAlchemy ORM.
Supports PostgreSQL with automatic schema provisioning and fallback support.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/aeroguard"
)

# Render and cloud providers supply 'postgres://', SQLAlchemy 2.0 requires 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite or PostgreSQL engine initialization
try:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
    # Test connection
    with engine.connect() as conn:
        pass
    print(f"[Database] Connected successfully to {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
except Exception as e:
    print(f"[Database] Primary database connection failed ({e}). Falling back to local SQLite engine...")
    DATABASE_URL = "sqlite:///./aeroguard.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes all database tables defined in ORM models."""
    Base.metadata.create_all(bind=engine)
    print("[Database] Schema synchronized successfully.")


def get_db():
    """FastAPI dependency for yielding database session with automatic cleanup."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
