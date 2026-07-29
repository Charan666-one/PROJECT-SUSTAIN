"""
Core RAG Engine — orchestrates retrieval + generation.
Sources: materia medica | clinic case outcomes | doctor personal notes.

Design guarantees:
- Never prescribes autonomously; output is decision support the doctor must approve.
- Runs end-to-end even without an Anthropic API key or a running Qdrant
  (returns an evidence summary instead of a generated recommendation), so the
  full clinical workflow is testable in dev/CI.
"""
from __future__ import annotations
import asyncio
from app.rag.retrievers.materia_medica import MateriaMedicaRetriever
from app.rag.retrievers.clinic_cases import ClinicCaseRetriever
from app.rag.retrievers.doctor_notes import DoctorNotesRetriever
from app.rag.prompts.recommendation_prompt import build_recommendation_prompt
from app.ml.red_flag.detector import RedFlagDetector
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are a clinical decision support assistant for a licensed homeopathic practitioner. "
    "Generate recommendations ONLY from the retrieved context provided. "
    "Always cite your sources. Never prescribe autonomously — this is decision support only. "
    "If retrieved evidence is weak, say so clearly."
)


class RAGEngine:
    def __init__(self, doctor_id: str, clinic_id: str):
        self.doctor_id = str(doctor_id)
        self.clinic_id = str(clinic_id)
        self.materia_retriever = MateriaMedicaRetriever()
        self.case_retriever = ClinicCaseRetriever(clinic_id)
        self.notes_retriever = DoctorNotesRetriever(doctor_id)
        self.red_flag_detector = RedFlagDetector()

    async def generate_recommendation(self, symptoms: dict, patient_context: dict) -> dict:
        # 1. Parallel retrieval + red-flag scan
        materia_context, similar_cases, doctor_notes, red_flags = await asyncio.gather(
            self.materia_retriever.retrieve(symptoms, top_k=5),
            self.case_retriever.retrieve(symptoms, top_k=3),
            self.notes_retriever.retrieve(symptoms, top_k=3),
            self.red_flag_detector.scan(symptoms),
        )

        # 2. Build grounded prompt
        prompt = build_recommendation_prompt(
            symptoms=symptoms,
            patient_context=patient_context,
            materia_context=materia_context,
            similar_cases=similar_cases,
            doctor_notes=doctor_notes,
        )

        # 3. Generation (graceful fallback if no key / API error)
        recommendation = await self._generate(prompt)

        return {
            "recommendation": recommendation,
            "red_flags": red_flags,
            "sources": {
                "materia_medica": [r.get("source") for r in materia_context],
                "similar_cases": [r.get("case_id") for r in similar_cases],
                "doctor_notes": [r.get("doc_id") for r in doctor_notes],
            },
            "confidence": self._compute_confidence(materia_context, similar_cases),
        }

    async def _generate(self, prompt: str) -> str:
        if not settings.ANTHROPIC_API_KEY:
            return (
                "[AI generation disabled — no ANTHROPIC_API_KEY configured]\n\n"
                "Evidence retrieved for the doctor to review:\n" + prompt
            )
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = await client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as exc:  # noqa: BLE001 — never let generation crash the consult
            return f"[AI generation unavailable: {exc}]\n\nRetrieved evidence:\n{prompt}"

    def _compute_confidence(self, materia_context, similar_cases) -> str:
        score = len(materia_context) * 0.6 + len(similar_cases) * 0.4
        if score >= 3:
            return "high"
        elif score >= 1:
            return "medium"
        return "low"
