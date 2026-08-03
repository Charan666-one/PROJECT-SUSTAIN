"""
Patient Portal — the patient-facing half of the clinic.

Hard rules enforced here:
- Everything is scoped to the logged-in patient (never another patient's data).
- Patients NEVER see AI output: no ai_recommendation, evidence, red flags, or the
  clinical anomaly taxonomy. Only doctor-approved prescriptions, their own
  follow-up forms, a friendly recovery status, and notifications.
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit
from app.models.clinical.prescription import Prescription
from app.models.clinical.followup import FollowUp, OutcomeEnum
from app.schemas.portal import (
    PatientLogin, PatientToken, PatientProfile, PatientPrescription,
    PatientFollowUp, FollowUpSubmit, PatientDashboard, Notification,
)
from app.services.pdf import build_prescription_pdf
from app.services.surveillance_ops import assess_and_advance
from app.services.audit import record_event
from app.api.dependencies.auth import get_current_patient

router = APIRouter()

_STATUS_TO_OUTCOME = {"better": "improved", "same": "no_change", "worse": "worsened"}


def _recovery_status(visit: Visit | None) -> str:
    """Doctor's clinical trend → friendly, non-clinical wording for the patient."""
    if not visit:
        return "No active treatment"
    if visit.surveillance_status == "recovered":
        return "Recovered 🎉"
    trend = visit.recovery_trend
    if trend == "improving":
        return "Recovering well"
    if trend == "worsening":
        return "Your doctor is monitoring you closely"
    return "Under your doctor's care"


async def _latest_visit(db: AsyncSession, patient_id) -> Visit | None:
    return (await db.execute(
        select(Visit).where(Visit.patient_id == patient_id, Visit.doctor_approved == True)  # noqa: E712
        .order_by(desc(Visit.completed_at))
    )).scalars().first()


# ---------------- Auth ----------------
@router.post("/auth/login", response_model=PatientToken)
async def patient_login(data: PatientLogin, db: AsyncSession = Depends(get_db)):
    patient = (await db.execute(
        select(Patient).where(Patient.phone == data.phone, Patient.access_code == data.access_code)
    )).scalars().first()
    if not patient:
        raise HTTPException(status_code=401, detail="Incorrect phone number or access code")
    token = create_access_token({"sub": str(patient.id), "role": "patient"})
    return PatientToken(access_token=token)


@router.get("/me", response_model=PatientProfile)
async def me(patient: Patient = Depends(get_current_patient)):
    return patient


# ---------------- Dashboard ----------------
@router.get("/dashboard", response_model=PatientDashboard)
async def dashboard(db: AsyncSession = Depends(get_db), patient: Patient = Depends(get_current_patient)):
    visit = await _latest_visit(db, patient.id)
    presc = None
    if visit:
        presc = (await db.execute(select(Prescription).where(Prescription.visit_id == visit.id))).scalar_one_or_none()

    next_fu = (await db.execute(
        select(FollowUp).where(FollowUp.patient_id == patient.id, FollowUp.responded_at.is_(None))
        .order_by(FollowUp.scheduled_at)
    )).scalars().first()

    notifications: List[Notification] = []
    if presc:
        notifications.append(Notification(type="prescription", message="Your prescription is ready to view.",
                                          at=presc.created_at))
    if next_fu:
        due = next_fu.scheduled_at <= datetime.utcnow() + timedelta(days=1)
        notifications.append(Notification(
            type="followup",
            message="A check-in is due — please tell your doctor how you're feeling." if due
                    else "You have an upcoming check-in.",
            at=next_fu.scheduled_at))

    return PatientDashboard(
        patient_name=patient.full_name,
        recovery_status=_recovery_status(visit),
        last_visit_at=visit.completed_at if visit else None,
        next_followup_at=next_fu.scheduled_at if next_fu else None,
        current_prescription=_to_presc(presc) if presc else None,
        notifications=notifications,
    )


# ---------------- Prescriptions ----------------
def _to_presc(p: Prescription) -> PatientPrescription:
    return PatientPrescription(
        id=p.id, remedies=p.remedies or [], dietary_advice=p.dietary_advice,
        lifestyle_advice=p.lifestyle_advice, precautions=p.precautions, created_at=p.created_at,
    )


@router.get("/prescriptions", response_model=List[PatientPrescription])
async def prescriptions(db: AsyncSession = Depends(get_db), patient: Patient = Depends(get_current_patient)):
    rows = (await db.execute(
        select(Prescription).join(Visit, Visit.id == Prescription.visit_id)
        .where(Visit.patient_id == patient.id).order_by(desc(Prescription.created_at))
    )).scalars().all()
    return [_to_presc(p) for p in rows]


