from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # 'user' or 'clinician' later if needed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One user can have many scans
    scans = relationship("Scan", back_populates="owner", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    original_image_path = Column(String(500), nullable=False)
    gradcam_image_path = Column(String(500), nullable=False)

    prediction = Column(String(50), nullable=False)   # 'NORMAL' or 'PNEUMONIA'
    confidence = Column(Float, nullable=False)
    risk_tier = Column(String(50), nullable=False)    # 'Low', 'Medium', 'High', etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Many scans belong to one user
    owner = relationship("User", back_populates="scans")