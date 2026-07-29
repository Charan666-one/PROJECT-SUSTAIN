"""
Clarifying-question generator.

Homeopathic case-taking needs modalities, mental-emotional picture, physical
generals, onset/causation, etc. This produces targeted questions for whatever is
missing from the symptom payload — a deterministic v1 that needs no LLM call.
"""
from __future__ import annotations
from typing import List


def generate_clarifying_questions(symptoms: dict) -> List[str]:
    questions: List[str] = []

    def _empty(key: str) -> bool:
        v = symptoms.get(key)
        return v is None or (isinstance(v, (str, dict, list)) and len(v) == 0)

    if _empty("modalities"):
        questions.append("What makes the complaint better or worse (time of day, temperature, position, motion, rest)?")
    if _empty("mental_emotional"):
        questions.append("How is the patient's mental-emotional state — mood, anxieties, irritability, any recent stressors?")
    if _empty("physical_generals"):
        questions.append("What are the physical generals — thirst, appetite, sweat, sleep, thermal preference (hot/chilly)?")

    text = " ".join(str(v) for v in symptoms.values() if v).lower()
    if "onset" not in text and "began" not in text and "started" not in text:
        questions.append("When and how did the complaint begin, and was there any clear cause or trigger?")
    if "worse" not in text and "better" not in text:
        questions.append("Is there a clear pattern to when symptoms intensify or ease?")

    # Always cap to keep the doctor's screen focused.
    return questions[:5]
