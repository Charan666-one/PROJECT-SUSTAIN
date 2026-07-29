import pytest
from app.ml.red_flag.detector import RedFlagDetector


@pytest.mark.asyncio
async def test_detects_cardiac_red_flag_from_nested_payload():
    det = RedFlagDetector()
    flags = await det.scan({"structured_symptoms": {"pain": "severe chest pain radiating to left arm"}})
    assert any(f["severity"] == "URGENT" for f in flags)


@pytest.mark.asyncio
async def test_no_false_positive_on_benign_symptoms():
    det = RedFlagDetector()
    flags = await det.scan({"chief_complaint": "mild seasonal sneezing and runny nose"})
    assert flags == []


@pytest.mark.asyncio
async def test_scans_chief_complaint_string():
    det = RedFlagDetector()
    flags = await det.scan({"chief_complaint": "sudden severe headache, worst headache of life"})
    assert flags and flags[0]["severity"] == "URGENT"
