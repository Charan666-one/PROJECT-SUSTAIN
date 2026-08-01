"""Global search across the clinic — patients, visits, prescriptions."""
from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit
from app.models.clinical.prescription import Prescription
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


@router.get("")
async def global_search(
    q: str,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    q = (q or "").strip()
    if len(q) < 2:
        return {"query": q, "patients": [], "visits": [], "prescriptions": []}
    like = f"%{q}%"

    patients = list((await db.execute(
        select(Patient)
        .where(Patient.clinic_id == doctor.id)
        .where(Patient.full_name.ilike(like) | Patient.phone.ilike(like))
        .limit(10)
    )).scalars().all())

    visits = list((await db.execute(
        select(Visit)
        .where(Visit.doctor_id == doctor.id, Visit.chief_complaint.ilike(like))
        .order_by(desc(Visit.scheduled_at)).limit(10)
    )).scalars().all())

    # Prescriptions store remedies as JSON — filter by remedy name in Python.
    presc_rows = list((await db.execute(
        select(Prescription).where(Prescription.doctor_id == doctor.id)
        .order_by(desc(Prescription.created_at)).limit(200)
    )).scalars().all())
    ql = q.lower()
    prescriptions: List[Any] = []
    for p in presc_rows:
        names = [r.get("name", "") for r in (p.remedies or [])]
        if any(ql in n.lower() for n in names):
            prescriptions.append({"id": str(p.id), "visit_id": str(p.visit_id),
                                  "remedies": ", ".join(n for n in names if n)})
        if len(prescriptions) >= 10:
            break

    return {
        "query": q,
        "patients": [{"id": str(p.id), "full_name": p.full_name, "phone": p.phone} for p in patients],
        "visits": [{"id": str(v.id), "patient_id": str(v.patient_id),
                    "chief_complaint": v.chief_complaint, "status": getattr(v.status, "value", v.status)}
                   for v in visits],
        "prescriptions": prescriptions,
    }
