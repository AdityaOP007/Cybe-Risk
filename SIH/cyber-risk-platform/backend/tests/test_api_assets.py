import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.telemetry import TelemetryEvent
from datetime import datetime, timezone

def create_test_org(db_session: Session) -> uuid.UUID:
    org = Organization(name="Test Org", industry="Tech", organization_type="enterprise", country="US")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org.id

def test_create_asset(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    response = client.post(
        "/api/v1/assets/",
        json={
            "organization_id": str(org_id),
            "name": "Test Server",
            "asset_type": "server",
            "environment": "production",
            "criticality": 90,
            "business_value": 100000.0,
            "hostname": "test-prod-1",
            "ip_address": "192.168.1.10"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Server"
    assert data["criticality"] == 90
    assert data["status"] == "active"
    assert data["ip_address"] == "192.168.1.10"

def test_create_duplicate_asset(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_data = {
        "organization_id": str(org_id),
        "name": "Test Server",
        "asset_type": "server",
        "environment": "production",
        "hostname": "test-prod-1",
        "ip_address": "192.168.1.10"
    }
    client.post("/api/v1/assets/", json=asset_data)
    
    # Second time should fail because of duplicate hostname/ip
    response = client.post("/api/v1/assets/", json=asset_data)
    assert response.status_code == 409

def test_update_asset(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    response = client.post(
        "/api/v1/assets/",
        json={
            "organization_id": str(org_id),
            "name": "Test Server",
            "asset_type": "server",
            "environment": "production"
        }
    )
    asset_id = response.json()["id"]
    
    update_resp = client.put(
        f"/api/v1/assets/{asset_id}",
        json={
            "name": "Updated Server",
            "criticality": 50
        }
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Server"
    assert update_resp.json()["criticality"] == 50

def test_retire_asset(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    response = client.post(
        "/api/v1/assets/",
        json={
            "organization_id": str(org_id),
            "name": "Test Server",
            "asset_type": "server",
            "environment": "production"
        }
    )
    asset_id = response.json()["id"]
    
    retire_resp = client.post(f"/api/v1/assets/{asset_id}/retire")
    assert retire_resp.status_code == 200
    
    get_resp = client.get(f"/api/v1/assets/{asset_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "retired"

def test_list_assets_with_filters(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    client.post("/api/v1/assets/", json={"organization_id": str(org_id), "name": "App1", "asset_type": "application", "environment": "production", "criticality": 100})
    client.post("/api/v1/assets/", json={"organization_id": str(org_id), "name": "DB1", "asset_type": "database", "environment": "development", "criticality": 20})
    client.post("/api/v1/assets/", json={"organization_id": str(org_id), "name": "Server1", "asset_type": "server", "environment": "production", "criticality": 80})

    # Test filtering by env
    resp = client.get("/api/v1/assets/?environment=production")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 2
    
    # Test filtering by criticality range
    resp = client.get("/api/v1/assets/?criticality_min=50")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 2
    
    # Test pagination
    resp = client.get("/api/v1/assets/?page=1&page_size=1")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1
    assert resp.json()["total"] == 3

def test_asset_posture(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    
    # Create asset
    asset = Asset(organization_id=org_id, name="Test Posture Asset", asset_type="server", environment="prod", criticality=90)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    
    # Add vulns
    v1 = Vulnerability(asset_id=asset.id, title="Vuln 1", severity="critical", cvss_score=9.8, status="open")
    v2 = Vulnerability(asset_id=asset.id, title="Vuln 2", severity="high", cvss_score=7.0, status="open")
    db_session.add_all([v1, v2])
    
    # Add telemetry
    t1 = TelemetryEvent(organization_id=org_id, asset_id=asset.id, source="firewall", event_type="port_scan", severity="low", occurred_at=datetime.now(timezone.utc))
    db_session.add(t1)
    db_session.commit()
    
    # Test posture endpoint
    resp = client.get(f"/api/v1/assets/{asset.id}/posture")
    assert resp.status_code == 200
    data = resp.json()
    assert data["open_vulnerabilities"] == 2
    assert data["critical_vulnerabilities"] == 1
    assert data["recent_telemetry_events"] == 1
