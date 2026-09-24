# ALOS–GENESIS internal route ownership

The internal OpenAPI intentionally describes both directions of one service boundary. A path-level
`x-service-owner` is authoritative; the document-level server is only the GENESIS default.

## GENESIS implements (Backend → GENESIS)

- `POST /internal/v1/agent-runs`
- `POST /internal/v1/reviews`
- `POST /internal/v1/factory/analyze`
- `POST /internal/v1/research`
- `POST /internal/v1/research/run`
- `GET /internal/v1/system/integration`
- `GET /internal/v1/system/info`

## ALOS Backend implements (GENESIS → Backend callbacks)

- `POST /internal/v1/tool-requests`
- `GET /internal/v1/agent-runs/{run_id}/cancellation`

Authenticated health probes and development-only integration inspection routes are operational
surfaces excluded from the published service contract. GENESIS remains non-authoritative and has no
direct access to the business PostgreSQL authority store.
