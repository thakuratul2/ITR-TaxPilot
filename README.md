# ITR-TaxPilot

> AI-powered Indian Income Tax Return analysis and assistance platform.

ITR-TaxPilot is designed to let a user upload a Form 16 and receive a clear, explainable estimate of their income-tax position for the selected Assessment Year, including extracted income details, applicable deductions, tax-regime comparison where supported, estimated tax/refund, and an ITR-form recommendation.

The long-term product can expand to AIS, Form 26AS, capital gains, deductions, multiple income sources, tax-document reconciliation, and guided ITR preparation.

---

## 1. Product Vision

### Core idea

**Upload Form 16 → understand the data → validate it → apply the correct tax rules → calculate tax deterministically → recommend the appropriate ITR → explain the result with AI.**

The product must prioritize **accuracy, traceability, privacy, and explainability** over flashy AI behavior.

### Primary MVP user journey

1. User opens TaxPilot.
2. User uploads Form 16 PDF.
3. Backend validates the file.
4. Document processor extracts text/tables.
5. AI extracts structured tax information.
6. Extraction is validated using strict schemas and deterministic checks.
7. Tax engine applies the rules for the selected Assessment Year.
8. ITR eligibility engine recommends an ITR form based on known facts and applicable rules.
9. Explanation AI explains the result in simple language.
10. User sees a tax summary and can download a report.

---

## 2. Critical Architecture Principle

### AI does NOT own the final tax calculation.

The system must separate responsibilities into three major layers:

### A. Document Intelligence

Use Gemini/Claude through a controlled AI abstraction layer to understand documents and extract structured values.

Example:

```text
Form 16 PDF
    ↓
PDF/Text/OCR extraction
    ↓
AI extraction
    ↓
Strict Pydantic schema
    ↓
Validated Form16Data
```

### B. Tax Engine

The final tax calculation must be deterministic Python code driven by versioned Assessment Year rules.

```text
Validated taxpayer data
        ↓
AY-specific rules
        ↓
Tax regime rules
        ↓
Income computation
        ↓
Deductions
        ↓
Tax slabs
        ↓
Rebate / surcharge where applicable
        ↓
Health & Education Cess where applicable
        ↓
TDS credit
        ↓
Tax payable / refund
```

### C. Explanation Intelligence

Claude or another approved model may explain the deterministic result, identify missing information, and answer user questions. It must not silently change the calculation produced by the tax engine.

---

## 3. Technology Stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic / Pydantic Settings
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- LangChain where orchestration genuinely adds value

### AI

- Anthropic Claude
- Google Gemini
- AI provider abstraction so models can be replaced without changing business logic
- Structured JSON outputs
- Prompt versioning
- AI validation and fallback strategy

### Document processing

- PyMuPDF / fitz for PDF text extraction
- Table extraction where required
- OCR fallback for scanned PDFs
- File-type and content validation

### Infrastructure

- Docker
- Docker Compose for local development
- Nginx/reverse proxy for production where appropriate
- Environment-based configuration

### Frontend

The initial UI may be implemented as a simple modern web application. Keep the frontend independent from the tax engine and AI provider implementation.

### Testing

- pytest
- FastAPI test client
- Unit tests for every tax-rule component
- Golden/sample Form 16 fixtures
- AI extraction validation tests
- API integration tests

---

## 4. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │      Frontend       │
                         │ Upload / Results UI │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │   REST API Layer    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
              ┌──────────┐   ┌────────────┐   ┌────────────┐
              │ Document │   │ AI Service │   │ Tax Engine │
              │ Service  │   │  Layer     │   │  (Python)  │
              └────┬─────┘   └─────┬──────┘   └─────┬──────┘
                   │               │                │
                   ▼               ▼                ▼
              PDF/OCR        Claude/Gemini     AY Rules
                                                   │
                                                   ▼
                                              ITR Engine

                    ┌───────────────────────────────────┐
                    │ PostgreSQL │ Redis │ Object Store │
                    └───────────────────────────────────┘
