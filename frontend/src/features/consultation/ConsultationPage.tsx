import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  consultationApi, prescriptionApi,
  type Recommendation, type Remedy, type Prescription,
} from "../../services/api/endpoints";
import EvidencePanel from "./EvidencePanel";

const EMPTY_REMEDY: Remedy = { name: "", potency: "", dosage: "", frequency: "", duration: "" };

export default function ConsultationPage() {
  const { visitId = "" } = useParams();

  const [sym, setSym] = useState({
    chief_complaint: "", structured_symptoms: "", worse: "", better: "",
    mental_emotional: "", physical_generals: "",
  });
  const [questions, setQuestions] = useState<string[]>([]);
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [remedies, setRemedies] = useState<Remedy[]>([{ ...EMPTY_REMEDY }]);
  const [dietary, setDietary] = useState("");
  const [precautions, setPrecautions] = useState("");
  const [notes, setNotes] = useState("");
  const [dismiss, setDismiss] = useState(false);
  const [prescription, setPrescription] = useState<Prescription | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<"" | "clarify" | "recommend" | "approve" | "wa">("");

  const setS = (k: string, v: string) => setSym((s) => ({ ...s, [k]: v }));

  const payload = () => ({
    chief_complaint: sym.chief_complaint,
    structured_symptoms: sym.structured_symptoms,
    modalities: { worse: sym.worse, better: sym.better },
    mental_emotional: sym.mental_emotional,
    physical_generals: sym.physical_generals,
  });

  const clarify = async () => {
    setBusy("clarify"); setError("");
    try { setQuestions((await consultationApi.clarify(visitId, payload())).data.questions); }
    catch { setError("Could not fetch clarifying questions."); }
    finally { setBusy(""); }
  };

  const recommend = async () => {
    setBusy("recommend"); setError("");
    try { setRec((await consultationApi.recommend(visitId, payload())).data); }
    catch (e: any) { setError(e?.response?.data?.detail || "Could not generate recommendation."); }
    finally { setBusy(""); }
  };

  const setRemedy = (i: number, k: keyof Remedy, v: string) =>
    setRemedies((rs) => rs.map((r, idx) => (idx === i ? { ...r, [k]: v } : r)));

  const urgent = (rec?.red_flags ?? []).filter((f) => f.severity === "URGENT");

  const approve = async () => {
    setBusy("approve"); setError("");
    try {
      const cleaned = remedies.filter((r) => r.name.trim());
      if (cleaned.length === 0) { setError("Add at least one remedy."); setBusy(""); return; }
      const { data } = await consultationApi.approve(visitId, {
        remedies: cleaned, dietary_advice: dietary, precautions,
        doctor_notes: notes, red_flag_dismissed: dismiss,
      });
      setPrescription(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Could not approve prescription.");
    } finally { setBusy(""); }
  };

  const sendWhatsapp = async () => {
    if (!prescription) return;
    setBusy("wa");
    try { setPrescription((await prescriptionApi.sendWhatsapp(prescription.id)).data); }
    finally { setBusy(""); }
  };

  if (prescription) {
    return (
      <div>
        <h1>Prescription approved ✓</h1>
        <div className="card">
          <h3>Remedies</h3>
          <table>
            <thead><tr><th>Remedy</th><th>Potency</th><th>Dosage</th><th>Frequency</th><th>Duration</th></tr></thead>
            <tbody>
              {prescription.remedies.map((r, i) => (
                <tr key={i}><td>{r.name}</td><td>{r.potency}</td><td>{r.dosage}</td><td>{r.frequency}</td><td>{r.duration}</td></tr>
              ))}
            </tbody>
          </table>
          <div className="row" style={{ marginTop: "1rem" }}>
            <a className="btn" href={prescriptionApi.pdfUrl(prescription.id)} target="_blank" rel="noreferrer">View / print PDF</a>
            <button className="btn accent" onClick={sendWhatsapp} disabled={busy === "wa"}>
              {prescription.whatsapp_sent ? "WhatsApp sent ✓" : busy === "wa" ? "Sending…" : "Send via WhatsApp"}
            </button>
            <Link className="btn secondary" to="/">Back to dashboard</Link>
          </div>
          <p className="muted" style={{ marginTop: ".75rem" }}>Day 3, 7 and 30 follow-ups have been scheduled automatically.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="row between"><h1>Consultation</h1><Link to="/patients" className="muted">← Patients</Link></div>
      {error && <div className="error">{error}</div>}

      <div className="grid consult-grid">
        <div className="card">
          <h3>Symptoms</h3>
          <label>Chief complaint</label>
          <input value={sym.chief_complaint} onChange={(e) => setS("chief_complaint", e.target.value)} />
          <label>Symptom details</label>
          <textarea value={sym.structured_symptoms} onChange={(e) => setS("structured_symptoms", e.target.value)} />
          <label>Worse from (aggravation)</label>
          <input value={sym.worse} onChange={(e) => setS("worse", e.target.value)} />
          <label>Better from (amelioration)</label>
          <input value={sym.better} onChange={(e) => setS("better", e.target.value)} />
          <label>Mental / emotional</label>
          <input value={sym.mental_emotional} onChange={(e) => setS("mental_emotional", e.target.value)} />
          <label>Physical generals</label>
          <input value={sym.physical_generals} onChange={(e) => setS("physical_generals", e.target.value)} />

          <div className="row" style={{ marginTop: "1rem" }}>
            <button className="btn secondary" onClick={clarify} disabled={!!busy}>{busy === "clarify" ? "…" : "Clarify"}</button>
            <button className="btn" onClick={recommend} disabled={!!busy || !sym.chief_complaint}>
              {busy === "recommend" ? "Analysing…" : "Get AI recommendation"}
            </button>
          </div>

          {questions.length > 0 && (
            <div style={{ marginTop: "1rem" }}>
              <h3>Consider asking</h3>
              <ul className="muted" style={{ paddingLeft: "1.1rem", margin: 0 }}>
                {questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </div>
          )}
        </div>

        <div>
          {rec && urgent.length > 0 && (
            <div className="redflag urgent">
              <h3>⚠ Urgent red flag</h3>
              {urgent.map((f, i) => <div key={i}>{f.message}</div>)}
              <label style={{ fontWeight: 400, marginTop: ".5rem" }}>
                <input type="checkbox" style={{ width: "auto", marginRight: ".4rem" }}
                       checked={dismiss} onChange={(e) => setDismiss(e.target.checked)} />
                I have advised the patient to seek conventional care and take clinical responsibility.
              </label>
            </div>
          )}

          {rec && (
            <div className="card">
              <div className="row between">
                <h3 style={{ margin: 0 }}>AI decision support</h3>
                <span className={`badge ${rec.confidence}`}>{rec.confidence} confidence</span>
              </div>
              <div className="recommendation-text">{rec.recommendation}</div>
              <p className="disclaimer">{rec.disclaimer}</p>
            </div>
          )}

          {rec && <EvidencePanel evidence={rec.evidence} />}

          {rec && (
            <div className="card">
              <h3>Doctor's prescription</h3>
              <div className="remedy-row muted" style={{ fontSize: ".72rem", fontWeight: 700 }}>
                <span>Remedy</span><span>Potency</span><span>Dosage</span><span>Frequency</span><span>Duration</span><span />
              </div>
              {remedies.map((r, i) => (
                <div className="remedy-row" key={i}>
                  <input placeholder="Arsenicum Album" value={r.name} onChange={(e) => setRemedy(i, "name", e.target.value)} />
                  <input placeholder="30C" value={r.potency} onChange={(e) => setRemedy(i, "potency", e.target.value)} />
                  <input placeholder="3 pills" value={r.dosage} onChange={(e) => setRemedy(i, "dosage", e.target.value)} />
                  <input placeholder="BD" value={r.frequency} onChange={(e) => setRemedy(i, "frequency", e.target.value)} />
                  <input placeholder="5 days" value={r.duration} onChange={(e) => setRemedy(i, "duration", e.target.value)} />
                  <button className="btn sm secondary" type="button"
                          onClick={() => setRemedies((rs) => rs.filter((_, idx) => idx !== i))}>✕</button>
                </div>
              ))}
              <button className="btn sm secondary" type="button" onClick={() => setRemedies((rs) => [...rs, { ...EMPTY_REMEDY }])}>+ Add remedy</button>

              <label>Dietary advice</label>
              <input value={dietary} onChange={(e) => setDietary(e.target.value)} />
              <label>Precautions</label>
              <input value={precautions} onChange={(e) => setPrecautions(e.target.value)} />
              <label>Doctor's notes</label>
              <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />

              <button className="btn accent" style={{ marginTop: "1rem" }} onClick={approve} disabled={!!busy}>
                {busy === "approve" ? "Approving…" : "Approve & generate prescription"}
              </button>
            </div>
          )}

          {!rec && <div className="card muted">Enter symptoms and request an AI recommendation to begin.</div>}
        </div>
      </div>
    </div>
  );
}
