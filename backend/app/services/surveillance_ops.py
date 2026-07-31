"""
DB-aware surveillance operations that sit on top of the pure analyzer.

Turns a visit's follow-up history into a recovery assessment, persists the
current trend/anomaly on the visit, and — crucially — keeps surveillance alive
by adaptively scheduling the next check-in until the patient recovers or the
doctor closes the episode.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical.visit import Visit
from app.models.clinical.followup import FollowUp, FollowUpType
from app.services.surveillance import analyze_recovery, Point, RecoveryAssessment, WATCH, URGENT


async def _followups(db: AsyncSession, visit_id) -> List[FollowUp]:
    return list((await db.execute(
        select(FollowUp).where(FollowUp.visit_id == visit_id).order_by(FollowUp.scheduled_at)
    )).scalars().all())


def _points(visit: Visit, followups: List[FollowUp]) -> List[Point]:
    base = visit.completed_at or visit.doctor_approved_at
    # Chronological by when the patient actually reported, so that when several
    # check-ins land on the same day the true "latest" report wins.
    responded = sorted((f for f in followups if f.responded_at is not None), key=lambda f: f.responded_at)
    points: List[Point] = []
    for i, fu in enumerate(responded):
        day = max(0, (fu.responded_at - base).days) if base is not None else i
        outcome = getattr(fu.outcome, "value", fu.outcome) or "not_reported"
        points.append(Point(day=day, score=fu.symptom_score, outcome=outcome))
    return points


async def assess_visit(db: AsyncSession, visit: Visit) -> RecoveryAssessment:
    """Read-only assessment of a visit's current recovery state."""
    fus = await _followups(db, visit.id)
    return analyze_recovery(_points(visit, fus))


async def assess_and_advance(db: AsyncSession, visit: Visit) -> RecoveryAssessment:
    """
    Assess, persist trend/anomaly on the visit, and adaptively schedule the next
    check-in so surveillance continues until recovery. Caller commits.
    """
    fus = await _followups(db, visit.id)
    assessment = analyze_recovery(_points(visit, fus))

    visit.recovery_trend = assessment.trend
    visit.recovery_anomaly = assessment.anomaly

    if assessment.recovered:
        visit.surveillance_status = "recovered"
        return assessment

    if visit.surveillance_status not in (None, "active"):
        return assessment  # doctor already closed it

    now = datetime.utcnow()
    has_future_pending = any(f.responded_at is None and f.scheduled_at > now for f in fus)
    has_pending_custom = any(f.responded_at is None and f.followup_type == FollowUpType.custom for f in fus)
    concerning = assessment.severity in (WATCH, URGENT)

    # Keep surveillance alive if nothing else is queued; OR insert an EARLIER
    # concerned check-in when the trajectory looks worrying.
    should_schedule = assessment.next_check_days is not None and (
        not has_future_pending or (concerning and not has_pending_custom)
    )
    if should_schedule:
        db.add(FollowUp(
            visit_id=visit.id,
            patient_id=visit.patient_id,
            followup_type=FollowUpType.custom,
            scheduled_at=now + timedelta(days=assessment.next_check_days),
        ))

    return assessment
