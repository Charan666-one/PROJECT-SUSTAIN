"""Clinic analytics — the retention hook: outcomes, remedies, volume."""
from datetime import datetime, timedelta
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.visit import Visit
from app.models.clinical.patient import Patient
from app.models.clinical.prescription import Prescription
from app.models.clinical.followup import FollowUp, OutcomeEnum
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db), doctor: Doctor = Depends(get_current_doctor)):
    total_patients = (await db.execute(select(func.count(Patient.id)))).scalar() or 0
    total_visits = (await db.execute(
        select(func.count(Visit.id)).where(Visit.doctor_id == doctor.id)
    )).scalar() or 0

    month_ago = datetime.utcnow() - timedelta(days=30)
    visits_30d = (await db.execute(
        select(func.count(Visit.id)).where(Visit.doctor_id == doctor.id, Visit.scheduled_at >= month_ago)
    )).scalar() or 0

    # Outcome distribution (from responded follow-ups on this doctor's visits).
    outcomes = (await db.execute(
        select(FollowUp.outcome, func.count(FollowUp.id))
        .join(Visit, Visit.id == FollowUp.visit_id)
        .where(Visit.doctor_id == doctor.id, FollowUp.responded_at.isnot(None))
        .group_by(FollowUp.outcome)
    )).all()
    outcome_dist = {getattr(o, "value", str(o)): c for o, c in outcomes}
    reported = sum(outcome_dist.values())
    improved = outcome_dist.get(OutcomeEnum.improved.value, 0)
    improvement_rate = round(100 * improved / reported, 1) if reported else None

    # Top remedies prescribed.
    presc_rows = (await db.execute(
        select(Prescription.remedies).where(Prescription.doctor_id == doctor.id)
    )).scalars().all()
    remedy_counter: Counter = Counter()
    for remedies in presc_rows:
        for r in (remedies or []):
            if r.get("name"):
                remedy_counter[r["name"]] += 1

    pending_followups = (await db.execute(
        select(func.count(FollowUp.id))
        .join(Visit, Visit.id == FollowUp.visit_id)
        .where(Visit.doctor_id == doctor.id, FollowUp.responded_at.is_(None),
               FollowUp.scheduled_at <= datetime.utcnow())
    )).scalar() or 0

    return {
        "total_patients": total_patients,
        "total_visits": total_visits,
        "visits_last_30d": visits_30d,
        "outcome_distribution": outcome_dist,
        "improvement_rate_pct": improvement_rate,
        "top_remedies": remedy_counter.most_common(5),
        "pending_followups": pending_followups,
    }
