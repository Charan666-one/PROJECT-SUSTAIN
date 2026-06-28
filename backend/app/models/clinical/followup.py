"""
Follow-up tracking — Day 3, Day 7, Day 30 outcome check-ins
Feeds outcome data back into the RAG knowledge base
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid, enum

class FollowUpType(str, enum.Enum):
    day_3  = "day_3"
    day_7  = "day_7"
    day_30 = "day_30"
    custom = "custom"

class OutcomeEnum(str, enum.Enum):
    improved    = "improved"
    no_change   = "no_change"
    worsened    = "worsened"
    not_reported= "not_reported"

class FollowUp(Base):
    __tablename__ = "followups"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id        = Column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=False)
    patient_id      = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    followup_type   = Column(Enum(FollowUpType), nullable=False)
    scheduled_at    = Column(DateTime, nullable=False)
    sent_at         = Column(DateTime)
    responded_at    = Column(DateTime)

    outcome         = Column(Enum(OutcomeEnum), default=OutcomeEnum.not_reported)
    patient_notes   = Column(Text)
    symptom_score   = Column(Integer)  # 1-10 self-reported

    # Flagged for escalation
    needs_escalation = Column(Boolean, default=False)
    escalation_reason= Column(Text)

    # Once outcome is recorded, index into vector DB
    indexed_to_vectordb = Column(Boolean, default=False)

    visit           = relationship("Visit", back_populates="followups")
