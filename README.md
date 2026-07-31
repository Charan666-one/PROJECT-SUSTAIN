# Homoeo CDSS
## Intelligent Homeopathic Clinical Decision Support & Patient Management System

### Quick Start (Docker)
```bash
cp .env.example .env          # fill in API keys + DB credentials
docker-compose up -d
python scripts/seed/index_knowledge_base.py   # seed knowledge base
```

### Run locally without Docker (verified dev path)
The app degrades gracefully: **no Anthropic key** → returns the retrieved evidence
instead of a generated answer; **no Qdrant** → uses a local file-backed vector store;
**no sentence-transformers** → uses a hashing embedder. So you can run the whole
clinical flow on just Python + Postgres.

```bash
# 1. Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
createdb homoeo_dev
export POSTGRES_DB=homoeo_dev POSTGRES_USER=$(whoami) POSTGRES_PASSWORD=""
export ANTHROPIC_API_KEY=""          # optional — set to enable LLM generation
uvicorn app.main:app --reload        # http://localhost:8000/api/docs

# 2. Seed the materia medica knowledge base
cd .. && PYTHONPATH=backend python scripts/seed/index_knowledge_base.py

# 3. Frontend
cd frontend && npm install && npm run dev   # http://localhost:5173

# 4. Tests
cd backend && pytest
```

### The differentiator: Recovery Surveillance
We don't replace the doctor and we don't stop at a one-shot recommendation. After
a prescription is approved, the patient enters **surveillance** — tracked until they
recover. The engine ([`services/surveillance.py`](backend/app/services/surveillance.py)):
- Builds a recovery trajectory from each check-in's wellness score + outcome.
- Classifies anomalies: **aggravation** (expected homeopathic dip), **plateau**,
  **non-response**, **relapse**, **worsening** — each with a triage severity.
- **Adaptively schedules the next check-in** (1 day if worsening, ~5 if improving)
  so surveillance continues until recovery or the doctor closes the episode.
- Recommends the next action and offers a remedy **re-suggestion** — as decision
  support. The doctor takes every action; nothing is autonomous.

See `GET /api/v1/surveillance` (the clinic watchlist) and the Surveillance page in the UI.

### Implementation status
- **Working end-to-end:** auth, multi-tenant patients (DPDP consent), visits, RAG
  recommend → red-flag safety gate → doctor approval → prescription PDF → WhatsApp →
  Day 3/7/30 follow-ups → **recovery surveillance with anomaly detection + adaptive
  scheduling + remedy re-suggestion** → outcome-fed learning loop → clinic analytics.
  Immutable hash-chained audit log on every clinical decision.
- **Stubbed / next:** voice (Whisper wiring), Celery auto-send of follow-ups,
  Alembic migrations, production Qdrant + a full materia medica corpus.

### Architecture
- **Frontend**: React 18 + TypeScript + Vite + PWA (offline-first)
- **Backend**: FastAPI + SQLAlchemy (async) + Celery
- **Primary DB**: PostgreSQL 15
- **Vector DB**: Qdrant (semantic retrieval)
- **LLM**: Claude via Anthropic API (RAG-grounded)
- **Voice**: OpenAI Whisper (multilingual)
- **Messaging**: WhatsApp Business API

### Key Features
- RAG from 3 sources: materia medica + clinic cases + doctor notes
- Red flag detection on every consultation
- Doctor digital approval + legal audit trail
- Automated follow-up at Day 3, 7, 30
- Offline-first PWA
- Multilingual voice input
- WhatsApp prescription delivery
- DPDP Act compliant

### Compliance
- DPDP Act 2023 (India) compliant
- AYUSH Ministry aligned
- All AI outputs require explicit doctor approval
- Immutable audit log for every clinical decision
