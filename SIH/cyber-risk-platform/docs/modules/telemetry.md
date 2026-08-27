# Module 04: Security Telemetry Ingestion & Normalization

## Purpose
This module provides a robust security telemetry ingestion layer. It receives, validates, normalizes, stores, queries, and displays cybersecurity events from varied sources. This establishes the foundation of raw data that future threat intelligence and risk calculations will rely on.

## Architecture
1. **Collector/Ingestion Endpoint**: Receives raw events via REST API (`/events`), batch REST (`/events/batch`), or CSV upload (`/events/upload`).
2. **Normalizer**: Transforms varying taxonomies (e.g., `sev1`, `priority_1` -> `critical`, `authentication_failure` -> `failed_login`) into the canonical `NormalizedTelemetryEvent`.
3. **Database Layer**: Persists the data in `TelemetryEvent` using PostgreSQL JSONB for flexible raw data retention, while strict canonical fields are indexed.
4. **Deduplication**: A partial unique index on `(organization_id, source, source_event_id)` ensures idempotent ingestion where source identifiers exist.

## Deduplication Strategy
To prevent double-counting of telemetry (especially important for SIEM log resends), a uniqueness constraint is placed in the database.
If a duplicate event arrives with an existing `source_event_id`, it gracefully fails at the service level (or is marked rejected in batch processing).

## Endpoints
- `POST /api/v1/telemetry/events` (Single ingest)
- `POST /api/v1/telemetry/events/batch` (Batch ingest)
- `POST /api/v1/telemetry/events/upload` (CSV ingest)
- `GET /api/v1/telemetry/events` (List/filter/paginate)
- `GET /api/v1/telemetry/events/recent`
- `GET /api/v1/telemetry/stats` (Aggregated counts)

## IMPORTANT: Telemetry ≠ Risk
This module **does not** calculate risk. It only collects what happened. The fact that an event is marked "Critical" severity does not mean it contributes to "Critical" cyber risk—this is a later evaluation determined by the future Risk Engine.

## Future Risk Engine Integration
In Module 06, the Risk Engine will consume telemetry statistics (e.g., frequency of failed logins over a time window) and combine it with Asset Criticality and Control Effectiveness to dynamically calculate quantified financial risk.
