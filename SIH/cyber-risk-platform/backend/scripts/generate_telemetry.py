import uuid
import random
import logging
from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.asset import Asset
from app.schemas.telemetry import TelemetryEventCreate
from app.services.telemetry_service import telemetry_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVENT_SCENARIOS = [
    {"source": "siem", "event_type": "failed_login", "severity": "high", "message": "Multiple failed login attempts detected"},
    {"source": "siem", "event_type": "successful_login", "severity": "informational", "message": "User logged in from new IP"},
    {"source": "edr", "event_type": "malware_detected", "severity": "critical", "message": "Ransomware signature detected and quarantined"},
    {"source": "edr", "event_type": "suspicious_process", "severity": "high", "message": "PowerShell execution with suspicious arguments"},
    {"source": "firewall", "event_type": "blocked_connection", "severity": "low", "message": "Inbound connection blocked by default deny rule"},
    {"source": "firewall", "event_type": "port_scan", "severity": "medium", "message": "Sequential port scan detected from external IP"},
    {"source": "ids", "event_type": "suspicious_connection", "severity": "high", "message": "Connection to known malicious C2 domain"},
    {"source": "iam", "event_type": "privilege_escalation", "severity": "critical", "message": "User added to Domain Admins group"},
    {"source": "cloud", "event_type": "configuration_change", "severity": "medium", "message": "S3 bucket made public"},
    {"source": "application", "event_type": "unauthorized_access", "severity": "high", "message": "Attempt to access administrative API endpoint"},
]

def generate_synthetic_telemetry(num_events: int = 100):
    db = SessionLocal()
    try:
        orgs = db.query(Organization).all()
        if not orgs:
            logger.error("No organizations found. Run seed_database first.")
            return
        
        org_with_assets = None
        assets = []
        for org in orgs:
            assets = db.query(Asset).filter(Asset.organization_id == org.id).all()
            if assets:
                org_with_assets = org
                break
                
        if not org_with_assets or not assets:
            logger.error("No assets found for any organization. Run seed_database first.")
            return

        org = org_with_assets
        logger.info(f"Generating {num_events} synthetic telemetry events for organization {org.name}...")
        
        now = datetime.now(timezone.utc)
        events = []
        
        for i in range(num_events):
            scenario = random.choice(EVENT_SCENARIOS)
            asset = random.choice(assets)
            
            # Scatter events over the last 7 days
            days_ago = random.uniform(0, 7)
            occurred_at = now - timedelta(days=days_ago)
            
            source_event_id = f"SYN-{uuid.uuid4().hex[:8].upper()}"
            
            event = TelemetryEventCreate(
                organization_id=org.id,
                asset_id=asset.id,
                source=scenario["source"],
                event_type=scenario["event_type"],
                severity=scenario["severity"],
                message=scenario["message"],
                source_event_id=source_event_id,
                occurred_at=occurred_at,
                event_data={
                    "synthetic": True,
                    "target_host": asset.hostname,
                    "target_ip": asset.ip_address
                }
            )
            events.append(event)
        
        result = telemetry_service.create_batch(db, events_in=events)
        logger.info(f"Synthetic generation complete: {result.accepted} accepted, {result.rejected} rejected.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_synthetic_telemetry()
