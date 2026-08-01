from pydantic import BaseModel
from typing import List, Any, Optional


class RedFlag(BaseModel):
    severity: str
    message: str
    matched: List[str] = []


class RecommendationOut(BaseModel):
    recommendation: str
    red_flags: List[RedFlag] = []
    sources: dict = {}
    confidence: str = "low"
    evidence: dict = {}   # explainable AI: matched terms + snippets per source
    disclaimer: str = (
        "AI-generated decision support. Not a prescription. "
        "A licensed practitioner must review and approve before any treatment."
    )


class ClarifyOut(BaseModel):
    questions: List[str] = []


class ApprovalIn(BaseModel):
    """What the doctor actually approves (may differ from the AI suggestion)."""
    remedies: List[dict]           # [{name, potency, dosage, frequency, duration}]
    dietary_advice: Optional[str] = None
    lifestyle_advice: Optional[str] = None
    precautions: Optional[str] = None
    notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    red_flag_dismissed: bool = False
