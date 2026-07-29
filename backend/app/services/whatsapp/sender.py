"""
WhatsApp Business API — prescription delivery + follow-up messages.

Module-level ``send_prescription`` / ``send_followup`` are the API entry points;
they no-op gracefully (returning ``{"sent": False, ...}``) when WhatsApp isn't
configured, so the rest of the workflow still works in dev/pilot.
"""
import httpx
from app.core.config import settings

FOLLOWUP_MESSAGES = {
    3: "Hi {name}, this is a check-in from your clinic. How are you feeling after starting your treatment? Reply: 1-Much better, 2-Slightly better, 3-No change, 4-Worse",
    7: "Hi {name}, it has been a week since your last visit. How is your progress? Reply 1-4 or call us for your follow-up appointment.",
    30: "Hi {name}, we are checking in after your treatment last month. How are you feeling overall? Your feedback helps us provide better care.",
}


class WhatsAppService:
    def __init__(self):
        self.url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_text(self, phone: str, body: str) -> dict:
        payload = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": body}}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(self.url, json=payload, headers=self.headers)
            return resp.json()


def _configured() -> bool:
    return bool(settings.WHATSAPP_API_URL and settings.WHATSAPP_PHONE_ID and settings.WHATSAPP_ACCESS_TOKEN)


def _format_prescription(prescription, doctor) -> str:
    lines = [f"Dear patient, your prescription from Dr. {doctor.full_name}:", ""]
    for r in (prescription.remedies or []):
        lines.append(
            f"• {r.get('name','')} {r.get('potency','')} — {r.get('dosage','')}, "
            f"{r.get('frequency','')} for {r.get('duration','')}".strip()
        )
    if prescription.dietary_advice:
        lines.append(f"\nDiet: {prescription.dietary_advice}")
    if prescription.precautions:
        lines.append(f"Precautions: {prescription.precautions}")
    lines.append("\nPlease follow the instructions and contact the clinic with any concerns.")
    return "\n".join(lines)


async def send_prescription(phone: str, prescription, doctor) -> dict:
    body = _format_prescription(prescription, doctor)
    if not _configured():
        return {"sent": False, "reason": "whatsapp_not_configured", "preview": body}
    try:
        resp = await WhatsAppService().send_text(phone, body)
        return {"sent": True, "response": resp}
    except Exception as exc:  # noqa: BLE001
        return {"sent": False, "reason": str(exc)}


async def send_followup(phone: str, patient_name: str, day: int) -> dict:
    if not _configured():
        return {"sent": False, "reason": "whatsapp_not_configured"}
    body = FOLLOWUP_MESSAGES.get(day, "Hi {name}, checking in from your clinic.").format(name=patient_name)
    try:
        resp = await WhatsAppService().send_text(phone, body)
        return {"sent": True, "response": resp}
    except Exception as exc:  # noqa: BLE001
        return {"sent": False, "reason": str(exc)}
