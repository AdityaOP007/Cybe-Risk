import asyncio
import logging
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.core.config import settings
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.telemetry import TelemetryEvent
from app.models.threat import Threat
from app.models.control import SecurityControl
from app.models.risk import RiskScore
from app.models.recommendation import Recommendation
from app.models.investment import SecurityInvestment
from app.models.simulation import Simulation
from app.models.compliance import ComplianceFramework, ComplianceControl, ControlAssessment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    engine = create_engine(str(settings.DATABASE_URL))
    
    with Session(engine) as session:
        # Check if already seeded
        if session.query(Organization).count() > 0:
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Seeding organization...")
        org = Organization(
            name="Demo Financial Institution",
            industry="Banking",
            organization_type="enterprise",
            country="United States",
            description="Synthetic demo organization for testing the Cyber Risk Platform"
        )
        session.add(org)
        session.commit()
        session.refresh(org)

        logger.info("Seeding assets...")
        assets = [
            Asset(organization_id=org.id, name="Customer Database", asset_type="database", environment="production", criticality=100, business_value=5000000, internet_exposed=False),
            Asset(organization_id=org.id, name="Payment Gateway", asset_type="application", environment="production", criticality=100, business_value=10000000, internet_exposed=True),
            Asset(organization_id=org.id, name="Internet Banking Server", asset_type="server", environment="production", criticality=95, business_value=8000000, internet_exposed=True),
            Asset(organization_id=org.id, name="Employee VPN", asset_type="network_device", environment="production", criticality=80, business_value=1000000, internet_exposed=True),
            Asset(organization_id=org.id, name="SIEM Server", asset_type="server", environment="production", criticality=90, business_value=2000000, internet_exposed=False),
            Asset(organization_id=org.id, name="HR Application", asset_type="application", environment="production", criticality=60, business_value=500000, internet_exposed=False),
        ]
        session.add_all(assets)
        session.commit()
        
        # Reload assets to get their IDs
        assets = session.query(Asset).all()
        payment_gateway = next(a for a in assets if a.name == "Payment Gateway")
        customer_db = next(a for a in assets if a.name == "Customer Database")

        logger.info("Seeding vulnerabilities...")
        vulns = [
            Vulnerability(asset_id=payment_gateway.id, title="Unpatched Struts vulnerability", cve_id="CVE-2017-5638", severity="critical", cvss_score=10.0, exploitability_score=3.9),
            Vulnerability(asset_id=payment_gateway.id, title="TLS 1.0 Enabled", severity="medium", cvss_score=4.3),
            Vulnerability(asset_id=customer_db.id, title="Default password in use", severity="high", cvss_score=8.5),
        ]
        session.add_all(vulns)

        from datetime import datetime, timezone

        logger.info("Seeding telemetry...")
        telemetry = [
            TelemetryEvent(organization_id=org.id, asset_id=payment_gateway.id, source="firewall", event_type="port_scan", severity="low", message="Port scan detected from external IP", event_data={"src_ip": "192.168.1.1"}, occurred_at=datetime.now(timezone.utc)),
            TelemetryEvent(organization_id=org.id, asset_id=payment_gateway.id, source="WAF", event_type="sql_injection", severity="high", message="Blocked SQLi attempt", event_data={"payload": "' OR 1=1--"}, occurred_at=datetime.now(timezone.utc)),
            TelemetryEvent(organization_id=org.id, asset_id=customer_db.id, source="EDR", event_type="suspicious_process", severity="critical", message="Unusual process execution", event_data={"process": "cmd.exe"}, occurred_at=datetime.now(timezone.utc)),
        ]
        session.add_all(telemetry)

        logger.info("Seeding threats...")
        threats = [
            Threat(organization_id=org.id, name="Fin7", threat_type="APT", severity="critical", threat_score=95.0, active=True),
            Threat(organization_id=org.id, name="Generic Ransomware", threat_type="ransomware", severity="high", threat_score=80.0, active=True),
        ]
        session.add_all(threats)

        logger.info("Seeding security controls...")
        controls = [
            SecurityControl(organization_id=org.id, name="Multi-Factor Authentication", control_type="identity", coverage_percentage=85.0, effectiveness_percentage=90.0),
            SecurityControl(organization_id=org.id, name="Web Application Firewall", control_type="network", coverage_percentage=100.0, effectiveness_percentage=80.0),
            SecurityControl(organization_id=org.id, name="Endpoint Detection and Response", control_type="endpoint", coverage_percentage=95.0, effectiveness_percentage=95.0),
        ]
        session.add_all(controls)

        logger.info("Seeding risk scores...")
        risks = [
            RiskScore(organization_id=org.id, asset_id=payment_gateway.id, score=85.5, risk_level="high", calculation_version="1.0", metadata_={"factors": ["critical_vulnerability", "internet_exposed"]}),
            RiskScore(organization_id=org.id, asset_id=customer_db.id, score=92.0, risk_level="critical", calculation_version="1.0", metadata_={"factors": ["high_business_value", "suspicious_process"]}),
        ]
        session.add_all(risks)

        logger.info("Seeding recommendations...")
        recs = [
            Recommendation(organization_id=org.id, asset_id=payment_gateway.id, title="Patch Apache Struts", priority="critical", estimated_cost=1000.0, expected_risk_reduction=40.0, status="proposed"),
            Recommendation(organization_id=org.id, asset_id=customer_db.id, title="Change default database password", priority="high", estimated_cost=100.0, expected_risk_reduction=20.0, status="proposed"),
        ]
        session.add_all(recs)

        logger.info("Seeding investments...")
        investments = [
            SecurityInvestment(organization_id=org.id, name="Implement Zero Trust Architecture", category="network", cost=150000.0, expected_risk_reduction=30.0, status="proposed"),
        ]
        session.add_all(investments)
        
        logger.info("Seeding compliance...")
        framework = ComplianceFramework(name="NIST CSF 2.0", version="2.0", description="National Institute of Standards and Technology Cybersecurity Framework")
        session.add(framework)
        session.commit()
        session.refresh(framework)
        
        comp_controls = [
            ComplianceControl(framework_id=framework.id, control_id="ID.AM-01", title="Inventories of hardware", category="Identify"),
            ComplianceControl(framework_id=framework.id, control_id="PR.AC-01", title="Identity management", category="Protect"),
        ]
        session.add_all(comp_controls)
        session.commit()

        logger.info("Database seeding complete!")

if __name__ == "__main__":
    seed_data()
