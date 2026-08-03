import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { portalApi, type PDashboard } from "../../services/api/portal";
import { Async } from "../../components/ui/State";

export default function PatientDashboardPage() {
  const [data, setData] = useState<PDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    portalApi.dashboard().then((r) => setData(r.data)).catch(() => setError("Could not load your dashboard")).finally(() => setLoading(false));
  }, []);

  return (
    <Async loading={loading} error={error} data={data}>
      {(d) => (
        <>
          <div className="hero-status">
            <div className="lbl">How your recovery is going</div>
            <div className="big">{d.recovery_status}</div>
            {d.next_followup_at && (
              <div style={{ marginTop: ".6rem", color: "#cdeee8" }}>
                Next check-in: {new Date(d.next_followup_at).toLocaleDateString()} —{" "}
                <Link to="/portal/checkins" style={{ color: "#fff", textDecoration: "underline" }}>update your doctor</Link>
              </div>
            )}
          </div>

          {d.current_prescription && (
            <div className="card" style={{ marginTop: "1.1rem" }}>
              <div className="row between">
                <h3 style={{ margin: 0 }}>Current medicine</h3>
                <Link to="/portal/prescriptions" className="muted">View all →</Link>
              </div>
              {d.current_prescription.remedies.map((r, i) => (
                <div key={i} style={{ padding: ".35rem 0", borderBottom: "1px solid var(--line-soft)" }}>
                  <strong>{r.name}</strong> <span className="muted">{r.potency}</span>
                  {(r.dosage || r.frequency) && <div className="muted" style={{ fontSize: ".85rem" }}>{[r.dosage, r.frequency, r.duration].filter(Boolean).join(" · ")}</div>}
                </div>
              ))}
              {d.current_prescription.dietary_advice && <p className="muted" style={{ marginTop: ".6rem" }}>Diet: {d.current_prescription.dietary_advice}</p>}
            </div>
          )}

          <div className="card">
            <h3>Notifications</h3>
            {d.notifications.length === 0 && <p className="muted">You're all caught up.</p>}
            {d.notifications.map((n, i) => (
              <div className="notif" key={i}>
                <span className="dot" />
                <div>
                  <div>{n.message}</div>
                  {n.at && <div className="muted" style={{ fontSize: ".76rem" }}>{new Date(n.at).toLocaleDateString()}</div>}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </Async>
  );
}
