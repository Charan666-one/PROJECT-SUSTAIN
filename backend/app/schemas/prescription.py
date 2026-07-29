from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class PrescriptionOut(BaseModel):
    id: UUID
    visit_id: UUID
    doctor_id: UUID
    remedies: List[Any]
    dietary_advice: Optional[str] = None
    lifestyle_advice: Optional[str] = None
    precautions: Optional[str] = None
    notes: Optional[str] = None
    pdf_url: Optional[str] = None
    whatsapp_sent: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
