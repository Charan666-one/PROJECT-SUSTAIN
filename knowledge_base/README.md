# Knowledge Base — RAG Source Documents

## Structure

```
materia_medica/        — Homeopathic materia medica texts (curated, indexed)
clinical_guidelines/   — Treatment protocols and dosage guidelines
treatment_protocols/   — Condition-specific treatment frameworks
uploads/               — Doctor personal notes and reference documents (per-doctor)
```

## Indexing
Run `scripts/seed/index_knowledge_base.py` to embed and index documents into Qdrant.
New documents dropped into these folders are auto-indexed nightly.

## Sources to include
- Boericke Materia Medica
- Kent Repertory excerpts (public domain)
- Clarke Dictionary excerpts (public domain)
- AYUSH clinical guidelines
- Practitioner-authored reference sheets
