import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { patientApi, visitApi, type Patient } from "../../services/api/endpoints";

const EMPTY = { full_name: "", date_of_birth: "", gender: "male", phone: "", consent_given: false };

export default function PatientsListPage() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [q, setQ] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<any>(EMPTY);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = (query = "") => patientApi.list(query).then((r) => setPatients(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  const create = async (e: React.FormEvent) => {
    e.preventDefault(); setError(""); setBusy(true);
    try {
      if (!form.consent_given) { setError("Patient consent is required (DPDP Act 2023)."); setBusy(false); return; }
      await patientApi.create(form);
      setForm(EMPTY); setShowForm(false); load(q);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not create patient.");
    } finally { setBusy(false); }
  };

  const startConsult = async (p: Patient) => {
    const { data } = await visitApi.create(p.id);
    navigate(`/consultation/${data.id}`);
  };

  return (
    <div>
      <div className="row between">
        <h1>Patients</h1>
        <button className="btn accent" onClick={() => setShowForm((s) => !s)}>{showForm ? "Close" : "+ Add patient"}</button>
      </div>

      {showForm && (
        <form className="card" onSubmit={create}>
          <h3>New patient</h3>
          <div className="grid grid-3">
            <div><label>Full name</label><input value={form.full_name} onChange={(e) => set("full_name", e.target.value)} required /></div>
            <div><label>Date of birth</label><input type="date" value={form.date_of_birth} onChange={(e) => set("date_of_birth", e.target.value)} required /></div>
            <div><label>Gender</label>
              <select value={form.gender} onChange={(e) => set("gender", e.target.value)}>
                <option value="male">Male</option><option value="female">Female</option><option value="other">Other</option>
              </select></div>
            <div><label>Phone</label><input value={form.phone} onChange={(e) => set("phone", e.target.value)} required /></div>
          </div>
          <label style={{ marginTop: ".75rem", fontWeight: 400 }}>
            <input type="checkbox" style={{ width: "auto", marginRight: ".4rem" }}
                   checked={form.consent_given} onChange={(e) => set("consent_given", e.target.checked)} />
            Patient has given consent to store their health data (DPDP Act 2023).
          </label>
          {error && <div className="error">{error}</div>}
          <button className="btn" style={{ marginTop: ".75rem" }} disabled={busy}>{busy ? "Saving…" : "Save patient"}</button>
        </form>
      )}

      <div className="card">
        <input placeholder="Search by name or phone…" value={q}
               onChange={(e) => { setQ(e.target.value); load(e.target.value); }} style={{ marginBottom: ".75rem" }} />
        <table>
          <thead><tr><th>Name</th><th>Phone</th><th>Gender</th><th></th></tr></thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.id}>
                <td><Link to={`/patients/${p.id}`}>{p.full_name}</Link></td>
                <td>{p.phone}</td><td>{p.gender}</td>
                <td style={{ textAlign: "right" }}>
                  <Link className="btn sm secondary" to={`/patients/${p.id}`}>Profile</Link>{" "}
                  <button className="btn sm" onClick={() => startConsult(p)}>Start consultation →</button>
                </td>
              </tr>
            ))}
            {patients.length === 0 && <tr><td colSpan={4} className="muted">No patients yet. Add your first patient to begin.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
