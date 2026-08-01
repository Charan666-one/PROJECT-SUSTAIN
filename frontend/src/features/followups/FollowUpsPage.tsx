import { useEffect, useState } from "react";
import { followupApi, type FollowUp } from "../../services/api/endpoints";

export default function FollowUpsPage() {
  const [all, setAll] = useState<FollowUp[]>([]);
  const [error, setError] = useState("");

  const load = () => followupApi.list(false).then((r) => setAll(r.data)).catch(() => setError("Could not load follow-ups"));
  useEffect(() => { load(); }, []);

  const respond = async (id: string, outcome: string) => {
    await followupApi.respond(id, { outcome });
    load();
  };

  const now = Date.now();
  const completed = all.filter((f) => f.responded_at);
  const missed = all.filter((f) => !f.responded_at && new Date(f.scheduled_at).getTime() < now);
  const upcoming = all.filter((f) => !f.responded_at && new Date(f.scheduled_at).getTime() >= now);

  const Row = ({ f, actions }: { f: FollowUp; actions?: boolean }) => (
    <div className="row between" style={{ padding: ".45rem 0", borderBottom: "1px solid var(--border)" }}>
      <span><span className="pill">{f.followup_type.replace("_", " ")}</span>{" "}
        <span className="muted">{new Date(f.scheduled_at).toLocaleDateString()}</span>
        {f.responded_at && <> · <span className="badge high">{f.outcome}</span></>}</span>
      {actions && (
        <div className="row">
          <button className="btn sm accent" onClick={() => respond(f.id, "improved")}>Improved</button>
          <button className="btn sm secondary" onClick={() => respond(f.id, "no_change")}>Same</button>
          <button className="btn sm secondary" onClick={() => respond(f.id, "worsened")}>Worse</button>
        </div>
      )}
    </div>
  );

  return (
    <div>
      <h1>Follow-ups</h1>
      {error && <div className="error">{error}</div>}
      <div className="card">
        <h3 style={{ color: "var(--danger)" }}>Missed ({missed.length})</h3>
        {missed.length === 0 && <p className="muted">None overdue.</p>}
        {missed.map((f) => <Row key={f.id} f={f} actions />)}
      </div>
      <div className="card">
        <h3>Upcoming ({upcoming.length})</h3>
        {upcoming.length === 0 && <p className="muted">Nothing scheduled.</p>}
        {upcoming.map((f) => <Row key={f.id} f={f} actions />)}
      </div>
      <div className="card">
        <h3>Completed ({completed.length})</h3>
        {completed.length === 0 && <p className="muted">No responses yet.</p>}
        {completed.map((f) => <Row key={f.id} f={f} />)}
      </div>
    </div>
  );
}
