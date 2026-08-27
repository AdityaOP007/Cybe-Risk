from sqlalchemy.orm import Session
from uuid import UUID
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.schemas.threat_intel import ThreatIntelligenceRecordCreate
from app.data_ingestion.threat_intel.normalizers import normalize_cve_id, normalize_severity, normalize_source
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class ThreatIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_record(self, data: ThreatIntelligenceRecordCreate) -> ThreatIntelligenceRecord:
        """
        Ingests a single threat intelligence record, handling normalization and deduplication.
        """
        # 1. Normalize Core Fields
        normalized_source = normalize_source(data.source)
        normalized_severity = normalize_severity(data.severity)
        
        # If it's a CVE, normalize the title/ID if it matches
        normalized_title = data.title
        if data.intelligence_type == 'vulnerability' and 'cve' in data.title.lower():
            normalized_title = normalize_cve_id(data.title)

        # 2. Check for existing record to handle deduplication gracefully
        existing = self.db.query(ThreatIntelligenceRecord).filter(
            ThreatIntelligenceRecord.source == normalized_source,
            ThreatIntelligenceRecord.source_record_id == data.source_record_id
        ).first()

        if existing:
            # We could update here, but for now we'll just return the existing to be idempotent
            return existing

        # 3. Create the parent record
        db_record = ThreatIntelligenceRecord(
            source=normalized_source,
            source_record_id=data.source_record_id,
            intelligence_type=data.intelligence_type,
            title=normalized_title,
            description=data.description,
            severity=normalized_severity,
            confidence=data.confidence,
            external_reference=data.external_reference,
            published_at=data.published_at,
            first_seen_at=data.first_seen_at,
            last_seen_at=data.last_seen_at,
            known_exploited=data.known_exploited,
            raw_data=data.raw_data,
            normalized_data=data.normalized_data
        )

        self.db.add(db_record)
        
        # 4. Create Indicators
        for ind in data.indicators:
            db_ind = ThreatIndicator(
                threat_record=db_record,
                indicator_type=ind.indicator_type,
                value=ind.value,
                confidence=ind.confidence,
                source=ind.source or normalized_source,
                active=ind.active,
                first_seen_at=ind.first_seen_at,
                last_seen_at=ind.last_seen_at,
                metadata_data=ind.metadata_data
            )
            self.db.add(db_ind)

        try:
            self.db.commit()
            self.db.refresh(db_record)
            return db_record
        except IntegrityError:
            self.db.rollback()
            # Concurrency fallback
            return self.db.query(ThreatIntelligenceRecord).filter(
                ThreatIntelligenceRecord.source == normalized_source,
                ThreatIntelligenceRecord.source_record_id == data.source_record_id
            ).first()

    def get_records(self, search: str = None, page: int = 1, page_size: int = 50):
        query = self.db.query(ThreatIntelligenceRecord)
        
        if search:
            query = query.filter(ThreatIntelligenceRecord.title.ilike(f"%{search}%"))
            
        total = query.count()
        items = query.order_by(ThreatIntelligenceRecord.last_seen_at.desc().nulls_last()).offset((page - 1) * page_size).limit(page_size).all()
        
        return items, total
