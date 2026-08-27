# Module 07: Financial Cyber Risk Quantification

## Overview
The Financial Cyber Risk Quantification module translates the deterministic `Cyber Risk` score into financial terms, answering the question: *"What could this cyber risk mean financially if it materialized?"*

Unlike generic risk scores, this module is transparent, explainable, and based strictly on inputted financial assumptions combined with deterministic risk mathematics.

## Architecture

1. **Cyber Risk Input (Module 06)**
   - The engine inherits the Cyber Risk Likelihood (mapped to Annual Event Frequency) and the Net Risk Score.
2. **Financial Assumptions**
   - The organization configures deterministic assumptions (e.g., *Revenue Impact Per Hour*, *Recovery Cost*, *Cost Per Data Record*).
3. **Loss Engine**
   - Calculates specific impact drivers independently.
4. **Aggregation**
   - Sums impact drivers to determine the `Potential Loss`.
   - Multiplies `Potential Loss` by `Annual Event Frequency` to calculate `Expected Annual Loss (EAL)`.

## Impact Categories

The module models nine distinct financial drivers:

| Driver | Description | Formula |
|---|---|---|
| **Direct Loss** | Emergency incident response, forensics, etc. | Explicit configuration (`incident_response_cost`) |
| **Data Loss** | Notification, legal, and credit monitoring. | `affected_records * cost_per_record` |
| **Business Interruption** | Lost revenue/productivity during downtime. | `downtime_hours * revenue_impact_per_hour` |
| **Recovery Cost** | Cost to restore infrastructure and systems. | Explicit configuration (`recovery_cost`) |
| **Customer Impact** | Compensation and SLAs. | Explicit configuration (`customer_impact`) |
| **Regulatory/Legal** | Estimated fines or legal exposure. | Explicit configuration (`regulatory_legal_estimate`) |
| **Third-Party Impact** | Supply chain or vendor impacts. | Explicit configuration (`third_party_impact`) |
| **Fraud Loss** | Direct financial theft / fraudulent transactions. | Explicit configuration (`fraud_loss_estimate`) |
| **Reputation Impact** | Long-term churn or brand devaluation. | Explicit configuration (`reputation_revenue_impact`) |

## Terminology

- **Modeled Potential Loss**: The total financial consequence if a cyber event fully materializes under the assumed worst-case scenario.
- **Expected Annual Loss (EAL)**: The probability-weighted loss expressed over a single year. `(Potential Loss * Event Frequency)`
- **Annual Event Frequency**: Derived from the underlying cyber risk likelihood, representing the expected number of events per year.
- **Confidence**: An internal metric (0-100%) indicating how much explicit financial data was available. If key inputs (like recovery cost or business value) are missing, confidence decreases.

## Double-Counting Controls

The module keeps the nine impact categories strictly separated to prevent double-counting. For example, `downtime_hours * revenue_impact_per_hour` only measures immediate business interruption, while `reputation_revenue_impact` tracks long-term churn. 

*Organizations must ensure their inputs respect these boundaries (e.g., not baking reputation costs into the hourly downtime cost).*

## Calculation Versioning

All assessments store their exact `assumptions_snapshot` and a `calculation_version`. Because financial estimates change over time, we never retroactively update historical assessments. This allows for historical auditing of financial risk reduction over time (to be utilized in Module 08 and Module 10).

## Worked Example

**Asset**: Payment Gateway
- **Cyber Risk Likelihood**: 0.25 (1 event every 4 years)

**Assumptions**:
- **Downtime Hours**: 24
- **Revenue Impact**: ₹500,000 / hr
- **Recovery Cost**: ₹2,500,000

**Calculations**:
1. Business Interruption = 24 * 500,000 = ₹12,000,000
2. Recovery Cost = ₹2,500,000
3. **Potential Loss** = ₹14,500,000
4. **Expected Annual Loss** = 14,500,000 * 0.25 = **₹3,625,000**
