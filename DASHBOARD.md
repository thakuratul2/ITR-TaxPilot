# 📊 ITR-TaxPilot — Project Execution Dashboard

> Live tracking dashboard for milestones, tasks, active branches, and implementation progress.  
> Governed by the rules in [`README.md`](file:///D:/Projects/ITR-TaxPilot/README.md) and executed via [`EXECUTION_PROMPT.md`](file:///D:/Projects/ITR-TaxPilot/EXECUTION_PROMPT.md).

---

## 📈 Overall Progress Summary

```text
Progress: [█████████████████░░░░░░░░░] 63% (9 / 18 Milestones Completed)
Total Tasks: 123 | Completed: 78 | In Progress: 0 | Pending: 45
Current Active Branch: milestone/m08-tax-regime-comparison
```

---

## 🚦 Milestones Status Table

| # | Milestone | Phase | Target Branch | Tasks | Completed | Status |
|:---:|---|:---:|---|:---:|:---:|:---:|
| **M01** | [Milestone 1 — Project Setup & Foundation](file:///D:/Projects/ITR-TaxPilot/milestones/milestone1-project-setup) | Phase 0 | `milestone/m01-project-setup` | 12 | 12 | 🟢 Completed |
| **M02** | [Milestone 2 — Backend Core & Architecture](file:///D:/Projects/ITR-TaxPilot/milestones/milestone2-backend-core) | Phase 1 | `milestone/m02-backend-core` | 10 | 10 | 🟢 Completed |
| **M03** | [Milestone 3 — Form 16 Upload & Document Pipeline](file:///D:/Projects/ITR-TaxPilot/milestones/milestone3-form16-upload-pipeline) | Phase 2 | `milestone/m03-form16-upload-pipeline` | 8 | 8 | 🟢 Completed |
| **M04** | [Milestone 4 — AI Extraction Layer](file:///D:/Projects/ITR-TaxPilot/milestones/milestone4-ai-extraction-layer) | Phase 3 | `milestone/m04-ai-extraction-layer` | 8 | 8 | 🟢 Completed |
| **M05** | [Milestone 5 — Validation & Data Normalization](file:///D:/Projects/ITR-TaxPilot/milestones/milestone5-validation-and-normalization) | Phase 4 | `milestone/m05-validation-and-normalization` | 7 | 7 | 🟢 Completed |
| **M06** | [Milestone 6 — Assessment Year Rule Engine](file:///D:/Projects/ITR-TaxPilot/milestones/milestone6-assessment-year-rules) | Phase 5 | `milestone/m06-assessment-year-rules` | 7 | 7 | 🟢 Completed |
| **M07** | [Milestone 7 — Deterministic Tax Engine](file:///D:/Projects/ITR-TaxPilot/milestones/milestone7-deterministic-tax-engine) | Phase 6 | `milestone/m07-deterministic-tax-engine` | 13 | 13 | 🟢 Completed |
| **M08** | [Milestone 8 — Tax Regime Comparison](file:///D:/Projects/ITR-TaxPilot/milestones/milestone8-tax-regime-comparison) | Phase 7 | `milestone/m08-tax-regime-comparison` | 5 | 5 | 🟢 Completed |
| **M09** | [Milestone 9 — ITR Recommendation Engine](file:///D:/Projects/ITR-TaxPilot/milestones/milestone9-itr-recommendation-engine) | Phase 8 | `milestone/m09-itr-recommendation-engine` | 6 | 0 | ⚪ Pending |
| **M10** | [Milestone 10 — Explanation AI & Guardrails](file:///D:/Projects/ITR-TaxPilot/milestones/milestone10-explanation-ai) | Phase 9 | `milestone/m10-explanation-ai` | 6 | 0 | ⚪ Pending |
| **M11** | [Milestone 11 — Redis & Job Processing](file:///D:/Projects/ITR-TaxPilot/milestones/milestone11-redis-job-processing) | Phase 10 | `milestone/m11-redis-job-processing` | 6 | 0 | ⚪ Pending |
| **M12** | [Milestone 12 — Frontend MVP](file:///D:/Projects/ITR-TaxPilot/milestones/milestone12-frontend-mvp) | Phase 11 | `milestone/m12-frontend-mvp` | 8 | 8 | 🟢 Completed |
| **M13** | [Milestone 13 — Report Generation](file:///D:/Projects/ITR-TaxPilot/milestones/milestone13-report-generation) | Phase 12 | `milestone/m13-report-generation` | 5 | 0 | ⚪ Pending |
| **M14** | [Milestone 14 — Security & Privacy](file:///D:/Projects/ITR-TaxPilot/milestones/milestone14-security-and-privacy) | Phase 13 | `milestone/m14-security-and-privacy` | 8 | 0 | ⚪ Pending |
| **M15** | [Milestone 15 — Testing & Quality Assurance](file:///D:/Projects/ITR-TaxPilot/milestones/milestone15-testing-and-qa) | Phase 14 | `milestone/m15-testing-and-qa` | 6 | 0 | ⚪ Pending |
| **M16** | [Milestone 16 — Observability & Monitoring](file:///D:/Projects/ITR-TaxPilot/milestones/milestone16-observability-monitoring) | Phase 15 | `milestone/m16-observability-monitoring` | 4 | 0 | ⚪ Pending |
| **M17** | [Milestone 17 — Production Deployment](file:///D:/Projects/ITR-TaxPilot/milestones/milestone17-production-deployment) | Phase 16 | `milestone/m17-production-deployment` | 5 | 0 | ⚪ Pending |
| **M18** | [Milestone 18 — Future Expansion (Post-MVP)](file:///D:/Projects/ITR-TaxPilot/milestones/milestone18-future-expansion) | Phase 17 | `milestone/m18-future-expansion` | 6 | 0 | ⚪ Pending |

---

## 📌 Milestone Detailed Status

### [Milestone 8 — Tax Regime Comparison](file:///D:/Projects/ITR-TaxPilot/milestones/milestone8-tax-regime-comparison)
- **Branch:** `milestone/m08-tax-regime-comparison`
- **Status:** `Completed`
- **Tasks Completed:** 5 / 5
  - [x] `TASK-8.1`: Parallel Old vs New Regime calculator (`backend/app/comparison/comparison_engine.py`)
  - [x] `TASK-8.2`: Net tax liability difference & savings analysis (`take_home_analysis`)
  - [x] `TASK-8.3`: Deduction breakeven threshold analysis (`backend/app/comparison/breakeven_solver.py`)
  - [x] `TASK-8.4`: Transparent regime comparison breakdown (`generate_line_items`)
  - [x] `TASK-8.5`: Unit tests for tax regime comparison (`backend/tests/test_regime_comparison.py`)

---

## 📌 Milestone Detailed Status

### [Milestone 1 — Project Setup & Foundation](file:///D:/Projects/ITR-TaxPilot/milestones/milestone1-project-setup)
- **Branch:** `milestone/m01-project-setup`
- **Status:** `Completed`
- **Tasks Completed:** 12 / 12
  - [x] `TASK-1.1`: Create backend and frontend directory structure
  - [x] `TASK-1.2`: Configure Python 3.12+ environment & `requirements.txt`
  - [x] `TASK-1.3`: Create `.env.example` configuration template
  - [x] `TASK-1.4`: Add `.gitignore` for Python and Docker
  - [x] `TASK-1.5`: Create backend Dockerfile
  - [x] `TASK-1.6`: Create `docker-compose.yml`
  - [x] `TASK-1.7`: Configure FastAPI application factory
  - [x] `TASK-1.8`: Configure structured JSON logging
  - [x] `TASK-1.9`: Implement root health endpoint `GET /health`
  - [x] `TASK-1.10`: Configure `pytest` test runner
  - [x] `TASK-1.11`: Setup linting & formatting (Ruff/Black)
  - [x] `TASK-1.12`: Add README and development docs

---

### [Milestone 2 — Backend Core & Architecture](file:///D:/Projects/ITR-TaxPilot/milestones/milestone2-backend-core)
- **Branch:** `milestone/m02-backend-core`
- **Status:** `Completed`
- **Tasks Completed:** 10 / 10
  - [x] `TASK-2.1`: FastAPI routing and `/api/v1` prefixing
  - [x] `TASK-2.2`: Standard Pydantic request/response envelope schemas
  - [x] `TASK-2.3`: Central exception handling & custom error codes
  - [x] `TASK-2.4`: Request ID and correlation tracing middleware
  - [x] `TASK-2.5`: Configuration management via Pydantic Settings
  - [x] `TASK-2.6`: PostgreSQL connection & session management
  - [x] `TASK-2.7`: SQLAlchemy database models
  - [x] `TASK-2.8`: Alembic migrations setup & baseline migration
  - [x] `TASK-2.9`: Redis connection pool & health check
  - [x] `TASK-2.10`: Implement initial API route stubs

---

### [Milestone 3 — Form 16 Upload & Document Pipeline](file:///D:/Projects/ITR-TaxPilot/milestones/milestone3-form16-upload-pipeline)
- **Branch:** `milestone/m03-form16-upload-pipeline`
- **Status:** `Completed`
- **Tasks Completed:** 8 / 8
  - [x] `TASK-3.1`: Secure PDF upload handler & MIME validation
  - [x] `TASK-3.2`: Malicious file safety checks and rejection
  - [x] `TASK-3.3`: PDF text extraction using PyMuPDF (fitz)
  - [x] `TASK-3.4`: Table extraction for Part A & Part B
  - [x] `TASK-3.5`: OCR fallback pipeline for scanned documents
  - [x] `TASK-3.6`: Form 16 document classification & validation
  - [x] `TASK-3.7`: Normalized document representation data model
  - [x] `TASK-3.8`: Ephemeral file storage and auto-cleanup

---

### [Milestone 4 — AI Extraction Layer](file:///D:/Projects/ITR-TaxPilot/milestones/milestone4-ai-extraction-layer)
- **Branch:** `milestone/m04-ai-extraction-layer`
- **Status:** `Completed`
- **Tasks Completed:** 8 / 8
  - [x] `TASK-4.1`: Strict Pydantic Form 16 extraction schema
  - [x] `TASK-4.2`: Abstract AIProvider base interface
  - [x] `TASK-4.3`: Google Gemini provider implementation
  - [x] `TASK-4.4`: Anthropic Claude provider implementation
  - [x] `TASK-4.5`: Versioned prompt templates for extraction
  - [x] `TASK-4.6`: JSON parsing and failure recovery
  - [x] `TASK-4.7`: Field-level confidence score calculation
  - [x] `TASK-4.8`: Dual-model cross-verification mechanism

---

### [Milestone 5 — Validation & Data Normalization](file:///D:/Projects/ITR-TaxPilot/milestones/milestone5-validation-and-normalization)
- **Branch:** `milestone/m05-validation-and-normalization`
- **Status:** `Completed`
- **Tasks Completed:** 7 / 7
  - [x] `TASK-5.1`: Mandatory fields & PAN/AY regex validation
  - [x] `TASK-5.2`: Non-negative currency and numeric validation
  - [x] `TASK-5.3`: Cross-check Part A vs Part B TDS consistency
  - [x] `TASK-5.4`: Arithmetic relationship consistency checks
  - [x] `TASK-5.5`: Explicit 0 vs unknown/not found distinction
  - [x] `TASK-5.6`: Duplicate field reconciliation and resolver
  - [x] `TASK-5.7`: Low-confidence field flagging & review states

---

### [Milestone 6 — Assessment Year Rule Engine](file:///D:/Projects/ITR-TaxPilot/milestones/milestone6-assessment-year-rules)
- **Branch:** `milestone/m06-assessment-year-rules`
- **Status:** `Completed`
- **Tasks Completed:** 7 / 7
  - [x] `TASK-6.1`: Modular rule engine architecture (`app/tax/rules/`)
  - [x] `TASK-6.2`: Rule metadata schema (AY, legal source, effective period)
  - [x] `TASK-6.3`: Implement AY 2025-26 tax rules
  - [x] `TASK-6.4`: Implement AY 2026-27 tax rules
  - [x] `TASK-6.5`: AY 2027-28 extensible rule module structure
  - [x] `TASK-6.6`: Chapter VI-A deduction eligibility catalog
  - [x] `TASK-6.7`: Comprehensive unit tests for all AY rules

---

### [Milestone 7 — Deterministic Tax Engine](file:///D:/Projects/ITR-TaxPilot/milestones/milestone7-deterministic-tax-engine)
- **Branch:** `milestone/m07-deterministic-tax-engine`
- **Status:** `Completed`
- **Tasks Completed:** 13 / 13
  - [x] `TASK-7.1`: Core calculation engine orchestration (`backend/app/calculator/tax_engine.py`)
  - [x] `TASK-7.2`: Gross Total Income computation (`salary_engine.py`, `house_property_engine.py`, `other_sources_engine.py`)
  - [x] `TASK-7.3`: Section 16 deductions computation (`salary_engine.py`)
  - [x] `TASK-7.4`: Chapter VI-A eligible deductions computation (`deduction_engine.py`)
  - [x] `TASK-7.5`: Net Taxable Income rounding Section 288A (`regime_comparator.py`)
  - [x] `TASK-7.6`: Slab-wise tax computation (`slab_engine.py`)
  - [x] `TASK-7.7`: Section 87A rebate & Marginal Relief (`rebate_engine.py`)
  - [x] `TASK-7.8`: Surcharge & Surcharge Marginal Relief (`surcharge_engine.py`)
  - [x] `TASK-7.9`: 4% Health & Education Cess computation (`tax_engine.py`)
  - [x] `TASK-7.10`: TDS credit offset & net tax computation (`interest_engine.py`, `tax_engine.py`)
  - [x] `TASK-7.11`: Final Tax Payable / Refund Section 288B (`tax_engine.py`, `regime_comparator.py`)
  - [x] `TASK-7.12`: Detailed calculation audit trail generator (`models.py`, `SlabBracketDetail`)
  - [x] `TASK-7.13`: Complete unit test suite for tax calculations (`test_deterministic_tax_engine.py`)

---

### [Milestone 8 — Tax Regime Comparison](file:///D:/Projects/ITR-TaxPilot/milestones/milestone8-tax-regime-comparison)
- **Branch:** `milestone/m08-tax-regime-comparison`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 5

---

### [Milestone 9 — ITR Recommendation Engine](file:///D:/Projects/ITR-TaxPilot/milestones/milestone9-itr-recommendation-engine)
- **Branch:** `milestone/m09-itr-recommendation-engine`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 6

---

### [Milestone 10 — Explanation AI & Guardrails](file:///D:/Projects/ITR-TaxPilot/milestones/milestone10-explanation-ai)
- **Branch:** `milestone/m10-explanation-ai`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 6

---

### [Milestone 11 — Redis & Job Processing](file:///D:/Projects/ITR-TaxPilot/milestones/milestone11-redis-job-processing)
- **Branch:** `milestone/m11-redis-job-processing`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 6

---

### [Milestone 12 — Frontend MVP](file:///D:/Projects/ITR-TaxPilot/milestones/milestone12-frontend-mvp)
- **Branch:** `milestone/m12-frontend-mvp`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 8

---

### [Milestone 13 — Report Generation](file:///D:/Projects/ITR-TaxPilot/milestones/milestone13-report-generation)
- **Branch:** `milestone/m13-report-generation`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 5

---

### [Milestone 14 — Security & Privacy](file:///D:/Projects/ITR-TaxPilot/milestones/milestone14-security-and-privacy)
- **Branch:** `milestone/m14-security-and-privacy`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 8

---

### [Milestone 15 — Testing & Quality Assurance](file:///D:/Projects/ITR-TaxPilot/milestones/milestone15-testing-and-qa)
- **Branch:** `milestone/m15-testing-and-qa`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 6

---

### [Milestone 16 — Observability & Monitoring](file:///D:/Projects/ITR-TaxPilot/milestones/milestone16-observability-monitoring)
- **Branch:** `milestone/m16-observability-monitoring`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 4

---

### [Milestone 17 — Production Deployment](file:///D:/Projects/ITR-TaxPilot/milestones/milestone17-production-deployment)
- **Branch:** `milestone/m17-production-deployment`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 5

---

### [Milestone 18 — Future Expansion (Post-MVP)](file:///D:/Projects/ITR-TaxPilot/milestones/milestone18-future-expansion)
- **Branch:** `milestone/m18-future-expansion`
- **Status:** `Pending`
- **Tasks Completed:** 0 / 6

---

*Last Updated: 2026-08-30 (Milestone 6 In Progress) | Maintained automatically via [`EXECUTION_PROMPT.md`](file:///D:/Projects/ITR-TaxPilot/EXECUTION_PROMPT.md)*
