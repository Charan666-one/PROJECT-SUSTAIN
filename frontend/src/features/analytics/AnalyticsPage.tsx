import { useEffect, useState } from "react";
import { analyticsApi, type AnalyticsSummary } from "../../services/api/endpoints";
import { Async } from "../../components/ui/State";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    analyticsApi.summary().then((r) => setData(r.data)).catch(() => setError("Could not load analytics")).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Analytics</h1>
      <Async loading={loading} error={error} data={data}>
        {(d) => (
          <>
            <div className="grid grid-4">
              <Stat label="Total patients" value={d.total_patients} />
              <Stat label="Consultations" value={d.total_visits} />
              <Stat label="Last 30 days" value={d.visits_last_30d} />
              <Stat label="Recovery rate" value={d.improvement_rate_pct != null ? `${d.improvement_rate_pct}%` : "—"} />
            </div>
            <div className="grid grid-2-1">
              <div className="card">
                <h3>Most prescribed remedies</h3>
                {d.top_remedies.length === 0 && <p className="muted">No prescriptions yet.</p>}
                <table><tbody>
                  {d.top_remedies.map(([name, count]) => {
                    const max = d.top_remedies[0][1] || 1;
                    return (
                      <tr key={name}>
                        <td style={{ width: "40%" }}>{name}</td>
                        <td>
                          <div style={{ background: "var(--primary)", height: 10, borderRadius: 5,
                            width: `${Math.max(6, (count / max) * 100)}%` }} />
                        </td>
                        <td style={{ textAlign: "right", width: 40 }}>{count}</td>
                      </tr>
                    );
                  })}
                </tbody></table>
              </div>
              <div className="card">
                <h3>Follow-up outcomes</h3>
                {Object.keys(d.outcome_distribution).length === 0 && <p className="muted">No outcomes recorded yet.</p>}
                <table><tbody>
                  {Object.entries(d.outcome_distribution).map(([k, v]) => (
                    <tr key={k}><td>{k.replace("_", " ")}</td><td style={{ textAlign: "right" }}>{v}</td></tr>
                  ))}
                </tbody></table>
                <p className="muted" style={{ marginTop: ".5rem" }}>{d.pending_followups} follow-ups pending.</p>
              </div>
            </div>
          </>
        )}
      </Async>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return <div className="card"><div className="stat">{value}</div><div className="muted">{label}</div></div>;
}
