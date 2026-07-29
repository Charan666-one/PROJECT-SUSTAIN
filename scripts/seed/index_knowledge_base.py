"""
Seed the materia medica collection into the vector store.

Usage (from repo root, with backend deps installed):
    PYTHONPATH=backend python scripts/seed/index_knowledge_base.py

Reads every *.json file under knowledge_base/materia_medica/ where each entry is
{remedy, source, text} and upserts embeddings into the materia_medica collection.
Works with either Qdrant (if running) or the local file-backed fallback store.
"""
import json
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.core.config import settings          # noqa: E402
from app.rag import embeddings                 # noqa: E402
from app.rag.vector_store import VectorStore   # noqa: E402

KB_DIR = REPO_ROOT / "knowledge_base" / "materia_medica"


def main() -> int:
    files = sorted(KB_DIR.glob("*.json"))
    if not files:
        print(f"No knowledge base files found in {KB_DIR}")
        return 1

    store = VectorStore(settings.QDRANT_COLLECTION_MATERIA_MEDICA)
    print(f"Vector backend: {store.backend} | embeddings: "
          f"{'hashing_fallback' if embeddings.is_fallback() else settings.EMBEDDING_MODEL}")

    points, count = [], 0
    for f in files:
        entries = json.loads(f.read_text())
        for e in entries:
            text = f"{e['remedy']}. {e['text']}"
            points.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, e["remedy"])),
                "vector": embeddings.embed(text),
                "payload": {"remedy": e["remedy"], "source": e.get("source", "materia_medica"), "text": e["text"]},
            })
            count += 1

    store.upsert(points)
    print(f"Indexed {count} materia medica entries into '{settings.QDRANT_COLLECTION_MATERIA_MEDICA}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
