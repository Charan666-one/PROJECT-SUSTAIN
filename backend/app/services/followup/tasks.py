"""
Celery tasks — automated surveillance check-in delivery.

The real work lives in the pure-async ``send_due_checkins`` (dispatch.py); these
are thin Celery wrappers so the same logic runs from beat OR a one-off script.
"""
import asyncio
from app.core.celery_app import celery_app
from app.services.followup.dispatch import send_due_checkins


@celery_app.task(name="app.services.followup.tasks.dispatch_due_checkins")
def dispatch_due_checkins():
    """Send every surveillance check-in that has fallen due (Day 3/7/30 + adaptive)."""
    return asyncio.run(send_due_checkins())
