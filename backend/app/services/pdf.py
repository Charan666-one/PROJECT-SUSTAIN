"""
Prescription PDF generator.

Deliberately dependency-free: emits a valid single-page PDF (Helvetica) by hand,
so no reportlab/weasyprint is required for the pilot. Good enough for a printable
/ shareable prescription; swap for a templated renderer later if needed.
"""
from __future__ import annotations
from datetime import datetime
from typing import List


def _esc(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _wrap(text: str, width: int = 90) -> List[str]:
    out: List[str] = []
    for raw in text.split("\n"):
        line = raw.rstrip()
        while len(line) > width:
            cut = line.rfind(" ", 0, width) or width
            cut = cut if cut > 0 else width
            out.append(line[:cut])
            line = line[cut:].lstrip()
        out.append(line)
    return out


def _pdf_from_lines(lines: List[str]) -> bytes:
    # Build the text stream (start near top, 16pt leading).
    content = ["BT", "/F1 11 Tf", "50 800 Td", "16 TL"]
    for ln in lines:
        content.append(f"({_esc(ln)}) Tj")
        content.append("T*")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF"
    ).encode()
    return bytes(out)


def build_prescription_pdf(prescription, doctor, patient) -> bytes:
    lines: List[str] = []
    lines.append(doctor.clinic_name or "Homeopathy Clinic")
    if doctor.clinic_address:
        lines.extend(_wrap(doctor.clinic_address))
    lines.append(f"Dr. {doctor.full_name}"
                 + (f"  |  Reg: {doctor.registration_no}" if doctor.registration_no else ""))
    lines.append("-" * 90)
    lines.append(f"Date: {datetime.utcnow().strftime('%d %b %Y')}")
    if patient:
        lines.append(f"Patient: {patient.full_name}   Phone: {patient.phone}")
    lines.append("")
    lines.append("PRESCRIPTION (Rx)")
    lines.append("")
    for i, r in enumerate(prescription.remedies or [], 1):
        lines.append(
            f"{i}. {r.get('name','')} {r.get('potency','')} — "
            f"{r.get('dosage','')}, {r.get('frequency','')} for {r.get('duration','')}"
        )
    lines.append("")
    if prescription.dietary_advice:
        lines.extend(_wrap(f"Dietary advice: {prescription.dietary_advice}"))
    if prescription.lifestyle_advice:
        lines.extend(_wrap(f"Lifestyle advice: {prescription.lifestyle_advice}"))
    if prescription.precautions:
        lines.extend(_wrap(f"Precautions: {prescription.precautions}"))
    if prescription.notes:
        lines.extend(_wrap(f"Notes: {prescription.notes}"))
    lines.append("")
    lines.append("-" * 90)
    lines.append("Digitally approved by the practitioner. This is decision-support-assisted care;")
    lines.append("the prescribing practitioner is responsible for all clinical decisions.")
    return _pdf_from_lines(lines)
