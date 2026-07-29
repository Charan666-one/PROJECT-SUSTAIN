"""
Clinic case retriever — this clinic's OWN past cases + recorded outcomes.
Scoped by doctor/clinic so each practice learns from its own results
(this is the product's retention moat).
"""
from __future__ import annotations
from typing import List, Dict, Any
from app.core.config import settings
from app.rag import embeddings
from app.rag.vector_store import VectorStore
from app.rag.retrievers.base import symptoms_to_query


class ClinicCaseRetriever:
    def __init__(self, clinic_id: str):
        self.clinic_id = str(clinic_id)
        self.store = VectorStore(settings.QDRANT_COLLECTION_CLINIC_CASES)

    async def retrieve(self, symptoms: dict, top_k: int = 3) -> List[Dict[str, Any]]:
        query = symptoms_to_query(symptoms)
        if not query:
            return []
        vector = embeddings.embed(query)
        hits = self.store.search(vector, top_k=top_k, where={"clinic_id": self.clinic_id})
        return [
            {
                "case_id": h["payload"].get("case_id"),
                "remedy": h["payload"].get("remedy"),
                "outcome": h["payload"].get("outcome"),
                "text": h["payload"].get("text", ""),
                "score": round(h["score"], 4),
            }
            for h in hits
        ]
