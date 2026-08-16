import { NavLink, useNavigate } from "react-router-dom";
import { Home, Pill, ClipboardCheck, Activity, LogOut } from "lucide-react";
import { usePatientAuthStore } from "../../store/slices/patientAuthStore";

const TABS = [
  { to: "/portal", label: "Home", Icon: Home, end: true },
  { to: "/portal/prescriptions", label: "Prescriptions", Icon: Pill },
  { to: "/portal/checkins", label: "Check-ins", Icon: ClipboardCheck },
  { to: "/portal/timeline", label: "My recovery", Icon: Activity },
];

export default function PatientShell({ children }: { children: React.ReactNode }) {
  const { patient, logout } = usePatientAuthStore();
  const navigate = useNavigate();
  return (
    <div className="portal">
      <header className="portal-top">
        <div className="mark">SUSTAIN<small>Patient</small></div>
        <span className="spacer" />
        <span style={{ fontSize: ".88rem", opacity: .9 }}>{patient?.full_name}</span>
        <button className="btn ghost sm" onClick={() => { logout(); navigate("/portal/login"); }}>
          <LogOut size={14} /> Log out
        </button>
      </header>
      <nav className="portal-tabs" aria-label="Patient navigation">
        {TABS.map((t) => (
          <NavLink key={t.to} to={t.to} end={t.end} className={({ isActive }) => (isActive ? "active" : "")}>
            <t.Icon size={16} /> {t.label}
          </NavLink>
        ))}
      </nav>
      <main className="portal-content">{children}</main>
      <footer className="app-footer" style={{ textAlign: "center", maxWidth: 720, margin: "0 auto" }}>
        Your data is private and encrypted · Cared for by your clinic
      </footer>
    </div>
  );
}
