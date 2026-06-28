/**
 * ConsultationPage — the core clinical workflow
 * 
 * Layout:
 * Left panel:   Patient summary + intake form responses + similar past cases
 * Center panel: Symptom entry (text or voice) + AI clarification Q&A
 * Right panel:  AI recommendation + confidence score + citations + red flags
 * Bottom:       Doctor review + approve/modify + generate prescription
 */
import { useState } from "react";
import SymptomEntryPanel     from "../../components/consultation/SymptomEntryPanel";
import AIRecommendationPanel from "../../components/consultation/AIRecommendationPanel";
import SimilarCasesPanel     from "../../components/consultation/SimilarCasesPanel";
import RedFlagAlert          from "../../components/consultation/RedFlagAlert";
import DoctorApprovalPanel   from "../../components/consultation/DoctorApprovalPanel";
import PatientSummaryCard    from "../../components/patient/PatientSummaryCard";
import VoiceInputButton      from "../../components/common/VoiceInputButton";

export default function ConsultationPage() {
  const [symptoms, setSymptoms]           = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [redFlags, setRedFlags]           = useState([]);
  const [approved, setApproved]           = useState(false);

  return (
    <div className="consultation-layout">
      {redFlags.length > 0 && <RedFlagAlert flags={redFlags} />}

      <div className="grid grid-cols-3 gap-4 h-full">
        <aside>
          <PatientSummaryCard />
          <SimilarCasesPanel symptoms={symptoms} />
        </aside>

        <main>
          <VoiceInputButton onTranscription={setSymptoms} />
          <SymptomEntryPanel onSymptomsChange={setSymptoms} />
        </main>

        <aside>
          <AIRecommendationPanel
            symptoms={symptoms}
            onRecommendation={setRecommendation}
            onRedFlags={setRedFlags}
          />
        </aside>
      </div>

      {recommendation && !approved && (
        <DoctorApprovalPanel
          recommendation={recommendation}
          onApprove={setApproved}
        />
      )}
    </div>
  );
}
