"""
Doctor / practitioner account model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Doctor(Base):
    __tablename__ = "doctors"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name       = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, nullable=False)
    phone           = Column(String(20), unique=True)
    password_hash   = Column(String(255), nullable=False)
    registration_no = Column(String(100))   # AYUSH registration
    qualifications  = Column(JSON)          # ["BHMS", "MD Homeopathy"]
    clinic_name     = Column(String(255))
    clinic_address  = Column(Text)
    languages       = Column(JSON, default=["en"])
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime)
    last_login      = Column(DateTime)
