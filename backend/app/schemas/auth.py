from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID


class DoctorRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    phone: Optional[str] = None
    registration_no: Optional[str] = None
    qualifications: List[str] = []
    clinic_name: Optional[str] = None
    clinic_address: Optional[str] = None
    languages: List[str] = ["en"]


class DoctorLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DoctorOut(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    clinic_name: Optional[str] = None
    registration_no: Optional[str] = None
    qualifications: List[str] = []
    languages: List[str] = ["en"]

    class Config:
        from_attributes = True
