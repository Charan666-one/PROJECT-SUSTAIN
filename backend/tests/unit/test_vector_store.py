from app.rag import embeddings
from app.rag.vector_store import VectorStore


def test_local_upsert_and_semantic_search():
    store = VectorStore("test_collection")
    store.upsert([
        {"id": "1", "vector": embeddings.embed("burning thirst restlessness anxiety after midnight"),
         "payload": {"remedy": "Arsenicum Album"}},
        {"id": "2", "vector": embeddings.embed("mild weepy craves consolation thirstless open air"),
         "payload": {"remedy": "Pulsatilla"}},
    ])
    hits = store.search(embeddings.embed("anxious restless burning worse after midnight"), top_k=1)
    assert hits
    assert hits[0]["payload"]["remedy"] == "Arsenicum Album"


def test_filter_by_payload_field():
    store = VectorStore("test_scoped")
    store.upsert([
        {"id": "a", "vector": embeddings.embed("headache"), "payload": {"clinic_id": "c1", "remedy": "X"}},
        {"id": "b", "vector": embeddings.embed("headache"), "payload": {"clinic_id": "c2", "remedy": "Y"}},
    ])
    hits = store.search(embeddings.embed("headache"), top_k=5, where={"clinic_id": "c1"})
    assert all(h["payload"]["clinic_id"] == "c1" for h in hits)
