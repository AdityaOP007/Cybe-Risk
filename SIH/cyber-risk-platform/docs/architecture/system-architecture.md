# System Architecture

## Overview

The **Cyber Risk Quantification & Decision Intelligence Platform** is designed as a modular monolith that can evolve into independent services as the system scales. The platform quantifies cyber risk in financial terms by combining security telemetry, asset criticality, vulnerabilities, threat intelligence, and AI/ML prediction.

## Current State (Module 01 — Foundation)

```mermaid
graph TD
    subgraph "Module 01 — Implemented"
        FE["React Frontend<br/>(Vite + TypeScript + Tailwind)"]
        API["FastAPI Backend<br/>(Python 3.12+)"]
        DB["PostgreSQL 16<br/>(Database)"]
    end

    FE -->|"REST API"| API
    API -->|"SQLAlchemy"| DB

    style FE fill:#3b82f6,stroke:#1e40af,color:#fff
    style API fill:#10b981,stroke:#047857,color:#fff
    style DB fill:#f59e0b,stroke:#b45309,color:#fff
```

## Target Architecture (All Modules)

```mermaid
graph TD
    subgraph "Data Sources"
        SIEM["SIEM Logs"]
        EDR["EDR Alerts"]
        VULN["Vulnerability Scanners"]
        TI["Threat Intelligence Feeds"]
        ASSETS["Asset Inventory"]
    end

    subgraph "Data Ingestion Layer"
        DI["Data Ingestion Engine<br/><i>Planned</i>"]
    end

    subgraph "Data Store"
        DB["PostgreSQL"]
    end

    subgraph "Core Engines"
        RE["Risk Engine<br/><i>Planned</i>"]
        AI["AI/ML Engine<br/><i>Planned</i>"]
        CE["Compliance Engine<br/><i>Planned</i>"]
    end

    subgraph "Decision Engines"
        REC["Recommendation Engine<br/><i>Planned</i>"]
        OPT["Budget Optimization Engine<br/><i>Planned</i>"]
        SIM["Scenario Simulation Engine<br/><i>Planned</i>"]
    end

    subgraph "API Layer"
        API["FastAPI Backend"]
    end

    subgraph "Presentation"
        FE["React Executive Dashboard"]
    end

    SIEM --> DI
    EDR --> DI
    VULN --> DI
    TI --> DI
    ASSETS --> DI

    DI --> DB

    DB --> RE
    DB --> AI
    DB --> CE

    RE --> REC
    AI --> REC
    RE --> OPT
    RE --> SIM

    REC --> API
    OPT --> API
    SIM --> API
    CE --> API
    RE --> API

    API --> FE

    style DI fill:#6b7280,stroke:#374151,color:#fff
    style RE fill:#6b7280,stroke:#374151,color:#fff
    style AI fill:#6b7280,stroke:#374151,color:#fff
    style CE fill:#6b7280,stroke:#374151,color:#fff
    style REC fill:#6b7280,stroke:#374151,color:#fff
    style OPT fill:#6b7280,stroke:#374151,color:#fff
    style SIM fill:#6b7280,stroke:#374151,color:#fff
    style DB fill:#f59e0b,stroke:#b45309,color:#fff
    style API fill:#10b981,stroke:#047857,color:#fff
    style FE fill:#3b82f6,stroke:#1e40af,color:#fff
```

## Component Details

### Frontend (React + TypeScript + Vite + Tailwind CSS)

- **Status**: ✅ Foundation implemented
- Single-page application serving the executive dashboard
- Communicates with backend exclusively via REST API
- Environment-driven API base URL configuration
- Component-based architecture with common/shared components

### Backend (FastAPI + Python 3.12+)

- **Status**: ✅ Foundation implemented
- RESTful API with versioned endpoints (`/api/v1/...`)
- Pydantic for request/response validation and configuration
- SQLAlchemy ORM for database access
- Alembic for schema migrations
- Structured logging with security-safe defaults
- CORS configured per environment

### Database (PostgreSQL 16)

- **Status**: ✅ Foundation implemented
- Primary data store for all platform data
- Schema managed via Alembic migrations
- Future tables: Assets, Vulnerabilities, TelemetryEvents, Threats, Controls, RiskScores, Recommendations, Investments, Simulations, ComplianceControls

### Data Ingestion Engine

- **Status**: 🔲 Planned
- Normalize and ingest data from SIEM, EDR, vulnerability scanners, threat feeds
- Write structured data to PostgreSQL

### Risk Engine

- **Status**: 🔲 Planned
- Quantify cyber risk in financial terms
- Combine asset criticality, vulnerability severity, threat likelihood, control effectiveness

### AI/ML Engine

- **Status**: 🔲 Planned
- Predictive risk scoring using machine learning
- Anomaly detection on telemetry data
- Risk trend forecasting

### Compliance Engine

- **Status**: 🔲 Planned
- Map controls to frameworks: NIST CSF, ISO 27001, RBI, SEBI
- Track compliance posture and gaps

### Recommendation Engine

- **Status**: 🔲 Planned
- Generate actionable mitigation recommendations
- Prioritize by risk reduction per dollar spent

### Budget Optimization Engine

- **Status**: 🔲 Planned
- Optimize security investment allocation given a budget constraint
- Cost-benefit analysis of security controls

### Scenario Simulation Engine

- **Status**: 🔲 Planned
- Simulate cyber attack scenarios
- Model impact on risk posture and financial exposure

## API Versioning

All API endpoints are versioned under `/api/v1/`. Future breaking changes will introduce `/api/v2/`.

| Future Endpoint | Module |
|----------------|--------|
| `/api/v1/assets` | Asset Management |
| `/api/v1/telemetry` | Security Telemetry |
| `/api/v1/threats` | Threat Intelligence |
| `/api/v1/risks` | Risk Engine |
| `/api/v1/recommendations` | Recommendation Engine |
| `/api/v1/budget` | Budget Optimization |
| `/api/v1/simulations` | Scenario Simulation |
| `/api/v1/compliance` | Compliance Engine |

## Design Principles

1. **Modular Monolith** — Single deployable unit with clear module boundaries, designed to split into services later if needed.
2. **Clean Architecture** — Business logic in services, not in route handlers.
3. **Configuration-driven** — All environment-specific values loaded from environment variables.
4. **Security by default** — No secrets in code, restricted CORS, structured logging that never exposes sensitive data.
5. **Future-ready** — Directory structure and interfaces designed for AI/ML integration without restructuring.
