"""
Comprehensive SIH Demo Seed Script
===================================

Seeds the "Example Bank" organization with realistic synthetic data across all 12 modules,
then runs the actual calculation engines in the correct dependency order to populate
derived data (risk scores, financial assessments, predictions, recommendations,
optimization runs, compliance assessments).

This ensures the Executive Dashboard displays rich, traceable, end-to-end data.

IMPORTANT: All data is SYNTHETIC and clearly labeled for SIH demonstration purposes.

Usage:
    cd backend
    python -m scripts.seed_database
"""

import uuid
import sys
import os
import logging
from datetime import datetime, timezone, timedelta

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.core.database import engine, Base
from app.models.organization import Organization
from app.models.user import User
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.telemetry import TelemetryEvent
from app.models.control import SecurityControl
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.models.financial_risk import FinancialAssumption
from app.models.compliance import (
    ComplianceFramework, ComplianceRequirement,
    ComplianceControlMapping, ComplianceEvidence
)
from app.models.recommendation import Recommendation
from app.models.optimization import CybersecurityInvestment
from app.models.prediction import RiskPrediction, RiskPredictionModel
from app.models.risk import RiskScore


logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("seed")

NOW = datetime.now(timezone.utc)


# ─── DETERMINISTIC IDs ────────────────────────────────────────────────
# Using deterministic UUIDs from namespace so re-runs are idempotent
NS = uuid.UUID("12345678-1234-5678-1234-567812345678")

def make_id(name: str) -> uuid.UUID:
    return uuid.uuid5(NS, name)


ORG_ID = make_id("example-bank")
USER_ID = make_id("admin-user")


# ─── ASSET DEFINITIONS ────────────────────────────────────────────────
ASSETS = [
    {
        "id": make_id("core-banking-server"),
        "name": "Core Banking Server (CBS)",
        "asset_type": "server",
        "criticality": 95,
        "business_value": 50000000,
        "internet_exposed": False,
        "operating_system": "RHEL 9",
        "ip_address": "10.1.1.10",
        "environment": "production",
        "owner": "IT Infrastructure",
        "description": "[SYNTHETIC] Primary core banking application server processing all financial transactions",
    },
    {
        "id": make_id("internet-banking-portal"),
        "name": "Internet Banking Portal",
        "asset_type": "web_application",
        "criticality": 90,
        "business_value": 30000000,
        "internet_exposed": True,
        "operating_system": "Ubuntu 22.04",
        "ip_address": "203.0.113.50",
        "environment": "production",
        "owner": "Digital Banking",
        "description": "[SYNTHETIC] Customer-facing internet banking web application",
    },
    {
        "id": make_id("mobile-banking-api"),
        "name": "Mobile Banking API Gateway",
        "asset_type": "api",
        "criticality": 88,
        "business_value": 25000000,
        "internet_exposed": True,
        "operating_system": "Kubernetes (EKS)",
        "ip_address": "203.0.113.60",
        "environment": "production",
        "owner": "Digital Banking",
        "description": "[SYNTHETIC] REST API gateway serving the mobile banking application",
    },
    {
        "id": make_id("customer-database"),
        "name": "Customer Database (PII)",
        "asset_type": "database",
        "criticality": 98,
        "business_value": 100000000,
        "internet_exposed": False,
        "operating_system": "Oracle Linux 8",
        "ip_address": "10.1.2.20",
        "environment": "production",
        "owner": "Data Management",
        "description": "[SYNTHETIC] Primary customer PII database containing 12M+ records",
    },
    {
        "id": make_id("payment-switch"),
        "name": "Payment Switch (NEFT/RTGS/UPI)",
        "asset_type": "server",
        "criticality": 96,
        "business_value": 75000000,
        "internet_exposed": False,
        "operating_system": "RHEL 8",
        "ip_address": "10.1.3.10",
        "environment": "production",
        "owner": "Treasury & Payments",
        "description": "[SYNTHETIC] Real-time payment processing switch handling NEFT, RTGS, and UPI",
    },
    {
        "id": make_id("atm-controller"),
        "name": "ATM Network Controller",
        "asset_type": "network_device",
        "criticality": 75,
        "business_value": 15000000,
        "internet_exposed": False,
        "operating_system": "Windows Server 2019",
        "ip_address": "10.1.4.5",
        "environment": "production",
        "owner": "IT Infrastructure",
        "description": "[SYNTHETIC] Central controller managing 2,500+ ATM terminals",
    },
    {
        "id": make_id("email-gateway"),
        "name": "Email Security Gateway",
        "asset_type": "network_device",
        "criticality": 60,
        "business_value": 5000000,
        "internet_exposed": True,
        "operating_system": "Appliance OS",
        "ip_address": "203.0.113.25",
        "environment": "production",
        "owner": "IT Security",
        "description": "[SYNTHETIC] Email filtering and anti-phishing gateway",
    },
    {
        "id": make_id("hr-portal"),
        "name": "HR & Payroll Portal",
        "asset_type": "web_application",
        "criticality": 45,
        "business_value": 3000000,
        "internet_exposed": False,
        "operating_system": "Ubuntu 20.04",
        "ip_address": "10.1.5.15",
        "environment": "production",
        "owner": "Human Resources",
        "description": "[SYNTHETIC] Internal HR management and payroll processing system",
    },
    {
        "id": make_id("swift-gateway"),
        "name": "SWIFT Messaging Gateway",
        "asset_type": "server",
        "criticality": 99,
        "business_value": 200000000,
        "internet_exposed": False,
        "operating_system": "RHEL 8",
        "ip_address": "10.1.6.5",
        "environment": "production",
        "owner": "Treasury & Payments",
        "description": "[SYNTHETIC] SWIFT Alliance Lite2 gateway for international fund transfers",
    },
    {
        "id": make_id("soc-siem"),
        "name": "SOC SIEM Platform",
        "asset_type": "server",
        "criticality": 70,
        "business_value": 8000000,
        "internet_exposed": False,
        "operating_system": "CentOS 8",
        "ip_address": "10.1.7.10",
        "environment": "production",
        "owner": "IT Security",
        "description": "[SYNTHETIC] Security Operations Center SIEM for log aggregation and alerting",
    },
    {
        "id": make_id("loan-management"),
        "name": "Loan Management System",
        "asset_type": "web_application",
        "criticality": 72,
        "business_value": 20000000,
        "internet_exposed": False,
        "operating_system": "Windows Server 2022",
        "ip_address": "10.1.8.20",
        "environment": "production",
        "owner": "Retail Banking",
        "description": "[SYNTHETIC] End-to-end loan origination, underwriting, and servicing platform",
    },
    {
        "id": make_id("devops-cicd"),
        "name": "DevOps CI/CD Pipeline",
        "asset_type": "server",
        "criticality": 55,
        "business_value": 4000000,
        "internet_exposed": False,
        "operating_system": "Ubuntu 22.04",
        "ip_address": "10.1.9.5",
        "environment": "staging",
        "owner": "Engineering",
        "description": "[SYNTHETIC] Jenkins/GitLab CI pipelines for application deployment",
    },
]


