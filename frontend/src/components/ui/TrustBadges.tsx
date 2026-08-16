import { ShieldCheck, Lock, Stethoscope } from "lucide-react";

/** Compact trust signals for the login screens. */
export default function TrustBadges() {
  const items = [
    { Icon: ShieldCheck, label: "DPDP Act 2023 aligned" },
    { Icon: Lock, label: "Encrypted & audit-logged" },
    { Icon: Stethoscope, label: "Doctor-directed AI" },
  ];
  return (
    <div className="trust-badges">
      {items.map(({ Icon, label }) => (
        <span key={label} className="trust-badge"><Icon size={14} /> {label}</span>
      ))}
    </div>
  );
}
