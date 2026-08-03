"""
Patient portal: the doctor<->patient loop and strict isolation.
Requires Postgres; skips if unavailable.
"""
import pytest
import httpx


@pytest.mark.asyncio
async def test_patient_portal_loop_and_isolation():
    from app.core.database import engine, Base
    from app.main import app as fa

    try:
        async with engine.begin() as c:
            await c.run_sync(Base.metadata.drop_all)
            await c.run_sync(Base.metadata.create_all)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Postgres not available: {exc}")

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=fa), base_url="http://x") as c:
        await c.post("/api/v1/auth/register", json={"full_name": "Dr K", "email": "k@c.in",
                     "password": "password123", "clinic_name": "K"})
        dh = {"Authorization": "Bearer " + (await c.post("/api/v1/auth/login-json",
              json={"email": "k@c.in", "password": "password123"})).json()["access_token"]}
        pid = (await c.post("/api/v1/patients", headers=dh, json={"full_name": "Sunita", "gender": "female",
               "phone": "9845012345", "consent_given": True})).json()["id"]
        code = (await c.get(f"/api/v1/patients/{pid}/access", headers=dh)).json()["access_code"]
        assert code and len(code) == 6

        vid = (await c.post("/api/v1/visits", headers=dh, json={"patient_id": pid})).json()["id"]
        await c.post(f"/api/v1/consultations/{vid}/recommend", headers=dh, json={"chief_complaint": "anxiety"})
        await c.post(f"/api/v1/consultations/{vid}/approve", headers=dh,
                     json={"remedies": [{"name": "Arsenicum Album", "potency": "30C"}]})

        # Patient logs in and sees only their (non-AI) data.
        ph = {"Authorization": "Bearer " + (await c.post("/api/v1/portal/auth/login",
              json={"phone": "9845012345", "access_code": code})).json()["access_token"]}
        dash = (await c.get("/api/v1/portal/dashboard", headers=ph)).json()
        assert dash["current_prescription"]["remedies"][0]["name"] == "Arsenicum Album"
        body = str(dash) + str((await c.get("/api/v1/portal/prescriptions", headers=ph)).json())
        assert "ai_recommendation" not in body and "red_flag" not in body and "evidence" not in body

        fus = (await c.get("/api/v1/portal/followups", headers=ph)).json()
        assert len(fus) == 3
        r = await c.post(f"/api/v1/portal/followups/{fus[0]['id']}/respond", headers=ph,
                         json={"status": "worse", "wellness": 2})
        assert r.status_code == 200

        # Doctor is notified via surveillance.
        surv = (await c.get("/api/v1/surveillance", headers=dh)).json()
        assert surv[0]["anomaly"] == "worsening"

        # Isolation both ways + wrong code.
        assert (await c.get("/api/v1/patients", headers=ph)).status_code == 401
        assert (await c.get("/api/v1/portal/me", headers=dh)).status_code == 401
        assert (await c.post("/api/v1/portal/auth/login",
                             json={"phone": "9845012345", "access_code": "000000"})).status_code == 401

    await engine.dispose()
