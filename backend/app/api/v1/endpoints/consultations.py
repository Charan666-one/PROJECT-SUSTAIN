"""
Consultation endpoints — RAG recommendation + clarification + red flag
"""
from fastapi import APIRouter, Depends, HTTPException
from app.rag.pipeline.rag_engine import RAGEngine
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()

@router.post("/{visit_id}/recommend")
async def get_recommendation(visit_id: str, symptoms: dict, doctor=Depends(get_current_doctor)):
    """
    Main RAG endpoint:
    1. Accepts structured symptoms
    2. Runs red flag scan
    3. Retrieves from all three knowledge sources
    4. Returns recommendation with confidence + citations
    Requires doctor to explicitly approve before saving to record
    """
    engine = RAGEngine(doctor_id=str(doctor.id), clinic_id=str(doctor.clinic_id))
    result = await engine.generate_recommendation(symptoms=symptoms, patient_context={})
    return result

@router.post("/{visit_id}/approve")
async def approve_recommendation(visit_id: str, approved_prescription: dict, doctor=Depends(get_current_doctor)):
    """
    Doctor explicitly approves (and optionally modifies) the AI recommendation.
    Creates the legal audit trail entry.
    """
    # Save approved prescription + digital signature + timestamp
    pass

@router.post("/{visit_id}/clarify")
async def get_clarifying_questions(visit_id: str, partial_symptoms: dict, doctor=Depends(get_current_doctor)):
    """
    Returns targeted clarifying questions based on symptom gaps
    (e.g., missing modalities, mental-emotional picture)
    """
    pass
