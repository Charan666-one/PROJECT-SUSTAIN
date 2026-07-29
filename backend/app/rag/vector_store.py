"""
Vector store abstraction.

Primary backend: Qdrant (as configured in docker-compose).
Fallback backend: a local JSON-backed in-memory store with cosine search, so the
whole RAG pipeline runs on a laptop / in CI without Qdrant running.

The interface is intentionally tiny: ``upsert`` and ``search``.
"""
from __future__ import annotations
import json
import os
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings

_LOCAL_DIR = Path(os.environ.get("VECTOR_STORE_DIR", "knowledge_base/_index"))


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class VectorStore:
    """Thin wrapper that prefers Qdrant and falls back to a local file store."""

    def __init__(self, collection: str):
        self.collection = collection
        self._client = None
        self._backend = "local"
        self._connect()

    def _connect(self):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models as qmodels

            client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=2.0)
            existing = {c.name for c in client.get_collections().collections}
            if self.collection not in existing:
                client.create_collection(
                    collection_name=self.collection,
                    vectors_config=qmodels.VectorParams(
                        size=settings.EMBEDDING_DIM, distance=qmodels.Distance.COSINE
                    ),
                )
            self._client = client
            self._backend = "qdrant"
        except Exception:
            self._backend = "local"

    # ----- local file backend helpers -----
    def _local_path(self) -> Path:
        _LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        return _LOCAL_DIR / f"{self.collection}.json"

    def _load_local(self) -> List[Dict[str, Any]]:
        p = self._local_path()
        if p.exists():
            return json.loads(p.read_text())
        return []

    def _save_local(self, rows: List[Dict[str, Any]]):
        self._local_path().write_text(json.dumps(rows))

    # ----- public API -----
    def upsert(self, points: List[Dict[str, Any]]):
        """points: [{id, vector, payload}]"""
        if self._backend == "qdrant":
            from qdrant_client.http import models as qmodels

            self._client.upsert(
                collection_name=self.collection,
                points=[
                    qmodels.PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                    for p in points
                ],
            )
            return

        rows = self._load_local()
        by_id = {r["id"]: r for r in rows}
        for p in points:
            by_id[p["id"]] = {"id": p["id"], "vector": p["vector"], "payload": p["payload"]}
        self._save_local(list(by_id.values()))

    def search(
        self, vector: List[float], top_k: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if self._backend == "qdrant":
            from qdrant_client.http import models as qmodels

            flt = None
            if where:
                flt = qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(key=k, match=qmodels.MatchValue(value=v))
                        for k, v in where.items()
                    ]
                )
            hits = self._client.search(
                collection_name=self.collection, query_vector=vector, limit=top_k, query_filter=flt
            )
            return [{"score": h.score, "payload": h.payload} for h in hits]

        # local cosine search
        rows = self._load_local()
        if where:
            rows = [r for r in rows if all(r["payload"].get(k) == v for k, v in where.items())]
        scored = [{"score": _cosine(vector, r["vector"]), "payload": r["payload"]} for r in rows]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    @property
    def backend(self) -> str:
        return self._backend
