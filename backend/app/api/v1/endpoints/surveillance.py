"""
Recovery Surveillance dashboard — the clinic's active watchlist.

Shows every patient still under surveillance, their recovery trajectory, any
anomaly flagged by the engine, and the recommended next action. The doctor acts;
the engine only surfaces and suggests.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.visit import Visit
from app.models.clinical.patient import Patient
from app.models.clinical.followup import FollowUp
from app.schemas.surveillance import SurveillanceEpisode
from app.services.surveillance_ops import assess_visit
from app.services.audit import record_event
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()

SEVERITY_RANK = {"urgent": 0, "watch": 1, "info": 2}


@router.get("", response_model=List[SurveillanceEpisode])
async def list_surveillance(
    include_recovered: bool = False,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    stmt = (
        select(Visit).where(Visit.doctor_id == doctor.id, Visit.doctor_approved == True)  # noqa: E712
    )
    if not include_recovered:
        stmt = stmt.where(Visit.surveillance_status == "active")
    visits = list((await db.execute(stmt)).scalars().all())

    episodes: List[SurveillanceEpisode] = []
    for v in visits:
        patient = (await db.execute(select(Patient).where(Patient.id == v.patient_id))).scalar_one_or_none()
        a = await assess_visit(db, v)
        next_at = (await db.execute(
            select(FollowUp.scheduled_at)
            .where(FollowUp.visit_id == v.id, FollowUp.responded_at.is_(None))
            .order_by(FollowUp.scheduled_at).limit(1)
        )).scalar_one_or_none()
        episodes.append(SurveillanceEpisode(
            visit_id=v.id, patient_id=v.patient_id,
            patient_name=patient.full_name if patient else "Unknown",
            chief_complaint=v.chief_complaint,
            surveillance_status=v.surveillance_status or "active",
            trend=a.trend, anomaly=a.anomaly, severity=a.severity, recovered=a.recovered,
            days_under_surveillance=a.days_under_surveillance, latest_score=a.latest_score,
            recommended_action=a.recommended_action, suggest_re_evaluation=a.suggest_re_evaluation,
            rationale=a.rationale, next_check_at=next_at,
        ))

    # Most urgent first, then longest under surveillance.
    episodes.sort(key=lambda e: (SEVERITY_RANK.get(e.severity, 3), -e.days_under_surveillance))
    return episodes


@router.post("/{visit_id}/close", response_model=SurveillanceEpisode)
async def close_episode(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    visit = (await db.execute(select(Visit).where(Visit.id == visit_id))).scalar_one_or_none()
    if not visit or str(visit.doctor_id) != str(doctor.id):
        raise HTTPException(status_code=404, detail="Episode not found")

    a = await assess_visit(db, visit)
    visit.surveillance_status = "recovered" if a.recovered else "closed"
    await record_event(
        db, event_type="SURVEILLANCE_EPISODE_CLOSED",
        doctor_id=str(doctor.id), patient_id=str(visit.patient_id), visit_id=str(visit.id),
        payload={"status": visit.surveillance_status, "trend": a.trend, "anomaly": a.anomaly},
    )
    await db.commit()

    patient = (await db.execute(select(Patient).where(Patient.id == visit.patient_id))).scalar_one_or_none()
    return SurveillanceEpisode(
        visit_id=visit.id, patient_id=visit.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        chief_complaint=visit.chief_complaint, surveillance_status=visit.surveillance_status,
        trend=a.trend, anomaly=a.anomaly, severity=a.severity, recovered=a.recovered,
        days_under_surveillance=a.days_under_surveillance, latest_score=a.latest_score,
        recommended_action=a.recommended_action, suggest_re_evaluation=a.suggest_re_evaluation,
        rationale=a.rationale, next_check_at=None,
    )
