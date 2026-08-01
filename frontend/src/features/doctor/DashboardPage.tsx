import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  analyticsApi, followupApi, auditApi,
  type AnalyticsSummary, type FollowUp, type AuditEntry,
} from "../../services/api/endpoints";

export default function DashboardPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [due, setDue] = useState<FollowUp[]>([]);
  const [activity, setActivity] = useState<AuditEntry[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    analyticsApi.summary().then((r) => setSummary(r.data)).catch(() => setError("Could not load analytics"));
    followupApi.list(true).then((r) => setDue(r.data)).catch(() => {});
    auditApi.list(8).then((r) => setActivity(r.data)).catch(() => {});
  }, []);

  const respond = async (id: string, outcome: string) => {
    await followupApi.respond(id, { outcome });
    setDue((d) => d.filter((f) => f.id !== id));
    analyticsApi.summary().then((r) => setSummary(r.data));
    auditApi.list(8).then((r) => setActivity(r.data));
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
        <Stat label="Recovery rate"
              value={summary?.improvement_rate_pct != null ? `${summary.improvement_rate_pct}%` : "—"} />
      </div>

      <div className="grid grid-2-1">
        <div className="card">
          <h3>Follow-ups due today</h3>
          {due.length === 0 && <p className="muted">No follow-ups due right now.</p>}
          {due.map((f) => (
            <div key={f.id} className="row between" style={{ padding: ".4rem 0", borderBottom: "1px solid var(--border)" }}>
              <span className="pill">{f.followup_type.replace("_", " ")}</span>
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
          <table><tbody>
            {(summary?.top_remedies ?? []).map(([name, count]) => (
              <tr key={name}><td>{name}</td><td style={{ textAlign: "right" }}>{count}</td></tr>
            ))}
          </tbody></table>
        </div>
      </div>

      <div className="card">
        <div className="row between"><h3 style={{ margin: 0 }}>Recent activity</h3><Link to="/audit" className="muted">View all →</Link></div>
        {activity.length === 0 && <p className="muted">No activity yet.</p>}
        {activity.map((a) => (
          <div key={a.id} className="row between" style={{ padding: ".35rem 0", borderBottom: "1px solid var(--border)" }}>
            <span>{a.label}</span>
            <span className="muted" style={{ fontSize: ".78rem" }}>{new Date(a.created_at).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return <div className="card"><div className="stat">{value}</div><div className="muted">{label}</div></div>;
}
