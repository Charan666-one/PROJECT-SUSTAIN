from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "homoeo_cdss",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.services.followup.tasks",
        "app.services.notification.tasks",
        "app.services.analytics.tasks",
    ]
)

celery_app.conf.beat_schedule = {
    "followup-day3":   {"task": "app.services.followup.tasks.send_day3_checkin",        "schedule": 3600.0},
    "followup-day7":   {"task": "app.services.followup.tasks.send_day7_reminder",        "schedule": 3600.0},
    "followup-day30":  {"task": "app.services.followup.tasks.send_day30_outcome_survey", "schedule": 3600.0},
    "analytics-daily": {"task": "app.services.analytics.tasks.refresh_clinic_dashboard", "schedule": 86400.0},
}
