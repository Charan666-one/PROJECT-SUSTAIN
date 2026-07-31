from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SurveillanceEpisode(BaseModel):
    visit_id: UUID
    patient_id: UUID
    patient_name: str
    chief_complaint: Optional[str] = None
    surveillance_status: str
    trend: str
    anomaly: str
    severity: str                 # info / watch / urgent
    recovered: bool
    days_under_surveillance: int
    latest_score: Optional[int] = None
    recommended_action: str
    suggest_re_evaluation: bool
    rationale: str
    next_check_at: Optional[datetime] = None
    doctor_in_loop: bool = True
