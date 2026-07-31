"""
Tenant isolation: patients belong to a clinic and never leak across clinics.
Requires Postgres (uses the app's real engine); skips if it can't connect.
"""
import pytest
import httpx


async def _signup(c: httpx.AsyncClient, email: str) -> dict:
    await c.post("/api/v1/auth/register", json={
        "full_name": f"Dr {email}", "email": email, "password": "password123", "clinic_name": email,
    })
    tok = (await c.post("/api/v1/auth/login-json",
                        json={"email": email, "password": "password123"})).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _patient(name: str, phone: str, gender: str) -> dict:
    return {"full_name": name, "date_of_birth": "1990-01-01", "gender": gender,
            "phone": phone, "consent_given": True}


@pytest.mark.asyncio
async def test_patients_are_isolated_per_clinic():
    from app.core.database import engine, Base
    from app.main import app as fastapi_app  # importing registers all models

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Postgres not available: {exc}")

    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        clinic_a = await _signup(c, "a@clinic.in")
        clinic_b = await _signup(c, "b@clinic.in")

        # Same phone number is allowed under BOTH clinics (per-clinic uniqueness).
        pa = await c.post("/api/v1/patients", headers=clinic_a, json=_patient("Pat A", "9800000001", "male"))
        pb = await c.post("/api/v1/patients", headers=clinic_b, json=_patient("Pat B", "9800000001", "female"))
        assert pa.status_code == 201, pa.text
        assert pb.status_code == 201, pb.text

        # Same phone twice in the SAME clinic is rejected.
        dup = await c.post("/api/v1/patients", headers=clinic_a, json=_patient("Dup", "9800000001", "male"))
        assert dup.status_code == 409

        # Each clinic sees only its own patients.
        list_a = (await c.get("/api/v1/patients", headers=clinic_a)).json()
        list_b = (await c.get("/api/v1/patients", headers=clinic_b)).json()
        assert [p["full_name"] for p in list_a] == ["Pat A"]
        assert [p["full_name"] for p in list_b] == ["Pat B"]

        # Cross-tenant reads and writes are blocked (404, not 403 — don't leak existence).
        a_pid = pa.json()["id"]
        assert (await c.get(f"/api/v1/patients/{a_pid}", headers=clinic_b)).status_code == 404
        assert (await c.patch(f"/api/v1/patients/{a_pid}", headers=clinic_b, json={"email": "x@y.z"})).status_code == 404
        assert (await c.post("/api/v1/visits", headers=clinic_b, json={"patient_id": a_pid})).status_code == 404

    await engine.dispose()
