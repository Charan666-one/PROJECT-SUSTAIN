from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class PatientCreate(BaseModel):
    full_name: str
    date_of_birth: date
    gender: str = Field(pattern="^(male|female|other)$")
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    language_pref: str = "en"
    consent_given: bool = False


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    language_pref: Optional[str] = None


class PatientOut(BaseModel):
    id: UUID
    full_name: str
    date_of_birth: date
    gender: str
    phone: str
    email: Optional[str] = None
    language_pref: str = "en"
    consent_given: bool = False
    consent_version: Optional[str] = None
    consent_at: Optional[datetime] = None

    class Config:
        from_attributes = True
