"""Patient management — CRUD with DPDP consent capture."""
import secrets
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _gen_access_code() -> str:
    """6-digit patient-portal access code (easy to share verbally / on WhatsApp)."""
    return f"{secrets.randbelow(1_000_000):06d}"

from app.core.database import get_db
from app.core.config import settings
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit
from app.models.clinical.prescription import Prescription
from app.models.clinical.followup import FollowUp
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.api.dependencies.auth import get_current_doctor
from app.services.audit import record_event

from sqlalchemy import desc

router = APIRouter()


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    if not data.consent_given:
        raise HTTPException(status_code=400, detail="Patient consent is required (DPDP Act 2023)")

    existing = (await db.execute(
        select(Patient).where(Patient.clinic_id == doctor.id, Patient.phone == data.phone)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="A patient with this phone number already exists in your clinic")

    patient = Patient(
        clinic_id=doctor.id,
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
        access_code=_gen_access_code(),
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
    stmt = select(Patient).where(Patient.clinic_id == doctor.id).order_by(Patient.full_name)
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
    patient = (await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.clinic_id == doctor.id)
    )).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/{patient_id}/access")
async def get_patient_access(
    patient_id: str,
    regenerate: bool = False,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    """The patient-portal credentials the doctor shares (phone + access code)."""
    patient = (await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.clinic_id == doctor.id)
    )).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if regenerate or not patient.access_code:
        patient.access_code = _gen_access_code()
        await db.commit()
        await db.refresh(patient)
    return {"phone": patient.phone, "access_code": patient.access_code, "portal_url": "/portal"}


@router.get("/{patient_id}/timeline")
async def patient_timeline(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    """Chronological treatment journey for one patient (clinic-scoped)."""
    patient = (await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.clinic_id == doctor.id)
    )).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    events = []
    if patient.consent_at:
        events.append({"type": "registered", "label": "Patient registered",
                       "at": patient.consent_at.isoformat(), "ref_id": str(patient.id)})

    visits = list((await db.execute(
        select(Visit).where(Visit.patient_id == patient.id).order_by(Visit.scheduled_at)
    )).scalars().all())
    for v in visits:
        when = v.completed_at or v.started_at or v.scheduled_at
        events.append({
            "type": "consultation", "label": "Consultation",
            "at": when.isoformat() if when else None, "ref_id": str(v.id),
            "meta": {"chief_complaint": v.chief_complaint,
                     "status": getattr(v.status, "value", v.status),
                     "surveillance_status": v.surveillance_status,
                     "recovery_trend": v.recovery_trend, "approved": v.doctor_approved},
        })
        presc = (await db.execute(
            select(Prescription).where(Prescription.visit_id == v.id)
        )).scalar_one_or_none()
        if presc:
            events.append({
                "type": "prescription", "label": "Prescription",
                "at": presc.created_at.isoformat() if presc.created_at else None,
                "ref_id": str(presc.id),
                "meta": {"remedies": [r.get("name") for r in (presc.remedies or [])]},
            })
        fus = list((await db.execute(
            select(FollowUp).where(FollowUp.visit_id == v.id).order_by(FollowUp.scheduled_at)
        )).scalars().all())
        for fu in fus:
            events.append({
                "type": "followup",
                "label": f"Follow-up ({fu.followup_type.value if hasattr(fu.followup_type,'value') else fu.followup_type})",
                "at": (fu.responded_at or fu.scheduled_at).isoformat(),
                "ref_id": str(fu.id),
                "meta": {"responded": fu.responded_at is not None,
                         "outcome": getattr(fu.outcome, "value", fu.outcome),
                         "wellness": fu.symptom_score},
            })
        if v.surveillance_status == "recovered":
            events.append({"type": "recovered", "label": "Recovered",
                           "at": v.completed_at.isoformat() if v.completed_at else None,
                           "ref_id": str(v.id)})

    events.sort(key=lambda e: e.get("at") or "")
    return {"patient": {"id": str(patient.id), "full_name": patient.full_name}, "events": events}


@router.patch("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    patient = (await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.clinic_id == doctor.id)
    )).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return patient
