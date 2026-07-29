"""
Immutable audit log — records every clinical decision event.
Append-only: rows are never updated or deleted (DPDP + medico-legal trail).
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id   = Column(UUID(as_uuid=True), ForeignKey("doctors.id"))
    patient_id  = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    visit_id    = Column(UUID(as_uuid=True), ForeignKey("visits.id"))

    # e.g. AI_RECOMMENDATION_GENERATED, RED_FLAG_DISMISSED,
    #      PRESCRIPTION_APPROVED, PRESCRIPTION_SENT, DATA_DELETION_REQUESTED
    event_type  = Column(String(64), nullable=False)
    payload     = Column(JSON)          # snapshot of the decision context
    signature   = Column(Text)          # sha256 hash chaining this event
    prev_hash   = Column(Text)          # hash of previous event (tamper-evidence)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
