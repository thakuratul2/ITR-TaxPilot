# Security & Privacy Guidelines

## 1. Zero PII Logging Policy
- **Never log PAN, Aadhaar, names, phone numbers, or raw salary amounts.**
- The application uses `app.core.logging.PIIMaskingFilter` to automatically scrub PAN, Aadhaar, and sensitive patterns from all console outputs and logs.

## 2. Document Retention & Sanitization
- Form 16 PDFs are temporarily processed in-memory / temporary storage with a maximum TTL defined by `DOCUMENT_RETENTION_MINUTES`.
- Uploaded filenames are sanitized against path traversal vulnerabilities via `sanitize_filename`.

## 3. Secret Management
- API keys (Anthropic, Gemini, DB credentials) must never be committed to Git or returned via API responses.
- All secrets are loaded via environment variables through `app.core.config.Settings`.
