"""Visits — create a consultation session, list, and fetch."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit, VisitStatus
from app.schemas.visit import VisitCreate, VisitOut
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


@router.post("", response_model=VisitOut, status_code=status.HTTP_201_CREATED)
async def create_visit(
    data: VisitCreate,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    patient = (await db.execute(
        select(Patient).where(Patient.id == data.patient_id, Patient.clinic_id == doctor.id)
    )).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    visit = Visit(
        patient_id=data.patient_id,
        doctor_id=doctor.id,
        scheduled_at=data.scheduled_at or datetime.utcnow(),
        started_at=datetime.utcnow(),
        status=VisitStatus.in_progress,
        chief_complaint=data.chief_complaint,
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return visit


@router.get("", response_model=List[VisitOut])
async def list_visits(
    patient_id: str = "",
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    stmt = select(Visit).where(Visit.doctor_id == doctor.id).order_by(desc(Visit.scheduled_at))
    if patient_id:
        stmt = stmt.where(Visit.patient_id == patient_id)
    return list((await db.execute(stmt)).scalars().all())


@router.get("/{visit_id}", response_model=VisitOut)
async def get_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    visit = (await db.execute(select(Visit).where(Visit.id == visit_id))).scalar_one_or_none()
    if not visit or str(visit.doctor_id) != str(doctor.id):
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit
