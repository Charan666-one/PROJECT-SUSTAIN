import type { Evidence } from "../../services/api/endpoints";

/** Explainable AI: shows WHY the assistant surfaced each source. Never a bare recommendation. */
export default function EvidencePanel({ evidence }: { evidence?: Evidence }) {
  if (!evidence) return null;
  const { materia_medica = [], similar_cases = [], doctor_notes = [] } = evidence;
  if (!materia_medica.length && !similar_cases.length && !doctor_notes.length) return null;

  return (
    <div className="card">
      <h3>Why this was suggested — supporting evidence</h3>

      {materia_medica.length > 0 && (
        <section style={{ marginBottom: ".75rem" }}>
          <div className="muted" style={{ fontWeight: 700, fontSize: ".78rem" }}>MATERIA MEDICA</div>
          {materia_medica.map((m, i) => (
            <div key={i} style={{ padding: ".5rem 0", borderBottom: "1px solid var(--border)" }}>
              <div className="row between">
                <strong>{m.remedy}</strong>
                {m.score != null && <span className="pill">match {Math.round((m.score || 0) * 100)}%</span>}
              </div>
              {m.matched_terms?.length > 0 && (
                <div className="row" style={{ margin: ".25rem 0" }}>
                  <span className="muted" style={{ fontSize: ".78rem" }}>Matched:</span>
                  {m.matched_terms.map((t) => <span key={t} className="pill">{t}</span>)}
                </div>
              )}
              <div className="muted" style={{ fontSize: ".82rem" }}>{m.snippet}</div>
              <div className="muted" style={{ fontSize: ".72rem" }}>Source: {m.source}</div>
            </div>
          ))}
        </section>
      )}

      {similar_cases.length > 0 && (
        <section style={{ marginBottom: ".75rem" }}>
          <div className="muted" style={{ fontWeight: 700, fontSize: ".78rem" }}>SIMILAR CLINIC CASES</div>
          {similar_cases.map((c, i) => (
            <div key={i} style={{ padding: ".4rem 0" }}>
              <strong>{c.remedy}</strong> {c.outcome && <span className="badge high">{c.outcome}</span>}
              <div className="muted" style={{ fontSize: ".82rem" }}>{c.snippet}</div>
            </div>
          ))}
        </section>
      )}

      {doctor_notes.length > 0 && (
        <section>
          <div className="muted" style={{ fontWeight: 700, fontSize: ".78rem" }}>YOUR NOTES</div>
          {doctor_notes.map((n, i) => (
            <div key={i} style={{ padding: ".4rem 0" }}>
              <strong>{n.title || "Note"}</strong>
              <div className="muted" style={{ fontSize: ".82rem" }}>{n.snippet}</div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