# ─── VULNERABILITY DEFINITIONS ────────────────────────────────────────
VULNERABILITIES = [
    {
        "id": make_id("vuln-log4j"),
        "asset_key": "internet-banking-portal",
        "cve_id": "CVE-2021-44228",
        "title": "Apache Log4j Remote Code Execution (Log4Shell)",
        "severity": "critical",
        "cvss_score": 10.0,
        "exploitability_score": 9.8,
        "status": "open",
        "source": "vulnerability_scanner",
        "description": "[SYNTHETIC] Critical RCE via Log4j in internet-facing portal",
    },
    {
        "id": make_id("vuln-spring4shell"),
        "asset_key": "mobile-banking-api",
        "cve_id": "CVE-2022-22965",
        "title": "Spring Framework RCE (Spring4Shell)",
        "severity": "critical",
        "cvss_score": 9.8,
        "exploitability_score": 8.5,
        "status": "open",
        "source": "vulnerability_scanner",
        "description": "[SYNTHETIC] Spring Framework RCE in API gateway",
    },
    {
        "id": make_id("vuln-openssl"),
        "asset_key": "payment-switch",
        "cve_id": "CVE-2023-0286",
        "title": "OpenSSL X.509 Certificate Verification Bypass",
        "severity": "high",
        "cvss_score": 7.4,
        "exploitability_score": 3.1,
        "status": "open",
        "source": "vulnerability_scanner",
        "description": "[SYNTHETIC] OpenSSL vulnerability in payment processing",
    },
    {
        "id": make_id("vuln-oracle-db"),
        "asset_key": "customer-database",
        "cve_id": "CVE-2023-21839",
        "title": "Oracle Database Privilege Escalation",
        "severity": "high",
        "cvss_score": 7.5,
        "exploitability_score": 5.0,
        "status": "open",
        "source": "vulnerability_scanner",
        "description": "[SYNTHETIC] Privilege escalation in customer PII database",
    },
    {
        "id": make_id("vuln-swift-tls"),
        "asset_key": "swift-gateway",
        "cve_id": "CVE-2024-0001",
        "title": "TLS 1.0 Still Enabled on SWIFT Gateway",
        "severity": "high",
        "cvss_score": 6.5,
        "exploitability_score": 2.5,
        "status": "open",
        "source": "configuration_audit",
        "description": "[SYNTHETIC] Deprecated TLS version enabled on critical payment gateway",
    },
    {
        "id": make_id("vuln-atm-rdp"),
        "asset_key": "atm-controller",
        "cve_id": "CVE-2019-0708",
        "title": "BlueKeep RDP Vulnerability",
        "severity": "critical",
        "cvss_score": 9.8,
        "exploitability_score": 9.0,
        "status": "open",
        "source": "vulnerability_scanner",
        "description": "[SYNTHETIC] BlueKeep on ATM network controller",
    },
]


# ─── TELEMETRY EVENTS ────────────────────────────────────────────────
TELEMETRY = [
    {
        "id": make_id("tel-brute-force"),
        "asset_key": "internet-banking-portal",
        "event_type": "authentication_failure",
        "severity": "high",
        "source": "WAF",
        "raw_event": {"attempts": 15000, "source_ips": 42, "window": "1h"},
        "description": "[SYNTHETIC] Distributed brute-force attack on login endpoint",
    },
    {
        "id": make_id("tel-data-exfil"),
        "asset_key": "customer-database",
        "event_type": "data_exfiltration_attempt",
        "severity": "critical",
        "source": "DLP",
        "raw_event": {"bytes_attempted": 52428800, "destination": "external", "blocked": True},
        "description": "[SYNTHETIC] Blocked data exfiltration attempt from PII database",
    },
    {
        "id": make_id("tel-lateral-move"),
        "asset_key": "core-banking-server",
        "event_type": "lateral_movement",
        "severity": "critical",
        "source": "EDR",
        "raw_event": {"technique": "T1021.002", "protocol": "SMB", "from": "10.1.5.99"},
        "description": "[SYNTHETIC] Suspicious lateral movement detected targeting CBS",
    },
    {
        "id": make_id("tel-malware"),
        "asset_key": "atm-controller",
        "event_type": "malware_detected",
        "severity": "high",
        "source": "Antivirus",
        "raw_event": {"malware_family": "Ploutus.D", "action": "quarantined"},
        "description": "[SYNTHETIC] ATM malware variant detected on controller",
    },
    {
        "id": make_id("tel-phishing"),
        "asset_key": "email-gateway",
        "event_type": "phishing_attempt",
        "severity": "medium",
        "source": "Email Gateway",
        "raw_event": {"emails_blocked": 230, "targeted_department": "Treasury", "campaign": "BEC"},
        "description": "[SYNTHETIC] Business Email Compromise campaign targeting Treasury",
    },
]


# ─── SECURITY CONTROLS ────────────────────────────────────────────────
CONTROLS = [
    {
        "id": make_id("ctrl-edr"),
        "name": "Endpoint Detection & Response (EDR)",
        "control_type": "detective",
        "coverage_percentage": 85.0,
        "effectiveness_percentage": 78.0,
        "status": "active",
        "implementation_status": "implemented",
        "owner": "IT Security",
    },
    {
        "id": make_id("ctrl-waf"),
        "name": "Web Application Firewall (WAF)",
        "control_type": "preventive",
        "coverage_percentage": 90.0,
        "effectiveness_percentage": 82.0,
        "status": "active",
        "implementation_status": "implemented",
        "owner": "IT Security",
    },
    {
        "id": make_id("ctrl-dlp"),
        "name": "Data Loss Prevention (DLP)",
        "control_type": "preventive",
        "coverage_percentage": 70.0,
        "effectiveness_percentage": 65.0,
        "status": "active",
        "implementation_status": "implemented",
        "owner": "IT Security",
    },
    {
        "id": make_id("ctrl-mfa"),
        "name": "Multi-Factor Authentication (MFA)",
        "control_type": "preventive",
        "coverage_percentage": 95.0,
        "effectiveness_percentage": 92.0,
        "status": "active",
        "implementation_status": "implemented",
        "owner": "IAM Team",
    },
    {
        "id": make_id("ctrl-siem"),
        "name": "Security Information & Event Management (SIEM)",
        "control_type": "detective",
        "coverage_percentage": 80.0,
        "effectiveness_percentage": 72.0,
        "status": "active",
        "implementation_status": "implemented",
        "owner": "SOC Team",
    },
    {
        "id": make_id("ctrl-patch"),
        "name": "Automated Patch Management",
        "control_type": "preventive",
        "coverage_percentage": 60.0,
        "effectiveness_percentage": 55.0,
        "status": "active",
        "implementation_status": "partially_implemented",
        "owner": "IT Operations",
    },
    {
        "id": make_id("ctrl-backup"),
        "name": "Offsite Backup & Recovery",
        "control_type": "corrective",
        "coverage_percentage": 100.0,
        "effectiveness_percentage": 90.0,
        "status": "active",
        "implementation_status": "implemented",
        "owner": "IT Infrastructure",
    },
]


