# API Reference Specification

## 1. Response Format Envelope

All JSON responses strictly follow the standard response envelope:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "req_1234567890abcdef"
}
```

In the event of an error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable explanation",
    "details": null
  },
  "request_id": "req_1234567890abcdef"
}
```

## 2. Base Endpoints

### `GET /health`
Returns application operational health status and metadata.

### `GET /api/v1/health`
Versioned health check endpoint.
