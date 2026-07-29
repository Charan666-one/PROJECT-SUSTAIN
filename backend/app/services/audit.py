"""
Audit service — writes tamper-evident, append-only clinical decision events.

Each event stores a sha256 signature over (prev_hash + event payload), forming a
hash chain so any later tampering with an earlier row is detectable.
"""
from __future__ import annotations
import hashlib
import json
from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.admin.audit_log import AuditLog


def _hash(prev_hash: str, event_type: str, payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(f"{prev_hash}|{event_type}|{body}".encode("utf-8")).hexdigest()


async def record_event(
    db: AsyncSession,
    *,
    event_type: str,
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    visit_id: Optional[str] = None,
    payload: Optional[dict] = None,
) -> AuditLog:
    payload = payload or {}
    last = (
        await db.execute(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(1))
    ).scalar_one_or_none()
    prev_hash = last.signature if last else "GENESIS"
    signature = _hash(prev_hash, event_type, payload)

    entry = AuditLog(
        event_type=event_type,
        doctor_id=doctor_id,
        patient_id=patient_id,
        visit_id=visit_id,
        payload=payload,
        prev_hash=prev_hash,
        signature=signature,
    )
    db.add(entry)
    await db.flush()
    return entry
