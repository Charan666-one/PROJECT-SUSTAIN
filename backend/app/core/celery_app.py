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
    # One task drains all due check-ins (fixed Day 3/7/30 + adaptive surveillance).
    "dispatch-due-checkins": {
        "task": "app.services.followup.tasks.dispatch_due_checkins",
        "schedule": 900.0,   # every 15 minutes
    },
    "analytics-daily": {
        "task": "app.services.analytics.tasks.refresh_clinic_dashboard",
        "schedule": 86400.0,
    },
}
