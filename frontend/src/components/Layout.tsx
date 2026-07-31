import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/slices/authStore";

export default function Layout({ children }: { children: React.ReactNode }) {
  const { doctor, logout } = useAuthStore();
  const navigate = useNavigate();

  const onLogout = () => { logout(); navigate("/login"); };

  return (
    <div>
      <nav className="nav">
        <span className="brand">Homoeo CDSS</span>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/patients">Patients</NavLink>
        <NavLink to="/surveillance">Surveillance</NavLink>
        <span className="spacer" />
        <span className="who">Dr. {doctor?.full_name} · {doctor?.clinic_name}</span>
        <button className="btn ghost sm" onClick={onLogout}>Log out</button>
      </nav>
      <div className="container">{children}</div>
    </div>
  );
}
