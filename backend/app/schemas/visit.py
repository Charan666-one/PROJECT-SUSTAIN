from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class VisitCreate(BaseModel):
    patient_id: UUID
    scheduled_at: Optional[datetime] = None
    chief_complaint: Optional[str] = None


class SymptomInput(BaseModel):
    chief_complaint: str = ""
    structured_symptoms: Any = None   # free text or structured dict
    modalities: Optional[dict] = None
    mental_emotional: Optional[str] = None


class VisitOut(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    status: str
    scheduled_at: Optional[datetime] = None
    chief_complaint: Optional[str] = None
    red_flags_detected: Optional[List[Any]] = None
    ai_recommendation: Optional[Any] = None
    ai_confidence_score: Optional[str] = None
    doctor_approved: bool = False

    class Config:
        from_attributes = True
