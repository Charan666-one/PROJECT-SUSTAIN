"""Prescriptions — fetch, generate a printable PDF, deliver via WhatsApp."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit
from app.models.clinical.prescription import Prescription
from app.schemas.prescription import PrescriptionOut
from app.services.pdf import build_prescription_pdf
from app.services.whatsapp.sender import send_prescription
from app.services.audit import record_event
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


async def _load(db: AsyncSession, prescription_id: str, doctor: Doctor):
    presc = (await db.execute(select(Prescription).where(Prescription.id == prescription_id))).scalar_one_or_none()
    if not presc or str(presc.doctor_id) != str(doctor.id):
        raise HTTPException(status_code=404, detail="Prescription not found")
    return presc


@router.get("/{prescription_id}", response_model=PrescriptionOut)
async def get_prescription(prescription_id: str, db: AsyncSession = Depends(get_db), doctor: Doctor = Depends(get_current_doctor)):
    return await _load(db, prescription_id, doctor)


@router.get("/{prescription_id}/pdf")
async def get_prescription_pdf(prescription_id: str, db: AsyncSession = Depends(get_db), doctor: Doctor = Depends(get_current_doctor)):
    presc = await _load(db, prescription_id, doctor)
    visit = (await db.execute(select(Visit).where(Visit.id == presc.visit_id))).scalar_one_or_none()
    patient = (await db.execute(select(Patient).where(Patient.id == visit.patient_id))).scalar_one_or_none() if visit else None
    pdf_bytes = build_prescription_pdf(presc, doctor, patient)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="prescription-{prescription_id}.pdf"'},
    )


@router.post("/{prescription_id}/send-whatsapp", response_model=PrescriptionOut)
async def send_whatsapp(prescription_id: str, db: AsyncSession = Depends(get_db), doctor: Doctor = Depends(get_current_doctor)):
    presc = await _load(db, prescription_id, doctor)
    visit = (await db.execute(select(Visit).where(Visit.id == presc.visit_id))).scalar_one_or_none()
    patient = (await db.execute(select(Patient).where(Patient.id == visit.patient_id))).scalar_one_or_none() if visit else None
    if not patient or not patient.phone:
        raise HTTPException(status_code=400, detail="Patient has no phone number on file")

    result = await send_prescription(patient.phone, presc, doctor)
    presc.whatsapp_sent = bool(result.get("sent"))
    presc.whatsapp_sent_at = datetime.utcnow() if result.get("sent") else None
    await record_event(
        db, event_type="PRESCRIPTION_SENT",
        doctor_id=str(doctor.id), patient_id=str(patient.id), visit_id=str(presc.visit_id),
        payload={"channel": "whatsapp", "sent": presc.whatsapp_sent},
    )
    await db.commit()
    await db.refresh(presc)
    return presc
