from types import SimpleNamespace
from app.services.pdf import build_prescription_pdf


def test_generates_valid_pdf_bytes():
    presc = SimpleNamespace(
        remedies=[{"name": "Arsenicum Album", "potency": "30C", "dosage": "3 pills",
                   "frequency": "twice daily", "duration": "5 days"}],
        dietary_advice="Avoid coffee", lifestyle_advice=None,
        precautions="Return if fever rises", notes=None,
    )
    doctor = SimpleNamespace(full_name="A Sharma", clinic_name="Sharma Homeopathy",
                             clinic_address="MG Road", registration_no="AYUSH123")
    patient = SimpleNamespace(full_name="R Kumar", phone="9999999999")
    pdf = build_prescription_pdf(presc, doctor, patient)
    assert pdf.startswith(b"%PDF-1.4")
    assert pdf.rstrip().endswith(b"%%EOF")