```

---

# 5. Development Phases

Development must happen sequentially. Do not build future features before the current phase is working and tested.

---

## Phase 0 — Project Rules & Foundation

### Goal

Create a clean, maintainable repository and development contract.

### Tasks

- Create backend/frontend directory structure.
- Configure Python environment.
- Add dependency management.
- Add `.env.example`.
- Add `.gitignore`.
- Add Dockerfile(s).
- Add Docker Compose.
- Configure FastAPI application factory.
- Configure structured logging.
- Add health endpoint.
- Add basic pytest setup.
- Add README and development documentation.
- Add formatting/linting configuration.

### Definition of Done

```text
GET /health
```

returns a healthy response and the complete application starts through Docker Compose.

---

## Phase 1 — Backend Core

### Goal

Build the API foundation before adding AI.

### Tasks

- FastAPI routing.
- API versioning: `/api/v1/...`.
- Pydantic request/response schemas.
- Central exception handling.
- Request validation.
- Logging and correlation/request IDs.
- Configuration management.
- PostgreSQL connection.
- SQLAlchemy models.
- Alembic migrations.
- Redis connection and health check.

### Initial endpoints

```text
GET  /health
GET  /api/v1/health
POST /api/v1/documents/form16
GET  /api/v1/jobs/{job_id}
GET  /api/v1/analysis/{analysis_id}
```

Do not expose internal AI prompts or API keys through endpoints.

---

## Phase 2 — Form 16 Upload & Document Pipeline

### Goal

Accept a Form 16 PDF safely and convert it into machine-readable content.

### Flow

```text
Upload PDF
   ↓
File validation
   ↓
Malware/content safety checks as applicable
   ↓
PDF parsing
   ↓
Text extraction
   ↓
Table extraction
   ↓
OCR fallback if required
   ↓
Document classification
   ↓
Normalized document representation
```

### Validation

- Accept PDF only for MVP.
- Validate MIME type and actual file signature.
- Limit file size.
- Reject malformed PDFs.
- Reject unsupported document types.
- Do not trust the filename alone.
- Do not store files indefinitely.

### Definition of Done

Given a valid Form 16, the service produces normalized text/content suitable for structured extraction.

---

## Phase 3 — AI Extraction Layer

### Goal

Extract Form 16 data into a strict, predictable schema.

### AI responsibilities

AI may identify:

- Assessment Year
- Financial Year where present
- Employee name
- PAN, where present
- Employer information
- Gross salary
- Salary components
- Standard deduction where explicitly shown
- Professional tax where applicable
- TDS
- Taxable salary/income fields present in the document
- Other Form 16-relevant fields
- Part A and Part B information

### Important rule

The model must return **structured data**, not prose.

Example conceptual schema:

```json
{
  "document_type": "FORM_16",
  "assessment_year": "2026-27",
  "employee": {
    "name": "...",
    "pan": "..."
  },
  "salary": {
    "gross_salary": 0,
    "standard_deduction": 0,
    "professional_tax": 0
  },
  "tax": {
    "tds": 0
  },
  "confidence": {
    "gross_salary": 0.99,
    "tds": 0.99
  }
}
```

The actual schema must be designed from authoritative Form 16 structures and real sample documents rather than guessed fields.

### AI provider strategy

Create an abstraction such as:

```text
AIProvider
 ├── ClaudeProvider
 └── GeminiProvider
```

The business logic must not directly depend on a specific model.

### Verification strategy

For important fields:

```text
AI extraction
      ↓
Schema validation
      ↓
Document consistency checks
      ↓
Optional second-model verification
      ↓
Validated data
```

AI disagreement must produce a review/uncertainty state, not a silently fabricated value.

---

## Phase 4 — Validation & Data Normalization

### Goal

Make extracted information trustworthy enough for deterministic calculation.

### Checks

- Required fields present.
- Numeric values are valid.
- Currency values are non-negative where appropriate.
- Assessment Year format is valid.
- TDS values are consistent with extracted document data.
- Duplicate fields are reconciled.
- Part A and Part B information are cross-checked where possible.
- Arithmetic relationships in the document are checked where applicable.
- Low-confidence fields are flagged.

### Rule

Never convert missing information into zero unless the document/rule explicitly supports that interpretation.

Distinguish:

```text
0
```

from:

```text
unknown / not found
```

This distinction is critical for tax accuracy.

---

# Phase 5 — Assessment Year Rule Engine

### Goal

Create a versioned tax-rule system.

The tax engine must never contain a single permanent hard-coded set of tax rules.

Recommended structure:

```text
app/tax/
├── engine.py
├── models.py
├── calculator.py
├── itr_selector.py
├── rules/
│   ├── common/
│   ├── ay_2025_26/
│   ├── ay_2026_27/
│   └── ay_2027_28/
└── tests/
```

Only implement an Assessment Year after its rules have been verified from authoritative sources.

### Rule categories

Depending on applicability:

- Tax regimes
- Income tax slabs
- Standard deduction
- Rebate rules
- Surcharge rules
- Cess
- Deduction eligibility
- Salary income computation
- TDS credit
- Total tax liability
- Refund/tax payable
- ITR eligibility

### Critical requirement

Every rule should have:

- Assessment Year
- Rule source/reference metadata
- Effective period
- Unit tests
- Clear implementation

Do not let an LLM invent tax rules.

---

# Phase 6 — Deterministic Tax Calculation Engine

### Goal

Calculate the taxpayer's result using validated data and versioned rules.

### Conceptual flow

```text
Form16Data
    ↓
