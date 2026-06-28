# Homoeo CDSS
## Intelligent Homeopathic Clinical Decision Support & Patient Management System

### Quick Start
```bash
cp .env.example .env
# Fill in your API keys and DB credentials

docker-compose up -d

# Seed knowledge base
python scripts/seed/index_knowledge_base.py
```

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
