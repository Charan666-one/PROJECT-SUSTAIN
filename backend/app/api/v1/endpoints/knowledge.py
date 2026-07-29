"""Knowledge base — doctor adds private notes/protocols that feed their RAG."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.admin.doctor import Doctor
from app.rag.indexer import index_doctor_note
from app.rag.embeddings import is_fallback
from app.rag.vector_store import VectorStore
from app.core.config import settings
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


class DoctorNoteIn(BaseModel):
    title: str
    text: str


@router.post("/notes")
async def add_note(data: DoctorNoteIn, doctor: Doctor = Depends(get_current_doctor)):
    doc_id = index_doctor_note(str(doctor.id), data.title, data.text)
    return {"doc_id": doc_id, "indexed": True}


@router.get("/status")
async def kb_status(doctor: Doctor = Depends(get_current_doctor)):
    """Diagnostics: which retrieval backend/embedder is active."""
    store = VectorStore(settings.QDRANT_COLLECTION_MATERIA_MEDICA)
    return {
        "vector_backend": store.backend,
        "embeddings": "hashing_fallback" if is_fallback() else settings.EMBEDDING_MODEL,
    }
