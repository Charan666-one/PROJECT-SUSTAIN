"""Patient management — CRUD with DPDP consent capture."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.api.dependencies.auth import get_current_doctor
from app.services.audit import record_event

router = APIRouter()


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    if not data.consent_given:
        raise HTTPException(status_code=400, detail="Patient consent is required (DPDP Act 2023)")

    existing = (await db.execute(select(Patient).where(Patient.phone == data.phone))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="A patient with this phone number already exists")

    patient = Patient(
        full_name=data.full_name,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        phone=data.phone,
        email=data.email,
        address=data.address,
        emergency_contact=data.emergency_contact,
        language_pref=data.language_pref,
        consent_given=True,
        consent_version=settings.CONSENT_VERSION,
        consent_at=datetime.utcnow(),
    )
    db.add(patient)
    await db.flush()
    await record_event(
        db, event_type="PATIENT_CREATED", doctor_id=str(doctor.id), patient_id=str(patient.id),
        payload={"consent_version": settings.CONSENT_VERSION},
    )
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("", response_model=List[PatientOut])
async def list_patients(
    q: str = "",
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    stmt = select(Patient).order_by(Patient.full_name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(Patient.full_name.ilike(like) | Patient.phone.ilike(like))
    return list((await db.execute(stmt)).scalars().all())


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    patient = (await db.execute(select(Patient).where(Patient.id == patient_id))).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    patient = (await db.execute(select(Patient).where(Patient.id == patient_id))).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return patient
