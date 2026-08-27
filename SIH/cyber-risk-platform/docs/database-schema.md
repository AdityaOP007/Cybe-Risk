# Cyber Risk Platform — Database Schema

This document outlines the database tables created for **Module 02**. All tables utilize UUIDs for primary keys and maintain standard `created_at` and `updated_at` timestamps via SQLAlchemy mixins.

## Core Entities

### 1. `organizations`
Represents the root entity. All other resources are scoped to an organization for multi-tenancy support.
- **Fields**: `name`, `industry`, `organization_type`, `country`, `description`

### 2. `assets`
Organizational assets (servers, databases, applications, etc.).
- **Fields**: `name`, `asset_type`, `environment`, `criticality` (0-100), `business_value`, `internet_exposed`, `status`
- **Relationships**: Belongs to `Organization`.

### 3. `vulnerabilities`
Security weaknesses found in assets.
- **Fields**: `title`, `cve_id`, `severity`, `cvss_score` (0.0-10.0), `status`
- **Relationships**: Belongs to `Asset`.

### 4. `telemetry_events`
Security events/logs gathered from external sources (e.g., SIEM, EDR, Firewall). Stored immutably.
- **Fields**: `source`, `event_type`, `severity`, `event_data` (JSONB), `occurred_at`
- **Relationships**: Belongs to `Organization`. Optional reference to `Asset`.

### 5. `threats`
Threat intelligence objects representing active or potential threat actors/malware.
- **Fields**: `name`, `threat_type`, `severity`, `threat_score` (0-100), `active`
- **Relationships**: Belongs to `Organization`.

### 6. `security_controls`
Safeguards or countermeasures implemented to avoid, detect, counteract, or minimize security risks.
- **Fields**: `name`, `control_type`, `coverage_percentage`, `effectiveness_percentage`
- **Relationships**: Belongs to `Organization`.

### 7. `risk_scores`
Point-in-time calculation of risk, captured immutably.
- **Fields**: `score` (0-100), `risk_level`, `metadata` (JSONB)
- **Relationships**: Belongs to `Organization`. Optional reference to `Asset`.

### 8. `recommendations`
Actionable mitigations proposed by the platform to reduce risk.
- **Fields**: `title`, `priority`, `estimated_cost`, `expected_risk_reduction`, `status`
- **Relationships**: Belongs to `Organization`. Optional reference to `Asset`.

### 9. `security_investments`
Strategic security expenditures for budget optimization.
- **Fields**: `name`, `category`, `cost`, `expected_risk_reduction`
- **Relationships**: Belongs to `Organization`.

### 10. `simulations`
Records of simulated cyber attack scenarios.
- **Fields**: `name`, `scenario_type`, `parameters` (JSONB), `results` (JSONB)
- **Relationships**: Belongs to `Organization`.

### 11. `compliance_frameworks`, `compliance_controls`, `control_assessments`
Entities representing standard frameworks (e.g., NIST, ISO) and the assessments of controls against them.
- **Relationships**: Frameworks have many Controls. Assessments link Organizations and Controls.
