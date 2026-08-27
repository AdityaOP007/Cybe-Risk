from sqlalchemy.orm import Session
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.models.vulnerability import Vulnerability
from app.models.asset import Asset
from app.models.telemetry import TelemetryEvent
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """
    Engine to correlate global threat intelligence with tenant-specific infrastructure.
    """
    def __init__(self, db: Session):
        self.db = db

    def run_full_correlation(self):
        """
        Runs correlation rules across all active threats.
        In a production system, this would be an async job.
        """
        threats = self.db.query(ThreatIntelligenceRecord).all()
        for threat in threats:
            self.correlate_cve_to_vulnerabilities(threat)
            self.correlate_indicators_to_telemetry(threat)

    def correlate_cve_to_vulnerabilities(self, threat: ThreatIntelligenceRecord):
        """
        Matches CVE threats to actual organization Vulnerabilities.
        If a match is found, correlates the Threat to the Vulnerability and the underlying Asset.
        """
        if threat.intelligence_type != "vulnerability":
            return
            
        cve_id = threat.title # Assuming we normalized this to CVE-YYYY-NNNNN
        if not cve_id.startswith("CVE-"):
            return
            
        # Find all vulnerabilities across all organizations matching this CVE
        vulns = self.db.query(Vulnerability).filter(Vulnerability.cve_id == cve_id).all()
        
        for vuln in vulns:
            # Create a correlation for the vulnerability
            self._create_correlation(
                organization_id=vuln.asset.organization_id,
                threat_id=threat.id,
                correlation_type="vulnerability_match",
                confidence=100,
                reason=f"Exact CVE match: {cve_id}",
                vulnerability_id=vuln.id,
                asset_id=vuln.asset_id
            )

    def correlate_indicators_to_telemetry(self, threat: ThreatIntelligenceRecord):
        """
        Matches IOCs (IPs, domains) to Telemetry Events.
        """
        for ind in threat.indicators:
            if ind.indicator_type in ["ipv4", "ipv6", "domain"]:
                # Very simple match: check if the indicator value is exactly in the telemetry event_data target_host or source_ip
                # This requires querying JSONB which can be slow, but works for the prototype
                # We'll just do a basic text search in the telemetry message/event_data for the prototype
                events = self.db.query(TelemetryEvent).filter(
                    TelemetryEvent.message.ilike(f"%{ind.value}%")
                ).all()
                
                for event in events:
                    if event.asset_id:
                        self._create_correlation(
                            organization_id=event.organization_id,
                            threat_id=threat.id,
                            correlation_type="indicator_match",
                            confidence=80,
                            reason=f"Telemetry matched indicator: {ind.value}",
                            asset_id=event.asset_id
                        )


    def _create_correlation(self, organization_id, threat_id, correlation_type, confidence, reason, vulnerability_id=None, asset_id=None):
        try:
            corr = ThreatCorrelation(
                organization_id=organization_id,
                threat_record_id=threat_id,
                asset_id=asset_id,
                vulnerability_id=vulnerability_id,
                correlation_type=correlation_type,
                confidence=confidence,
                reason=reason
            )
            self.db.add(corr)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            # Correlation already exists, this is fine
            pass
