import pytest
from sqlalchemy.exc import IntegrityError
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.telemetry import TelemetryEvent
from app.models.control import SecurityControl
from app.models.risk import RiskScore

def test_create_organization(db_session):
    org = Organization(name="Test Org", industry="Tech")
    db_session.add(org)
    db_session.commit()
    
    assert org.id is not None
    assert org.name == "Test Org"
    assert org.industry == "Tech"

def test_asset_creation_and_relationship(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    asset = Asset(
        organization_id=org.id,
        name="Test Asset",
        asset_type="server",
        environment="production",
        criticality=50
    )
    db_session.add(asset)
    db_session.commit()
    
    assert asset.id is not None
    assert asset.organization_id == org.id
    assert asset.organization.name == "Test Org"

def test_vulnerability_belongs_to_asset(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    asset = Asset(
        organization_id=org.id, name="Test Asset", asset_type="server", environment="production"
    )
    db_session.add(asset)
    db_session.commit()
    
    vuln = Vulnerability(
        asset_id=asset.id, title="Test Vuln", severity="high", cvss_score=8.5
    )
    db_session.add(vuln)
    db_session.commit()
    
    assert vuln.id is not None
    assert vuln.asset_id == asset.id
    assert vuln.asset.name == "Test Asset"

from datetime import datetime, timezone

def test_telemetry_belongs_to_organization(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    telemetry = TelemetryEvent(
        organization_id=org.id, source="firewall", event_type="block", severity="low", occurred_at=datetime.now(timezone.utc)
    )
    db_session.add(telemetry)
    db_session.commit()
    
    assert telemetry.id is not None
    assert telemetry.organization_id == org.id

def test_security_control_belongs_to_organization(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    control = SecurityControl(
        organization_id=org.id, name="MFA", control_type="identity", coverage_percentage=100.0
    )
    db_session.add(control)
    db_session.commit()
    
    assert control.id is not None
    assert control.organization_id == org.id

def test_risk_score_references_org_and_asset(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    asset = Asset(
        organization_id=org.id, name="Test Asset", asset_type="server", environment="production"
    )
    db_session.add(asset)
    db_session.commit()
    
    risk = RiskScore(
        organization_id=org.id, asset_id=asset.id, score=90.0, risk_level="critical"
    )
    db_session.add(risk)
    db_session.commit()
    
    assert risk.id is not None
    assert risk.organization_id == org.id
    assert risk.asset_id == asset.id

def test_invalid_criticality_rejected(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    # Criticality > 100
    asset = Asset(
        organization_id=org.id, name="Test Asset", asset_type="server", environment="production", criticality=150
    )
    db_session.add(asset)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_invalid_cvss_score_rejected(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    asset = Asset(
        organization_id=org.id, name="Test Asset", asset_type="server", environment="production"
    )
    db_session.add(asset)
    db_session.commit()
    
    # CVSS score > 10.0
    vuln = Vulnerability(
        asset_id=asset.id, title="Test Vuln", severity="high", cvss_score=11.0
    )
    db_session.add(vuln)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_invalid_percentage_values_rejected(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    # Percentage > 100
    control = SecurityControl(
        organization_id=org.id, name="MFA", control_type="identity", coverage_percentage=105.0
    )
    db_session.add(control)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_required_foreign_keys(db_session):
    # Missing organization_id
    asset = Asset(
        name="Test Asset", asset_type="server", environment="production"
    )
    db_session.add(asset)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
