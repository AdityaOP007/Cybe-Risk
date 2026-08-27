# Module 06: Cyber Risk Engine & Risk Quantification

## Overview
Module 06 establishes the **Cyber Risk Engine**, the foundational component that bridges all previously collected data (Assets, Vulnerabilities, Telemetry, Threat Intel, and Controls) to produce a deterministic, explainable Risk Score.

## Mathematical Framework
The engine avoids black-box ML algorithms and relies on a transparent likelihood/impact model modified by security controls.

### 1. Impact (Max 100 Points)
- **Asset Criticality (60%)**: Scaled directly from the Asset's `criticality` rating.
- **Business Value (30%)**: Scaled logarithmically using the Asset's `business_value`.
- **Exposure (10%)**: A fixed bonus added if the asset is internet-exposed.

### 2. Likelihood (Max 100 Points)
- **Base Likelihood**: Minimum ambient risk (10 points).
- **Vulnerabilities**: Driven by the maximum CVSS score associated with the asset (Up to 40 points).
- **Telemetry**: Up to 30 points awarded based on the volume and severity of recent correlated security alerts.
- **Threat Intelligence**: A flat +10 points if correlated with generic intel, jumping to +30 points if the asset is vulnerable to a Known Exploited Vulnerability (CISA KEV).

### 3. Gross Risk
`Gross Risk = (Impact * Likelihood) / 100`

### 4. Control Mitigation Factor
The gross risk is discounted by the effectiveness of the organization's active `SecurityControl`s.
- `Factor = Average(Coverage * Effectiveness)`
- The mitigation factor is capped at 0.8 (meaning risk can only be reduced by a maximum of 80%, as 100% security is impossible).

### 5. Net Risk
`Net Risk = Gross Risk * (1 - Mitigation Factor)`

## Explainability
The risk calculation generates a `metadata` payload that includes:
- **Numeric Factors**: The exact numbers used in the calculation.
- **Drivers**: A list of plain-english reasons explaining why the score is what it is.
- **Confidence**: A percentage reflecting data completeness (e.g., if there's no telemetry or threat intel data, confidence is lower).

## Organization Aggregation
Organization risk is not a simple average. It uses a **Criticality-Weighted Average** to ensure that highly critical assets have a stronger pull on the organization's overall risk posture. If the crown jewels are at risk, the entire organization is at risk.

## Frontend
- Added `RiskScoreMeter` component (SVG dial).
- Added `RiskDriversList` to explicitly explain the risk.
- Added `RiskTrendChart` to plot historical point-in-time calculations.
- Displayed natively on both the `Dashboard` and `AssetDetails` pages.
