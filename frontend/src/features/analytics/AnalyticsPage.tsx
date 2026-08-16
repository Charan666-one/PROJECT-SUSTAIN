import { useEffect, useState } from "react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell,
  PieChart, Pie, Legend,
} from "recharts";
import { analyticsApi, type AnalyticsSummary } from "../../services/api/endpoints";
import { Async } from "../../components/ui/State";

const OUTCOME_COLORS: Record<string, string> = {
  improved: "#059669", no_change: "#b45309", worsened: "#dc2626", not_reported: "#94a3b8",
};

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
        {(d) => {
          const remedyData = d.top_remedies.map(([name, count]) => ({ name, count }));
          const outcomeData = Object.entries(d.outcome_distribution).map(([k, v]) => ({ name: k.replace("_", " "), key: k, value: v }));
          return (
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
                  {remedyData.length === 0 ? <p className="muted">No prescriptions yet.</p> : (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={remedyData} margin={{ top: 8, right: 12, left: -8, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" vertical={false} />
                        <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} interval={0} angle={-12} textAnchor="end" height={54} />
                        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#64748b" }} />
                        <Tooltip cursor={{ fill: "rgba(15,118,110,.06)" }} contentStyle={{ borderRadius: 10, border: "1px solid #e7ebf0", fontSize: 13 }} />
                        <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="#0f766e" maxBarSize={46} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>
                <div className="card">
                  <h3>Follow-up outcomes</h3>
                  {outcomeData.length === 0 ? <p className="muted">No outcomes recorded yet.</p> : (
                    <ResponsiveContainer width="100%" height={220}>
                      <PieChart>
                        <Pie data={outcomeData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={72} paddingAngle={2}>
                          {outcomeData.map((o) => <Cell key={o.key} fill={OUTCOME_COLORS[o.key] || "#94a3b8"} />)}
                        </Pie>
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e7ebf0", fontSize: 13 }} />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                  <p className="muted" style={{ marginTop: ".25rem" }}>{d.pending_followups} follow-ups pending.</p>
                </div>
              </div>
            </>
          );
        }}
      </Async>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return <div className="card"><div className="stat">{value}</div><div className="muted">{label}</div></div>;
}