Income computation
    ↓
Eligible deductions
    ↓
Taxable income
    ↓
Tax regime calculation
    ↓
Rebate / surcharge / cess as applicable
    ↓
Gross tax liability
    ↓
TDS credit
    ↓
Final payable/refund
```

### Required characteristics

- Deterministic.
- Reproducible.
- Unit tested.
- Explainable.
- Versioned by Assessment Year.
- No direct LLM arithmetic.
- No hidden assumptions.

### Calculation result should contain an audit trail

Example:

```text
Gross salary:                 ₹X
Less: eligible deduction:     ₹Y
Taxable income:               ₹Z
Tax before rebate:            ₹A
Rebate:                       ₹B
Cess:                         ₹C
Total tax:                    ₹D
TDS credit:                   ₹E
Final payable/refund:         ₹F
```

The exact fields must be determined by the applicable tax rules.

---

# Phase 7 — Tax Regime Comparison

Where the taxpayer is eligible and the necessary information is available, calculate supported regimes independently.

```text
Regime A calculation
        │
        ├── Tax
        └── Refund/payable

Regime B calculation
        │
        ├── Tax
        └── Refund/payable
```

Then present:

- Tax under each regime.
- Difference.
- Key assumptions.
- Which option appears more beneficial based on the supplied data.

Do not claim that one regime is universally better without considering the required inputs and eligibility rules.

---

# Phase 8 — ITR Recommendation Engine

### Goal

Recommend an appropriate ITR form based on deterministic eligibility rules.

### Conceptual input

```text
Income sources
Employment income
Business/professional income
Capital gains
Other sources
Residential status
Asset/foreign-income indicators
Applicable legal conditions
```

### Output

```json
{
  "recommended_itr": "ITR-1",
  "confidence": "high",
  "reasons": [
    "Salary income detected",
    "No business income detected"
  ],
  "limitations": [
    "Recommendation is based only on supplied information"
  ]
}
```

The recommendation must be treated as an eligibility analysis, not a guarantee that filing is complete or legally compliant.

---

# Phase 9 — Explanation AI

### Goal

Make the deterministic result understandable to a normal user.

Example user question:

> Why is my tax refund this amount?

The system should answer from structured calculation results and verified source data.

### Explanation architecture

```text
Tax Engine Result
       ↓
Structured explanation context
       ↓
Claude
       ↓
Simple explanation
```

### Guardrails

The explanation model must:

- Never alter tax-engine numbers.
- Never invent deductions.
- Never invent income.
- Never invent tax rules.
- Clearly state missing information.
- Clearly distinguish estimate from final filing outcome.

---

# Phase 10 — Redis & Job Processing

### Goal

Make document analysis asynchronous and scalable.

Use Redis for:

- Job state.
- Temporary processing state.
- Rate limiting.
- Short-lived cache where appropriate.
- Coordination for background work.

Example:

```text
POST /documents/form16
        ↓
job_id = abc123
        ↓
Redis: PROCESSING
        ↓
Document extraction
        ↓
AI extraction
        ↓
Tax calculation
        ↓
Redis: COMPLETED
```

Do not store sensitive document contents in Redis unnecessarily.

---

# Phase 11 — Frontend MVP

### Goal

Build a simple, professional user experience.

### Screen 1 — Landing / Upload

```text
ITR-TaxPilot

Understand your tax from Form 16

[ Upload Form 16 ]

