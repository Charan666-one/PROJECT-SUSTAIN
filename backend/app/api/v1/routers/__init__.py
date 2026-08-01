from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, patients, visits, consultations,
    prescriptions, followups, analytics, voice, knowledge, surveillance,
    search, audit
)

api_router = APIRouter()
api_router.include_router(auth.router,          prefix="/auth",          tags=["Authentication"])
api_router.include_router(patients.router,      prefix="/patients",      tags=["Patients"])
api_router.include_router(visits.router,        prefix="/visits",        tags=["Visits"])
api_router.include_router(consultations.router, prefix="/consultations", tags=["Consultations"])
api_router.include_router(prescriptions.router, prefix="/prescriptions", tags=["Prescriptions"])
api_router.include_router(followups.router,     prefix="/followups",     tags=["Follow-Ups"])
api_router.include_router(surveillance.router,  prefix="/surveillance",  tags=["Recovery Surveillance"])
api_router.include_router(search.router,        prefix="/search",        tags=["Search"])
api_router.include_router(audit.router,         prefix="/audit",         tags=["Audit Log"])
api_router.include_router(analytics.router,     prefix="/analytics",     tags=["Analytics"])
api_router.include_router(voice.router,         prefix="/voice",         tags=["Voice"])
api_router.include_router(knowledge.router,     prefix="/knowledge",     tags=["Knowledge Base"])
