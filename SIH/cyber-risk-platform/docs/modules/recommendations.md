# Module 09: AI-Powered Mitigation Recommendation Engine

## Overview
The AI-Powered Mitigation Recommendation Engine synthesizes data from Asset Management (Mod 03), Security Telemetry (Mod 04), Threat Intelligence (Mod 05), Vulnerability Scanners, Risk Engines (Mod 06 & 08), and Financial Risk Quantification (Mod 07).

Unlike generic LLM wrappers that spit out "Use MFA" or "Patch systems", this engine deterministically builds a correlation graph between known infrastructure weaknesses and active threats to prioritize what must be done first, justifying its recommendations using expected Risk Reduction and Financial Benefit.

## Pipeline Architecture

1. **Gap Analysis & Evidence Gathering**:
   - Queries open vulnerabilities for each asset.
   - Cross-references active threat campaigns (IoCs) mapped to the asset's OS or environment.
   - Ingests predicted 30-day risk trends.
   - Pulls the asset's Expected Annual Loss (EAL).

2. **Deterministic Candidate Generation**:
   - The engine uses a robust rules matrix. For example:
     - **Rule 1**: Internet Exposed Asset + Critical Vulnerability -> Generate "Emergency Patch" recommendation.
     - **Rule 2**: Active Threat Campaign matching Asset OS -> Generate "Deploy IoC Blocks" recommendation.
     - **Rule 3**: Worsening AI Forecast -> Generate "Conduct Security Review" recommendation.

3. **Scoring & Ranking**:
   - **Risk Reduction**: Calculated dynamically based on the specific rule triggered and the severity of the underlying evidence.
   - **Financial Benefit**: Calculated deterministically by applying the Risk Reduction percentage against the asset's financial Expected Annual Loss (EAL). 
   - **Prioritization**: Recommendations are sorted first by Priority/Urgency, then by highest Financial Benefit.

## Models

- `Recommendation`: Enhanced with a structured `metadata` schema that explicitly answers:
  - `rationale`: Why should we do this?
  - `risk_driver`: What risk is being mitigated?
  - `urgency`: Time-bound execution priority (e.g. 24 Hours).
  - `implementation_effort`: Estimated organizational friction.
  - `confidence`: Mathematical confidence in the recommendation (0-100).
  - `evidence`: Specific correlated alerts, CVEs, or Threat campaigns triggering the rule.

## Automation & Triggers
The engine can be triggered manually via the dashboard or run on a schedule (e.g. nightly cron via `generate_recommendations.py`) to continually re-evaluate organizational priorities as new telemetry streams in.
