"""
Audit / activity log — read the immutable clinical-decision trail and verify the
tamper-evident hash chain. Read-only; entries are written by services.audit.
"""
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.admin.audit_log import AuditLog
from app.services.audit import _hash
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()

# Human-readable labels for the activity timeline.
EVENT_LABELS = {
    "PATIENT_CREATED": "Registered patient",
    "AI_RECOMMENDATION_GENERATED": "Generated AI recommendation",
    "AI_RE_RECOMMENDATION_GENERATED": "Generated follow-up AI suggestion",
    "PRESCRIPTION_APPROVED": "Approved prescription",
    "PRESCRIPTION_SENT": "Sent prescription",
    "FOLLOWUP_OUTCOME_RECORDED": "Recorded follow-up outcome",
    "SURVEILLANCE_EPISODE_CLOSED": "Closed surveillance episode",
}


class AuditEntry(BaseModel):
    id: str
    event_type: str
    label: str
    patient_id: str | None = None
    visit_id: str | None = None
    payload: dict = {}
    created_at: str


@router.get("", response_model=List[AuditEntry])
async def list_audit(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    rows = list((await db.execute(
        select(AuditLog).where(AuditLog.doctor_id == doctor.id)
        .order_by(desc(AuditLog.created_at)).limit(min(limit, 500))
    )).scalars().all())
    return [AuditEntry(
        id=str(r.id), event_type=r.event_type,
        label=EVENT_LABELS.get(r.event_type, r.event_type.replace("_", " ").title()),
        patient_id=str(r.patient_id) if r.patient_id else None,
        visit_id=str(r.visit_id) if r.visit_id else None,
        payload=r.payload or {}, created_at=r.created_at.isoformat() if r.created_at else "",
    ) for r in rows]


@router.get("/verify")
async def verify_chain(db: AsyncSession = Depends(get_db), doctor: Doctor = Depends(get_current_doctor)):
    """Recompute the global hash chain and report the first break, if any."""
    rows = list((await db.execute(select(AuditLog).order_by(AuditLog.created_at))).scalars().all())
    prev = "GENESIS"
    for i, r in enumerate(rows):
        expected = _hash(prev, r.event_type, r.payload or {})
        if expected != r.signature or (r.prev_hash or "GENESIS") != prev:
            return {"ok": False, "count": len(rows), "first_broken_index": i}
        prev = r.signature
    return {"ok": True, "count": len(rows)}
