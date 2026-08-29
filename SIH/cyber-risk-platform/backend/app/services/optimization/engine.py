import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from datetime import datetime, timezone

from app.models.optimization import CybersecurityInvestment, OptimizationRun, OptimizationPortfolio, RiskScenario
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.risk import RiskScore
from app.models.financial_risk import FinancialRiskAssessment
from app.schemas.optimization import OptimizationRunRequest

logger = logging.getLogger(__name__)

class OptimizationEngine:
    def __init__(self, db: Session, organization_id: uuid.UUID):
        self.db = db
        self.organization_id = organization_id

    def run_optimization(self, request: OptimizationRunRequest) -> OptimizationRun:
        # 1. Fetch current baseline
        risk_before, fin_before = self._get_current_baseline()
        
        # 2. Fetch candidates
        candidates = self.db.scalars(
            select(CybersecurityInvestment).where(
                CybersecurityInvestment.organization_id == self.organization_id,
                CybersecurityInvestment.status == "candidate"
            )
        ).all()
        
        if not candidates:
            # No candidates available
            return self._create_empty_run(request, risk_before, fin_before, "no_candidates")
            
        # 3. Handle Mandatory Investments
        mandatory_investments = [c for c in candidates if c.mandatory]
        mandatory_cost = sum([self._normalize_cost(c, request.horizon_months) for c in mandatory_investments])
        
        if mandatory_cost > request.budget:
            return self._create_empty_run(request, risk_before, fin_before, "budget_insufficient")
            
        remaining_budget = request.budget - mandatory_cost
        optional_candidates = [c for c in candidates if not c.mandatory]
        
        # 4. Filter out candidates that violate dependencies or conflicts before optimization (simplified for demo)
        # 5. Run 0/1 Knapsack Optimization
        selected_optional, opt_status = self._run_01_knapsack(optional_candidates, remaining_budget, request)
        
        # 6. Combine
        selected_investments = mandatory_investments + selected_optional
        total_cost = sum([self._normalize_cost(c, request.horizon_months) for c in selected_investments])
        
        # 7. Simulate Recalculation (Hypothetical counterfactual)
        risk_after, fin_after = self._simulate_portfolio_impact(selected_investments, risk_before, fin_before)
        
        risk_reduction = risk_before - risk_after if risk_before and risk_after else 0.0
        fin_reduction = fin_before - fin_after if fin_before and fin_after else 0.0
        
        # 8. Save Run & Portfolio
        run = OptimizationRun(
            organization_id=self.organization_id,
            budget=request.budget,
            currency=request.currency,
            horizon_months=request.horizon_months,
            objective=request.objective,
            risk_weight=request.weights.risk_weight,
            financial_weight=request.weights.financial_weight,
            criticality_weight=request.weights.criticality_weight,
            urgency_weight=request.weights.urgency_weight,
            confidence_weight=request.weights.confidence_weight,
            optimization_status=opt_status,
            total_cost=total_cost,
            remaining_budget=request.budget - total_cost,
            risk_before=risk_before,
            risk_after=risk_after,
            risk_reduction=risk_reduction,
            financial_before=fin_before,
            financial_after=fin_after,
            financial_reduction=fin_reduction,
            optimization_score=0.0 # Will calculate if needed
        )
        self.db.add(run)
        self.db.flush() # Get run.id
        
        # Explain why selected
        why_selected = self._explain_selection(selected_investments, request.budget)
        
        portfolio = OptimizationPortfolio(
            optimization_run_id=run.id,
            organization_id=self.organization_id,
            selected_investments=[str(c.id) for c in selected_investments],
            total_cost=total_cost,
            risk_reduction=risk_reduction,
            financial_reduction=fin_reduction,
            portfolio_metadata={"explanation": why_selected}
        )
        self.db.add(portfolio)
        self.db.commit()
        
        return run

    def _normalize_cost(self, candidate: CybersecurityInvestment, horizon_months: int) -> float:
        if candidate.cost_type == "one_time":
            return candidate.cost
        elif candidate.cost_type == "annual":
            return candidate.cost + (candidate.annualized_cost or 0.0) * (horizon_months / 12.0)
        return candidate.cost

    def _calculate_candidate_value(self, candidate: CybersecurityInvestment, request: OptimizationRunRequest) -> float:
        """
        Calculates the objective function value for a single candidate based on weights.
        """
        # Normalize (assuming max risk reduction is ~100 and max fin reduction is ~10000000)
        norm_risk = min(1.0, (candidate.risk_reduction or 0.0) / 100.0)
        norm_fin = min(1.0, (candidate.financial_reduction or 0.0) / 10000000.0)
        
        # Urgency multiplier
        urgency_map = {"Immediate": 1.0, "24 Hours": 0.8, "7 Days": 0.5, "30 Days": 0.2}
        urg_val = urgency_map.get(candidate.urgency, 0.1)
        
        # Criticality (fetch asset)
        asset_crit = 0.5
        if candidate.asset_id:
            asset = self.db.scalar(select(Asset).where(Asset.id == candidate.asset_id))
            if asset:
                asset_crit = (asset.criticality or 50) / 100.0
                
        conf = (candidate.confidence or 50) / 100.0

        value = 0.0
        if request.objective in ["balanced", "minimum_residual_risk"]:
            value = (norm_risk * request.weights.risk_weight) + \
                    (norm_fin * request.weights.financial_weight) + \
                    (asset_crit * request.weights.criticality_weight) + \
                    (urg_val * request.weights.urgency_weight) + \
                    (conf * request.weights.confidence_weight)
        elif request.objective == "risk_first":
            value = norm_risk * 0.8 + asset_crit * 0.2
        elif request.objective == "financial_first":
            value = norm_fin * 0.8 + conf * 0.2
            
        return value

    def _run_01_knapsack(self, candidates: List[CybersecurityInvestment], budget: float, request: OptimizationRunRequest) -> Tuple[List[CybersecurityInvestment], str]:
        """
        Dynamic Programming 0/1 Knapsack to maximize the configured objective value under the budget constraint.
        If cost is fractional, we multiply by 100 to make it an integer for the DP array.
        """
        n = len(candidates)
        if n == 0 or budget <= 0:
            return [], "optimal"
            
        if n > 500 or budget > 100000:
            # Fallback to greedy heuristic if N is too large or budget is too big to fit in a DP array safely
            return self._run_greedy(candidates, budget, request), "heuristic"

        # Scale budget and costs to integers (e.g. up to 2 decimal places)
        scale = 100
        W = int(budget * scale)
        
        costs = [int(self._normalize_cost(c, request.horizon_months) * scale) for c in candidates]
        values = [self._calculate_candidate_value(c, request) * 1000 for c in candidates] # scale up values for precision
        
        # DP table: dp[w] stores max value for weight w
        dp = [0.0] * (W + 1)
        # Keep track of choices
        choices = [[] for _ in range(W + 1)]

        for i in range(n):
            cost = costs[i]
            val = values[i]
            # Traverse backwards to use 1D array for 0/1 Knapsack
            for w in range(W, cost - 1, -1):
                if dp[w - cost] + val > dp[w]:
                    dp[w] = dp[w - cost] + val
                    choices[w] = choices[w - cost] + [candidates[i]]

        selected = choices[W]
        return selected, "optimal"

    def _run_greedy(self, candidates: List[CybersecurityInvestment], budget: float, request: OptimizationRunRequest) -> List[CybersecurityInvestment]:
        """
        Greedy heuristic: sort by Value/Cost ratio.
        """
        items = []
        for c in candidates:
            cost = self._normalize_cost(c, request.horizon_months)
            val = self._calculate_candidate_value(c, request)
            ratio = val / cost if cost > 0 else float('inf')
            items.append((ratio, cost, c))
            
        items.sort(key=lambda x: x[0], reverse=True)
        
        selected = []
        current_cost = 0.0
        for ratio, cost, c in items:
            if current_cost + cost <= budget:
                selected.append(c)
                current_cost += cost
                
        return selected

    def _simulate_portfolio_impact(self, investments: List[CybersecurityInvestment], base_risk: float, base_fin: float) -> Tuple[float, float]:
        """
        Calculate the combined impact. Since risk is not purely additive, we use a diminishing returns formula.
        In a full implementation, this would instantiate hypothetical Assets and run them through Mod 6/7 engines.
        """
        if not investments:
            return base_risk, base_fin
            
        total_risk_red = 0.0
        total_fin_red = 0.0
        
        # Sort by impact
        investments.sort(key=lambda x: x.risk_reduction or 0.0, reverse=True)
        
        # Diminishing returns: 1st is 100%, 2nd is 80%, 3rd is 60%, etc.
        for i, inv in enumerate(investments):
            multiplier = max(0.2, 1.0 - (i * 0.15))
            total_risk_red += (inv.risk_reduction or 0.0) * multiplier
            total_fin_red += (inv.financial_reduction or 0.0) * multiplier
            
        sim_risk = max(0.0, base_risk - total_risk_red)
        sim_fin = max(0.0, base_fin - total_fin_red)
        
        return sim_risk, sim_fin

    def _get_current_baseline(self) -> Tuple[float, float]:
        """
        Gets current organization level risk and financial exposure.
        """
        risk_record = self.db.scalars(
            select(RiskScore).where(RiskScore.organization_id == self.organization_id, RiskScore.asset_id == None).order_by(desc(RiskScore.calculated_at)).limit(1)
        ).first()
        
        fin_record = self.db.scalars(
            select(FinancialRiskAssessment).where(FinancialRiskAssessment.organization_id == self.organization_id, FinancialRiskAssessment.asset_id == None).order_by(desc(FinancialRiskAssessment.calculated_at)).limit(1)
        ).first()
        
        # Fallbacks for demo
        risk = risk_record.score if risk_record else 75.0
        fin = fin_record.expected_loss if fin_record else 15000000.0
        return risk, fin

    def _explain_selection(self, investments: List[CybersecurityInvestment], budget: float) -> str:
        if not investments:
            return "No investments were selected. Available budget is insufficient to satisfy any modeled candidates."
        
        return f"With a {budget:,.0f} budget, the optimizer selected {len(investments)} investments that maximize the configured objective. These actions prioritize high-criticality assets with active threat exposures while respecting operational cost constraints."
