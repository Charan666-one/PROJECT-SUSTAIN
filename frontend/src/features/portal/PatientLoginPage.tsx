import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { portalAuth } from "../../services/api/portal";
import { usePatientAuthStore } from "../../store/slices/patientAuthStore";
import { getErrorMessage } from "../../services/api/errors";

export default function PatientLoginPage() {
  const navigate = useNavigate();
  const login = usePatientAuthStore((s) => s.login);
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      const { data } = await portalAuth.login(phone.trim(), code.trim());
      login({ id: "", full_name: "", phone, gender: "" }, data.access_token);
      const me = await portalAuth.me();
      login(me.data, data.access_token);
      navigate("/portal");
    } catch (err: any) {
      setError(getErrorMessage(err, "Could not sign in. Check your phone number and access code."));
    } finally { setBusy(false); }
  };

  return (
    <div className="center-screen">
      <div className="auth-shell">
        <aside className="auth-brand">
          <div className="mark">SUSTAIN<small>Patient Portal</small></div>
          <div className="lead">Your treatment, in your pocket.</div>
          <div className="sub">See your prescription, track your recovery, and tell your doctor how you're feeling.</div>
          <div className="dots"><i /><i /><i /></div>
        </aside>
        <form className="auth-panel" onSubmit={submit} noValidate>
          <h2 style={{ marginBottom: ".1rem" }}>Welcome</h2>
          <p className="muted" style={{ marginTop: 0 }}>Sign in with the details your clinic gave you.</p>
          <label>Phone number</label>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} inputMode="tel" placeholder="Registered mobile number" />
          <label>Access code</label>
          <input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" placeholder="6-digit code from your clinic" />
          {error && <div className="error">{error}</div>}
          <button className="btn" style={{ width: "100%", marginTop: "1rem", justifyContent: "center" }} disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
          <p className="muted" style={{ textAlign: "center", marginTop: ".9rem", fontSize: ".82rem" }}>
            Don't have a code? Ask your clinic to share it.
          </p>
          <div style={{ borderTop: "1px solid var(--line)", marginTop: ".6rem", paddingTop: ".9rem", textAlign: "center" }}>
            <Link to="/login" className="muted" style={{ fontSize: ".85rem" }}>
              Are you a clinic / doctor? Sign in here →
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
