"""Notification tasks (placeholder targets referenced by the Celery app)."""
from app.core.celery_app import celery_app


@celery_app.task(name="app.services.notification.tasks.send_appointment_reminder")
def send_appointment_reminder(visit_id: str):
    # Wired in when appointment reminders are enabled for the pilot.
    return {"visit_id": visit_id, "status": "noop"}
