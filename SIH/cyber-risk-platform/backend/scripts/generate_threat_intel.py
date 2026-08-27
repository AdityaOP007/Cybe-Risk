import json
import logging
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.schemas.threat_intel import ThreatIntelligenceRecordCreate, ThreatIndicatorCreate
from app.services.threat_intel_service import ThreatIntelligenceService
from app.services.correlation_engine import CorrelationEngine
from app.models.vulnerability import Vulnerability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_threat_intel():
    db = SessionLocal()
    try:
        service = ThreatIntelligenceService(db)
        
        # We need to find some existing vulnerabilities to make correlation interesting
        vulns = db.query(Vulnerability).limit(10).all()
        cves_to_ingest = ["CVE-2024-38063", "CVE-2024-38077"] # Hardcoded interesting ones
        
        for v in vulns:
            if v.cve_id:
                cves_to_ingest.append(v.cve_id)
                
        logger.info(f"Generating threat intel for {len(set(cves_to_ingest))} CVEs...")
        
        # Generate Vulnerability Intelligence
        for cve in set(cves_to_ingest):
            if not cve: continue
            record = ThreatIntelligenceRecordCreate(
                source="nvd",
                source_record_id=cve.lower(),
                intelligence_type="vulnerability",
                title=cve.upper(),
                description=f"Synthetic threat intelligence for {cve}",
                severity="critical",
                known_exploited=True,
                published_at=datetime.now(timezone.utc)
            )
            service.ingest_record(record)
            
        # Generate Threat Actors
        actor = ThreatIntelligenceRecordCreate(
            source="mandiant",
            source_record_id="apt-29",
            intelligence_type="actor",
            title="APT29",
            description="Russian state-sponsored cyber espionage group.",
            severity="critical",
            indicators=[
                ThreatIndicatorCreate(indicator_type="domain", value="malicious-login.com")
            ]
        )
        service.ingest_record(actor)
        
        # Generate Campaign
        campaign = ThreatIntelligenceRecordCreate(
            source="internal",
            source_record_id="camp-2026-08",
            intelligence_type="campaign",
            title="Q3 Credential Harvesting",
            description="Active campaign targeting financial sector.",
            severity="high",
            indicators=[
                ThreatIndicatorCreate(indicator_type="ipv4", value="103.111.22.33")
            ]
        )
        service.ingest_record(campaign)
        
        # Run correlation engine
        logger.info("Running correlation engine...")
        engine = CorrelationEngine(db)
        engine.run_full_correlation()
        
        logger.info("Synthetic threat intelligence generation complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_threat_intel()
