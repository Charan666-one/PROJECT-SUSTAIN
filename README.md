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

### Implementation status
- **Working end-to-end:** auth, patients (DPDP consent), visits, RAG recommend →
  red-flag safety gate → doctor approval → prescription PDF → WhatsApp → Day 3/7/30
  follow-ups → outcome-fed learning loop → clinic analytics. Immutable hash-chained
  audit log on every clinical decision.
- **Stubbed / next:** voice (Whisper wiring), Celery auto-send of follow-ups,
  richer patient timeline UI, production Qdrant + real materia medica corpus.

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
