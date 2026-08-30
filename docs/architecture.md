# ITR-TaxPilot System Architecture

## 1. Overview & Core Philosophy

ITR-TaxPilot is structured with a strict separation of concerns across three core pillars:
1. **Document Intelligence**: Extracts structured financial fields from PDF Form 16 documents using AI provider abstractions (Gemini/Claude) and PyMuPDF.
2. **Tax Engine**: 100% deterministic, Python-driven computation based on versioned statutory rules (`app/tax/rules/ay_YYYY_YY/`). **AI is never permitted to perform or modify arithmetic tax calculations.**
3. **Explanation Layer**: Generates human-friendly explanations and highlights assumptions based on deterministic calculation results.

```text
┌────────────────────────┐
│     Form 16 PDF        │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ PyMuPDF / Extraction   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│   AI Provider Layer    │
│ (Gemini / Claude JSON) │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Strict Pydantic Schema │
│   (Data Validation)    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Deterministic Engine   │
│  (AY Rules & Regimes)  │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│   ITR Recommendation   │
│   & AI Explanation     │
└────────────────────────┘
```

## 2. Directory Layout

```text
ITR-TaxPilot/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # REST endpoints (versioned /api/v1)
│   │   ├── core/            # Configuration, logging, security
│   │   ├── db/              # SQLAlchemy sessions and connection engine
│   │   ├── models/          # Database ORM models
│   │   ├── schemas/         # Pydantic schemas (requests, responses, envelopes)
│   │   ├── services/        # Orchestration services
│   │   ├── documents/       # PDF parsing, OCR, and table extraction
│   │   ├── ai/              # Provider abstraction (Claude/Gemini) and prompts
│   │   ├── tax/             # Deterministic tax engine & versioned rules
│   │   └── cache/           # Redis job state and rate limiting
│   ├── tests/               # Pytest suite
│   ├── requirements.txt     # Pinned Python dependencies
│   └── Dockerfile           # Multi-stage container definition
├── frontend/                # Web application UI
├── docs/                    # Architecture and developer documentation
├── milestones/              # Milestone and task specifications
├── docker-compose.yml       # Local stack (Backend, Postgres, Redis)
└── README.md                # Master engineering blueprint
```