Secure • Simple • AI-assisted
```

### Screen 2 — Processing

```text
Uploading Form 16...
Reading document...
Extracting tax information...
Validating information...
Calculating tax...
Preparing your result...
```

### Screen 3 — Result

```text
Tax Summary

Assessment Year: XXXX-XX

Gross Income        ₹XX,XX,XXX
Deductions          ₹XX,XXX
Taxable Income      ₹XX,XX,XXX
Tax                ₹XX,XXX
TDS                ₹XX,XXX

Estimated Refund / Payable
₹XX,XXX

Recommended ITR
ITR-X

[View Calculation]
[Download Report]
```

### UI principles

- Clean.
- Minimal.
- No unnecessary graphs.
- No excessive animations.
- Focus on numbers and explanations.
- Show assumptions and missing information clearly.

---

# Phase 12 — Report Generation

Generate a downloadable analysis report containing:

- Assessment Year.
- Extracted Form 16 summary.
- Income calculation.
- Deductions used.
- Tax regime comparison where applicable.
- Tax calculation breakdown.
- TDS.
- Estimated refund/payable.
- ITR recommendation.
- Assumptions.
- Missing information.
- Disclaimer.

The report must be generated from deterministic application data, not copied blindly from an LLM response.

---

# Phase 13 — Security & Privacy

This application processes highly sensitive financial and identity information.

### Mandatory controls

- Never log PAN.
- Never log complete Form 16 contents.
- Never expose API keys to the frontend.
- Store secrets only in environment/secret management systems.
- Validate uploaded files.
- Limit file size.
- Delete temporary files after processing where possible.
- Encrypt stored documents if persistent storage is introduced.
- Use HTTPS in production.
- Implement authentication before persistent user accounts are introduced.
- Implement authorization for user-owned analysis data.
- Apply rate limiting.
- Avoid storing AI prompts/responses containing sensitive data unless required.
- Define retention and deletion policies.

### Privacy principle

**Collect the minimum data necessary to perform the requested analysis.**

---

# Phase 14 — Testing & Quality Assurance

Accuracy is the highest priority.

### Unit tests

Test:

- Every tax calculation function.
- Every Assessment Year rule.
- Tax slab boundaries.
- Rebate boundaries.
- Deduction limits.
- Cess/surcharge behavior where applicable.
- TDS/refund calculations.
- ITR eligibility rules.

### Document tests

Create anonymized/sample Form 16 fixtures covering:

- Normal text PDFs.
- Different layouts.
- Multiple employers where relevant.
- Missing optional fields.
- Scanned PDFs.
- OCR-required documents.
- Low-quality documents.
- Different salary structures.

### AI tests

Test:

- Correct extraction.
- Missing fields.
- Wrong field placement.
- Numeric formatting.
- OCR errors.
- Model disagreement.
- Malformed JSON.
- Hallucinated values.

### Golden tests

Maintain expected structured extraction and expected deterministic tax results for approved test documents.

AI changes must not silently change deterministic tax results.

---

# Phase 15 — Observability

Add:

- Structured logs.
- Request IDs.
- Job IDs.
- Processing duration.
- AI provider/model metadata without sensitive prompt contents.
- Extraction success/failure metrics.
- Tax engine errors.
- API latency.
- Redis/PostgreSQL health.

Never put sensitive taxpayer data into monitoring systems.

---

# Phase 16 — Production Deployment

### Target architecture

```text
Internet
   ↓
HTTPS / Reverse Proxy
   ↓
Frontend
   ↓
FastAPI
   ├── PostgreSQL
   ├── Redis
   ├── Document Processing
   └── AI Providers
