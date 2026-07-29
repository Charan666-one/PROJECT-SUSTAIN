"""Shared retriever helpers."""
from __future__ import annotations
from typing import Any


def symptoms_to_query(symptoms: dict) -> str:
    """Flatten a symptom dict into a single query string for embedding."""
    parts: list[str] = []
    for key in ("chief_complaint", "structured_symptoms", "mental_emotional"):
        val = symptoms.get(key)
        if val:
            parts.append(val if isinstance(val, str) else str(val))
    modalities = symptoms.get("modalities")
    if isinstance(modalities, dict):
        parts.extend(f"{k}: {v}" for k, v in modalities.items())
    return " ".join(parts).strip()
