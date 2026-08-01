import { useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/slices/authStore";
import { searchApi } from "../../services/api/endpoints";

const NAV = [
  { section: "Clinical" },
  { to: "/", label: "Dashboard", icon: "◱", end: true },
  { to: "/patients", label: "Patients", icon: "☺" },
  { to: "/consultations", label: "Consultations", icon: "✎" },
  { to: "/surveillance", label: "Surveillance", icon: "❤" },
  { to: "/followups", label: "Follow-ups", icon: "↻" },
  { section: "Knowledge & Insight" },
  { to: "/knowledge", label: "Knowledge Base", icon: "▤" },
  { to: "/analytics", label: "Analytics", icon: "▧" },
  { to: "/audit", label: "Audit Log", icon: "⛨" },
  { section: "Clinic" },
  { to: "/settings", label: "Settings", icon: "⚙" },
];

export default function DoctorShell({ children }: { children: React.ReactNode }) {
  const { doctor, logout } = useAuthStore();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [results, setResults] = useState<any>(null);
  const timer = useRef<number | undefined>(undefined);

  const onSearch = (value: string) => {
    setQ(value);
    window.clearTimeout(timer.current);
    if (value.trim().length < 2) { setResults(null); return; }
    // Debounce so the request fires after you stop typing (keeps typing smooth).
    timer.current = window.setTimeout(async () => {
      try { setResults((await searchApi.query(value)).data); } catch { setResults(null); }
    }, 250);
  };

  const go = (path: string) => { setResults(null); setQ(""); navigate(path); };

  return (
    <div className="shell">
      <aside className="sidebar" aria-label="Doctor navigation">
        <div className="brand">SUSTAIN<small>Clinic OS</small></div>
        {NAV.map((n, i) =>
          "section" in n ? (
            <div className="section" key={`s${i}`}>{n.section}</div>
          ) : (
            <NavLink key={n.to} to={n.to!} end={(n as any).end}
              className={({ isActive }) => (isActive ? "active" : "")}>
              <span className="ico" aria-hidden>{n.icon}</span> {n.label}
            </NavLink>
          )
        )}
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="search-wrap">
            <input aria-label="Global search" placeholder="Search patients, symptoms, remedies…"
              value={q} onChange={(e) => onSearch(e.target.value)} />
            {results && (
              <div className="search-results">
                <SearchGroup title="Patients" rows={results.patients}
                  render={(p: any) => <div key={p.id} className="item" onClick={() => go(`/patients/${p.id}`)}>
                    {p.full_name} · <span className="muted">{p.phone}</span></div>} />
                <SearchGroup title="Consultations" rows={results.visits}
                  render={(v: any) => <div key={v.id} className="item" onClick={() => go(`/consultation/${v.id}`)}>
                    {v.chief_complaint || "Consultation"} · <span className="muted">{v.status}</span></div>} />
                <SearchGroup title="Prescriptions" rows={results.prescriptions}
                  render={(p: any) => <div key={p.id} className="item" onClick={() => go(`/consultation/${p.visit_id}`)}>
                    {p.remedies}</div>} />
                {results.patients.length + results.visits.length + results.prescriptions.length === 0 && (
                  <div className="item muted">No matches for “{results.query}”.</div>
                )}
              </div>
            )}
          </div>
          <div className="who row" style={{ gap: ".6rem" }}>
            <div className="avatar" aria-hidden>{(doctor?.full_name || "D").trim().charAt(0).toUpperCase()}</div>
            <div style={{ lineHeight: 1.15 }}>
              <div style={{ color: "var(--ink)", fontWeight: 600 }}>Dr. {doctor?.full_name}</div>
              <div style={{ fontSize: ".76rem" }}>{doctor?.clinic_name}</div>
            </div>
          </div>
          <button className="btn sm secondary" onClick={() => { logout(); navigate("/login"); }}>Log out</button>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}

function SearchGroup({ title, rows, render }: { title: string; rows: any[]; render: (r: any) => React.ReactNode }) {
  if (!rows || rows.length === 0) return null;
  return (<><div className="grp">{title}</div>{rows.map(render)}</>);
}
