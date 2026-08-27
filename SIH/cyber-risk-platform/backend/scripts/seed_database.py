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
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.models.control import SecurityControl
from app.models.risk import RiskScore
from app.models.recommendation import Recommendation
from app.models.optimization import OptimizationRun, OptimizationPortfolio, CybersecurityInvestment

from app.models.compliance import ComplianceFramework, ComplianceRequirement, ComplianceAssessment

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
            Asset(organization_id=org.id, name="Core Banking Server", asset_type="server", environment="production", criticality=100, business_value=150000000, internet_exposed=False, owner="IT Ops", department="Infrastructure", hostname="cbs-prod-01", ip_address="10.0.1.10", operating_system="Linux", technology="Mainframe"),
            Asset(organization_id=org.id, name="Customer Database", asset_type="database", environment="production", criticality=98, business_value=500000000, internet_exposed=False, owner="Data Platform", department="Engineering", hostname="db-cust-prod", ip_address="10.0.2.20", operating_system="Linux", technology="PostgreSQL"),
            Asset(organization_id=org.id, name="Payment Gateway", asset_type="payment_system", environment="production", criticality=95, business_value=250000000, internet_exposed=True, owner="Payments Team", department="Technology", hostname="pay-gw-prod", ip_address="10.0.10.15", operating_system="Linux", technology="Java/Spring"),
            Asset(organization_id=org.id, name="Internet Banking API", asset_type="api", environment="production", criticality=90, business_value=100000000, internet_exposed=True, owner="Digital Banking", department="Engineering", hostname="api-ib-prod", ip_address="10.0.10.16", operating_system="Linux", technology="Node.js"),
            Asset(organization_id=org.id, name="Mobile Banking API", asset_type="api", environment="production", criticality=90, business_value=120000000, internet_exposed=True, owner="Mobile Team", department="Engineering", hostname="api-mob-prod", ip_address="10.0.10.17", operating_system="Linux", technology="Node.js"),
            Asset(organization_id=org.id, name="ATM Processing Server", asset_type="server", environment="production", criticality=92, business_value=80000000, internet_exposed=False, owner="Retail Banking", department="Infrastructure", hostname="atm-proc-01", ip_address="10.0.5.50", operating_system="Windows Server", technology=".NET"),
            Asset(organization_id=org.id, name="Employee VPN", asset_type="network_device", environment="production", criticality=85, business_value=5000000, internet_exposed=True, owner="Network Security", department="Security", hostname="vpn-gw-01", ip_address="198.51.100.1", operating_system="Cisco IOS", technology="VPN"),
            Asset(organization_id=org.id, name="SIEM Server", asset_type="server", environment="production", criticality=90, business_value=20000000, internet_exposed=False, owner="SOC", department="Security", hostname="siem-prod-01", ip_address="10.0.100.10", operating_system="Linux", technology="Splunk"),
            Asset(organization_id=org.id, name="Backup Server", asset_type="storage", environment="production", criticality=80, business_value=10000000, internet_exposed=False, owner="IT Ops", department="Infrastructure", hostname="bkp-san-01", ip_address="10.0.1.50", operating_system="Linux", technology="SAN"),
            Asset(organization_id=org.id, name="HR Application", asset_type="application", environment="production", criticality=65, business_value=5000000, internet_exposed=False, owner="HR Dept", department="Human Resources", hostname="hr-app-01", ip_address="10.0.3.10", operating_system="Linux", technology="PHP"),
            Asset(organization_id=org.id, name="Cloud Storage", asset_type="cloud_resource", environment="production", criticality=70, business_value=15000000, internet_exposed=False, owner="Data Platform", department="Engineering", hostname="s3-bucket-main", technology="AWS S3"),
            Asset(organization_id=org.id, name="API Gateway", asset_type="network_device", environment="staging", criticality=50, business_value=100000, internet_exposed=True, owner="Platform Team", department="Engineering", hostname="api-gw-stg", ip_address="10.0.20.10", operating_system="Linux", technology="Kong"),
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
            CybersecurityInvestment(organization_id=org.id, title="Implement Zero Trust Architecture", category="network", cost=150000.0, risk_reduction=30.0, status="candidate"),
        ]
        session.add_all(investments)
        
        logger.info("Seeding compliance...")
        framework = ComplianceFramework(name="NIST CSF 2.0", version="2.0")
        session.add(framework)
        session.commit()
        session.refresh(framework)
        
        comp_controls = [
            ComplianceRequirement(framework_id=framework.id, requirement_id="ID.AM-01", title="Inventories of hardware", category="Identify"),
            ComplianceRequirement(framework_id=framework.id, requirement_id="PR.AC-01", title="Identity management", category="Protect"),
        ]
        session.add_all(comp_controls)
        session.commit()

        logger.info("Database seeding complete!")

if __name__ == "__main__":
    seed_data()
