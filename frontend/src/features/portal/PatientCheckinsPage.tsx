import { useEffect, useState } from "react";
import { portalApi, type PFollowUp } from "../../services/api/portal";
import { getErrorMessage } from "../../services/api/errors";
import { Async } from "../../components/ui/State";

export default function PatientCheckinsPage() {
  const [data, setData] = useState<PFollowUp[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => portalApi.followups().then((r) => setData(r.data)).catch(() => setError("Could not load check-ins")).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const pending = (data ?? []).filter((f) => !f.responded);
  const done = (data ?? []).filter((f) => f.responded);

  return (
    <>
      <h1>Check-ins</h1>
      <p className="muted" style={{ marginTop: 0 }}>Let your doctor know how you're feeling. It only takes a moment.</p>
      <Async loading={loading} error={error} data={data}>
        {() => (
          <>
            {pending.length === 0 && <div className="card muted">No check-ins due right now. Thank you!</div>}
            {pending.map((f) => <CheckinCard key={f.id} f={f} onDone={load} />)}
            {done.length > 0 && (
              <div className="card">
                <h3>Past check-ins</h3>
                {done.map((f) => (
                  <div key={f.id} className="row between" style={{ padding: ".4rem 0", borderBottom: "1px solid var(--line-soft)" }}>
                    <span>{new Date(f.scheduled_at).toLocaleDateString()}</span>
                    <span className="badge high">{f.outcome === "improved" ? "Better" : f.outcome === "worsened" ? "Worse" : "Same"}{f.wellness ? ` · ${f.wellness}/10` : ""}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </Async>
    </>
  );
}

function CheckinCard({ f, onDone }: { f: PFollowUp; onDone: () => void }) {
  const [status, setStatus] = useState<"" | "better" | "same" | "worse">("");
  const [wellness, setWellness] = useState(5);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    if (!status) { setError("Please choose how you're feeling."); return; }
    setBusy(true); setError("");
    try { await portalApi.respond(f.id, { status, wellness, notes }); onDone(); }
    catch (e) { setError(getErrorMessage(e, "Could not submit. Please try again.")); setBusy(false); }
  };

  return (
    <div className="card">
      <h3>How are you feeling since your last visit?</h3>
      <div className="feel-btns">
        <button className={status === "better" ? "sel-better" : ""} onClick={() => setStatus("better")}>😊 Better</button>
        <button className={status === "same" ? "sel-same" : ""} onClick={() => setStatus("same")}>😐 Same</button>
        <button className={status === "worse" ? "sel-worse" : ""} onClick={() => setStatus("worse")}>😟 Worse</button>
      </div>
      <label style={{ marginTop: "1rem" }}>Overall wellness: <strong>{wellness}/10</strong></label>
      <input type="range" min={1} max={10} value={wellness} onChange={(e) => setWellness(Number(e.target.value))} />
      <label>Anything you'd like your doctor to know? (optional)</label>
      <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
      {error && <div className="error">{error}</div>}
      <button className="btn accent" style={{ marginTop: ".75rem" }} onClick={submit} disabled={busy}>
        {busy ? "Sending…" : "Send to my doctor"}
      </button>
    </div>
  );
}
