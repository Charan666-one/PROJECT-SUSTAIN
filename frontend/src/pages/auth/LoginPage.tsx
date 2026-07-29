import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../../services/api/endpoints";
import { useAuthStore } from "../../store/slices/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ full_name: "", clinic_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      if (mode === "register") {
        await authApi.register({
          full_name: form.full_name, clinic_name: form.clinic_name,
          email: form.email, password: form.password,
        });
      }
      const { data } = await authApi.login(form.email, form.password);
      // Set token first so the /me request is authenticated.
      login({ id: "", full_name: form.full_name, email: form.email }, data.access_token);
      const me = await authApi.me();
      login(me.data, data.access_token);
      navigate("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Something went wrong. Check your details and try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="center-screen">
      <form className="card auth-card" onSubmit={submit}>
        <h2 style={{ color: "var(--primary)" }}>Homoeo CDSS</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          {mode === "login" ? "Sign in to your clinic" : "Create your clinic account"}
        </p>

        {mode === "register" && (
          <>
            <label>Full name</label>
            <input value={form.full_name} onChange={(e) => set("full_name", e.target.value)} required />
            <label>Clinic name</label>
            <input value={form.clinic_name} onChange={(e) => set("clinic_name", e.target.value)} />
          </>
        )}
        <label>Email</label>
        <input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} required />
        <label>Password</label>
        <input type="password" value={form.password} onChange={(e) => set("password", e.target.value)}
               required minLength={8} />

        {error && <div className="error">{error}</div>}

        <button className="btn" style={{ width: "100%", marginTop: "1rem", justifyContent: "center" }}
                disabled={busy}>
          {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
        </button>

        <p className="muted" style={{ textAlign: "center", marginTop: ".9rem" }}>
          {mode === "login" ? "New clinic? " : "Already registered? "}
          <a href="#" onClick={(e) => { e.preventDefault(); setError(""); setMode(mode === "login" ? "register" : "login"); }}>
            {mode === "login" ? "Create an account" : "Sign in"}
          </a>
        </p>
      </form>
    </div>
  );
}
