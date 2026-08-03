from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class PatientLogin(BaseModel):
    phone: str
    access_code: str


class PatientToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PatientProfile(BaseModel):
    id: UUID
    full_name: str
    phone: str
    gender: str
    language_pref: str = "en"

    class Config:
        from_attributes = True


class PatientPrescription(BaseModel):
    id: UUID
    remedies: List[Any]
    dietary_advice: Optional[str] = None
    lifestyle_advice: Optional[str] = None
    precautions: Optional[str] = None
    created_at: Optional[datetime] = None


class PatientFollowUp(BaseModel):
    id: UUID
    followup_type: str
    scheduled_at: datetime
    responded: bool
    outcome: Optional[str] = None
    wellness: Optional[int] = None


class FollowUpSubmit(BaseModel):
    # Patient-friendly: better / same / worse maps to the clinical outcome enum.
    status: str = Field(pattern="^(better|same|worse)$")
    wellness: Optional[int] = Field(default=None, ge=1, le=10)
    notes: Optional[str] = None


class Notification(BaseModel):
    type: str
    message: str
    at: Optional[datetime] = None


class PatientDashboard(BaseModel):
    patient_name: str
    recovery_status: str                     # friendly, non-clinical
    last_visit_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    current_prescription: Optional[PatientPrescription] = None
    notifications: List[Notification] = []
