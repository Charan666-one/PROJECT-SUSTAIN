"""
Celery tasks — daily clinic analytics refresh
"""
from app.core.celery_app import celery_app

@celery_app.task(name="app.services.analytics.tasks.refresh_clinic_dashboard")
def refresh_clinic_dashboard():
    """Recompute clinic analytics: patient retention, remedy trends, outcome rates"""
    pass
