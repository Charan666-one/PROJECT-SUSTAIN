"""
Patient model — stores demographic, consent, and contact info
DPDP Act compliant: tracks consent version and timestamp
"""
from sqlalchemy import Column, String, Date, Boolean, DateTime, Text, Enum, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid, enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class Patient(Base):
    __tablename__ = "patients"
    # Tenant isolation: a phone number is unique WITHIN a clinic, not globally,
    # so two clinics can each hold the same patient's number.
    __table_args__ = (
        UniqueConstraint("clinic_id", "phone", name="uq_patient_clinic_phone"),
        Index("ix_patient_clinic", "clinic_id"),
    )

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Owning clinic scope. In the single-doctor-clinic MVP this equals the
    # doctor's id (matches RAGEngine(clinic_id=str(doctor.id))).
    clinic_id       = Column(UUID(as_uuid=True), nullable=False)
    full_name       = Column(String(255), nullable=False)
    date_of_birth   = Column(Date, nullable=False)
    gender          = Column(Enum(GenderEnum), nullable=False)
    phone           = Column(String(20), nullable=False)
    email           = Column(String(255))
    address         = Column(Text)
    emergency_contact = Column(String(255))
    language_pref   = Column(String(10), default="en")

    # DPDP Compliance
    consent_given   = Column(Boolean, default=False)
    consent_version = Column(String(10))
    consent_at      = Column(DateTime)
    data_deletion_requested = Column(Boolean, default=False)

    # Relationships
    visits          = relationship("Visit", back_populates="patient")
    intake_forms    = relationship("PatientIntakeForm", back_populates="patient")
