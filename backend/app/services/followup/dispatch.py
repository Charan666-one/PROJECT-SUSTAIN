"""
Send due surveillance check-ins over WhatsApp.

This is the outbound half of Recovery Surveillance: whatever check-ins the
adaptive scheduler has queued (fixed Day 3/7/30 or adaptive custom ones) get
sent to the patient when they fall due. Pure async so it can run from a Celery
beat task OR a one-off script (scripts/send_checkins.py) with no broker.

Delivery is best-effort and idempotent: each due follow-up is marked ``sent_at``
once processed so it is never sent twice. WhatsApp itself no-ops gracefully when
unconfigured (returns delivered=0), which is fine for dev/pilot.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import DATABASE_URL
from app.models.clinical.followup import FollowUp, FollowUpType
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit
from app.services.whatsapp.sender import send_followup

_NOMINAL_DAY = {FollowUpType.day_3: 3, FollowUpType.day_7: 7, FollowUpType.day_30: 30}


async def send_due_checkins(now: Optional[datetime] = None) -> dict:
    now = now or datetime.utcnow()
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    processed = delivered = 0
    try:
        async with Session() as db:
            rows = (await db.execute(
                select(FollowUp, Patient)
                .join(Patient, Patient.id == FollowUp.patient_id)
                .join(Visit, Visit.id == FollowUp.visit_id)
                .where(
                    FollowUp.responded_at.is_(None),
                    FollowUp.sent_at.is_(None),
                    FollowUp.scheduled_at <= now,
                    # Don't keep pinging patients whose episode is already closed.
                    or_(Visit.surveillance_status.is_(None), Visit.surveillance_status == "active"),
                )
            )).all()

            for fu, patient in rows:
                day = _NOMINAL_DAY.get(fu.followup_type, 0)
                result = await send_followup(patient.phone, patient.full_name, day)
                fu.sent_at = now
                processed += 1
                if result.get("sent"):
                    delivered += 1

            if processed:
                await db.commit()
    finally:
        await engine.dispose()

    return {"processed": processed, "delivered": delivered}
