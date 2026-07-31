"""
Visit / consultation session model
Links patient -> doctor -> AI recommendation -> doctor approval -> prescription
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid, enum

class VisitStatus(str, enum.Enum):
    scheduled    = "scheduled"
    in_progress  = "in_progress"
    completed    = "completed"
    cancelled    = "cancelled"

class Visit(Base):
    __tablename__ = "visits"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id      = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id       = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    scheduled_at    = Column(DateTime, nullable=False)
    started_at      = Column(DateTime)
    completed_at    = Column(DateTime)
    status          = Column(Enum(VisitStatus), default=VisitStatus.scheduled)

    chief_complaint = Column(Text)
    symptoms_raw    = Column(Text)       # Raw doctor/voice input
    symptoms_structured = Column(JSON)   # Parsed symptom schema
    clarifying_qa   = Column(JSON)       # AI clarification Q&A pairs

    red_flags_detected  = Column(JSON)   # List of detected red flags
    red_flag_dismissed  = Column(Boolean, default=False)
    red_flag_dismissed_by = Column(UUID(as_uuid=True))

    ai_recommendation   = Column(JSON)   # Full RAG output
    ai_confidence_score = Column(String(10))  # high / medium / low
    ai_sources_cited    = Column(JSON)

    # Recovery surveillance: active until the patient recovers or the doctor closes it.
    surveillance_status = Column(String(20), default="active")   # active / recovered / closed
    recovery_trend      = Column(String(20))                     # improving / plateau / worsening / recovered / pending
    recovery_anomaly    = Column(String(20))                     # latest anomaly flag (see services.surveillance)

    doctor_notes        = Column(Text)
    doctor_approved     = Column(Boolean, default=False)
    doctor_approved_at  = Column(DateTime)
    doctor_signature    = Column(Text)   # Digital signature hash

    patient             = relationship("Patient", back_populates="visits")
    prescription        = relationship("Prescription", back_populates="visit", uselist=False)
    followups           = relationship("FollowUp", back_populates="visit")
