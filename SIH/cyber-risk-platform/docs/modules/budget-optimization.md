# Module 10: Cybersecurity Budget Optimization & Scenario Simulation

## Overview
Module 10 acts as the ultimate Decision Intelligence layer for CISOs and CFOs. It bridges the gap between active threats (Module 5), financial risk (Module 7), and tactical mitigations (Module 9) by applying combinatorial optimization to answer:

> "Given a bounded budget of ₹X, which exact combination of cybersecurity investments will yield the maximum modeled financial risk reduction without exceeding available capital?"

## Optimization Engine
The core solver (`OptimizationEngine` in `backend/app/services/optimization/engine.py`) uses a **0/1 Knapsack Algorithm via Dynamic Programming (DP)**. 

### Why 0/1 Knapsack?
Cybersecurity investments are generally indivisible (you cannot buy "half an EDR agent deployment"). The 0/1 Knapsack elegantly handles this discrete optimization. For smaller datasets (e.g., < 500 candidate mitigations), the DP matrix calculates the exact, globally optimal portfolio. If candidates exceed this bound, the engine automatically degrades into a greedy heuristic (sorting by a calculated Value/Cost ratio) to preserve performance.

### Objective Function & Weighting
The objective value of any single `CybersecurityInvestment` is a normalized, weighted sum of:
1. **Risk Reduction** (Module 6)
2. **Financial Exposure Reduction** (Module 7 Expected Annual Loss drop)
3. **Asset Criticality** (Module 3 Context)
4. **Urgency** (Based on Threat Intel or Vulnerability state)
5. **Confidence**

The default configuration is "Balanced", weighing Risk Reduction at 40% and Financial Exposure at 30%. Users can explicitly toggle the engine to "Maximize Risk Reduction" or "Maximize Financial Reduction".

## Pipeline Execution

1. **Baseline**: The engine captures the organization's current `RiskScore` and `FinancialRiskAssessment`.
2. **Mandatory Filtering**: The engine deducts the cost of any `mandatory` investments from the budget before optimization. If mandatory costs exceed the budget, it immediately returns `budget_insufficient`.
3. **Optimization**: DP Knapsack selects the optional investments that maximize the objective function.
4. **Hypothetical Simulation**: The engine simulates the combined effect of the selected investments. It applies a diminishing returns formula (since stacking security controls rarely yields perfectly additive risk drops).
5. **Persistence**: The run and its resulting `OptimizationPortfolio` are stored in the database to allow leaders to compare different budget scenarios (e.g., "What does ₹25L buy us versus ₹50L?").

## Constraints and Limits
- **Counterfactual Only**: The simulation NEVER patches a real machine or executes a purchase order. It strictly models hypothetical organizational states.
- **Explainability**: The system enforces explainability, logging `metadata.explanation` to describe why the final portfolio was selected.
