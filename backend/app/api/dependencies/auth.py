from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
# Patients authenticate at a different endpoint; separate scheme keeps the portals distinct.
patient_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/portal/auth/login")

_CREDS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_doctor(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Doctor:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        doctor_id = payload.get("sub")
        # A patient token must never be usable on doctor endpoints.
        if not doctor_id or payload.get("role") == "patient":
            raise _CREDS_EXC
    except JWTError:
        raise _CREDS_EXC

    doctor = (await db.execute(select(Doctor).where(Doctor.id == doctor_id))).scalar_one_or_none()
    if doctor is None or not doctor.is_active:
        raise _CREDS_EXC
    return doctor


async def get_current_patient(
    token: str = Depends(patient_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Patient:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # Only tokens explicitly minted for a patient are accepted here.
        if payload.get("role") != "patient" or not payload.get("sub"):
            raise _CREDS_EXC
        patient_id = payload["sub"]
    except JWTError:
        raise _CREDS_EXC

    patient = (await db.execute(select(Patient).where(Patient.id == patient_id))).scalar_one_or_none()
    if patient is None:
        raise _CREDS_EXC
    return patient
