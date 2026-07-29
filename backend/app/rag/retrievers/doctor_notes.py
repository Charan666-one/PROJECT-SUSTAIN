"""
Doctor notes retriever — the practitioner's OWN private notes / protocols.
Scoped by doctor_id so one doctor never sees another's private notes.
"""
from __future__ import annotations
from typing import List, Dict, Any
from app.core.config import settings
from app.rag import embeddings
from app.rag.vector_store import VectorStore
from app.rag.retrievers.base import symptoms_to_query


class DoctorNotesRetriever:
    def __init__(self, doctor_id: str):
        self.doctor_id = str(doctor_id)
        self.store = VectorStore(settings.QDRANT_COLLECTION_DOCTOR_NOTES)

    async def retrieve(self, symptoms: dict, top_k: int = 3) -> List[Dict[str, Any]]:
        query = symptoms_to_query(symptoms)
        if not query:
            return []
        vector = embeddings.embed(query)
        hits = self.store.search(vector, top_k=top_k, where={"doctor_id": self.doctor_id})
        return [
            {
                "doc_id": h["payload"].get("doc_id"),
                "title": h["payload"].get("title"),
                "text": h["payload"].get("text", ""),
                "score": round(h["score"], 4),
            }
            for h in hits
        ]
