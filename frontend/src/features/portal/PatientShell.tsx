import { NavLink, useNavigate } from "react-router-dom";
import { usePatientAuthStore } from "../../store/slices/patientAuthStore";

export default function PatientShell({ children }: { children: React.ReactNode }) {
  const { patient, logout } = usePatientAuthStore();
  const navigate = useNavigate();
  return (
    <div className="portal">
      <header className="portal-top">
        <div className="mark">SUSTAIN<small>Patient</small></div>
        <span className="spacer" />
        <span style={{ fontSize: ".88rem", opacity: .9 }}>{patient?.full_name}</span>
        <button className="btn ghost sm" onClick={() => { logout(); navigate("/portal/login"); }}>Log out</button>
      </header>
      <nav className="portal-tabs" aria-label="Patient navigation">
        <NavLink to="/portal" end className={({ isActive }) => (isActive ? "active" : "")}>Home</NavLink>
        <NavLink to="/portal/prescriptions" className={({ isActive }) => (isActive ? "active" : "")}>Prescriptions</NavLink>
        <NavLink to="/portal/checkins" className={({ isActive }) => (isActive ? "active" : "")}>Check-ins</NavLink>
        <NavLink to="/portal/timeline" className={({ isActive }) => (isActive ? "active" : "")}>My recovery</NavLink>
      </nav>
      <main className="portal-content">{children}</main>
    </div>
  );
}
