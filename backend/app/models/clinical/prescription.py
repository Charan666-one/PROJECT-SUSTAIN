"""
Prescription — what the doctor actually prescribes (may differ from AI suggestion)
Stored separately from AI recommendation for legal clarity
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Prescription(Base):
    __tablename__ = "prescriptions"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id        = Column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=False)
    doctor_id       = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)

    remedies        = Column(JSON, nullable=False)  # [{name, potency, dosage, frequency, duration}]
    dietary_advice  = Column(Text)
    lifestyle_advice= Column(Text)
    precautions     = Column(Text)
    follow_up_date  = Column(DateTime)
    notes           = Column(Text)

    pdf_url         = Column(String(512))
    whatsapp_sent   = Column(Boolean, default=False)
    whatsapp_sent_at= Column(DateTime)

    created_at      = Column(DateTime)
    visit           = relationship("Visit", back_populates="prescription")
