import { useEffect, useState } from "react";
import { portalApi, type PTimelineEvent } from "../../services/api/portal";
import { Async } from "../../components/ui/State";

const NODE: Record<string, string> = { recovered: "recovered", checkin: "followup" };

export default function PatientTimelinePage() {
  const [data, setData] = useState<PTimelineEvent[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    portalApi.timeline().then((r) => setData(r.data.events)).catch(() => setError("Could not load your recovery")).finally(() => setLoading(false));
  }, []);

  return (
    <>
      <h1>My recovery</h1>
      <p className="muted" style={{ marginTop: 0 }}>Every step of your treatment, from your first visit.</p>
      <Async loading={loading} error={error} data={data}>
        {(events) => (
          <div className="card">
            {events.length === 0 && <p className="muted">Your journey will appear here after your first consultation.</p>}
            <div className="timeline">
              {events.map((e, i) => (
                <div key={i} className={`node ${NODE[e.type] || ""}`}>
                  <div className="row between">
                    <strong>{e.label}</strong>
                    <span className="when">{e.at ? new Date(e.at).toLocaleDateString() : ""}</span>
                  </div>
                  {e.type === "prescription" && e.meta?.remedies && (
                    <div className="muted">{e.meta.remedies.filter(Boolean).join(", ")}</div>
                  )}
                  {e.type === "checkin" && e.meta?.responded && e.meta?.wellness != null && (
                    <div className="muted">You reported wellness {e.meta.wellness}/10</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </Async>
    </>
  );
}
