"""
Materia medica retriever — shared, clinic-agnostic homeopathic reference corpus
(public-domain classics: Boericke, Kent, Clarke, ...).
"""
from __future__ import annotations
from typing import List, Dict, Any
from app.core.config import settings
from app.rag import embeddings
from app.rag.vector_store import VectorStore
from app.rag.retrievers.base import symptoms_to_query


class MateriaMedicaRetriever:
    def __init__(self):
        self.store = VectorStore(settings.QDRANT_COLLECTION_MATERIA_MEDICA)

    async def retrieve(self, symptoms: dict, top_k: int = 5) -> List[Dict[str, Any]]:
        query = symptoms_to_query(symptoms)
        if not query:
            return []
        vector = embeddings.embed(query)
        hits = self.store.search(vector, top_k=top_k)
        return [
            {
                "source": h["payload"].get("source", "materia_medica"),
                "remedy": h["payload"].get("remedy"),
                "text": h["payload"].get("text", ""),
                "score": round(h["score"], 4),
            }
            for h in hits
        ]