@router.get("/prescriptions/{prescription_id}/pdf")
async def prescription_pdf(
    prescription_id: str, db: AsyncSession = Depends(get_db), patient: Patient = Depends(get_current_patient)
):
    presc = (await db.execute(
        select(Prescription).join(Visit, Visit.id == Prescription.visit_id)
        .where(Prescription.id == prescription_id, Visit.patient_id == patient.id)
    )).scalars().first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    doctor = (await db.execute(select(Doctor).where(Doctor.id == presc.doctor_id))).scalar_one_or_none()
    pdf = build_prescription_pdf(presc, doctor, patient)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="prescription-{prescription_id}.pdf"'})


# ---------------- Recovery timeline (patient-friendly, no clinical jargon) ----------------
@router.get("/timeline")
async def timeline(db: AsyncSession = Depends(get_db), patient: Patient = Depends(get_current_patient)):
    events = []
    if patient.consent_at:
        events.append({"type": "registered", "label": "Registered at the clinic", "at": patient.consent_at.isoformat()})
    visits = (await db.execute(
        select(Visit).where(Visit.patient_id == patient.id, Visit.doctor_approved == True)  # noqa: E712
        .order_by(Visit.scheduled_at)
    )).scalars().all()
    for v in visits:
        when = v.completed_at or v.scheduled_at
        events.append({"type": "consultation", "label": "Consultation", "at": when.isoformat() if when else None})
        presc = (await db.execute(select(Prescription).where(Prescription.visit_id == v.id))).scalar_one_or_none()
        if presc:
            events.append({"type": "prescription", "label": "Medicine started",
                           "at": presc.created_at.isoformat() if presc.created_at else None,
                           "meta": {"remedies": [r.get("name") for r in (presc.remedies or [])]}})
        for fu in (await db.execute(
            select(FollowUp).where(FollowUp.visit_id == v.id).order_by(FollowUp.scheduled_at)
        )).scalars().all():
            responded = fu.responded_at is not None
            events.append({
                "type": "checkin",
                "label": ("Check-in" if not responded else "Check-in completed"),
                "at": (fu.responded_at or fu.scheduled_at).isoformat(),
                "meta": {"responded": responded, "wellness": fu.symptom_score},
            })
        if v.surveillance_status == "recovered":
            events.append({"type": "recovered", "label": "Recovered 🎉",
                           "at": v.completed_at.isoformat() if v.completed_at else None})
    events.sort(key=lambda e: e.get("at") or "")
    return {"events": events}


# ---------------- Follow-up forms ----------------
@router.get("/followups", response_model=List[PatientFollowUp])
async def followups(db: AsyncSession = Depends(get_db), patient: Patient = Depends(get_current_patient)):
    rows = (await db.execute(
        select(FollowUp).where(FollowUp.patient_id == patient.id).order_by(FollowUp.scheduled_at)
    )).scalars().all()
    return [PatientFollowUp(
        id=f.id, followup_type=getattr(f.followup_type, "value", f.followup_type),
        scheduled_at=f.scheduled_at, responded=f.responded_at is not None,
        outcome=getattr(f.outcome, "value", f.outcome), wellness=f.symptom_score,
    ) for f in rows]


@router.post("/followups/{followup_id}/respond", response_model=PatientFollowUp)
async def submit_followup(
    followup_id: str, data: FollowUpSubmit,
    db: AsyncSession = Depends(get_db), patient: Patient = Depends(get_current_patient),
):
    """Patient submits how they're feeling — this notifies the doctor and updates surveillance."""
    fu = (await db.execute(
        select(FollowUp).where(FollowUp.id == followup_id, FollowUp.patient_id == patient.id)
    )).scalar_one_or_none()
    if not fu:
        raise HTTPException(status_code=404, detail="Check-in not found")
    if fu.responded_at is not None:
        raise HTTPException(status_code=409, detail="You have already responded to this check-in")

    outcome = _STATUS_TO_OUTCOME[data.status]
    fu.outcome = OutcomeEnum(outcome)
    fu.symptom_score = data.wellness
    fu.patient_notes = data.notes
    fu.responded_at = datetime.utcnow()
    if outcome == "worsened" or (data.wellness is not None and data.wellness <= 3):
        fu.needs_escalation = True
        fu.escalation_reason = "Patient-reported worsening / low wellness (via portal)"

    visit = (await db.execute(select(Visit).where(Visit.id == fu.visit_id))).scalar_one_or_none()
    if visit:
        assessment = await assess_and_advance(db, visit)  # updates trend + schedules next check
        await record_event(
            db, event_type="PATIENT_FOLLOWUP_SUBMITTED",
            doctor_id=str(visit.doctor_id), patient_id=str(patient.id), visit_id=str(visit.id),
            payload={"outcome": outcome, "wellness": data.wellness,
                     "trend": assessment.trend, "escalation": fu.needs_escalation},
        )
    await db.commit()
    await db.refresh(fu)
    return PatientFollowUp(
        id=fu.id, followup_type=getattr(fu.followup_type, "value", fu.followup_type),
        scheduled_at=fu.scheduled_at, responded=True,
        outcome=getattr(fu.outcome, "value", fu.outcome), wellness=fu.symptom_score,
    )
