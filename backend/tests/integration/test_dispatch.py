"""
Surveillance check-in dispatch: due check-ins are sent once and only once.
Requires Postgres; skips if unavailable.
"""
from datetime import datetime, timedelta
import pytest
import httpx
from sqlalchemy import select, update


@pytest.mark.asyncio
async def test_due_checkins_dispatched_once():
    from app.core.database import engine, Base, AsyncSessionLocal
    from app.main import app as fastapi_app
    from app.models.clinical.followup import FollowUp
    from app.services.followup.dispatch import send_due_checkins

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Postgres not available: {exc}")

    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        await c.post("/api/v1/auth/register", json={"full_name": "Dr D", "email": "d@c.in",
                     "password": "password123", "clinic_name": "D Clinic"})
        tok = (await c.post("/api/v1/auth/login-json",
                            json={"email": "d@c.in", "password": "password123"})).json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        pid = (await c.post("/api/v1/patients", headers=h, json={"full_name": "P", "date_of_birth": "1990-01-01",
               "gender": "male", "phone": "9800000001", "consent_given": True})).json()["id"]
        vid = (await c.post("/api/v1/visits", headers=h, json={"patient_id": pid})).json()["id"]
        await c.post(f"/api/v1/consultations/{vid}/recommend", headers=h, json={"chief_complaint": "cough"})
        await c.post(f"/api/v1/consultations/{vid}/approve", headers=h,
                     json={"remedies": [{"name": "Bryonia", "potency": "30C"}]})

    # Approval scheduled Day 3/7/30 in the future -> nothing due yet.
    assert (await send_due_checkins())["processed"] == 0

    # Backdate one check-in so it is now due.
    async with AsyncSessionLocal() as db:
        fu_id = (await db.execute(select(FollowUp.id).limit(1))).scalar_one()
        await db.execute(update(FollowUp).where(FollowUp.id == fu_id)
                         .values(scheduled_at=datetime.utcnow() - timedelta(days=1)))
        await db.commit()

    first = await send_due_checkins()
    assert first["processed"] >= 1          # the due one is picked up
    second = await send_due_checkins()
    assert second["processed"] == 0         # idempotent: already marked sent

    await engine.dispose()
