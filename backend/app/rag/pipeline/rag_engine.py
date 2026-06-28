"""
Core RAG Engine — orchestrates retrieval + generation
Sources: materia medica | clinic case outcomes | doctor personal notes
"""
from app.rag.retrievers.materia_medica import MateriaMedicaRetriever
from app.rag.retrievers.clinic_cases import ClinicCaseRetriever
from app.rag.retrievers.doctor_notes import DoctorNotesRetriever
from app.rag.prompts.recommendation_prompt import build_recommendation_prompt
from app.ml.red_flag.detector import RedFlagDetector
from app.core.config import settings
import anthropic

class RAGEngine:
    def __init__(self, doctor_id: str, clinic_id: str):
        self.doctor_id = doctor_id
        self.clinic_id = clinic_id
        self.materia_retriever   = MateriaMedicaRetriever()
        self.case_retriever      = ClinicCaseRetriever(clinic_id)
        self.notes_retriever     = DoctorNotesRetriever(doctor_id)
        self.red_flag_detector   = RedFlagDetector()
        self.client              = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_recommendation(self, symptoms: dict, patient_context: dict) -> dict:
        # 1. Parallel retrieval from all three sources
        materia_context = await self.materia_retriever.retrieve(symptoms, top_k=5)
        similar_cases   = await self.case_retriever.retrieve(symptoms, top_k=3)
        doctor_notes    = await self.notes_retriever.retrieve(symptoms, top_k=3)

        # 2. Red flag scan (runs in parallel with retrieval)
        red_flags = await self.red_flag_detector.scan(symptoms)

        # 3. Build grounded prompt
        prompt = build_recommendation_prompt(
            symptoms=symptoms,
            patient_context=patient_context,
            materia_context=materia_context,
            similar_cases=similar_cases,
            doctor_notes=doctor_notes,
        )

        # 4. LLM generation
        response = self.client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            system=(
                "You are a clinical decision support assistant for a licensed homeopathic practitioner. "
                "Generate recommendations ONLY from the retrieved context provided. "
                "Always cite your sources. Never prescribe autonomously — this is decision support only. "
                "If retrieved evidence is weak, say so clearly."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        return {
            "recommendation": response.content[0].text,
            "red_flags": red_flags,
            "sources": {
                "materia_medica": [r["source"] for r in materia_context],
                "similar_cases":  [r["case_id"] for r in similar_cases],
                "doctor_notes":   [r["doc_id"] for r in doctor_notes],
            },
            "confidence": self._compute_confidence(materia_context, similar_cases),
        }

    def _compute_confidence(self, materia_context, similar_cases) -> str:
        score = len(materia_context) * 0.6 + len(similar_cases) * 0.4
        if score >= 3:   return "high"
        elif score >= 1: return "medium"
        else:            return "low"
