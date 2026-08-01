import { useEffect, useState } from "react";
import { auditApi, type AuditEntry } from "../../services/api/endpoints";

export default function AuditLogPage() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [verify, setVerify] = useState<{ ok: boolean; count: number } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    auditApi.list(200).then((r) => setEntries(r.data)).catch(() => setError("Could not load audit log"));
    auditApi.verify().then((r) => setVerify(r.data)).catch(() => {});
  }, []);

  return (
    <div>
      <div className="row between">
        <h1>Audit Log</h1>
        {verify && (
          <span className={`badge ${verify.ok ? "high" : "low"}`}>
            {verify.ok ? `✓ Chain verified · ${verify.count} events` : "⚠ Tamper detected"}
          </span>
        )}
      </div>
      <p className="muted" style={{ marginTop: 0 }}>
        Every clinical decision is recorded in a tamper-evident hash chain (DPDP / medico-legal trail).
      </p>
      {error && <div className="error">{error}</div>}

      <div className="card">
        <div className="timeline">
          {entries.length === 0 && <p className="muted">No activity recorded yet.</p>}
          {entries.map((a) => (
            <div key={a.id} className="node">
              <div className="row between">
                <strong>{a.label}</strong>
                <span className="when">{new Date(a.created_at).toLocaleString()}</span>
              </div>
              {a.payload && Object.keys(a.payload).length > 0 && (
                <div className="muted" style={{ fontSize: ".78rem" }}>
                  {Object.entries(a.payload).slice(0, 4).map(([k, v]) =>
                    `${k}: ${typeof v === "object" ? JSON.stringify(v) : v}`).join(" · ")}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
