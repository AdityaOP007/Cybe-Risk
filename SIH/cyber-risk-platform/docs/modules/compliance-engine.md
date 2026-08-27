# Module 11: Compliance & Regulatory Mapping Engine

## Overview

The Compliance & Regulatory Mapping Engine bridges the gap between active security operations and regulatory requirements. It continuously assesses the organization's posture against frameworks like NIST CSF, ISO 27001, RBI, and SEBI.

## Core Features

### Multi-Framework Assessment
Assesses controls against multiple frameworks simultaneously, providing a real-time view of compliance status for different regulatory bodies.

### Evidence Freshness
Unlike traditional GRC tools where a control is "Implemented" permanently, this engine tracks the freshness of evidence. If an audit log or policy document expires (`valid_until` passes), the control's compliance status degrades to `Insufficient Evidence`.

### Crosswalk Visualization
A central mapping engine allows a single security control (e.g., "Enterprise MFA") to satisfy requirements across multiple frameworks simultaneously. The "Control Crosswalk" visualizes this mapping and calculates the confidence and coverage for each mapping.

### Applicability & Exceptions
Tracks applicability overrides (if a requirement is not applicable to the organization) and manages formal, time-bound risk exceptions.

## Usage

1. Navigate to the **Compliance** dashboard.
2. View the real-time coverage and metrics for each tracked framework.
3. Review the **Actionable Compliance Gaps** table to see prioritized gaps based on cyber risk, financial exposure, and control effectiveness.
4. Click **Crosswalk** on a gap to see how implementing the missing control will improve compliance across multiple frameworks simultaneously.
