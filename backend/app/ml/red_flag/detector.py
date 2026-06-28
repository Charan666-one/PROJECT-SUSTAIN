"""
Red Flag Detector — scans symptoms for patterns requiring urgent conventional care
Runs in parallel with RAG retrieval on every consultation
"""

RED_FLAG_PATTERNS = [
    {"pattern": ["chest pain", "chest tightness", "left arm pain"], "severity": "URGENT",   "message": "Possible cardiac event — immediate conventional evaluation recommended"},
    {"pattern": ["sudden severe headache", "worst headache of life"],  "severity": "URGENT",   "message": "Possible subarachnoid haemorrhage — refer immediately"},
    {"pattern": ["facial drooping", "arm weakness", "speech difficulty"],"severity": "URGENT","message": "Possible stroke — refer immediately"},
    {"pattern": ["unexplained weight loss", "night sweats", "blood in stool"], "severity": "HIGH", "message": "Possible malignancy — conventional investigation required"},
    {"pattern": ["high fever", "stiff neck", "photophobia"],           "severity": "URGENT",   "message": "Possible meningitis — refer immediately"},
    {"pattern": ["difficulty breathing", "breathlessness at rest"],    "severity": "HIGH",     "message": "Respiratory compromise — conventional evaluation needed"},
    {"pattern": ["sudden vision loss", "eye pain"],                    "severity": "HIGH",     "message": "Possible acute glaucoma — refer to ophthalmology"},
    {"pattern": ["child convulsions", "seizure"],                      "severity": "URGENT",   "message": "Seizure — immediate conventional evaluation"},
    {"pattern": ["suicidal thoughts", "self harm"],                    "severity": "URGENT",   "message": "Mental health emergency — refer to crisis support immediately"},
]

class RedFlagDetector:
    async def scan(self, symptoms: dict) -> list:
        detected = []
        symptom_text = " ".join([
            str(symptoms.get("structured_symptoms", "")),
            str(symptoms.get("chief_complaint", "")),
        ]).lower()

        for flag in RED_FLAG_PATTERNS:
            if any(p in symptom_text for p in flag["pattern"]):
                detected.append({
                    "severity": flag["severity"],
                    "message":  flag["message"],
                    "matched":  [p for p in flag["pattern"] if p in symptom_text],
                })

        return detected
