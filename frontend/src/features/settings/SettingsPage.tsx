import { useEffect, useState } from "react";
import { authApi, type Doctor } from "../../services/api/endpoints";
import { useAuthStore } from "../../store/slices/authStore";
import { Async } from "../../components/ui/State";

export default function SettingsPage() {
  const setAuth = useAuthStore((s) => s.login);
  const token = useAuthStore((s) => s.token);
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    authApi.me().then((r) => { setDoctor(r.data); if (token) setAuth(r.data, token); })
      .catch(() => setError("Could not load profile")).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Clinic Settings</h1>
      <Async loading={loading} error={error} data={doctor}>
        {(d) => (
          <>
            <div className="card">
              <h3>Doctor profile</h3>
              <Field label="Name" value={`Dr. ${d.full_name}`} />
              <Field label="Email" value={d.email} />
              <Field label="Registration no." value={d.registration_no || "—"} />
              <Field label="Qualifications" value={(d.qualifications || []).join(", ") || "—"} />
            </div>
            <div className="card">
              <h3>Clinic profile</h3>
              <Field label="Clinic" value={d.clinic_name || "—"} />
              <Field label="Languages" value={(d.languages || []).join(", ") || "en"} />
            </div>
            <div className="card">
              <h3>Integrations</h3>
              <p className="muted">
                WhatsApp delivery, voice intake, and the AI model are configured via server
                environment variables (see the README). Editable integration settings are on the roadmap.
              </p>
            </div>
          </>
        )}
      </Async>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="row between" style={{ padding: ".4rem 0", borderBottom: "1px solid var(--border)" }}>
      <span className="muted">{label}</span><span>{value}</span>
    </div>
  );
}
