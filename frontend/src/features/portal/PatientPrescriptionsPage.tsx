import { useEffect, useState } from "react";
import { portalApi, type PPrescription } from "../../services/api/portal";
import { usePatientAuthStore } from "../../store/slices/patientAuthStore";
import { openPdf } from "../../services/pdf";
import { Async } from "../../components/ui/State";

export default function PatientPrescriptionsPage() {
  const token = usePatientAuthStore((s) => s.token);
  const [data, setData] = useState<PPrescription[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    portalApi.prescriptions().then((r) => setData(r.data)).catch(() => setError("Could not load prescriptions")).finally(() => setLoading(false));
  }, []);

  return (
    <>
      <h1>My prescriptions</h1>
      <Async loading={loading} error={error} data={data}>
        {(list) => list.length === 0 ? <div className="card muted">No prescriptions yet.</div> : (
          <>
            {list.map((p, idx) => (
              <div className="card" key={p.id}>
                <div className="row between">
                  <h3 style={{ margin: 0 }}>{idx === 0 ? "Current prescription" : "Previous prescription"}</h3>
                  <span className="muted" style={{ fontSize: ".8rem" }}>{p.created_at ? new Date(p.created_at).toLocaleDateString() : ""}</span>
                </div>
                <table>
                  <thead><tr><th>Medicine</th><th>Potency</th><th>How to take</th></tr></thead>
                  <tbody>
                    {p.remedies.map((r, i) => (
                      <tr key={i}><td>{r.name}</td><td>{r.potency}</td><td>{[r.dosage, r.frequency, r.duration].filter(Boolean).join(" · ")}</td></tr>
                    ))}
                  </tbody>
                </table>
                {p.dietary_advice && <p className="muted">Diet: {p.dietary_advice}</p>}
                {p.precautions && <p className="muted">Precautions: {p.precautions}</p>}
                <button className="btn secondary sm" style={{ marginTop: ".5rem" }}
                        onClick={() => openPdf(portalApi.pdfUrl(p.id), token)}>Download PDF</button>
              </div>
            ))}
          </>
        )}
      </Async>
    </>
  );
}
