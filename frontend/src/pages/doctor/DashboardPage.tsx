import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  analyticsApi, followupApi,
  type AnalyticsSummary, type FollowUp,
} from "../../services/api/endpoints";

export default function DashboardPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [due, setDue] = useState<FollowUp[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    analyticsApi.summary().then((r) => setSummary(r.data)).catch(() => setError("Could not load analytics"));
    followupApi.list(true).then((r) => setDue(r.data)).catch(() => {});
  }, []);

  const respond = async (id: string, outcome: string) => {
    await followupApi.respond(id, { outcome });
    setDue((d) => d.filter((f) => f.id !== id));
    analyticsApi.summary().then((r) => setSummary(r.data));
  };

  return (
    <div>
      <div className="row between">
        <h1>Clinic Dashboard</h1>
        <Link to="/patients" className="btn accent">+ New consultation</Link>
      </div>
      {error && <div className="error">{error}</div>}

      <div className="grid grid-4">
        <Stat label="Patients" value={summary?.total_patients ?? "—"} />
        <Stat label="Consultations" value={summary?.total_visits ?? "—"} />
        <Stat label="Last 30 days" value={summary?.visits_last_30d ?? "—"} />
        <Stat label="Improvement rate"
              value={summary?.improvement_rate_pct != null ? `${summary.improvement_rate_pct}%` : "—"} />
      </div>

      <div className="grid grid-2-1">
        <div className="card">
          <h3>Follow-ups due</h3>
          {due.length === 0 && <p className="muted">No follow-ups due right now.</p>}
          {due.map((f) => (
            <div key={f.id} className="row between" style={{ padding: ".4rem 0", borderBottom: "1px solid var(--border)" }}>
              <span><span className="pill">{f.followup_type.replace("_", " ")}</span></span>
              <div className="row">
                <button className="btn sm accent" onClick={() => respond(f.id, "improved")}>Improved</button>
                <button className="btn sm secondary" onClick={() => respond(f.id, "no_change")}>No change</button>
                <button className="btn sm secondary" onClick={() => respond(f.id, "worsened")}>Worsened</button>
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <h3>Top remedies</h3>
          {(summary?.top_remedies ?? []).length === 0 && <p className="muted">No prescriptions yet.</p>}
          <table>
            <tbody>
              {(summary?.top_remedies ?? []).map(([name, count]) => (
                <tr key={name}><td>{name}</td><td style={{ textAlign: "right" }}>{count}</td></tr>
              ))}
            </tbody>
          </table>
          {summary?.pending_followups ? (
            <p className="muted" style={{ marginTop: ".75rem" }}>{summary.pending_followups} follow-ups pending overall.</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="card">
      <div className="stat">{value}</div>
      <div className="muted">{label}</div>
    </div>
  );
}
