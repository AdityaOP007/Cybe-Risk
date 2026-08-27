import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.control import SecurityControl
from app.models.compliance import (
    ComplianceFramework, ComplianceRequirement, ComplianceApplicability,
    ComplianceControlMapping, ComplianceEvidence, ComplianceAssessment,
    ComplianceGap, ComplianceException
)

def seed_compliance():
    db = SessionLocal()
    org = db.scalars(select(Organization)).first()
    if not org:
        print("No organization found. Seed core first.")
        return

    # 1. Frameworks
    nist_fw = ComplianceFramework(
        name="NIST CSF 2.0",
        version="2.0",
        jurisdiction="US/Global",
        effective_date=datetime(2024, 2, 26, tzinfo=timezone.utc),
        source_reference="https://www.nist.gov/cyberframework",
        status="active"
    )
    iso_fw = ComplianceFramework(
        name="ISO/IEC 27001",
        version="2022",
        jurisdiction="Global",
        effective_date=datetime(2022, 10, 25, tzinfo=timezone.utc),
        source_reference="https://www.iso.org/standard/27001",
        status="active"
    )
    rbi_fw = ComplianceFramework(
        name="RBI Cyber Security Framework",
        version="2016",
        jurisdiction="India (Financial)",
        source_reference="RBI/2015-16/418",
        status="active"
    )
    sebi_fw = ComplianceFramework(
        name="SEBI Cyber Security & Resilience",
        version="2023",
        jurisdiction="India (Capital Markets)",
        source_reference="SEBI/HO/MRD/DP/CIR/P/2015/55",
        status="active"
    )
    
    db.add_all([nist_fw, iso_fw, rbi_fw, sebi_fw])
    db.commit()

    # 2. Requirements (Subset for prototype)
    nist_reqs = [
        ComplianceRequirement(framework_id=nist_fw.id, requirement_id="ID.AM-01", title="Inventories of hardware, software, services, and systems are maintained", category="Identify (ID)", subcategory="Asset Management (AM)"),
        ComplianceRequirement(framework_id=nist_fw.id, requirement_id="PR.AC-01", title="Identities and credentials are managed (MFA)", category="Protect (PR)", subcategory="Access Control (AC)"),
        ComplianceRequirement(framework_id=nist_fw.id, requirement_id="DE.CM-01", title="Network and environment are monitored for anomalies", category="Detect (DE)", subcategory="Continuous Monitoring (CM)"),
    ]
    iso_reqs = [
        ComplianceRequirement(framework_id=iso_fw.id, requirement_id="A.8.1.1", title="Inventory of assets", category="Asset Management"),
        ComplianceRequirement(framework_id=iso_fw.id, requirement_id="A.9.2.3", title="Management of privileged access rights", category="Access Control"),
        ComplianceRequirement(framework_id=iso_fw.id, requirement_id="A.12.4.1", title="Event logging", category="Operations Security"),
    ]
    rbi_reqs = [
        ComplianceRequirement(framework_id=rbi_fw.id, requirement_id="RBI-1", title="Asset Registry (IT and Data)", category="Asset Management"),
        ComplianceRequirement(framework_id=rbi_fw.id, requirement_id="RBI-2", title="Multi-Factor Authentication for Critical Systems", category="Access Control"),
        ComplianceRequirement(framework_id=rbi_fw.id, requirement_id="RBI-5", title="Real-time SOC monitoring", category="Detect"),
    ]
    db.add_all(nist_reqs + iso_reqs + rbi_reqs)
    db.commit()

    # 3. Applicability
    # Say DE.CM-01 is not applicable for some reason
    db.add(ComplianceApplicability(
        organization_id=org.id,
        requirement_id=nist_reqs[2].id,
        status="not_applicable",
        rationale="Outsourced to MSSP entirely, covered by a different framework requirement"
    ))

    # 4. Create some Controls
    c_mfa = SecurityControl(
        organization_id=org.id,
        name="Enterprise MFA",
        description="Okta based MFA for all employees",
        control_type="Preventative",
        coverage_percentage=95.0,
        effectiveness_percentage=98.0,
        implementation_status="implemented"
    )
    c_asset = SecurityControl(
        organization_id=org.id,
        name="Asset Inventory Tool",
        description="Snipe-IT deployed",
        control_type="Detective",
        coverage_percentage=70.0,
        effectiveness_percentage=80.0,
        implementation_status="partially_implemented"
    )
    c_soc = SecurityControl(
        organization_id=org.id,
        name="SOC SIEM",
        description="Splunk Cloud",
        control_type="Detective",
        coverage_percentage=90.0,
        effectiveness_percentage=95.0,
        implementation_status="implemented"
    )
    db.add_all([c_mfa, c_asset, c_soc])
    db.commit()

    # 5. Mappings (The Crosswalk)
    mappings = [
        # MFA Maps to NIST, ISO, RBI
        ComplianceControlMapping(framework_id=nist_fw.id, requirement_id=nist_reqs[1].id, control_id=c_mfa.id, mapping_type="direct"),
        ComplianceControlMapping(framework_id=iso_fw.id, requirement_id=iso_reqs[1].id, control_id=c_mfa.id, mapping_type="direct"),
        ComplianceControlMapping(framework_id=rbi_fw.id, requirement_id=rbi_reqs[1].id, control_id=c_mfa.id, mapping_type="direct"),
        
        # Asset Maps to NIST, ISO, RBI
        ComplianceControlMapping(framework_id=nist_fw.id, requirement_id=nist_reqs[0].id, control_id=c_asset.id, mapping_type="partial", coverage_percentage=70.0),
        ComplianceControlMapping(framework_id=iso_fw.id, requirement_id=iso_reqs[0].id, control_id=c_asset.id, mapping_type="partial", coverage_percentage=70.0),
        ComplianceControlMapping(framework_id=rbi_fw.id, requirement_id=rbi_reqs[0].id, control_id=c_asset.id, mapping_type="partial", coverage_percentage=70.0),

        # SOC Maps to NIST, ISO, RBI
        ComplianceControlMapping(framework_id=nist_fw.id, requirement_id=nist_reqs[2].id, control_id=c_soc.id, mapping_type="direct"),
        ComplianceControlMapping(framework_id=iso_fw.id, requirement_id=iso_reqs[2].id, control_id=c_soc.id, mapping_type="direct"),
        ComplianceControlMapping(framework_id=rbi_fw.id, requirement_id=rbi_reqs[2].id, control_id=c_soc.id, mapping_type="direct"),
    ]
    db.add_all(mappings)
    
    # 6. Evidence
    now = datetime.now(timezone.utc)
    evidences = [
        # Valid Evidence for MFA
        ComplianceEvidence(
            organization_id=org.id, control_id=c_mfa.id, evidence_type="Policy Document",
            title="Okta MFA Enforced Policy Screenshot", collected_at=now, valid_from=now - timedelta(days=30),
            valid_until=now + timedelta(days=330), status="valid"
        ),
        # Valid Evidence for Asset
        ComplianceEvidence(
            organization_id=org.id, control_id=c_asset.id, evidence_type="System Export",
            title="Snipe-IT Active Asset List", collected_at=now, valid_from=now - timedelta(days=5),
            valid_until=now + timedelta(days=25), status="valid"
        ),
        # Expired Evidence for SOC
        ComplianceEvidence(
            organization_id=org.id, control_id=c_soc.id, evidence_type="Audit Log",
            title="Splunk Q1 Alert Report", collected_at=now - timedelta(days=120), valid_from=now - timedelta(days=120),
            valid_until=now - timedelta(days=30), status="valid" # valid until is in past, so it's technically expired
        ),
    ]
    db.add_all(evidences)
    
    # 7. Exception for ISO A.12.4.1 (SOC Logging)
    db.add(ComplianceException(
        organization_id=org.id,
        requirement_id=iso_reqs[2].id,
        control_id=c_soc.id,
        reason="Logging system migration underway",
        business_justification="Accepting risk of incomplete logs during Q3 migration to Datadog",
        approved_by="CISO",
        approved_at=now - timedelta(days=10),
        expires_at=now + timedelta(days=50),
        status="approved"
    ))
    
    db.commit()
    print("Compliance module seeded successfully!")
    
    # Run Engine Assessment
    from app.services.compliance.engine import ComplianceEngine
    engine = ComplianceEngine(db, org.id)
    print(engine.assess_framework(nist_fw.id))
    print(engine.assess_framework(iso_fw.id))
    print(engine.assess_framework(rbi_fw.id))
    print(engine.assess_framework(sebi_fw.id))
    db.close()

if __name__ == "__main__":
    seed_compliance()
