"""
WhatsApp Business API — prescription delivery + follow-up messages
"""
import httpx
from app.core.config import settings

class WhatsAppService:
    BASE_URL = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"
    HEADERS  = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type":  "application/json",
    }

    async def send_prescription(self, phone: str, patient_name: str, pdf_url: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "document",
            "document": {
                "link":     pdf_url,
                "caption":  f"Dear {patient_name}, please find your prescription attached. Follow the instructions carefully and contact us if you have any concerns.",
                "filename": "prescription.pdf",
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.BASE_URL, json=payload, headers=self.HEADERS)
            return resp.json()

    async def send_followup_checkin(self, phone: str, patient_name: str, day: int):
        messages = {
            3:  f"Hi {patient_name}, this is a check-in from your clinic. How are you feeling after starting your treatment? Please reply: 1-Much better, 2-Slightly better, 3-No change, 4-Worse",
            7:  f"Hi {patient_name}, it has been a week since your last visit. How is your progress? Please reply 1-4 or call us for your follow-up appointment.",
            30: f"Hi {patient_name}, we are checking in after your treatment last month. How are you feeling overall? Your feedback helps us provide better care.",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to":   phone,
            "type": "text",
            "text": {"body": messages.get(day, f"Hi {patient_name}, checking in from your clinic.")},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.BASE_URL, json=payload, headers=self.HEADERS)
            return resp.json()
