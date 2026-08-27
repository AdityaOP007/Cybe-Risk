from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.control import SecurityControl
from app.models.risk import RiskScore
from app.services.risk_engine import RiskEngine
import uuid

def create_test_org(db_session: Session) -> uuid.UUID:
    org = Organization(name="Test Org Risk", industry="Tech", organization_type="enterprise", country="US")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org.id

def create_test_asset(db_session: Session, org_id: uuid.UUID) -> uuid.UUID:
    asset = Asset(
        organization_id=org_id, 
        name="Internet Facing Web Server", 
        asset_type="server", 
        environment="production", 
        criticality=100,
        business_value=1000000,
        internet_exposed=True
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset.id

def test_risk_calculation(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)

    # 1. Base Risk Calculation
    response = client.post(f"/api/v1/risk/calculate/asset/{asset_id}")
    assert response.status_code == 200
    data = response.json()
    print("DEBUG DATA:", data)
    base_score = data["score"]
    
    # Assert impact is calculated correctly
    assert data["metadata"]["factors"]["impact"] > 0
    assert "Asset is internet exposed" in data["metadata"]["drivers"]

    # 2. Add Vulnerability to increase likelihood
    vuln = Vulnerability(
        asset_id=asset_id,
        cve_id="CVE-2024-RISK",
        title="Critical RCE",
        severity="critical",
        cvss_score=9.8
    )
    db_session.add(vuln)
    db_session.commit()

    response = client.post(f"/api/v1/risk/calculate/asset/{asset_id}")
    data = response.json()
    vuln_score = data["score"]
    assert vuln_score > base_score # Risk should go up
    assert data["metadata"]["factors"]["likelihood"] > 0

    # 3. Add Security Control to mitigate risk
    ctrl = SecurityControl(
        organization_id=org_id,
        name="WAF",
        control_type="preventative",
        coverage_percentage=100,
        effectiveness_percentage=50, # Should mitigate 50%
        status="active"
    )
    db_session.add(ctrl)
    db_session.commit()

    response = client.post(f"/api/v1/risk/calculate/asset/{asset_id}")
    data = response.json()
    mitigated_score = data["score"]
    
    assert mitigated_score < vuln_score # Risk should go down due to control
    assert data["metadata"]["factors"]["mitigation_factor"] == 0.5
    
    # 4. Calculate Org Risk
    response = client.post(f"/api/v1/risk/calculate/organization/{org_id}")
    assert response.status_code == 200
    org_data = response.json()
    assert org_data["metadata"]["factors"]["total_assets"] == 1
    assert org_data["score"] == mitigated_score # Only 1 asset, so org risk = asset risk

def test_get_risk_trend(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)
    
    client.post(f"/api/v1/risk/calculate/asset/{asset_id}")
    
    response = client.get(f"/api/v1/risk/assets/{asset_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "current_score" in data
    assert "historical_trend" in data
    assert len(data["historical_trend"]) >= 1
