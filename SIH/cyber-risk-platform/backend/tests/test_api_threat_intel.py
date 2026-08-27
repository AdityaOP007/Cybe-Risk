from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.models.vulnerability import Vulnerability
from app.models.asset import Asset
from app.models.organization import Organization
import uuid

def create_test_org(db_session: Session) -> uuid.UUID:
    org = Organization(name="Test Org Threat Intel", industry="Tech", organization_type="enterprise", country="US")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org.id

def create_test_asset(db_session: Session, org_id: uuid.UUID) -> uuid.UUID:
    asset = Asset(organization_id=org_id, name="Test Asset Threat Intel", asset_type="server", environment="production", criticality=90)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset.id

def test_ingest_threat_intel(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)

    # Ensure asset has a specific vulnerability to match
    vuln = Vulnerability(
        asset_id=asset_id,
        cve_id="CVE-2026-99999",
        title="Test CVE",
        severity="critical"
    )
    db_session.add(vuln)
    db_session.commit()
    db_session.refresh(vuln)

    # Ingest a threat that should correlate
    payload = {
        "source": "nvd",
        "source_record_id": "cve-2026-99999",
        "intelligence_type": "vulnerability",
        "title": "cve-2026-99999",
        "severity": "critical",
        "known_exploited": True,
        "indicators": [
            {
                "indicator_type": "ipv4",
                "value": "1.2.3.4",
                "confidence": 90
            }
        ]
    }
    
    response = client.post("/api/v1/threat-intelligence/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "CVE-2026-99999" # Should be normalized to uppercase
    assert data["severity"] == "critical"
    
    # Check deduplication
    response2 = client.post("/api/v1/threat-intelligence/", json=payload)
    assert response2.status_code == 201
    assert response2.json()["id"] == data["id"] # Should return the existing ID
    
    # Check correlation was created
    correlations = db_session.query(ThreatCorrelation).filter(ThreatCorrelation.threat_record_id == data["id"]).all()
    assert len(correlations) > 0
    assert correlations[0].vulnerability_id == vuln.id
    assert correlations[0].asset_id == asset_id
    assert correlations[0].organization_id == org_id

def test_get_threat_intel(client: TestClient, db_session: Session):
    response = client.get("/api/v1/threat-intelligence/")
    assert response.status_code == 200
    assert "items" in response.json()

def test_get_threat_stats(client: TestClient, db_session: Session):
    response = client.get("/api/v1/threat-intelligence/stats")
    assert response.status_code == 200
    assert "total_threats" in response.json()
