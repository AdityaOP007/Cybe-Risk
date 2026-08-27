import uuid
from typing import Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from sqlalchemy.exc import IntegrityError
from collections import defaultdict

from app.models.telemetry import TelemetryEvent
from app.models.organization import Organization
from app.models.asset import Asset
from app.schemas.telemetry import TelemetryEventCreate, TelemetryBatchResult, TelemetryStats
from app.data_ingestion.normalizers.generic import GenericNormalizer

class TelemetryService:
    def __init__(self):
        self.normalizer = GenericNormalizer()

    def _validate_relations(self, db: Session, organization_id: uuid.UUID, asset_id: uuid.UUID | None = None) -> None:
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")
            
        if asset_id:
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            if asset.organization_id != organization_id:
                raise ValueError(f"Asset {asset_id} does not belong to organization {organization_id}")

    def create(self, db: Session, *, obj_in: TelemetryEventCreate) -> TelemetryEvent:
        self._validate_relations(db, obj_in.organization_id, obj_in.asset_id)
        
        normalized = self.normalizer.normalize(obj_in.model_dump())
        
        db_obj = TelemetryEvent(
            organization_id=normalized.organization_id,
            asset_id=normalized.asset_id,
            source=normalized.source,
            event_type=normalized.event_type,
            severity=normalized.severity,
            message=normalized.message,
            source_event_id=normalized.source_event_id,
            occurred_at=normalized.occurred_at,
            event_data=normalized.event_data
        )
        
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            if "ix_telemetry_dedup" in str(e):
                raise ValueError("Duplicate telemetry event detected")
            raise

    def create_batch(self, db: Session, *, events_in: list[TelemetryEventCreate]) -> TelemetryBatchResult:
        accepted = 0
        rejected = 0
        errors = []
        
        # Cache validations within the batch
        valid_orgs = set()
        valid_assets = {} # asset_id -> org_id
        
        for idx, event_in in enumerate(events_in):
            try:
                # Validation caching
                if event_in.organization_id not in valid_orgs:
                    org = db.query(Organization).filter(Organization.id == event_in.organization_id).first()
                    if not org:
                        raise ValueError(f"Organization {event_in.organization_id} not found")
                    valid_orgs.add(event_in.organization_id)
                
                if event_in.asset_id and event_in.asset_id not in valid_assets:
                    asset = db.query(Asset).filter(Asset.id == event_in.asset_id).first()
                    if not asset:
                        raise ValueError(f"Asset {event_in.asset_id} not found")
                    if asset.organization_id != event_in.organization_id:
                        raise ValueError(f"Asset {event_in.asset_id} does not belong to organization {event_in.organization_id}")
                    valid_assets[event_in.asset_id] = asset.organization_id
                elif event_in.asset_id and valid_assets[event_in.asset_id] != event_in.organization_id:
                    raise ValueError(f"Asset {event_in.asset_id} does not belong to organization {event_in.organization_id}")

                normalized = self.normalizer.normalize(event_in.model_dump())
                
                db_obj = TelemetryEvent(
                    organization_id=normalized.organization_id,
                    asset_id=normalized.asset_id,
                    source=normalized.source,
                    event_type=normalized.event_type,
                    severity=normalized.severity,
                    message=normalized.message,
                    source_event_id=normalized.source_event_id,
                    occurred_at=normalized.occurred_at,
                    event_data=normalized.event_data
                )
                
                # We have to commit individually or handle flush errors to avoid failing the whole batch
                # PostgreSQL SAVEPOINT could be used, but committing individually for now for simplicity and error isolation
                db.add(db_obj)
                db.commit()
                accepted += 1
                
            except IntegrityError as e:
                db.rollback()
                rejected += 1
                if "ix_telemetry_dedup" in str(e):
                    errors.append({"index": idx, "error": "Duplicate telemetry event detected"})
                else:
                    errors.append({"index": idx, "error": "Database integrity error"})
            except Exception as e:
                db.rollback()
                rejected += 1
                errors.append({"index": idx, "error": str(e)})

        return TelemetryBatchResult(
            total=len(events_in),
            accepted=accepted,
            rejected=rejected,
            errors=errors
        )

    def get(self, db: Session, id: uuid.UUID) -> TelemetryEvent | None:
        return db.query(TelemetryEvent).filter(TelemetryEvent.id == id).first()

    def get_all(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        organization_id: uuid.UUID | None = None,
        asset_id: uuid.UUID | None = None,
        source: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        search: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        sort_by: str = "occurred_at",
        sort_order: str = "desc"
    ) -> tuple[list[TelemetryEvent], int]:
        
        query = db.query(TelemetryEvent)

        if organization_id:
            query = query.filter(TelemetryEvent.organization_id == organization_id)
        if asset_id:
            query = query.filter(TelemetryEvent.asset_id == asset_id)
        if source:
            query = query.filter(TelemetryEvent.source == source)
        if event_type:
            query = query.filter(TelemetryEvent.event_type == event_type)
        if severity:
            query = query.filter(TelemetryEvent.severity == severity)
            
        if from_time:
            query = query.filter(TelemetryEvent.occurred_at >= from_time)
        if to_time:
            query = query.filter(TelemetryEvent.occurred_at <= to_time)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    TelemetryEvent.message.ilike(search_term),
                    TelemetryEvent.source_event_id.ilike(search_term)
                )
            )

        total = query.count()

        sort_col = getattr(TelemetryEvent, sort_by, TelemetryEvent.occurred_at)
        if sort_order == "desc":
            sort_col = sort_col.desc()
            
        query = query.order_by(sort_col)
        items = query.offset(skip).limit(limit).all()

        return items, total

    def get_stats(self, db: Session, organization_id: uuid.UUID | None = None) -> TelemetryStats:
        from sqlalchemy import Integer
        query = db.query(
            func.count(TelemetryEvent.id).label('total'),
            func.sum(func.cast(TelemetryEvent.severity == 'critical', Integer)).label('critical'),
            func.sum(func.cast(TelemetryEvent.severity == 'high', Integer)).label('high'),
            func.sum(func.cast(TelemetryEvent.severity == 'medium', Integer)).label('medium'),
            func.sum(func.cast(TelemetryEvent.severity == 'low', Integer)).label('low'),
            func.sum(func.cast(TelemetryEvent.severity == 'informational', Integer)).label('informational')
        )
        
        if organization_id:
            query = query.filter(TelemetryEvent.organization_id == organization_id)
            
        result = query.first()
        
        # Source aggregation
        source_query = db.query(TelemetryEvent.source, func.count(TelemetryEvent.id))
        if organization_id:
            source_query = source_query.filter(TelemetryEvent.organization_id == organization_id)
        source_counts = {r[0]: r[1] for r in source_query.group_by(TelemetryEvent.source).all()}
        
        # Event type aggregation
        event_query = db.query(TelemetryEvent.event_type, func.count(TelemetryEvent.id))
        if organization_id:
            event_query = event_query.filter(TelemetryEvent.organization_id == organization_id)
        event_counts = {r[0]: r[1] for r in event_query.group_by(TelemetryEvent.event_type).all()}

        return TelemetryStats(
            total_events=result.total or 0,
            critical_events=result.critical or 0,
            high_events=result.high or 0,
            medium_events=result.medium or 0,
            low_events=result.low or 0,
            informational_events=result.informational or 0,
            by_source=source_counts,
            by_event_type=event_counts
        )

telemetry_service = TelemetryService()