```

### Deployment requirements

- Docker images.
- Environment-specific configuration.
- Health checks.
- Database migrations.
- Secret management.
- HTTPS.
- Backups for persistent data.
- Resource limits.
- Monitoring.
- Error handling.
- Safe document retention/deletion.

---

# Phase 17 — Future Expansion

Do not implement these during the initial MVP unless explicitly requested.

### Additional tax documents

- AIS.
- Form 26AS.
- Salary slips.
- Investment proofs.
- Capital gains statements.
- Bank interest information.

### Additional tax scenarios

- Multiple employers.
- Capital gains.
- Rental income.
- Other sources.
- Business/professional income.
- Foreign income/assets where legally applicable.
- Multiple tax regimes and advanced comparisons.

### Advanced product features

- User accounts.
- Historical tax analyses.
- Secure document vault.
- Tax-saving suggestions.
- Guided ITR preparation.
- CA review workflow.
- Professional dashboard.
- Team/workspace support.
- Subscription/payment system.
- Filing integration, only after legal, technical, and authorization requirements are properly established.

---

# 6. AI Model Responsibilities

## Gemini

Preferred for document understanding/extraction where it provides strong document handling.

Responsibilities may include:

- Form 16 classification.
- Field extraction.
- Table understanding.
- OCR/document interpretation.

## Claude

Preferred for:

- Extraction verification.
- Reasoning over structured tax context.
- User-friendly explanations.
- Identifying ambiguities and missing information.

Claude must not override the deterministic tax engine.

## Codex

Codex is a **development-time engineering agent**, not a taxpayer-facing runtime calculator.

Use it for:

- Implementing features.
- Refactoring.
- Writing tests.
- Reviewing code.
- Debugging.
- Improving documentation.
- Maintaining tax-rule implementations after authoritative requirements are established.

Codex must not independently invent tax law or modify tax calculations without tests and verified requirements.

---

# 7. LangChain Usage Rules

LangChain should be used only where it provides real value.

Potential uses:

```text
Document context
      ↓
Structured extraction chain
      ↓
Validation
      ↓
Verification chain
      ↓
Explanation chain
```

Do not introduce unnecessary agent loops.

Avoid architectures where an LLM autonomously decides every application action.

Prefer explicit workflows and typed state.

---

# 8. API Design Principles

All APIs should:

- Use `/api/v1` versioning.
- Return consistent JSON structures.
- Validate all input.
- Use appropriate HTTP status codes.
- Avoid leaking internal exceptions.
- Never return secrets.
- Never return raw provider errors directly.
- Never return unnecessary sensitive document data.

Example response structure:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "..."
}
```

For errors:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORM16_INVALID",
    "message": "The uploaded document could not be processed."
  },
  "request_id": "..."
}
```

---

# 9. Suggested Repository Structure

```text
ITR-TaxPilot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── documents/
│   │   ├── ai/
│   │   │   ├── providers/
│   │   │   ├── prompts/
│   │   │   └── chains/
│   │   ├── tax/
│   │   │   ├── engine.py
│   │   │   ├── models.py
│   │   │   ├── itr_selector.py
│   │   │   └── rules/
│   │   └── cache/
│   │       └── redis.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│
├── docs/
│   ├── architecture.md
│   ├── tax-rules.md
│   ├── security.md
│   └── api.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

The exact structure may evolve, but responsibilities must remain separated.

---

# 10. Environment Variables

Use `.env.example`, never commit real secrets.

Conceptual variables:

```env
APP_ENV=development
APP_NAME=ITR-TaxPilot

DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://...

ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

MAX_UPLOAD_SIZE_MB=10
DOCUMENT_RETENTION_MINUTES=30
```

Never commit:

- API keys.
- Database passwords.
- Production credentials.
- User documents.
- PAN/Aadhaar/financial information.

---

# 11. Git & Development Workflow

Use small, focused commits.

Recommended commit style:

```text
feat: add Form 16 upload endpoint
feat: add Form 16 extraction schema
feat: add AY 2026-27 tax engine
fix: correct rebate calculation boundary
test: add Form 16 extraction fixtures
docs: update tax engine architecture
refactor: isolate AI provider abstraction
```

For larger changes:

```text
main
  │
  ├── feature/form16-upload
  ├── feature/ai-extraction
  ├── feature/tax-engine
  └── feature/frontend-mvp
```

Do not push experimental secrets or generated sensitive documents.

---

# 12. Development Rules for Antigravity / AI Coding Agents

This section is mandatory for any AI coding agent working on the repository.

### Rule 1 — Read before changing

Before implementing a feature:

1. Read this README.
2. Inspect the existing repository.
3. Identify the current phase.
4. Inspect related code/tests.
5. Reuse existing architecture where appropriate.

### Rule 2 — Work phase-by-phase

Do not jump from Phase 0 to advanced filing integration.

Complete the current phase before introducing future functionality.

### Rule 3 — Do not invent tax rules

For tax calculations:

- Use authoritative requirements.
- Record rule/source metadata.
- Write tests.
- Do not rely on model memory for tax-law values.

### Rule 4 — AI must not replace deterministic business logic

