"""
Indexer — writes clinic cases and doctor notes into the vector store so future
consultations retrieve them. This is the feedback loop that makes each clinic's
knowledge base compound over time.
"""
from __future__ import annotations
import uuid
from typing import Optional
from app.core.config import settings
from app.rag import embeddings
from app.rag.vector_store import VectorStore


def index_doctor_note(doctor_id: str, title: str, text: str, doc_id: Optional[str] = None) -> str:
    doc_id = doc_id or str(uuid.uuid4())
    store = VectorStore(settings.QDRANT_COLLECTION_DOCTOR_NOTES)
    store.upsert([{
        "id": doc_id,
        "vector": embeddings.embed(f"{title}\n{text}"),
        "payload": {"doc_id": doc_id, "doctor_id": str(doctor_id), "title": title, "text": text},
    }])
    return doc_id


def index_clinic_case(
    clinic_id: str,
    case_id: str,
    symptoms_text: str,
    remedy: str,
    outcome: str,
) -> str:
    """Called once a case reaches a recorded outcome (e.g. from a follow-up)."""
    store = VectorStore(settings.QDRANT_COLLECTION_CLINIC_CASES)
    store.upsert([{
        "id": str(case_id),
        "vector": embeddings.embed(symptoms_text),
        "payload": {
            "case_id": str(case_id),
            "clinic_id": str(clinic_id),
            "remedy": remedy,
            "outcome": outcome,
            "text": symptoms_text,
        },
    }])
    return str(case_id)
