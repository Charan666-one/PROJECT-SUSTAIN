"""
Patient intake form — self-reported data captured before the consultation
(often via a shared link / tablet in the waiting room).
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class PatientIntakeForm(Base):
    __tablename__ = "patient_intake_forms"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id      = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    chief_complaint = Column(Text)
    responses       = Column(JSON)      # structured intake questionnaire answers
    submitted_at    = Column(DateTime(timezone=True), server_default=func.now())

    patient         = relationship("Patient", back_populates="intake_forms")