# ─── THREAT INTELLIGENCE ─────────────────────────────────────────────
THREATS = [
    {
        "id": make_id("threat-lazarus"),
        "source": "CISA",
        "source_record_id": "AA24-001A",
        "intelligence_type": "campaign",
        "title": "Lazarus Group SWIFT Banking Campaign",
        "description": "[SYNTHETIC] North Korean state-sponsored campaign targeting SWIFT infrastructure in APAC banks",
        "severity": "critical",
        "confidence": 95,
        "known_exploited": True,
        "indicators": [
            {"type": "ipv4", "value": "185.141.63.120"},
            {"type": "domain", "value": "swift-update.com"},
            {"type": "hash", "value": "a3b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6"},
        ],
    },
    {
        "id": make_id("threat-log4shell-exploit"),
        "source": "NVD",
        "source_record_id": "CVE-2021-44228",
        "intelligence_type": "vulnerability",
        "title": "Log4Shell Active Exploitation (CISA KEV)",
        "description": "[SYNTHETIC] Widespread active exploitation of Log4j affecting Java-based banking applications",
        "severity": "critical",
        "confidence": 100,
        "known_exploited": True,
        "indicators": [
            {"type": "domain", "value": "log4j-callback.xyz"},
        ],
    },
    {
        "id": make_id("threat-ransomware-india"),
        "source": "CERT-In",
        "source_record_id": "CIAD-2024-0089",
        "intelligence_type": "campaign",
        "title": "Targeted Ransomware Campaign Against Indian Financial Sector",
        "description": "[SYNTHETIC] CERT-In advisory on ransomware wave targeting Indian BFSI sector via phishing",
        "severity": "high",
        "confidence": 85,
        "known_exploited": False,
        "indicators": [
            {"type": "ipv4", "value": "91.234.99.42"},
            {"type": "domain", "value": "rbi-update-portal.in"},
        ],
    },
]


# ─── FINANCIAL ASSUMPTIONS (INR) ──────────────────────────────────────
FINANCIAL_ASSUMPTIONS = [
    {"category": "downtime_hours", "name": "Expected Downtime (hours)", "value": 48, "unit": "hours"},
    {"category": "revenue_impact_per_hour", "name": "Revenue Impact Per Hour", "value": 2500000, "unit": "INR", "currency": "INR"},
    {"category": "affected_records", "name": "Affected Customer Records", "value": 500000, "unit": "records"},
    {"category": "cost_per_record", "name": "Cost Per Breached Record", "value": 175, "unit": "INR", "currency": "INR"},
    {"category": "recovery_cost", "name": "Incident Recovery Cost", "value": 15000000, "unit": "INR", "currency": "INR"},
    {"category": "incident_response_cost", "name": "Incident Response & Forensics", "value": 8000000, "unit": "INR", "currency": "INR"},
    {"category": "customer_impact", "name": "Customer Notification & Support", "value": 12000000, "unit": "INR", "currency": "INR"},
    {"category": "third_party_impact", "name": "Third-Party Liability", "value": 5000000, "unit": "INR", "currency": "INR"},
    {"category": "regulatory_legal_estimate", "name": "Regulatory & Legal Exposure (RBI)", "value": 25000000, "unit": "INR", "currency": "INR"},
    {"category": "fraud_loss_estimate", "name": "Estimated Fraud Losses", "value": 10000000, "unit": "INR", "currency": "INR"},
    {"category": "reputation_revenue_impact", "name": "Reputation & Revenue Impact", "value": 50000000, "unit": "INR", "currency": "INR"},
]


