"""
Prompt builder for RAG recommendation generation
"""

def build_recommendation_prompt(symptoms, patient_context, materia_context, similar_cases, doctor_notes) -> str:
    similar_cases_text = ""
    for i, case in enumerate(similar_cases, 1):
        similar_cases_text += (
            f"Case {i}: {case.get('text', '')} | "
            f"Remedy: {case.get('remedy')} | Outcome: {case.get('outcome')}\n"
        )

    materia_text = "\n".join([f"- [{r.get('source')} / {r.get('remedy')}]: {r.get('text', '')}" for r in materia_context])
    notes_text   = "\n".join([f"- [{n.get('title') or n.get('doc_id')}]: {n.get('text', '')}" for n in doctor_notes])

    return f"""
PATIENT CONTEXT:
Age: {patient_context.get("age")} | Gender: {patient_context.get("gender")}
Concurrent medications: {patient_context.get("concurrent_medications", "None reported")}
Known allergies: {patient_context.get("allergies", "None")}

CURRENT SYMPTOMS:
{symptoms.get("structured_symptoms")}

Modalities: {symptoms.get("modalities")}
Mental/Emotional: {symptoms.get("mental_emotional")}
Physical Generals: {symptoms.get("physical_generals")}

RETRIEVED MATERIA MEDICA CONTEXT:
{materia_text}

SIMILAR PAST CASES FROM THIS CLINIC:
{similar_cases_text if similar_cases_text else "No similar past cases found."}

DOCTOR PERSONAL NOTES:
{notes_text if notes_text else "No relevant personal notes found."}

TASK:
Based ONLY on the above retrieved context, generate:
1. Top 2-3 remedy considerations with rationale
2. Suggested potency range and dosage (note: final decision rests with the doctor)
3. Dietary and lifestyle advice
4. Precautions and what to watch for
5. Recommended follow-up timeline
6. Confidence level for each suggestion (based on how strongly context supports it)
7. Source citations for every recommendation

IMPORTANT: If the retrieved context does not strongly support a recommendation, say so explicitly.
This output is decision support only. The licensed practitioner makes all final decisions.
"""
