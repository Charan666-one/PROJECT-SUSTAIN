"""
Central model registry.

Importing every model here ensures they are all registered on
``Base.metadata`` before ``init_db()`` calls ``create_all`` — without this,
no tables are created and relationships fail to resolve.
"""
from app.models.admin.doctor import Doctor
from app.models.admin.audit_log import AuditLog
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit
from app.models.clinical.prescription import Prescription
from app.models.clinical.followup import FollowUp
from app.models.clinical.intake_form import PatientIntakeForm

__all__ = [
    "Doctor",
    "AuditLog",
    "Patient",
    "Visit",
    "Prescription",
    "FollowUp",
    "PatientIntakeForm",
]
