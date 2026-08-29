import uuid
import hashlib
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func

from app.models.organization import Organization
from app.models.risk import RiskScore
from app.models.financial_risk import FinancialRiskAssessment
from app.models.prediction import RiskPrediction
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.threat_intel import ThreatIntelligenceRecord
from app.models.recommendation import Recommendation
from app.models.optimization import OptimizationRun, OptimizationPortfolio
from app.models.compliance import ComplianceFramework, ComplianceAssessment, ComplianceGap
from app.models.dashboard import DashboardAlert, ExecutiveInsight

from app.schemas.dashboard import (
    ExecutiveDashboardData, RiskSummary, FinancialSummary, PredictionSummary,
    AssetRiskSummary, TopRiskDrivers, ThreatSummary, VulnerabilitySummary,
    RecommendationSummary, BudgetSummary, ComplianceSummary as ComplianceSummarySchema,
    DashboardAlertRead, ExecutiveInsightRead, DataQuality
)
from app.models.mixins import get_utc_now


class DashboardAggregatorService:
    def __init__(self, db: Session, organization_id: uuid.UUID):
        self.db = db
        self.org_id = organization_id
        self.now = get_utc_now()

    def get_dashboard(self) -> ExecutiveDashboardData:
        risk_summary = self._get_risk_summary()
        financial_summary = self._get_financial_summary()
        prediction_summary = self._get_prediction_summary()
        top_assets = self._get_top_assets()
        risk_drivers = self._get_risk_drivers()
        threats = self._get_threat_summary()
        vulnerabilities = self._get_vulnerability_summary()
        recommendations = self._get_recommendation_summary()
        budget_summary = self._get_budget_summary()
        compliance_summary = self._get_compliance_summary()

        # Generate dynamic insights
        insights = self._generate_insights(
            risk_summary, financial_summary, top_assets, recommendations, compliance_summary
        )

        # Commit any new alerts
        self.db.commit()

        # Load Active Alerts
        alerts = self._get_active_alerts()

        data_quality = DataQuality(
            risk_engine="Healthy" if risk_summary else "No Data",
            prediction="Healthy" if prediction_summary else "No Data",
            financial_model="Healthy" if financial_summary else "No Data",
            compliance="Healthy" if compliance_summary else "No Data"
        )

        if not risk_summary:
            risk_summary = RiskSummary(
                current_score=0.0, risk_level="Unknown", trend="stable", last_updated=self.now
            )

        return ExecutiveDashboardData(
            organization_id=self.org_id,
            last_updated=self.now,
            risk=risk_summary,
            financial=financial_summary,
            prediction=prediction_summary,
            top_assets=top_assets,
            risk_drivers=risk_drivers,
            threats=threats,
            vulnerabilities=vulnerabilities,
            recommendations=recommendations,
            budget=budget_summary,
            compliance=compliance_summary,
            alerts=alerts,
            insights=insights,
            data_quality=data_quality
        )

    # ─── RISK ───────────────────────────────────────────────
    def _get_risk_summary(self) -> Optional[RiskSummary]:
        scores = self.db.scalars(
            select(RiskScore)
            .where(RiskScore.organization_id == self.org_id, RiskScore.asset_id == None)
            .order_by(desc(RiskScore.calculated_at))
            .limit(2)
        ).all()

        if not scores:
            return None

        current = scores[0]
        prev = scores[1] if len(scores) > 1 else None

        change = (current.score - prev.score) if prev else 0.0
        trend = "stable"
        if change > 2:
            trend = "increasing"
        elif change < -2:
            trend = "decreasing"

        if current.score > 80:
            self._create_alert(
                "Critical Organizational Risk",
                f"Overall cyber risk score is {current.score:.1f} ({current.risk_level})",
                "Module 6", "critical"
            )

        return RiskSummary(
            current_score=current.score,
            risk_level=current.risk_level,
            previous_score=prev.score if prev else None,
            change=change,
            trend=trend,
            last_updated=current.calculated_at
        )

    # ─── FINANCIAL ──────────────────────────────────────────
    def _get_financial_summary(self) -> Optional[FinancialSummary]:
        # Financial assessments are per-asset, so aggregate across org
        assessments = self.db.scalars(
            select(FinancialRiskAssessment)
            .where(FinancialRiskAssessment.organization_id == self.org_id)
            .order_by(desc(FinancialRiskAssessment.calculated_at))
        ).all()

        if not assessments:
            return None

        # Find most recent per-asset
        seen_assets = set()
        latest = []
        for a in assessments:
            if a.asset_id not in seen_assets:
                seen_assets.add(a.asset_id)
                latest.append(a)

        total_exposure = sum(float(a.potential_loss) for a in latest)
        total_eal = sum(float(a.annualized_expected_loss) for a in latest)
        last_calc = max(a.calculated_at for a in latest)

        breakdown = {
            "Business Interruption": sum(float(a.business_interruption_loss) for a in latest),
            "Data Loss": sum(float(a.data_loss) for a in latest),
            "Recovery": sum(float(a.recovery_loss) for a in latest),
            "Regulatory / Legal": sum(float(a.regulatory_legal_exposure) for a in latest),
            "Third Party": sum(float(a.third_party_impact) for a in latest),
            "Customer Impact": sum(float(a.customer_impact) for a in latest),
        }

        return FinancialSummary(
            modeled_exposure=total_exposure,
            expected_annual_loss=total_eal,
            breakdown=breakdown,
            last_updated=last_calc
        )

    # ─── PREDICTION ─────────────────────────────────────────
    def _get_prediction_summary(self) -> Optional[PredictionSummary]:
        pred = self.db.scalars(
            select(RiskPrediction)
            .where(RiskPrediction.organization_id == self.org_id)
            .order_by(desc(RiskPrediction.prediction_timestamp))
            .limit(1)
        ).first()

        if not pred:
            return None

        return PredictionSummary(
            forecast_30_day=pred.predicted_risk,
            trend=pred.trend,
            confidence=pred.confidence,
            last_updated=pred.prediction_timestamp
        )

    # ─── TOP ASSETS ─────────────────────────────────────────
    def _get_top_assets(self) -> List[AssetRiskSummary]:
        assets = self.db.scalars(
            select(Asset).where(Asset.organization_id == self.org_id)
        ).all()

        results = []
        for a in assets:
            rs = self.db.scalars(
                select(RiskScore)
                .where(RiskScore.asset_id == a.id)
                .order_by(desc(RiskScore.calculated_at))
                .limit(1)
            ).first()
            if rs:
                fin = self.db.scalars(
                    select(FinancialRiskAssessment)
                    .where(FinancialRiskAssessment.asset_id == a.id)
                    .order_by(desc(FinancialRiskAssessment.calculated_at))
                    .limit(1)
                ).first()

                results.append(AssetRiskSummary(
                    asset_id=a.id,
                    asset_name=a.name,
                    risk_score=rs.score,
                    criticality=a.criticality,
                    financial_exposure=float(fin.potential_loss) if fin else 0.0,
                    predicted_risk=None,
                    trend="stable"
                ))

        results.sort(key=lambda x: x.risk_score, reverse=True)
        return results[:5]

    # ─── RISK DRIVERS ───────────────────────────────────────
    def _get_risk_drivers(self) -> List[TopRiskDrivers]:
        score = self.db.scalars(
            select(RiskScore)
            .where(RiskScore.organization_id == self.org_id, RiskScore.asset_id == None)
            .order_by(desc(RiskScore.calculated_at))
            .limit(1)
        ).first()

        drivers = []
        if score and score.risk_metadata:
            factors = score.risk_metadata.get("factors", score.risk_metadata)
            if isinstance(factors, dict):
                for key, val in factors.items():
                    if isinstance(val, (int, float)) and val > 0:
                        drivers.append(TopRiskDrivers(
                            driver_name=key.replace("_", " ").title(),
                            risk_contribution=float(val),
                            category="General"
                        ))
        return sorted(drivers, key=lambda x: x.risk_contribution, reverse=True)[:5]

    # ─── THREATS ────────────────────────────────────────────
    def _get_threat_summary(self) -> List[ThreatSummary]:
        from app.models.threat_intel import ThreatCorrelation
        # Find global threats that correlate to this org
        threats = self.db.scalars(
            select(ThreatIntelligenceRecord)
            .join(ThreatCorrelation, ThreatCorrelation.threat_record_id == ThreatIntelligenceRecord.id)
            .where(ThreatCorrelation.organization_id == self.org_id)
            .order_by(desc(ThreatIntelligenceRecord.severity), desc(ThreatIntelligenceRecord.confidence))
            .limit(5)
        ).unique().all()

        results = []
        for t in threats:
            results.append(ThreatSummary(
                threat_id=t.id,
                name=t.title,
                affected_assets=0,
                confidence=t.confidence or 0.0,
                severity=t.severity,
                trend="increasing" if t.known_exploited else "stable"
            ))
        return results

    # ─── VULNERABILITIES ────────────────────────────────────
    def _get_vulnerability_summary(self) -> List[VulnerabilitySummary]:
        vulns = self.db.scalars(
            select(Vulnerability)
            .join(Asset, Asset.id == Vulnerability.asset_id)
            .where(Asset.organization_id == self.org_id)
            .order_by(desc(Vulnerability.cvss_score))
            .limit(5)
        ).all()

        results = []
        for v in vulns:
            # We don't have is_exploited_in_wild on the base model, so we infer it from exploitability_score
            is_exploited = (v.exploitability_score or 0.0) >= 7.0
            
            results.append(VulnerabilitySummary(
                vulnerability_id=v.id,
                name=f"{v.cve_id or 'VULN'} - {v.title}",
                severity=v.severity,
                known_exploited=is_exploited,
                affected_assets=1,
                risk_contribution=v.cvss_score or 0.0
            ))
            if is_exploited and v.severity == "critical":
                self._create_alert(
                    f"Known Exploited Vulnerability: {v.cve_id or 'Unknown'}",
                    "A critical vulnerability with high exploitability is present.",
                    "Module 4", "critical"
                )
        return results

    # ─── RECOMMENDATIONS ────────────────────────────────────
    def _get_recommendation_summary(self) -> List[RecommendationSummary]:
        recs = self.db.scalars(
            select(Recommendation)
            .where(Recommendation.organization_id == self.org_id, Recommendation.status == "proposed")
            .order_by(desc(Recommendation.expected_risk_reduction))
            .limit(5)
        ).all()

        results = []
        for r in recs:
            results.append(RecommendationSummary(
                recommendation_id=r.id,
                action=r.title,
                asset_name=None,
                priority=r.priority,
                estimated_risk_reduction=r.expected_risk_reduction or 0.0,
                financial_exposure_reduction=0.0,
                urgency=r.priority,
                status=r.status
            ))
        return results

    # ─── BUDGET ─────────────────────────────────────────────
    def _get_budget_summary(self) -> Optional[BudgetSummary]:
        run = self.db.scalars(
            select(OptimizationRun)
            .where(
                OptimizationRun.organization_id == self.org_id,
                OptimizationRun.optimization_status.in_(["optimal", "feasible", "heuristic"])
            )
            .order_by(desc(OptimizationRun.created_at))
            .limit(1)
        ).first()

        if not run:
            return None

        return BudgetSummary(
            recommended_budget=run.budget,
            budget_used=run.total_cost,
            budget_remaining=run.remaining_budget,
            selected_investments=len(run.portfolios) if run.portfolios else 0,
            risk_before=run.risk_before or 0.0,
            risk_after=run.risk_after or 0.0,
            financial_exposure_before=run.financial_before or 0.0,
            financial_exposure_after=run.financial_after or 0.0,
            last_updated=run.created_at
        )

    # ─── COMPLIANCE ─────────────────────────────────────────
    def _get_compliance_summary(self) -> List[ComplianceSummarySchema]:
        fws = self.db.scalars(select(ComplianceFramework)).all()
        results = []

        for fw in fws:
            assessments = self.db.scalars(
                select(ComplianceAssessment)
                .where(ComplianceAssessment.organization_id == self.org_id, ComplianceAssessment.framework_id == fw.id)
            ).all()

            if not assessments:
                continue

            metrics = {"compliant": 0, "partial": 0, "non": 0, "insufficient": 0, "total_reqs": 0}
            for a in assessments:
                if a.status != "not_applicable":
                    metrics["total_reqs"] += 1
                if a.status == "compliant":
                    metrics["compliant"] += 1
                elif a.status == "partially_compliant":
                    metrics["partial"] += 1
                elif a.status == "non_compliant":
                    metrics["non"] += 1
                elif a.status == "insufficient_evidence":
                    metrics["insufficient"] += 1

            gaps = self.db.scalars(
                select(ComplianceGap)
                .where(ComplianceGap.organization_id == self.org_id, ComplianceGap.framework_id == fw.id, ComplianceGap.status == "open")
            ).all()

            coverage = (metrics["compliant"] / metrics["total_reqs"] * 100) if metrics["total_reqs"] > 0 else 0.0

            results.append(ComplianceSummarySchema(
                framework_name=fw.name,
                coverage_percentage=round(coverage, 2),
                compliant=metrics["compliant"],
                partially_compliant=metrics["partial"],
                non_compliant=metrics["non"],
                insufficient_evidence=metrics["insufficient"],
                open_gaps=len(gaps)
            ))

            if metrics["insufficient"] > 0:
                self._create_alert(
                    f"{fw.name} Evidence Expired",
                    f"There are {metrics['insufficient']} controls with expired or missing evidence.",
                    "Module 11", "high"
                )

        return results

    # ─── ALERTS ─────────────────────────────────────────────
    def _create_alert(self, title: str, reason: str, source: str, severity: str):
        fingerprint = hashlib.md5(f"{self.org_id}:{title}:{source}".encode()).hexdigest()

        existing = self.db.scalars(
            select(DashboardAlert).where(
                DashboardAlert.organization_id == self.org_id,
                DashboardAlert.fingerprint == fingerprint,
                DashboardAlert.status == "active"
            )
        ).first()

        if not existing:
            alert = DashboardAlert(
                organization_id=self.org_id,
                title=title,
                reason=reason,
                source_module=source,
                severity=severity,
                fingerprint=fingerprint
            )
            self.db.add(alert)

    def _get_active_alerts(self) -> List[DashboardAlertRead]:
        alerts = self.db.scalars(
            select(DashboardAlert)
            .where(DashboardAlert.organization_id == self.org_id, DashboardAlert.status == "active")
            .order_by(desc(DashboardAlert.first_seen))
        ).all()

        return [
            DashboardAlertRead(
                id=a.id, title=a.title, reason=a.reason, source_module=a.source_module,
                severity=a.severity, action_link=a.action_link, status=a.status,
                first_seen=a.first_seen, last_seen=a.last_seen
            ) for a in alerts
        ]

    # ─── INSIGHTS ───────────────────────────────────────────
    def _generate_insights(
        self, risk: Optional[RiskSummary], fin: Optional[FinancialSummary],
        assets: List[AssetRiskSummary], recs: List[RecommendationSummary],
        comp: List[ComplianceSummarySchema]
    ) -> List[ExecutiveInsightRead]:

        texts = []

        if risk:
            if risk.trend == "increasing":
                texts.append(f"Organizational cyber risk has increased to {risk.current_score:.0f}/100. Immediate attention recommended.")
            elif risk.trend == "decreasing":
                texts.append(f"Cyber risk has successfully decreased to {risk.current_score:.0f}/100.")
            else:
                texts.append(f"Organizational cyber risk is stable at {risk.current_score:.0f}/100.")

        if fin and fin.modeled_exposure > 0:
            texts.append(f"Total modeled financial exposure stands at ₹{(fin.modeled_exposure / 10000000):.1f} Cr.")

        if assets:
            top = assets[0]
            texts.append(f"Exposure is highly concentrated in '{top.asset_name}' with a risk score of {top.risk_score:.0f}.")

        if recs:
            top_rec = recs[0]
            texts.append(f"The most impactful action is '{top_rec.action}', which could reduce risk by {top_rec.estimated_risk_reduction:.0f} points.")

        return [
            ExecutiveInsightRead(
                id=uuid.uuid4(), content=text, insight_type="General", generated_at=self.now
            )
            for text in texts
        ]
