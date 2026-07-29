"""
Text embeddings with a graceful fallback.

Primary: sentence-transformers (as configured, EMBEDDING_MODEL / EMBEDDING_DIM).
Fallback: a deterministic hashing embedder so the app + tests run even when the
model isn't downloaded (e.g. CI, first-boot dev). The fallback is NOT good for
production retrieval quality — it only keeps the pipeline functional.
"""
from __future__ import annotations
import hashlib
import math
from typing import List
from app.core.config import settings

_model = None
_use_fallback = False


def _load_model():
    global _model, _use_fallback
    if _model is not None or _use_fallback:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    except Exception:
        # Model unavailable — degrade to deterministic hashing embedder.
        _use_fallback = True


def _hash_embed(text: str, dim: int) -> List[float]:
    """Bag-of-tokens hashing → L2-normalised vector. Deterministic, dependency-free."""
    vec = [0.0] * dim
    for token in text.lower().split():
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed(text: str) -> List[float]:
    _load_model()
    if _use_fallback or _model is None:
        return _hash_embed(text or "", settings.EMBEDDING_DIM)
    return _model.encode(text or "", normalize_embeddings=True).tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    _load_model()
    if _use_fallback or _model is None:
        return [_hash_embed(t or "", settings.EMBEDDING_DIM) for t in texts]
    return [v.tolist() for v in _model.encode(texts, normalize_embeddings=True)]


def is_fallback() -> bool:
    _load_model()
    return _use_fallback
