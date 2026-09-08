import { Link } from "react-router-dom";
import {
  Stethoscope, HeartPulse, Sparkles, Activity, ShieldCheck, ArrowRight,
  ClipboardList, Bell, Users, FileText,
} from "lucide-react";
import { useAuthStore } from "../../store/slices/authStore";
import TrustBadges from "../../components/ui/TrustBadges";

export default function LandingPage() {
  const isDoctor = useAuthStore((s) => s.isAuthenticated);

  return (
    <div className="landing">
      {/* Top nav */}
      <header className="landing-nav">
        <div className="mark">SUSTAIN<small>Clinic OS</small></div>
        <nav className="landing-nav-actions">
          <Link to="/portal/login" className="btn secondary sm">Patient portal</Link>
          {isDoctor
            ? <Link to="/dashboard" className="btn sm">Open dashboard <ArrowRight size={15} /></Link>
            : <Link to="/login" className="btn sm">Doctor sign in <ArrowRight size={15} /></Link>}
        </nav>
      </header>

      {/* Hero */}
      <section className="landing-hero">
        <div className="landing-hero-inner">
          <span className="eyebrow">Clinic OS for AYUSH &amp; homeopathy practices</span>
          <h1>AI-assisted care,<br />directed by <em>you</em>.</h1>
          <p className="lede">
            SUSTAIN runs your whole clinic — patient records, explainable decision support you approve,
            recovery surveillance until your patient is well, and a patient portal that keeps everyone
            in the loop from the first visit to full recovery.
          </p>
          <div className="landing-actions">
            {isDoctor
              ? <Link to="/dashboard" className="btn lg">Open your dashboard <ArrowRight size={18} /></Link>
              : <Link to="/login" className="btn lg">Doctor sign in <ArrowRight size={18} /></Link>}
            <Link to="/portal/login" className="btn secondary lg">I'm a patient</Link>
          </div>
          <TrustBadges />
        </div>
      </section>

      {/* Two-sided value */}
      <section className="landing-section">
        <div className="landing-two">
          <div className="card side-card">
            <div className="side-head"><span className="side-ico doc"><Stethoscope size={20} /></span>
              <h3>For your clinic</h3></div>
            <ul className="ticks">
              <li><Users size={15} /> Patient records with consent &amp; a full treatment timeline</li>
              <li><Sparkles size={15} /> Explainable AI decision support — with sources, that <strong>you</strong> approve</li>
              <li><ShieldCheck size={15} /> Red-flag safety net + tamper-evident audit trail</li>
              <li><Activity size={15} /> Recovery surveillance that flags plateaus &amp; relapses</li>
              <li><FileText size={15} /> Prescriptions as PDF &amp; over WhatsApp</li>
            </ul>
          </div>
          <div className="card side-card">
            <div className="side-head"><span className="side-ico pat"><HeartPulse size={20} /></span>
              <h3>For your patients</h3></div>
            <ul className="ticks">
              <li><FileText size={15} /> Their current &amp; past prescriptions, anytime</li>
              <li><Activity size={15} /> A friendly recovery timeline</li>
              <li><ClipboardList size={15} /> Simple “Better / Same / Worse” check-ins</li>
              <li><Bell size={15} /> Reminders &amp; notifications from the clinic</li>
              <li><ShieldCheck size={15} /> Private &amp; encrypted — never sees AI internals</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Feature row */}
      <section className="landing-section">
        <h2 className="landing-h2">Built for trust</h2>
        <div className="feature-grid">
          <Feature Icon={Sparkles} title="Explainable AI — the doctor decides"
            body="Every suggestion shows the matched symptoms, evidence and sources behind it. Nothing is prescribed without your approval." />
          <Feature Icon={Activity} title="Surveillance until recovery"
            body="We track each patient's trajectory and adaptively schedule check-ins, flagging aggravation, plateau, relapse or worsening." />
          <Feature Icon={ShieldCheck} title="DPDP-aligned & audit-logged"
            body="Consent capture, encryption, and an immutable, tamper-evident record of every clinical decision." />
        </div>
      </section>

      {/* Control strip */}
      <section className="landing-strip">
        <p><strong>You make every clinical decision.</strong> SUSTAIN is decision support — never a replacement for your judgement.</p>
      </section>

      <footer className="app-footer" style={{ textAlign: "center", borderTop: "1px solid var(--line)" }}>
        © {new Date().getFullYear()} SUSTAIN · AI-assisted clinical decision support · DPDP Act 2023 aligned · Every action audit-logged
      </footer>
    </div>
  );
}

function Feature({ Icon, title, body }: { Icon: any; title: string; body: string }) {
  return (
    <div className="feature-card">
      <span className="feature-ico"><Icon size={22} /></span>
      <h3>{title}</h3>
      <p className="muted">{body}</p>
    </div>
  );
}
