"""
Follow-ups — list due check-ins and record patient-reported outcomes.

Recording an outcome closes the learning loop: the case (symptoms + remedy +
outcome) is indexed into this clinic's vector store so future consultations
retrieve it. Worsened outcomes are flagged for escalation.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.visit import Visit
from app.models.clinical.prescription import Prescription
from app.models.clinical.followup import FollowUp, OutcomeEnum
from app.schemas.followup import FollowUpRespond, FollowUpOut
from app.rag.indexer import index_clinic_case
from app.rag.retrievers.base import symptoms_to_query
from app.services.audit import record_event
from app.services.surveillance_ops import assess_and_advance
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


@router.get("", response_model=List[FollowUpOut])
async def list_followups(
    due_only: bool = False,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    stmt = (
        select(FollowUp)
        .join(Visit, Visit.id == FollowUp.visit_id)
        .where(Visit.doctor_id == doctor.id)
        .order_by(FollowUp.scheduled_at)
    )
    if due_only:
        stmt = stmt.where(FollowUp.responded_at.is_(None), FollowUp.scheduled_at <= datetime.utcnow())
    return list((await db.execute(stmt)).scalars().all())


@router.post("/{followup_id}/respond", response_model=FollowUpOut)
async def respond_followup(
    followup_id: str,
    data: FollowUpRespond,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    fu = (await db.execute(select(FollowUp).where(FollowUp.id == followup_id))).scalar_one_or_none()
    if not fu:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    visit = (await db.execute(select(Visit).where(Visit.id == fu.visit_id))).scalar_one_or_none()
    if not visit or str(visit.doctor_id) != str(doctor.id):
        raise HTTPException(status_code=404, detail="Follow-up not found")

    fu.outcome = OutcomeEnum(data.outcome)
    fu.symptom_score = data.symptom_score
    fu.patient_notes = data.patient_notes
    fu.responded_at = datetime.utcnow()

    if data.outcome == "worsened" or (data.symptom_score is not None and data.symptom_score <= 3):
        fu.needs_escalation = True
        fu.escalation_reason = "Patient reported worsening / low symptom score"

    # Learning loop: index the completed case into this clinic's knowledge base.
    presc = (await db.execute(select(Prescription).where(Prescription.visit_id == visit.id))).scalar_one_or_none()
    if presc and not fu.indexed_to_vectordb:
        symptoms_text = symptoms_to_query(visit.symptoms_structured or {}) or (visit.chief_complaint or "")
        remedy_names = ", ".join(r.get("name", "") for r in (presc.remedies or []))
        if symptoms_text:
            index_clinic_case(
                clinic_id=str(doctor.id),
                case_id=str(visit.id),
                symptoms_text=symptoms_text,
                remedy=remedy_names,
                outcome=data.outcome,
            )
            fu.indexed_to_vectordb = True

    # Surveillance: assess the recovery trajectory and adaptively schedule the
    # next check-in (continues until recovery or the doctor closes the episode).
    assessment = await assess_and_advance(db, visit)

    await record_event(
        db, event_type="FOLLOWUP_OUTCOME_RECORDED",
        doctor_id=str(doctor.id), patient_id=str(fu.patient_id), visit_id=str(fu.visit_id),
        payload={"outcome": data.outcome, "symptom_score": data.symptom_score,
                 "escalation": fu.needs_escalation,
                 "trend": assessment.trend, "anomaly": assessment.anomaly,
                 "recovered": assessment.recovered},
    )
    await db.commit()
    await db.refresh(fu)
    return fu
