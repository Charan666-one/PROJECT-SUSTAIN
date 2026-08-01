import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { patientApi, visitApi, type Patient, type TimelineEvent } from "../../services/api/endpoints";
import { Async } from "../../components/ui/State";

const NODE_CLASS: Record<string, string> = { recovered: "recovered", followup: "followup" };

export default function PatientProfilePage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [events, setEvents] = useState<TimelineEvent[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([patientApi.get(id), patientApi.timeline(id)])
      .then(([p, t]) => { setPatient(p.data); setEvents(t.data.events); })
      .catch(() => setError("Could not load patient"))
      .finally(() => setLoading(false));
  }, [id]);

  const startConsult = async () => {
    const { data } = await visitApi.create(id);
    navigate(`/consultation/${data.id}`);
  };

  return (
    <div>
      <div className="row between">
        <Link to="/patients" className="muted">← Patients</Link>
        <button className="btn accent" onClick={startConsult}>Start consultation →</button>
      </div>

      <Async loading={loading} error={error} data={patient}>
        {(p) => (
          <>
            <h1 style={{ marginBottom: ".25rem" }}>{p.full_name}</h1>
            <p className="muted" style={{ marginTop: 0 }}>
              {p.gender} · DOB {p.date_of_birth} · {p.phone}
              {p.consent_given && <> · <span className="badge high">consent on file</span></>}
            </p>

            <div className="card">
              <h3>Treatment timeline</h3>
              {(!events || events.length === 0) && <p className="muted">No visits yet.</p>}
              <div className="timeline">
                {(events ?? []).map((e, i) => (
                  <div key={i} className={`node ${NODE_CLASS[e.type] || ""}`}>
                    <div className="row between">
                      <strong>
                        {e.type === "consultation" && e.meta?.chief_complaint
                          ? `${e.label} · ${e.meta.chief_complaint}` : e.label}
                        {e.type === "consultation" && e.ref_id && (
                          <> <Link to={`/consultation/${e.ref_id}`} className="muted" style={{ fontWeight: 400, fontSize: ".8rem" }}>open →</Link></>
                        )}
                      </strong>
                      <span className="when">{e.at ? new Date(e.at).toLocaleDateString() : ""}</span>
                    </div>
                    {e.type === "prescription" && (
                      <div className="muted">{(e.meta?.remedies || []).filter(Boolean).join(", ")}</div>
                    )}
                    {e.type === "followup" && e.meta?.responded && (
                      <div className="muted">Outcome: {e.meta.outcome}{e.meta.wellness != null ? ` · wellness ${e.meta.wellness}/10` : ""}</div>
                    )}
                    {e.type === "consultation" && e.meta?.recovery_trend && (
                      <div className="muted">Surveillance: {e.meta.surveillance_status} · {e.meta.recovery_trend}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </Async>
    </div>
  );
}