Do not ask Claude/Gemini to directly produce the final tax amount when Python can calculate it.

### Rule 5 — No unnecessary complexity

Avoid:

- Unnecessary microservices.
- Unnecessary agents.
- Unnecessary queues.
- Unnecessary vector databases.
- Complex graphs for a simple Form 16 workflow.

Start with a modular monolith. Split services only when there is a demonstrated need.

### Rule 6 — Tests are required

Every important business rule must have tests.

### Rule 7 — Protect taxpayer data

Never expose sensitive user information in logs, error messages, tests, commits, screenshots, or monitoring.

### Rule 8 — Explain assumptions

If information is missing, show it as missing. Do not silently guess.

### Rule 9 — Keep provider abstraction

Do not hard-code Claude/Gemini calls throughout the codebase. Use a provider abstraction.

### Rule 10 — Verify before claiming completion

Before marking a feature complete:

```text
Run tests
   ↓
Run lint/type checks
   ↓
Run Docker build
   ↓
Run API smoke tests
   ↓
Review security implications
   ↓
Update documentation
```

---

# 13. MVP Definition

The MVP is complete when all of the following work reliably:

- [ ] User can upload a valid Form 16 PDF.
- [ ] Invalid files are rejected safely.
- [ ] Text/tables can be extracted.
- [ ] Form 16 is detected.
- [ ] Structured fields are extracted.
- [ ] Pydantic validation works.
- [ ] Missing/uncertain fields are clearly identified.
- [ ] Supported Assessment Year rules are implemented and tested.
- [ ] Deterministic tax calculation works.
- [ ] TDS is incorporated correctly.
- [ ] Refund/payable is calculated correctly for supported scenarios.
- [ ] Supported tax regimes can be compared where applicable.
- [ ] ITR recommendation is rule-based.
- [ ] AI explanation uses the deterministic result.
- [ ] Redis job processing works.
- [ ] PostgreSQL persistence works where needed.
- [ ] Docker Compose starts the system.
- [ ] Security controls are implemented.
- [ ] Automated tests pass.
- [ ] Sample Form 16 scenarios pass expected results.

---

# 14. MVP Non-Goals

Do **not** include these in the first MVP unless explicitly approved:

- Direct ITR filing.
- Complete tax-portal automation.
- Payment gateway.
- Subscription billing.
- Full CA practice management.
- Complex capital-gain engine.
- Business income engine.
- Foreign income/asset workflows.
- Large enterprise multi-tenant architecture.
- Autonomous AI agents making legal/tax decisions.

---

# 15. Accuracy & Safety Disclaimer

ITR-TaxPilot is intended to provide AI-assisted tax analysis and estimates based on information supplied by the user and the rules implemented for the selected Assessment Year.

The application must clearly communicate that:

- An estimate is not necessarily a final filed return.
- Missing documents/information can change the result.
- Tax rules may change.
- Users should verify important information before filing.
- Professional tax advice may be appropriate for complex situations.

The product must never present an uncertain AI output as a guaranteed legal or tax conclusion.

---

# 16. Recommended First Build Sequence

The first implementation should follow exactly this order:

```text
1. Repository foundation
2. Docker + Docker Compose
3. FastAPI application
4. PostgreSQL
5. Redis
6. Health checks
7. Form 16 upload
8. PDF extraction
9. Form 16 detection
10. Pydantic extraction schema
11. Gemini/Claude provider abstraction
12. AI extraction
13. Extraction validation
14. Assessment Year rule module
15. Deterministic tax engine
16. Tax calculation tests
17. ITR recommendation engine
18. Claude explanation layer
19. Job processing
20. Simple frontend
21. Report generation
22. Security hardening
23. Integration tests
24. Production Docker setup
```

---

# 17. Success Criteria

TaxPilot should feel like this to the user:

> **I upload my Form 16, and TaxPilot clearly tells me what information it found, how my tax was calculated, what I may receive/pay, which ITR form appears applicable, and why.**

The system should feel:

- Fast.
- Professional.
- Transparent.
- Easy to understand.
- Technically robust.
- Privacy-conscious.
- AI-assisted but not AI-dependent for deterministic tax calculations.

---

# 18. Final Engineering Principle

```text
AI understands.
Code calculates.
Rules decide.
AI explains.
Tests verify.
Humans remain in control.
```

That is the core engineering philosophy of **ITR-TaxPilot**.
