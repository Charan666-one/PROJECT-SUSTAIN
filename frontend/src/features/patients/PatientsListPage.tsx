import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { patientApi, visitApi, type Patient } from "../../services/api/endpoints";
import { getErrorMessage } from "../../services/api/errors";

const EMPTY = { full_name: "", date_of_birth: "", gender: "male", phone: "", consent_given: false };

export default function PatientsListPage() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [q, setQ] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<any>(EMPTY);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);
  const searchTimer = useRef<number | undefined>(undefined);

  const load = (query = "") => patientApi.list(query).then((r) => setPatients(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);
  useEffect(() => { if (showForm) nameRef.current?.focus(); }, [showForm]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  // Debounced search so typing stays smooth (one request after you pause).
  const onSearch = (value: string) => {
    setQ(value);
    window.clearTimeout(searchTimer.current);
    searchTimer.current = window.setTimeout(() => load(value), 250);
  };

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    // Explicit validation with clear messages (no silent browser tooltips).
    if (!form.full_name.trim()) return setError("Please enter the patient's full name.");
    if (!form.phone.trim()) return setError("Please enter a phone number.");
    if (!form.consent_given) return setError("Patient consent is required (DPDP Act 2023).");

    setBusy(true);
    try {
      await patientApi.create({
        full_name: form.full_name.trim(),
        phone: form.phone.trim(),
        gender: form.gender,
        consent_given: true,
        date_of_birth: form.date_of_birth || null,   // "" -> null (date of birth is optional)
      });
      setForm(EMPTY); setShowForm(false); load(q);
      toast.success(`${form.full_name.trim()} added`);
    } catch (err: any) {
      setError(getErrorMessage(err, "Could not create patient. Please try again."));
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
        <button className="btn accent" onClick={() => { setError(""); setShowForm((s) => !s); }}>
          {showForm ? "Close" : "+ Add patient"}
        </button>
      </div>

      {showForm && (
        <form className="card" onSubmit={create} noValidate>
          <h3>New patient</h3>
          <div className="grid grid-3">
            <div><label>Full name</label>
              <input ref={nameRef} value={form.full_name} onChange={(e) => set("full_name", e.target.value)} placeholder="e.g. Ravi Sharma" /></div>
            <div><label>Phone</label>
              <input value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="10-digit mobile" inputMode="tel" /></div>
            <div><label>Gender</label>
              <select value={form.gender} onChange={(e) => set("gender", e.target.value)}>
                <option value="male">Male</option><option value="female">Female</option><option value="other">Other</option>
              </select></div>
            <div><label>Date of birth <span className="muted" style={{ fontWeight: 400 }}>(optional)</span></label>
              <input type="date" value={form.date_of_birth} onChange={(e) => set("date_of_birth", e.target.value)} /></div>
          </div>
          <label style={{ marginTop: ".85rem", fontWeight: 400, display: "flex", alignItems: "center", gap: ".45rem" }}>
            <input type="checkbox" style={{ width: "auto" }}
                   checked={form.consent_given} onChange={(e) => set("consent_given", e.target.checked)} />
            Patient has given consent to store their health data (DPDP Act 2023).
          </label>
          {error && <div className="error">{error}</div>}
          <div className="row" style={{ marginTop: ".85rem" }}>
            <button className="btn" disabled={busy}>{busy ? "Saving…" : "Save patient"}</button>
            <button type="button" className="btn secondary" onClick={() => { setShowForm(false); setError(""); }}>Cancel</button>
          </div>
        </form>
      )}

      <div className="card">
        <input placeholder="Search by name or phone…" value={q} onChange={(e) => onSearch(e.target.value)} style={{ marginBottom: ".85rem" }} />
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
