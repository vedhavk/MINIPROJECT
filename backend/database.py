from sqlalchemy import (
    create_engine, Column, Integer, String,
    Float, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Models ──────────────────────────────────────────────────────────────────

class Farmer(Base):
    __tablename__ = "farmer"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    pin_code = Column(String(10), nullable=False)
    email    = Column(String, unique=True, nullable=False, index=True)
    district = Column(String, nullable=False)
    state    = Column(String, nullable=False)
    password = Column(String, nullable=False)          # stored as bcrypt hash


class Veterinary(Base):
    __tablename__ = "veterinary"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    pin_code = Column(String(10), nullable=False)
    email    = Column(String, unique=True, nullable=False, index=True)
    district = Column(String, nullable=False)
    state    = Column(String, nullable=False)
    password = Column(String, nullable=False)


class AlertCallFarmer(Base):
    __tablename__ = "alertcall_farmer"

    id          = Column(Integer, primary_key=True, index=True)
    latitude    = Column(Float, nullable=False)
    longitude   = Column(Float, nullable=False)
    pin_code    = Column(String(10), nullable=False)
    farmer_id   = Column(Integer, ForeignKey("farmer.id"), nullable=False)
    prediction  = Column(String, nullable=False)          # e.g. "diseased"
    file_type   = Column(String, nullable=False)          # "image" | "video"
    alert_sent  = Column(String, default="pending")       # pending | sent | failed
    created_at  = Column(DateTime, default=datetime.utcnow)


class AlertCallVeterinary(Base):
    __tablename__ = "alertcall_veterinary"

    id             = Column(Integer, primary_key=True, index=True)
    latitude       = Column(Float, nullable=False)
    longitude      = Column(Float, nullable=False)
    pin_code       = Column(String(10), nullable=False)
    veterinary_id  = Column(Integer, ForeignKey("veterinary.id"), nullable=False)
    prediction     = Column(String, nullable=False)
    file_type      = Column(String, nullable=False)
    alert_sent     = Column(String, default="pending")
    created_at     = Column(DateTime, default=datetime.utcnow)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_db():
    """FastAPI dependency – yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)
