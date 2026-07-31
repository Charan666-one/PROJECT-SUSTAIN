import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { surveillanceApi, type SurveillanceEpisode } from "../../services/api/endpoints";

const ANOMALY_LABEL: Record<string, string> = {
  on_track: "On track",
  aggravation: "Homeopathic aggravation",
  plateau: "Plateau",
  non_response: "No response",
  relapse: "Relapse",
  worsening: "Worsening",
};

export default function SurveillancePage() {
  const navigate = useNavigate();
  const [episodes, setEpisodes] = useState<SurveillanceEpisode[]>([]);
  const [showRecovered, setShowRecovered] = useState(false);
  const [error, setError] = useState("");

  const load = (rec = showRecovered) =>
    surveillanceApi.list(rec).then((r) => setEpisodes(r.data)).catch(() => setError("Could not load surveillance"));

  useEffect(() => { load(); }, [showRecovered]);

  const close = async (visitId: string) => {
    await surveillanceApi.close(visitId);
    load();
  };

  const active = episodes.filter((e) => !e.recovered && e.surveillance_status === "active");
  const flagged = active.filter((e) => e.severity !== "info").length;

  return (
    <div>
      <div className="row between">
        <h1>Recovery Surveillance</h1>
        <label style={{ fontWeight: 400, margin: 0 }}>
          <input type="checkbox" style={{ width: "auto", marginRight: ".4rem" }}
                 checked={showRecovered} onChange={(e) => setShowRecovered(e.target.checked)} />
          Show recovered
        </label>
      </div>
      <p className="muted" style={{ marginTop: 0 }}>
        Patients tracked until they recover. The engine flags anomalies and suggests the next step —
        <strong> you decide every action.</strong>
      </p>

      <div className="grid grid-3">
        <div className="card"><div className="stat">{active.length}</div><div className="muted">Under surveillance</div></div>
        <div className="card"><div className="stat" style={{ color: "var(--danger)" }}>{flagged}</div><div className="muted">Needing attention</div></div>
        <div className="card"><div className="stat" style={{ color: "var(--ok)" }}>{episodes.filter((e) => e.recovered).length}</div><div className="muted">Recovered</div></div>
      </div>

      {error && <div className="error">{error}</div>}

      {episodes.length === 0 && (
        <div className="card muted">No episodes yet. Approve a prescription to begin surveillance of that patient's recovery.</div>
      )}

      {episodes.map((e) => (
        <div key={e.visit_id} className={`card episode ${e.severity}`}>
          <div className="row between">
            <div>
              <strong style={{ fontSize: "1.05rem" }}>{e.patient_name}</strong>
              <span className="muted"> · {e.chief_complaint || "—"}</span>
            </div>
            <span className={`sev ${e.severity}`}>{e.severity}</span>
          </div>

          <div className="row" style={{ marginTop: ".5rem", gap: "1.25rem" }}>
            <span>Trend: <span className={`trend-${e.trend}`}>{e.trend}</span></span>
            <span className="muted">Anomaly: {ANOMALY_LABEL[e.anomaly] || e.anomaly}</span>
            <span className="muted">Day {e.days_under_surveillance}</span>
            {e.latest_score != null && <span className="muted">Wellness {e.latest_score}/10</span>}
            {e.next_check_at && <span className="muted">Next check: {new Date(e.next_check_at).toLocaleDateString()}</span>}
          </div>

          <div style={{ marginTop: ".6rem" }}>
            <strong>Recommended:</strong> {e.recommended_action}
            <div className="muted" style={{ fontSize: ".8rem" }}>{e.rationale}</div>
          </div>

          <div className="row" style={{ marginTop: ".75rem" }}>
            {e.suggest_re_evaluation && (
              <button className="btn sm" onClick={() => navigate(`/consultation/${e.visit_id}`)}>
                Re-evaluate remedy →
              </button>
            )}
            {!e.recovered && e.surveillance_status === "active" && (
              <button className="btn sm secondary" onClick={() => close(e.visit_id)}>
                {e.trend === "recovered" ? "Mark recovered" : "Close episode"}
              </button>
            )}
            {e.recovered && <span className="badge high">recovered</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