# ─── COMPLIANCE FRAMEWORKS ───────────────────────────────────────────
COMPLIANCE_FRAMEWORKS = [
    {
        "id": make_id("fw-nist-csf"),
        "name": "NIST CSF 2.0",
        "version": "2.0",
        "jurisdiction": "International",
        "requirements": [
            {"req_id": "GV.OC-01", "title": "Organizational Context", "category": "Govern", "subcategory": "Organizational Context"},
            {"req_id": "GV.RM-01", "title": "Risk Management Strategy", "category": "Govern", "subcategory": "Risk Management Strategy"},
            {"req_id": "ID.AM-01", "title": "Asset Inventory Management", "category": "Identify", "subcategory": "Asset Management"},
            {"req_id": "ID.RA-01", "title": "Vulnerability Identification", "category": "Identify", "subcategory": "Risk Assessment"},
            {"req_id": "PR.AC-01", "title": "Identity & Access Management", "category": "Protect", "subcategory": "Access Control"},
            {"req_id": "PR.DS-01", "title": "Data Security", "category": "Protect", "subcategory": "Data Security"},
            {"req_id": "DE.CM-01", "title": "Continuous Monitoring", "category": "Detect", "subcategory": "Continuous Monitoring"},
            {"req_id": "RS.AN-01", "title": "Incident Analysis", "category": "Respond", "subcategory": "Analysis"},
            {"req_id": "RC.RP-01", "title": "Recovery Planning", "category": "Recover", "subcategory": "Recovery Planning"},
        ],
    },
    {
        "id": make_id("fw-iso27001"),
        "name": "ISO 27001:2022",
        "version": "2022",
        "jurisdiction": "International",
        "requirements": [
            {"req_id": "A.5.1", "title": "Information Security Policies", "category": "Organizational Controls", "subcategory": "Policies"},
            {"req_id": "A.6.1", "title": "Screening", "category": "People Controls", "subcategory": "Pre-employment"},
            {"req_id": "A.7.1", "title": "Physical Security Perimeters", "category": "Physical Controls", "subcategory": "Perimeters"},
            {"req_id": "A.8.1", "title": "User Endpoint Devices", "category": "Technological Controls", "subcategory": "Endpoint"},
            {"req_id": "A.8.5", "title": "Secure Authentication", "category": "Technological Controls", "subcategory": "Authentication"},
            {"req_id": "A.8.8", "title": "Management of Technical Vulnerabilities", "category": "Technological Controls", "subcategory": "Vulnerability Management"},
            {"req_id": "A.8.16", "title": "Monitoring Activities", "category": "Technological Controls", "subcategory": "Monitoring"},
        ],
    },
    {
        "id": make_id("fw-rbi-it"),
        "name": "RBI IT Framework",
        "version": "2023",
        "jurisdiction": "India",
        "requirements": [
            {"req_id": "RBI.IT.1", "title": "IT Governance Framework", "category": "Governance", "subcategory": "IT Governance"},
            {"req_id": "RBI.IT.2", "title": "Information Security Governance", "category": "Governance", "subcategory": "IS Governance"},
            {"req_id": "RBI.IT.3", "title": "Cyber Security Framework", "category": "Security", "subcategory": "Cyber Security"},
            {"req_id": "RBI.IT.4", "title": "IT Audit & Compliance", "category": "Audit", "subcategory": "IT Audit"},
            {"req_id": "RBI.IT.5", "title": "Business Continuity Planning", "category": "Resilience", "subcategory": "BCP/DR"},
            {"req_id": "RBI.IT.6", "title": "Customer Data Protection", "category": "Data Protection", "subcategory": "Customer Data"},
        ],
    },
    {
        "id": make_id("fw-sebi-cyber"),
        "name": "SEBI Cyber Security Framework",
        "version": "2024",
        "jurisdiction": "India",
        "requirements": [
            {"req_id": "SEBI.CS.1", "title": "Cyber Security Policy", "category": "Policy", "subcategory": "CS Policy"},
            {"req_id": "SEBI.CS.2", "title": "CISO Appointment & SOC", "category": "Organization", "subcategory": "CISO/SOC"},
            {"req_id": "SEBI.CS.3", "title": "Vulnerability Assessment & Penetration Testing", "category": "Testing", "subcategory": "VAPT"},
            {"req_id": "SEBI.CS.4", "title": "Incident Reporting & Response", "category": "Response", "subcategory": "Incident Response"},
            {"req_id": "SEBI.CS.5", "title": "Audit Trail & Forensics", "category": "Audit", "subcategory": "Audit Trail"},
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════
# SEEDING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def seed_organization(db: Session):
    """Seed the Example Bank organization and admin user."""
    existing = db.get(Organization, ORG_ID)
    if existing:
        logger.info("Organization 'Example Bank' already exists. Skipping.")
        return

    org = Organization(
        id=ORG_ID,
        name="Example Bank",
        industry="Banking & Financial Services (BFSI)",
        description="[SYNTHETIC] A mid-sized Indian commercial bank used for SIH demonstration. All data is synthetic.",
        country="India",
    )
    db.add(org)

    user = User(
        id=USER_ID,
        organization_id=ORG_ID,
        email="admin@examplebank.in",
        hashed_password="$2b$12$synthetic_hash_for_demo_only",  # Not a real hash
        full_name="Demo Admin",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.flush()
    logger.info("✓ Organization 'Example Bank' and admin user created.")


def seed_assets(db: Session):
    """Seed the 12 demo assets."""
    existing = db.scalar(select(Asset).where(Asset.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Assets already seeded. Skipping.")
        return

    for a in ASSETS:
        asset = Asset(
            id=a["id"],
            organization_id=ORG_ID,
            name=a["name"],
            asset_type=a["asset_type"],
            criticality=a["criticality"],
            business_value=a["business_value"],
            internet_exposed=a["internet_exposed"],
            operating_system=a.get("operating_system"),
            ip_address=a.get("ip_address"),
            environment=a.get("environment", "production"),
            owner=a.get("owner"),
            description=a.get("description"),
            status="active",
        )
        db.add(asset)

    db.flush()
    logger.info(f"✓ {len(ASSETS)} assets seeded.")


def seed_vulnerabilities(db: Session):
    """Seed demo vulnerabilities."""
    existing = db.scalar(select(Vulnerability).limit(1))
    if existing:
        logger.info("Vulnerabilities already seeded. Skipping.")
        return

    asset_map = {a["id"]: a for a in ASSETS}
    asset_key_map = {a.get("name", ""): a["id"] for a in ASSETS}

    for v in VULNERABILITIES:
        asset_id = make_id(v["asset_key"])
        vuln = Vulnerability(
            id=v["id"],
            asset_id=asset_id,
            cve_id=v.get("cve_id"),
            title=v["title"],
            description=v.get("description"),
            severity=v["severity"],
            cvss_score=v.get("cvss_score"),
            exploitability_score=v.get("exploitability_score"),
            status=v.get("status", "open"),
            source=v.get("source", "vulnerability_scanner"),
        )
        db.add(vuln)

    db.flush()
    logger.info(f"✓ {len(VULNERABILITIES)} vulnerabilities seeded.")


def seed_telemetry(db: Session):
    """Seed demo telemetry events."""
    existing = db.scalar(select(TelemetryEvent).limit(1))
    if existing:
        logger.info("Telemetry events already seeded. Skipping.")
        return

    for t in TELEMETRY:
        asset_id = make_id(t["asset_key"])
        event = TelemetryEvent(
            id=t["id"],
            asset_id=asset_id,
            event_type=t["event_type"],
            severity=t["severity"],
            source=t.get("source"),
            raw_event=t.get("raw_event", {}),
            description=t.get("description"),
        )
        db.add(event)

    db.flush()
    logger.info(f"✓ {len(TELEMETRY)} telemetry events seeded.")


def seed_controls(db: Session):
    """Seed demo security controls."""
    existing = db.scalar(select(SecurityControl).where(SecurityControl.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Security controls already seeded. Skipping.")
        return

    for c in CONTROLS:
        ctrl = SecurityControl(
            id=c["id"],
            organization_id=ORG_ID,
            name=c["name"],
            control_type=c["control_type"],
            coverage_percentage=c["coverage_percentage"],
            effectiveness_percentage=c["effectiveness_percentage"],
            status=c["status"],
            implementation_status=c.get("implementation_status", "implemented"),
            owner=c.get("owner"),
        )
        db.add(ctrl)

    db.flush()
    logger.info(f"✓ {len(CONTROLS)} security controls seeded.")


def seed_threat_intelligence(db: Session):
    """Seed threat intelligence records, indicators, and correlations."""
    existing = db.scalar(select(ThreatIntelligenceRecord).limit(1))
    if existing:
        logger.info("Threat intelligence already seeded. Skipping.")
        return

    for t in THREATS:
        record = ThreatIntelligenceRecord(
            id=t["id"],
            source=t["source"],
            source_record_id=t["source_record_id"],
            intelligence_type=t["intelligence_type"],
            title=t["title"],
            description=t.get("description"),
            severity=t["severity"],
            confidence=t.get("confidence"),
            known_exploited=t.get("known_exploited", False),
            published_at=NOW - timedelta(days=30),
            first_seen_at=NOW - timedelta(days=60),
            last_seen_at=NOW - timedelta(hours=6),
            raw_data={"synthetic": True},
            normalized_data={"synthetic": True},
        )
        db.add(record)
        db.flush()

        # Add indicators
        for idx, ind in enumerate(t.get("indicators", [])):
            indicator = ThreatIndicator(
                id=make_id(f"ind-{t['source_record_id']}-{idx}"),
                threat_record_id=record.id,
                indicator_type=ind["type"],
                value=ind["value"],
                confidence=t.get("confidence"),
                source=t["source"],
                first_seen_at=NOW - timedelta(days=30),
                last_seen_at=NOW - timedelta(hours=6),
                metadata_data={"synthetic": True},
            )
            db.add(indicator)

    db.flush()

    # Create correlations: link threats to assets
    correlations = [
        (make_id("threat-lazarus"), make_id("swift-gateway"), None, "campaign_targeting", "SWIFT infrastructure targeted by Lazarus Group"),
        (make_id("threat-lazarus"), make_id("payment-switch"), None, "campaign_targeting", "Payment infrastructure in scope of Lazarus campaign"),
        (make_id("threat-log4shell-exploit"), make_id("internet-banking-portal"), make_id("vuln-log4j"), "vulnerability_match", "Log4Shell CVE matches detected vulnerability"),
        (make_id("threat-ransomware-india"), make_id("email-gateway"), None, "indicator_match", "Phishing indicators match email gateway traffic"),
        (make_id("threat-ransomware-india"), make_id("core-banking-server"), None, "campaign_targeting", "Indian BFSI ransomware campaign targets core banking"),
    ]

    for threat_id, asset_id, vuln_id, corr_type, reason in correlations:
        corr = ThreatCorrelation(
            id=make_id(f"corr-{threat_id}-{asset_id}"),
            organization_id=ORG_ID,
            threat_record_id=threat_id,
            asset_id=asset_id,
            vulnerability_id=vuln_id,
            correlation_type=corr_type,
            confidence=90,
            reason=reason,
            metadata_data={"synthetic": True},
        )
        db.add(corr)

    db.flush()
    logger.info(f"✓ {len(THREATS)} threat intelligence records, indicators, and {len(correlations)} correlations seeded.")


def seed_financial_assumptions(db: Session):
    """Seed financial assumptions for the organization."""
    existing = db.scalar(select(FinancialAssumption).where(FinancialAssumption.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Financial assumptions already seeded. Skipping.")
        return

    for fa in FINANCIAL_ASSUMPTIONS:
        assumption = FinancialAssumption(
            id=make_id(f"fa-{fa['category']}"),
            organization_id=ORG_ID,
            category=fa["category"],
            name=fa["name"],
            value=fa["value"],
            unit=fa.get("unit"),
            currency=fa.get("currency"),
            source="organization_input",
            confidence=90,
        )
        db.add(assumption)

    db.flush()
    logger.info(f"✓ {len(FINANCIAL_ASSUMPTIONS)} financial assumptions seeded (INR).")


def seed_compliance_frameworks(db: Session):
    """Seed compliance frameworks and requirements."""
    existing = db.scalar(select(ComplianceFramework).limit(1))
    if existing:
        logger.info("Compliance frameworks already seeded. Skipping.")
        return

    for fw_def in COMPLIANCE_FRAMEWORKS:
        fw = ComplianceFramework(
            id=fw_def["id"],
            name=fw_def["name"],
            version=fw_def["version"],
            jurisdiction=fw_def.get("jurisdiction"),
        )
        db.add(fw)
        db.flush()

        for req_def in fw_def["requirements"]:
            req = ComplianceRequirement(
                id=make_id(f"req-{fw_def['name']}-{req_def['req_id']}"),
                framework_id=fw.id,
                requirement_id=req_def["req_id"],
                title=req_def["title"],
                category=req_def.get("category"),
                subcategory=req_def.get("subcategory"),
                applicability="applicable",
            )
            db.add(req)

    db.flush()
    total_reqs = sum(len(fw["requirements"]) for fw in COMPLIANCE_FRAMEWORKS)
    logger.info(f"✓ {len(COMPLIANCE_FRAMEWORKS)} compliance frameworks with {total_reqs} requirements seeded.")


def seed_compliance_mappings_and_evidence(db: Session):
    """Map controls to compliance requirements and add evidence."""
    existing = db.scalar(select(ComplianceControlMapping).limit(1))
    if existing:
        logger.info("Compliance mappings already seeded. Skipping.")
        return

    # Map controls to requirements (simplified but realistic)
    control_req_mappings = [
        # EDR -> NIST DE.CM-01, ISO A.8.16, RBI IT.3, SEBI CS.2
        (make_id("ctrl-edr"), [
            (make_id("fw-nist-csf"), "DE.CM-01"),
            (make_id("fw-iso27001"), "A.8.16"),
            (make_id("fw-rbi-it"), "RBI.IT.3"),
            (make_id("fw-sebi-cyber"), "SEBI.CS.2"),
        ]),
        # WAF -> NIST PR.DS-01, ISO A.8.1
        (make_id("ctrl-waf"), [
            (make_id("fw-nist-csf"), "PR.DS-01"),
            (make_id("fw-iso27001"), "A.8.1"),
        ]),
        # DLP -> NIST PR.DS-01, RBI IT.6
        (make_id("ctrl-dlp"), [
            (make_id("fw-nist-csf"), "PR.DS-01"),
            (make_id("fw-rbi-it"), "RBI.IT.6"),
        ]),
        # MFA -> NIST PR.AC-01, ISO A.8.5, SEBI CS.1
        (make_id("ctrl-mfa"), [
            (make_id("fw-nist-csf"), "PR.AC-01"),
            (make_id("fw-iso27001"), "A.8.5"),
            (make_id("fw-sebi-cyber"), "SEBI.CS.1"),
        ]),
        # SIEM -> NIST DE.CM-01, ISO A.8.16, RBI IT.3, SEBI CS.5
        (make_id("ctrl-siem"), [
            (make_id("fw-nist-csf"), "DE.CM-01"),
            (make_id("fw-iso27001"), "A.8.16"),
            (make_id("fw-rbi-it"), "RBI.IT.3"),
            (make_id("fw-sebi-cyber"), "SEBI.CS.5"),
        ]),
        # Patch Mgmt -> NIST ID.RA-01, ISO A.8.8, SEBI CS.3
        (make_id("ctrl-patch"), [
            (make_id("fw-nist-csf"), "ID.RA-01"),
            (make_id("fw-iso27001"), "A.8.8"),
            (make_id("fw-sebi-cyber"), "SEBI.CS.3"),
        ]),
        # Backup -> NIST RC.RP-01, RBI IT.5
        (make_id("ctrl-backup"), [
            (make_id("fw-nist-csf"), "RC.RP-01"),
            (make_id("fw-rbi-it"), "RBI.IT.5"),
        ]),
    ]

    mapping_count = 0
    for ctrl_id, req_refs in control_req_mappings:
        for fw_id, req_id_str in req_refs:
            # Find the requirement by framework + requirement_id
            req = db.scalar(
                select(ComplianceRequirement).where(
                    ComplianceRequirement.framework_id == fw_id,
                    ComplianceRequirement.requirement_id == req_id_str
                )
            )
            if req:
                mapping = ComplianceControlMapping(
                    id=make_id(f"map-{ctrl_id}-{req.id}"),
                    framework_id=fw_id,
                    requirement_id=req.id,
                    control_id=ctrl_id,
                    mapping_type="direct",
                    coverage_percentage=85.0,
                    confidence=90.0,
                    source="manual",
                )
                db.add(mapping)
                mapping_count += 1

                # Add evidence for implemented controls
                evidence = ComplianceEvidence(
                    id=make_id(f"ev-{ctrl_id}-{req.id}"),
                    organization_id=ORG_ID,
                    control_id=ctrl_id,
                    requirement_id=req.id,
                    evidence_type="configuration_report",
                    title=f"Configuration report for control mapping",
                    source="automated_scan",
                    collected_at=NOW - timedelta(days=7),
                    valid_from=NOW - timedelta(days=7),
                    valid_until=NOW + timedelta(days=90),
                    status="valid",
                    confidence=85.0,
                )
                db.add(evidence)

    db.flush()
    logger.info(f"✓ {mapping_count} compliance control mappings and evidence records seeded.")


# ═══════════════════════════════════════════════════════════════════════
# ENGINE EXECUTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def run_risk_engine(db: Session):
    """Run the Risk Engine (Module 6) for all assets and organization."""
    from app.services.risk_engine import RiskEngine

    existing = db.scalar(select(RiskScore).where(RiskScore.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Risk scores already exist. Skipping engine run.")
        return

    engine = RiskEngine(db)

    for asset_def in ASSETS:
        try:
            score = engine.calculate_asset_risk(asset_def["id"])
            logger.info(f"  Risk: {asset_def['name']} → {score.score:.1f} ({score.risk_level})")
        except Exception as e:
            logger.warning(f"  Risk calculation failed for {asset_def['name']}: {e}")

    # Organization-level risk
    try:
        org_score = engine.calculate_organization_risk(ORG_ID)
        logger.info(f"  ✓ Organization Risk → {org_score.score:.1f} ({org_score.risk_level})")
    except Exception as e:
        logger.warning(f"  Organization risk calculation failed: {e}")


def run_financial_engine(db: Session):
    """Run the Financial Risk Engine (Module 7) for all assets."""
    from app.services.financial_risk.engine import FinancialRiskEngine

    existing = db.scalar(
        select(FinancialRiskAssessment).where(FinancialRiskAssessment.organization_id == ORG_ID).limit(1)
    )
    if existing:
        logger.info("Financial risk assessments already exist. Skipping engine run.")
        return

    from app.models.financial_risk import FinancialRiskAssessment

    engine = FinancialRiskEngine(db)
    try:
        engine.calculate_organization_financial_risk(ORG_ID)
        logger.info("  ✓ Financial Risk Engine completed for all assets.")
    except Exception as e:
        logger.warning(f"  Financial risk engine failed: {e}")


def seed_predictions(db: Session):
    """
    Seed prediction records directly (deterministic) instead of requiring
    a trained ML model artifact. This ensures the dashboard shows prediction data.
    """
    existing = db.scalar(select(RiskPrediction).where(RiskPrediction.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Predictions already exist. Skipping.")
        return

    # First, register a synthetic model record
    model = RiskPredictionModel(
        id=make_id("model-demo-v1"),
        name="cyber_risk_forecaster",
        version="v_demo_1.0",
        model_type="DeterministicBaseline",
        dataset_version="ds_demo",
        feature_version="fv_demo",
        metrics={"mae": 4.2, "rmse": 5.8, "r2": 0.72, "baseline_mae": 8.5},
        hyperparameters={"method": "deterministic_baseline_for_demo"},
        training_started_at=NOW - timedelta(hours=1),
        training_completed_at=NOW,
        status="active",
        artifact_path="models/demo_model_placeholder.joblib",
    )
    db.add(model)
    db.flush()

    # Generate predictions for each asset with a risk score
    for asset_def in ASSETS:
        risk = db.scalar(
            select(RiskScore)
            .where(RiskScore.asset_id == asset_def["id"])
            .order_by(RiskScore.calculated_at.desc())
            .limit(1)
        )
        if not risk:
            continue

        # Deterministic prediction: slight drift based on criticality
        current = risk.score
        drift = 3.5 if asset_def["criticality"] > 85 else -1.5
        predicted = max(0, min(100, current + drift))
        trend = "increasing" if drift > 2 else ("decreasing" if drift < -2 else "stable")
        confidence = max(60, risk.risk_metadata.get("confidence", 80) - 10) if risk.risk_metadata else 70

        # Financial exposure forecast
        from app.models.financial_risk import FinancialRiskAssessment
        fin = db.scalar(
            select(FinancialRiskAssessment)
            .where(FinancialRiskAssessment.asset_id == asset_def["id"])
            .order_by(FinancialRiskAssessment.calculated_at.desc())
            .limit(1)
        )
        pred_eal = float(fin.potential_loss) * (predicted / 100.0) if fin else None

        prediction = RiskPrediction(
            id=make_id(f"pred-{asset_def['id']}"),
            organization_id=ORG_ID,
            asset_id=asset_def["id"],
            risk_score_id=risk.id,
            forecast_horizon_days=30,
            predicted_risk=round(predicted, 2),
            lower_bound=round(max(0, predicted - 6), 2),
            upper_bound=round(min(100, predicted + 6), 2),
            trend=trend,
            confidence=round(confidence, 2),
            predicted_financial_exposure=pred_eal,
            financial_lower_bound=pred_eal * 0.8 if pred_eal else None,
            financial_upper_bound=pred_eal * 1.2 if pred_eal else None,
            model_name="cyber_risk_forecaster",
            model_version="v_demo_1.0",
            feature_version="fv_demo",
            dataset_version="ds_demo",
            prediction_metadata={"drivers": [
                {"feature": "historical_trend", "importance": 0.65, "direction": trend,
                 "description": "Prediction based on current risk trajectory and asset criticality."}
            ]},
        )
        db.add(prediction)

    db.flush()
    logger.info("  ✓ Deterministic predictions seeded for all assets.")


def seed_recommendations(db: Session):
    """Seed recommendations directly for the demo."""
    existing = db.scalar(select(Recommendation).where(Recommendation.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Recommendations already exist. Skipping.")
        return

    recs_data = [
        {
            "id": make_id("rec-patch-log4j"),
            "asset_id": make_id("internet-banking-portal"),
            "title": "Emergency Patch CVE-2021-44228 (Log4Shell) on Internet Banking Portal",
            "description": "Critical RCE vulnerability on an internet-facing asset. Immediate patching required.",
            "priority": "Critical",
            "estimated_cost": 50000,
            "expected_risk_reduction": 18.0,
            "rec_metadata": {
                "rationale": "Internet-exposed RCE with active exploitation in the wild (CISA KEV).",
                "risk_driver": "Unpatched Vulnerability",
                "urgency": "Immediate",
                "expected_financial_benefit": 15000000,
                "implementation_effort": "Low",
                "confidence": 98.0,
                "evidence": [{"source": "Vulnerability Scanner", "detail": "CVE-2021-44228 on internet-facing portal", "severity": "critical"}],
            },
        },
        {
            "id": make_id("rec-block-lazarus"),
            "asset_id": make_id("swift-gateway"),
            "title": "Deploy IoC Blocks for Lazarus Group SWIFT Campaign",
            "description": "Threat intelligence indicates active Lazarus Group campaign targeting SWIFT infrastructure.",
            "priority": "Critical",
            "estimated_cost": 25000,
            "expected_risk_reduction": 22.0,
            "rec_metadata": {
                "rationale": "State-sponsored threat actor actively targeting SWIFT. Blocking known IoCs is highest priority.",
                "risk_driver": "Active Threat Campaign",
                "urgency": "Immediate",
                "expected_financial_benefit": 40000000,
                "implementation_effort": "Medium",
                "confidence": 95.0,
                "evidence": [{"source": "Threat Intelligence", "detail": "Lazarus Group SWIFT campaign (CISA AA24-001A)", "severity": "critical"}],
            },
        },
        {
            "id": make_id("rec-patch-spring4shell"),
            "asset_id": make_id("mobile-banking-api"),
            "title": "Patch CVE-2022-22965 (Spring4Shell) on Mobile Banking API",
            "description": "Critical Spring Framework RCE on internet-facing API gateway.",
            "priority": "Critical",
            "estimated_cost": 75000,
            "expected_risk_reduction": 15.0,
            "rec_metadata": {
                "rationale": "API gateway with Spring4Shell RCE accessible from internet.",
                "risk_driver": "Unpatched Vulnerability",
                "urgency": "24 Hours",
                "expected_financial_benefit": 12000000,
                "implementation_effort": "Medium",
                "confidence": 92.0,
                "evidence": [{"source": "Vulnerability Scanner", "detail": "CVE-2022-22965 on API gateway", "severity": "critical"}],
            },
        },
        {
            "id": make_id("rec-patch-bluekeep"),
            "asset_id": make_id("atm-controller"),
            "title": "Remediate BlueKeep (CVE-2019-0708) on ATM Controller",
            "description": "Wormable RDP vulnerability on ATM network controller.",
            "priority": "High",
            "estimated_cost": 100000,
            "expected_risk_reduction": 12.0,
            "rec_metadata": {
                "rationale": "BlueKeep is wormable and ATM malware has been detected on this host.",
                "risk_driver": "Unpatched Vulnerability + Active Malware",
                "urgency": "24 Hours",
                "expected_financial_benefit": 8000000,
                "implementation_effort": "High",
                "confidence": 88.0,
                "evidence": [{"source": "EDR + Vulnerability Scanner", "detail": "BlueKeep + Ploutus.D malware detected", "severity": "high"}],
            },
        },
        {
            "id": make_id("rec-tls-swift"),
            "asset_id": make_id("swift-gateway"),
            "title": "Disable TLS 1.0 on SWIFT Gateway",
            "description": "Deprecated TLS version enables downgrade attacks on payment gateway.",
            "priority": "High",
            "estimated_cost": 30000,
            "expected_risk_reduction": 8.0,
            "rec_metadata": {
                "rationale": "RBI mandates TLS 1.2+ for financial transaction systems.",
                "risk_driver": "Weak Cryptography",
                "urgency": "7 Days",
                "expected_financial_benefit": 5000000,
                "implementation_effort": "Low",
                "confidence": 90.0,
                "evidence": [{"source": "Configuration Audit", "detail": "TLS 1.0 enabled on SWIFT Alliance Lite2", "severity": "high"}],
            },
        },
        {
            "id": make_id("rec-review-cbs"),
            "asset_id": make_id("core-banking-server"),
            "title": "Conduct Security Review of Core Banking Server",
            "description": "AI engine predicts increasing risk for CBS due to lateral movement and high criticality.",
            "priority": "Medium",
            "estimated_cost": 200000,
            "expected_risk_reduction": 10.0,
            "rec_metadata": {
                "rationale": "Lateral movement detected + predicted risk increase warrants proactive review.",
                "risk_driver": "Negative Risk Trend",
                "urgency": "7 Days",
                "expected_financial_benefit": 7000000,
                "implementation_effort": "High",
                "confidence": 78.0,
                "evidence": [{"source": "AI Prediction Engine", "detail": "Risk forecasted to increase by 3.5 points in 30 days", "severity": "high"}],
            },
        },
    ]

    for r in recs_data:
        rec = Recommendation(
            id=r["id"],
            organization_id=ORG_ID,
            asset_id=r["asset_id"],
            title=r["title"],
            description=r["description"],
            priority=r["priority"],
            estimated_cost=r["estimated_cost"],
            expected_risk_reduction=r["expected_risk_reduction"],
            status="proposed",
            rec_metadata=r["rec_metadata"],
        )
        db.add(rec)

    db.flush()
    logger.info(f"  ✓ {len(recs_data)} recommendations seeded.")


def seed_investments_and_optimization(db: Session):
    """Seed investment candidates and run a budget optimization."""
    existing = db.scalar(select(CybersecurityInvestment).where(CybersecurityInvestment.organization_id == ORG_ID).limit(1))
    if existing:
        logger.info("Investment candidates already exist. Skipping.")
        return

    investments = [
        {
            "id": make_id("inv-patch-log4j"),
            "rec_id": make_id("rec-patch-log4j"),
            "asset_id": make_id("internet-banking-portal"),
            "title": "Patch Log4Shell on Internet Banking",
            "cost": 50000, "risk_reduction": 18.0, "financial_reduction": 15000000,
            "priority": "Critical", "urgency": "Immediate", "confidence": 98, "mandatory": True,
        },
        {
            "id": make_id("inv-block-lazarus"),
            "rec_id": make_id("rec-block-lazarus"),
            "asset_id": make_id("swift-gateway"),
            "title": "Deploy IoC Blocks for Lazarus Campaign",
            "cost": 25000, "risk_reduction": 22.0, "financial_reduction": 40000000,
            "priority": "Critical", "urgency": "Immediate", "confidence": 95, "mandatory": True,
        },
        {
            "id": make_id("inv-patch-spring4shell"),
            "rec_id": make_id("rec-patch-spring4shell"),
            "asset_id": make_id("mobile-banking-api"),
            "title": "Patch Spring4Shell on Mobile API",
            "cost": 75000, "risk_reduction": 15.0, "financial_reduction": 12000000,
            "priority": "Critical", "urgency": "24 Hours", "confidence": 92,
        },
        {
            "id": make_id("inv-patch-bluekeep"),
            "rec_id": make_id("rec-patch-bluekeep"),
            "asset_id": make_id("atm-controller"),
            "title": "Remediate BlueKeep on ATM Controller",
            "cost": 100000, "risk_reduction": 12.0, "financial_reduction": 8000000,
            "priority": "High", "urgency": "24 Hours", "confidence": 88,
        },
        {
            "id": make_id("inv-tls-swift"),
            "rec_id": make_id("rec-tls-swift"),
            "asset_id": make_id("swift-gateway"),
            "title": "Disable TLS 1.0 on SWIFT",
            "cost": 30000, "risk_reduction": 8.0, "financial_reduction": 5000000,
            "priority": "High", "urgency": "7 Days", "confidence": 90,
        },
        {
            "id": make_id("inv-review-cbs"),
            "rec_id": make_id("rec-review-cbs"),
            "asset_id": make_id("core-banking-server"),
            "title": "Security Review of CBS",
            "cost": 200000, "risk_reduction": 10.0, "financial_reduction": 7000000,
            "priority": "Medium", "urgency": "7 Days", "confidence": 78,
        },
    ]

    for inv in investments:
        candidate = CybersecurityInvestment(
            id=inv["id"],
            organization_id=ORG_ID,
            recommendation_id=inv.get("rec_id"),
            asset_id=inv.get("asset_id"),
            title=inv["title"],
            cost=inv["cost"],
            currency="INR",
            cost_type="one_time",
            risk_reduction=inv["risk_reduction"],
            financial_reduction=inv["financial_reduction"],
            priority=inv["priority"],
            urgency=inv["urgency"],
            confidence=inv["confidence"],
            mandatory=inv.get("mandatory", False),
            status="candidate",
        )
        db.add(candidate)

    db.flush()
    logger.info(f"  ✓ {len(investments)} investment candidates seeded.")

    # Run optimization with ₹50 Lakh budget
    try:
        from app.services.optimization.engine import OptimizationEngine
        from app.schemas.optimization import OptimizationRunRequest, OptimizationWeights

        request = OptimizationRunRequest(
            budget=5000000,  # ₹50 Lakh
            currency="INR",
            horizon_months=12,
            objective="balanced",
            weights=OptimizationWeights(),
        )
        opt_engine = OptimizationEngine(db, ORG_ID)
        run = opt_engine.run_optimization(request)
        logger.info(f"  ✓ Optimization Run: {run.optimization_status}, Selected cost: ₹{run.total_cost:,.0f}, Risk reduction: {run.risk_reduction:.1f}")
    except Exception as e:
        logger.warning(f"  Optimization engine failed (non-critical): {e}")


def run_compliance_engine(db: Session):
    """Run the Compliance Engine (Module 11) for all frameworks."""
    from app.services.compliance.engine import ComplianceEngine

    existing = db.scalar(
        select(ComplianceAssessment).where(ComplianceAssessment.organization_id == ORG_ID).limit(1)
    )
    if existing:
        logger.info("Compliance assessments already exist. Skipping.")
        return

    from app.models.compliance import ComplianceAssessment

    engine = ComplianceEngine(db, ORG_ID)
    frameworks = db.scalars(select(ComplianceFramework)).all()

    for fw in frameworks:
        try:
            summary = engine.assess_framework(fw.id)
            logger.info(f"  Compliance: {fw.name} → {summary.coverage_percentage:.0f}% coverage, {summary.non_compliant} non-compliant, {summary.open_gaps} gaps")
        except Exception as e:
            logger.warning(f"  Compliance assessment failed for {fw.name}: {e}")

    logger.info("  ✓ Compliance Engine completed for all frameworks.")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    logger.info("=" * 60)
    logger.info("SIH Demo Seed Script — Example Bank")
    logger.info("All data is SYNTHETIC for demonstration only.")
    logger.info("=" * 60)

    with Session(engine) as db:
        try:
            # Phase 1: Base data
            logger.info("\n▶ Phase 1: Seeding base data...")
            seed_organization(db)
            seed_assets(db)
            seed_vulnerabilities(db)
            seed_telemetry(db)
            seed_controls(db)
            seed_threat_intelligence(db)
            seed_financial_assumptions(db)
            seed_compliance_frameworks(db)
            seed_compliance_mappings_and_evidence(db)
            db.commit()
            logger.info("  ✓ Base data committed.\n")

            # Phase 2: Run engines in dependency order
            logger.info("▶ Phase 2: Running calculation engines...")

            logger.info("\n  [Module 6] Risk Engine...")
            run_risk_engine(db)

            logger.info("\n  [Module 7] Financial Risk Engine...")
            run_financial_engine(db)

            logger.info("\n  [Module 8] Prediction Engine...")
            seed_predictions(db)

            logger.info("\n  [Module 9] Recommendation Engine...")
            seed_recommendations(db)

            logger.info("\n  [Module 10] Optimization Engine...")
            seed_investments_and_optimization(db)

            logger.info("\n  [Module 11] Compliance Engine...")
            run_compliance_engine(db)

            db.commit()
            logger.info("\n  ✓ All engines completed and data committed.\n")

            # Phase 3: Verification
            logger.info("▶ Phase 3: Verification...")
            verify_seed(db)

            logger.info("\n" + "=" * 60)
            logger.info("✅ SIH Demo seed completed successfully!")
            logger.info("=" * 60)

        except Exception as e:
            db.rollback()
            logger.error(f"\n❌ Seed failed: {e}")
            raise


def verify_seed(db: Session):
    """Quick verification of seeded data."""
    checks = [
        ("Organizations", Organization, 1),
        ("Users", User, 1),
        ("Assets", Asset, len(ASSETS)),
        ("Vulnerabilities", Vulnerability, len(VULNERABILITIES)),
        ("Telemetry Events", TelemetryEvent, len(TELEMETRY)),
        ("Security Controls", SecurityControl, len(CONTROLS)),
        ("Threat Intel Records", ThreatIntelligenceRecord, len(THREATS)),
        ("Financial Assumptions", FinancialAssumption, len(FINANCIAL_ASSUMPTIONS)),
        ("Risk Scores", RiskScore, None),
        ("Financial Assessments", FinancialRiskAssessment, None),
        ("Predictions", RiskPrediction, None),
        ("Recommendations", Recommendation, None),
        ("Compliance Frameworks", ComplianceFramework, len(COMPLIANCE_FRAMEWORKS)),
    ]

    all_pass = True
    for name, model, expected in checks:
        count = db.scalar(select(func.count()).select_from(model))
        status = "✓" if (expected is None and count > 0) or count >= (expected or 0) else "✗"
        if status == "✗":
            all_pass = False
        detail = f"(expected ≥{expected})" if expected else ""
        logger.info(f"  {status} {name}: {count} records {detail}")

    if not all_pass:
        logger.warning("  ⚠ Some checks failed — dashboard may have incomplete data.")


if __name__ == "__main__":
    main()
