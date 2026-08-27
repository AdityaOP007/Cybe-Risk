import re
from typing import Any

def normalize_cve_id(raw_cve: str) -> str:
    """
    Normalizes a CVE ID to standard uppercase format.
    Example: 'cve-2026-12345' -> 'CVE-2026-12345'
    """
    if not raw_cve:
        return ""
        
    cleaned = raw_cve.strip().upper()
    
    # Ensure it follows CVE format CVE-YYYY-NNNNN
    if re.match(r'^CVE-\d{4}-\d{4,}$', cleaned):
        return cleaned
        
    return cleaned

def normalize_severity(raw_severity: str) -> str:
    """
    Normalizes varied severity strings into our canonical 5 levels:
    critical, high, medium, low, informational
    """
    if not raw_severity:
        return "informational"
        
    sev = str(raw_severity).strip().lower()
    
    critical_matches = ["critical", "crit", "sev-1", "sev1", "priority_1"]
    high_matches = ["high", "sev-2", "sev2", "priority_2"]
    medium_matches = ["medium", "med", "sev-3", "sev3", "priority_3"]
    low_matches = ["low", "sev-4", "sev4", "priority_4"]
    
    if any(m in sev for m in critical_matches):
        return "critical"
    if any(m in sev for m in high_matches):
        return "high"
    if any(m in sev for m in medium_matches):
        return "medium"
    if any(m in sev for m in low_matches):
        return "low"
        
    return "informational"

def normalize_source(raw_source: str) -> str:
    """
    Normalizes source names for deduplication.
    """
    if not raw_source:
        return "unknown"
    return str(raw_source).strip().lower()
