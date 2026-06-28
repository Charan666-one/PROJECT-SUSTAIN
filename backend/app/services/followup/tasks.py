"""
Celery tasks — automated follow-up scheduling and execution
"""
from app.core.celery_app import celery_app
from app.services.whatsapp.sender import WhatsAppService
from datetime import datetime, timedelta

whatsapp = WhatsAppService()

@celery_app.task(name="app.services.followup.tasks.send_day3_checkin")
def send_day3_checkin():
    """Find all prescriptions from 3 days ago and send check-in"""
    # Query DB for prescriptions created 3 days ago with no day-3 followup sent
    # For each: send WhatsApp + mark followup as sent
    pass

@celery_app.task(name="app.services.followup.tasks.send_day7_reminder")
def send_day7_reminder():
    pass

@celery_app.task(name="app.services.followup.tasks.send_day30_outcome_survey")
def send_day30_outcome_survey():
    pass
