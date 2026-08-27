import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.financial_risk import FinancialAssumption
from app.models.asset import Asset
from app.models.organization import Organization
from app.models.risk import RiskScore

def create_test_org(db: Session) -> str:
    org = Organization(
        name="Test Fin Org",
        industry="Finance",
        organization_type="Enterprise"
    )
    db.add(org)
    db.commit()
    return str(org.id)

def create_test_asset(db: Session, org_id: str) -> str:
    asset = Asset(
        organization_id=org_id,
        name="Test Gateway",
        asset_type="server",
        environment="production",
        criticality=100,
        business_value=1000000.0,
        internet_exposed=True
    )
    db.add(asset)
    db.commit()
    return str(asset.id)

def create_test_risk_score(db: Session, org_id: str, asset_id: str) -> str:
    rs = RiskScore(
        organization_id=org_id,
        asset_id=asset_id,
        score=72.0,
        risk_level="high",
        calculation_version="v1.0",
        metadata_={"factors": {"likelihood": 72.0}, "confidence": 100}
    )
    db.add(rs)
    db.commit()
    return str(rs.id)

def create_test_assumptions(db: Session, org_id: str):
    assumptions = [
        FinancialAssumption(organization_id=org_id, category="downtime_hours", name="Downtime", value=10, unit="hours"),
        FinancialAssumption(organization_id=org_id, category="revenue_impact_per_hour", name="Revenue Impact", value=200000, unit="INR"),
        FinancialAssumption(organization_id=org_id, category="recovery_cost", name="Recovery", value=1500000, unit="INR"),
        FinancialAssumption(organization_id=org_id, category="annual_event_frequency", name="Frequency", value=0.25, unit="events/year")
    ]
    db.add_all(assumptions)
    db.commit()

def test_financial_risk_calculation(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)
    create_test_risk_score(db_session, org_id, asset_id)
    create_test_assumptions(db_session, org_id)

    # Calculate Asset Financial Risk
    response = client.post(f"/api/v1/financial-risk/assets/{asset_id}/calculate")
    assert response.status_code == 200
    data = response.json()
    
    # 10 * 200000 = 2,000,000 BI
    # Recovery = 1,500,000
    # Potential = 3,500,000
    # EAL = 3,500,000 * 0.25 = 875,000
    
    assert float(data["potential_loss"]) == 3500000.0
    assert float(data["expected_loss"]) == 875000.0
    assert float(data["business_interruption_loss"]) == 2000000.0
    assert float(data["recovery_loss"]) == 1500000.0

def test_org_financial_risk_aggregation(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)
    create_test_risk_score(db_session, org_id, asset_id)
    create_test_assumptions(db_session, org_id)
    
    # First, calculate
    client.post(f"/api/v1/financial-risk/assets/{asset_id}/calculate")
    
    # Then fetch org aggregate
    response = client.get(f"/api/v1/financial-risk/organizations/{org_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert float(data["total_potential_loss"]) == 3500000.0
    assert float(data["total_expected_annual_loss"]) == 875000.0
    assert len(data["top_financial_risk_assets"]) == 1
