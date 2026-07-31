"""
Consultation endpoints — the core clinical workflow.

recommend → (optional) clarify → doctor approve.
Every AI output is stored on the visit and logged; nothing is prescribed until
the doctor explicitly approves (which creates the prescription + follow-ups +
the immutable audit trail).
"""
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin.doctor import Doctor
from app.models.clinical.patient import Patient
from app.models.clinical.visit import Visit, VisitStatus
from app.models.clinical.prescription import Prescription
from app.models.clinical.followup import FollowUp, FollowUpType
from app.schemas.visit import SymptomInput
from app.schemas.consultation import RecommendationOut, ClarifyOut, ApprovalIn
from app.schemas.prescription import PrescriptionOut
from app.rag.pipeline.rag_engine import RAGEngine
from app.services.clarify import generate_clarifying_questions
from app.services.audit import record_event
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()

# Day 3 / 7 / 30 follow-up schedule (feeds outcomes back into the knowledge base).
FOLLOWUP_SCHEDULE = [(FollowUpType.day_3, 3), (FollowUpType.day_7, 7), (FollowUpType.day_30, 30)]


async def _load_visit(db: AsyncSession, visit_id: str, doctor: Doctor) -> Visit:
    visit = (await db.execute(select(Visit).where(Visit.id == visit_id))).scalar_one_or_none()
    if not visit or str(visit.doctor_id) != str(doctor.id):
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.post("/{visit_id}/recommend", response_model=RecommendationOut)
async def get_recommendation(
    visit_id: str,
    symptoms: SymptomInput,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    visit = await _load_visit(db, visit_id, doctor)
    patient = (await db.execute(select(Patient).where(Patient.id == visit.patient_id))).scalar_one_or_none()

    symptom_dict = symptoms.model_dump()
    patient_context = {}
    if patient:
        age = None
        if patient.date_of_birth:
            age = (datetime.utcnow().date() - patient.date_of_birth).days // 365
        patient_context = {"age": age, "gender": getattr(patient.gender, "value", patient.gender)}

    engine = RAGEngine(doctor_id=str(doctor.id), clinic_id=str(doctor.id))
    result = await engine.generate_recommendation(symptoms=symptom_dict, patient_context=patient_context)

    # Persist AI output on the visit (not a prescription — pending doctor approval).
    visit.symptoms_structured = symptom_dict
    if symptoms.chief_complaint:
        visit.chief_complaint = symptoms.chief_complaint
    visit.ai_recommendation = result
    visit.ai_confidence_score = result["confidence"]
    visit.ai_sources_cited = result["sources"]
    visit.red_flags_detected = result["red_flags"]

    await record_event(
        db, event_type="AI_RECOMMENDATION_GENERATED",
        doctor_id=str(doctor.id), patient_id=str(visit.patient_id), visit_id=str(visit.id),
        payload={"confidence": result["confidence"], "red_flags": result["red_flags"]},
    )
    await db.commit()
    return result


@router.post("/{visit_id}/re-recommend", response_model=RecommendationOut)
async def re_recommend(
    visit_id: str,
    symptoms: SymptomInput,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    """
    Follow-up remedy suggestion during the recovery period (e.g. after a plateau
    or relapse the surveillance engine flags). Runs the RAG engine on the updated
    symptom picture — decision support only; the doctor starts a new visit to
    actually prescribe.
    """
    visit = await _load_visit(db, visit_id, doctor)
    engine = RAGEngine(doctor_id=str(doctor.id), clinic_id=str(doctor.id))
    result = await engine.generate_recommendation(symptoms=symptoms.model_dump(), patient_context={})
    await record_event(
        db, event_type="AI_RE_RECOMMENDATION_GENERATED",
        doctor_id=str(doctor.id), patient_id=str(visit.patient_id), visit_id=str(visit.id),
        payload={"confidence": result["confidence"]},
    )
    await db.commit()
    return result


@router.post("/{visit_id}/clarify", response_model=ClarifyOut)
async def get_clarifying_questions(
    visit_id: str,
    symptoms: SymptomInput,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    await _load_visit(db, visit_id, doctor)
    return ClarifyOut(questions=generate_clarifying_questions(symptoms.model_dump()))


@router.post("/{visit_id}/approve", response_model=PrescriptionOut)
async def approve_recommendation(
    visit_id: str,
    approval: ApprovalIn,
    db: AsyncSession = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    visit = await _load_visit(db, visit_id, doctor)
    if visit.doctor_approved:
        raise HTTPException(status_code=409, detail="This visit has already been approved")
    if not approval.remedies:
        raise HTTPException(status_code=400, detail="At least one remedy is required to approve")

    # Block approval if an unaddressed URGENT red flag is present.
    urgent = [f for f in (visit.red_flags_detected or []) if f.get("severity") == "URGENT"]
    if urgent and not approval.red_flag_dismissed:
        raise HTTPException(
            status_code=428,
            detail="Urgent red flag(s) present. Acknowledge (red_flag_dismissed=true) before approving.",
        )

    now = datetime.utcnow()
    signature = hashlib.sha256(
        f"{doctor.id}|{visit.id}|{approval.remedies}|{now.isoformat()}".encode()
    ).hexdigest()

    prescription = Prescription(
        visit_id=visit.id,
        doctor_id=doctor.id,
        remedies=approval.remedies,
        dietary_advice=approval.dietary_advice,
        lifestyle_advice=approval.lifestyle_advice,
        precautions=approval.precautions,
        notes=approval.notes,
    )
    db.add(prescription)

    visit.doctor_notes = approval.doctor_notes
    visit.doctor_approved = True
    visit.doctor_approved_at = now
    visit.doctor_signature = signature
    visit.status = VisitStatus.completed
    visit.completed_at = now
    if urgent and approval.red_flag_dismissed:
        visit.red_flag_dismissed = True
        visit.red_flag_dismissed_by = doctor.id

    # Schedule Day 3 / 7 / 30 follow-ups.
    for ftype, days in FOLLOWUP_SCHEDULE:
        db.add(FollowUp(
            visit_id=visit.id, patient_id=visit.patient_id,
            followup_type=ftype, scheduled_at=now + timedelta(days=days),
        ))

    await record_event(
        db, event_type="PRESCRIPTION_APPROVED",
        doctor_id=str(doctor.id), patient_id=str(visit.patient_id), visit_id=str(visit.id),
        payload={"remedies": approval.remedies, "signature": signature,
                 "red_flag_dismissed": bool(urgent and approval.red_flag_dismissed)},
    )
    await db.commit()
    await db.refresh(prescription)
    return prescription
