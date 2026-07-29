from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class FollowUpRespond(BaseModel):
    outcome: str = Field(pattern="^(improved|no_change|worsened|not_reported)$")
    symptom_score: Optional[int] = Field(default=None, ge=1, le=10)
    patient_notes: Optional[str] = None


class FollowUpOut(BaseModel):
    id: UUID
    visit_id: UUID
    patient_id: UUID
    followup_type: str
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    outcome: str
    symptom_score: Optional[int] = None
    needs_escalation: bool = False

    class Config:
        from_attributes = True
