from typing import Any
from datetime import datetime, timezone
import uuid
from app.data_ingestion.normalizers.base import BaseNormalizer
from app.data_ingestion.schemas.normalized_event import NormalizedTelemetryEvent

class GenericNormalizer(BaseNormalizer):
    """
    A generic normalizer that attempts to parse standard REST or JSON inputs,
    mapping known severity and event_type variations to our internal taxonomy.
    """
    
    SEVERITY_MAP = {
        "critical": "critical",
        "sev1": "critical",
        "priority_1": "critical",
        "fatal": "critical",
        
        "high": "high",
        "sev2": "high",
        "priority_2": "high",
        "error": "high",
        
        "medium": "medium",
        "sev3": "medium",
        "priority_3": "medium",
        "warning": "medium",
        
        "low": "low",
        "sev4": "low",
        "priority_4": "low",
        
        "informational": "informational",
        "info": "informational",
        "sev5": "informational",
        "priority_5": "informational",
        "debug": "informational"
    }

    EVENT_TYPE_MAP = {
        "authentication_failure": "failed_login",
        "login_failed": "failed_login",
        "failed_login": "failed_login",
        
        "authentication_success": "successful_login",
        "login_success": "successful_login",
        "successful_login": "successful_login",
        
        "malware": "malware_detected",
        "ransomware_detected": "malware_detected",
        "virus_found": "malware_detected",
        "malware_detected": "malware_detected",
        
        "port_scan_detected": "port_scan",
        "port_scan": "port_scan",
        
        "suspicious_connection": "suspicious_connection",
        "blocked_connection": "blocked_connection",
        "vulnerability_detected": "vulnerability_detected",
        "data_exfiltration": "data_exfiltration",
        "privilege_escalation": "privilege_escalation",
        "unauthorized_access": "unauthorized_access"
    }

    def _normalize_severity(self, raw_severity: str) -> str:
        if not raw_severity:
            return "informational"
        normalized = str(raw_severity).lower().strip()
        return self.SEVERITY_MAP.get(normalized, "informational")
        
    def _normalize_event_type(self, raw_type: str) -> str:
        if not raw_type:
            return "other"
        normalized = str(raw_type).lower().strip()
        return self.EVENT_TYPE_MAP.get(normalized, "other")

    def normalize(self, raw_event: dict[str, Any], **kwargs) -> NormalizedTelemetryEvent:
        """
        Normalizes a generic telemetry event.
        Expects organization_id, source, occurred_at to be present or passed via kwargs.
        """
        # Merge kwargs with raw_event for processing, kwargs take precedence for routing context
        context = {**raw_event, **kwargs}
        
        org_id_str = context.get("organization_id")
        if not org_id_str:
            raise ValueError("organization_id is required")
            
        try:
            organization_id = uuid.UUID(str(org_id_str))
        except ValueError:
            raise ValueError("Invalid organization_id UUID")

        asset_id_str = context.get("asset_id")
        asset_id = None
        if asset_id_str:
            try:
                asset_id = uuid.UUID(str(asset_id_str))
            except ValueError:
                pass # Or raise depending on strictness

        source = context.get("source", "unknown").lower()
        event_type = self._normalize_event_type(context.get("event_type", "other"))
        severity = self._normalize_severity(context.get("severity", "info"))
        
        message = context.get("message")
        source_event_id = context.get("source_event_id")
        
        occurred_at_val = context.get("occurred_at")
        if isinstance(occurred_at_val, datetime):
            occurred_at = occurred_at_val
        elif isinstance(occurred_at_val, str):
            try:
                occurred_at = datetime.fromisoformat(occurred_at_val.replace('Z', '+00:00'))
            except ValueError:
                occurred_at = datetime.now(timezone.utc) # Fallback
        else:
            occurred_at = datetime.now(timezone.utc)
            
        event_data = context.get("event_data", {})
        if not isinstance(event_data, dict):
            event_data = {"raw": event_data}

        # Stash original values in event_data if we normalized them
        if "severity" in raw_event and raw_event["severity"] != severity:
            event_data["original_severity"] = raw_event["severity"]
        if "event_type" in raw_event and raw_event["event_type"] != event_type:
            event_data["original_event_type"] = raw_event["event_type"]

        return NormalizedTelemetryEvent(
            organization_id=organization_id,
            asset_id=asset_id,
            source=source,
            event_type=event_type,
            severity=severity,
            message=message,
            source_event_id=source_event_id,
            occurred_at=occurred_at,
            event_data=event_data
        )
