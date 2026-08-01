import { useEffect, useState } from "react";
import { knowledgeApi } from "../../services/api/endpoints";

export default function KnowledgeBasePage() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<{ vector_backend: string; embeddings: string } | null>(null);

  useEffect(() => { knowledgeApi.status().then((r) => setStatus(r.data)).catch(() => {}); }, []);

  const save = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setMsg("");
    try {
      await knowledgeApi.addNote(title, text);
      setMsg("Saved — this note will now inform future AI recommendations.");
      setTitle(""); setText("");
    } catch { setMsg("Could not save the note."); }
    finally { setBusy(false); }
  };

  return (
    <div>
      <h1>Knowledge Base</h1>
      <p className="muted" style={{ marginTop: 0 }}>
        Your private notes and protocols are retrieved as evidence during consultations —
        the clinic's knowledge compounds over time.
      </p>

      <form className="card" onSubmit={save}>
        <h3>Add a note / protocol</h3>
        <label>Title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="e.g. My approach to paediatric coughs" />
        <label>Note</label>
        <textarea value={text} onChange={(e) => setText(e.target.value)} required style={{ minHeight: 140 }} />
        {msg && <div className={msg.startsWith("Could not") ? "error" : "muted"} style={{ marginTop: ".5rem" }}>{msg}</div>}
        <button className="btn" style={{ marginTop: ".75rem" }} disabled={busy || !title || !text}>
          {busy ? "Saving…" : "Save note"}
        </button>
      </form>

      {status && (
        <div className="card muted" style={{ fontSize: ".82rem" }}>
          Retrieval backend: <span className="pill">{status.vector_backend}</span>{" "}
          Embeddings: <span className="pill">{status.embeddings}</span>
        </div>
      )}
    </div>
  );
}
