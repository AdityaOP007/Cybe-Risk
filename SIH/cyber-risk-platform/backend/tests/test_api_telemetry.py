import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from app.models.organization import Organization
from app.models.asset import Asset
from app.models.telemetry import TelemetryEvent

def create_test_org(db_session: Session) -> uuid.UUID:
    org = Organization(name="Test Org Telemetry", industry="Tech", organization_type="enterprise", country="US")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org.id

def create_test_asset(db_session: Session, org_id: uuid.UUID) -> uuid.UUID:
    asset = Asset(organization_id=org_id, name="Test Asset Telemetry", asset_type="server", environment="production", criticality=90)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset.id

def test_create_telemetry_single(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)
    
    response = client.post(
        "/api/v1/telemetry/events",
        json={
            "organization_id": str(org_id),
            "asset_id": str(asset_id),
            "source": "siem",
            "event_type": "authentication_failure", # Should normalize to failed_login
            "severity": "priority_1", # Should normalize to critical
            "message": "Auth failed",
            "source_event_id": "SIEM-001",
            "occurred_at": datetime.now(timezone.utc).isoformat()
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "failed_login"
    assert data["severity"] == "critical"
    assert data["source"] == "siem"

def test_create_telemetry_duplicate(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    
    payload = {
        "organization_id": str(org_id),
        "source": "edr",
        "event_type": "malware_detected",
        "severity": "high",
        "source_event_id": "EDR-999",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    }
    
    # First create should succeed
    resp1 = client.post("/api/v1/telemetry/events", json=payload)
    assert resp1.status_code == 201
    
    # Second create with same source_event_id and source and org should fail
    resp2 = client.post("/api/v1/telemetry/events", json=payload)
    assert resp2.status_code == 409

def test_create_batch_telemetry(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    asset_id = create_test_asset(db_session, org_id)
    
    # Another org for testing validation
    org_id_2 = create_test_org(db_session)
    
    payload = {
        "events": [
            {
                "organization_id": str(org_id),
                "asset_id": str(asset_id),
                "source": "fw",
                "event_type": "port_scan",
                "severity": "low",
                "source_event_id": "FW-1",
            },
            {
                "organization_id": str(org_id),
                "source": "fw",
                "event_type": "port_scan",
                "severity": "low",
                "source_event_id": "FW-2",
            },
            {
                # Should fail: asset doesn't belong to this org
                "organization_id": str(org_id_2),
                "asset_id": str(asset_id),
                "source": "fw",
                "event_type": "port_scan",
                "severity": "low",
            }
        ]
    }
    
    resp = client.post("/api/v1/telemetry/events/batch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["total"] == 3
    assert data["accepted"] == 2
    assert data["rejected"] == 1
    assert "belong to organization" in data["errors"][0]["error"]

def test_telemetry_stats(client: TestClient, db_session: Session):
    org_id = create_test_org(db_session)
    
    client.post("/api/v1/telemetry/events", json={"organization_id": str(org_id), "source": "siem", "event_type": "failed_login", "severity": "critical"})
    client.post("/api/v1/telemetry/events", json={"organization_id": str(org_id), "source": "siem", "event_type": "failed_login", "severity": "high"})
    client.post("/api/v1/telemetry/events", json={"organization_id": str(org_id), "source": "fw", "event_type": "blocked_connection", "severity": "low"})
    
    resp = client.get(f"/api/v1/telemetry/stats?organization_id={org_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["total_events"] == 3
    assert data["critical_events"] == 1
    assert data["high_events"] == 1
    assert data["low_events"] == 1
    assert data["by_source"]["siem"] == 2
    assert data["by_source"]["fw"] == 1
