import pytest
from app.rag.pipeline.rag_engine import RAGEngine


@pytest.mark.asyncio
async def test_engine_runs_without_api_key_and_returns_contract():
    engine = RAGEngine(doctor_id="doc-1", clinic_id="doc-1")
    result = await engine.generate_recommendation(
        symptoms={"chief_complaint": "anxiety with burning pains worse after midnight"},
        patient_context={"age": 40, "gender": "female"},
    )
    assert set(result) == {"recommendation", "red_flags", "sources", "confidence"}
    assert result["confidence"] in {"high", "medium", "low"}
    assert isinstance(result["recommendation"], str) and result["recommendation"]


@pytest.mark.asyncio
async def test_engine_surfaces_red_flags():
    engine = RAGEngine(doctor_id="doc-1", clinic_id="doc-1")
    result = await engine.generate_recommendation(
        symptoms={"chief_complaint": "facial drooping, arm weakness and speech difficulty"},
        patient_context={},
    )
    assert any(f["severity"] == "URGENT" for f in result["red_flags"])
