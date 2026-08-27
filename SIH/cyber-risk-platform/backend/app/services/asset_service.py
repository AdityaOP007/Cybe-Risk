import uuid
from typing import Sequence, Tuple, Any
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.telemetry import TelemetryEvent
from app.schemas.asset import AssetCreate, AssetUpdate

class AssetService:
    @staticmethod
    def _check_duplicates(db: Session, organization_id: uuid.UUID, hostname: str | None, ip_address: str | None, exclude_id: uuid.UUID | None = None) -> None:
        """
        Check for obvious duplicate assets by hostname or IP address within an organization.
        """
        if not hostname and not ip_address:
            return
            
        query = select(Asset).where(
            Asset.organization_id == organization_id,
            Asset.status != "retired"  # Allow re-use of IPs/Hostnames if old asset is retired
        )
        
        if exclude_id:
            query = query.where(Asset.id != exclude_id)
            
        conditions = []
        if hostname:
            conditions.append(Asset.hostname == hostname)
        if ip_address:
            conditions.append(Asset.ip_address == ip_address)
            
        query = query.where(or_(*conditions))
        existing = db.scalars(query).first()
        
        if existing:
            if existing.hostname == hostname and hostname:
                raise HTTPException(status_code=409, detail="An active asset with this hostname already exists.")
            if existing.ip_address == ip_address and ip_address:
                raise HTTPException(status_code=409, detail="An active asset with this IP address already exists.")

    @staticmethod
    def create(db: Session, obj_in: AssetCreate) -> Asset:
        # Prevent duplicates
        AssetService._check_duplicates(db, obj_in.organization_id, obj_in.hostname, obj_in.ip_address)
        
        db_obj = Asset(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, id: uuid.UUID) -> Asset | None:
        return db.get(Asset, id)

    @staticmethod
    def get_all(
        db: Session, 
        organization_id: uuid.UUID | None = None,
        skip: int = 0, 
        limit: int = 100,
        search: str | None = None,
        asset_type: str | None = None,
        environment: str | None = None,
        status: str | None = None,
        internet_exposed: bool | None = None,
        criticality_min: int | None = None,
        criticality_max: int | None = None,
        department: str | None = None,
        owner: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[Sequence[Asset], int]:
        query = select(Asset)
        
        if organization_id:
            query = query.where(Asset.organization_id == organization_id)
        if asset_type:
            query = query.where(Asset.asset_type == asset_type)
        if environment:
            query = query.where(Asset.environment == environment)
        if status:
            query = query.where(Asset.status == status)
        if internet_exposed is not None:
            query = query.where(Asset.internet_exposed == internet_exposed)
        if criticality_min is not None:
            query = query.where(Asset.criticality >= criticality_min)
        if criticality_max is not None:
            query = query.where(Asset.criticality <= criticality_max)
        if department:
            query = query.where(Asset.department == department)
        if owner:
            query = query.where(Asset.owner == owner)
            
        if search:
            search_filter = f"%{search}%"
            query = query.where(or_(
                Asset.name.ilike(search_filter),
                Asset.hostname.ilike(search_filter),
                Asset.owner.ilike(search_filter),
                Asset.department.ilike(search_filter),
                Asset.technology.ilike(search_filter)
            ))

        # Safe sorting logic
        sort_column = getattr(Asset, sort_by, Asset.created_at)
        # Ensure only allowed columns can be sorted
        allowed_sorts = ['name', 'criticality', 'business_value', 'created_at', 'updated_at']
        if sort_by not in allowed_sorts:
            sort_column = Asset.created_at
            
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        total = db.scalar(select(func.count()).select_from(query.subquery()))
        if total is None:
            total = 0
            
        items = db.scalars(query.offset(skip).limit(limit)).all()
        return items, total

    @staticmethod
    def update(db: Session, db_obj: Asset, obj_in: AssetUpdate) -> Asset:
        # Check duplicates if hostname or ip changed
        new_hostname = obj_in.hostname if obj_in.hostname is not None else db_obj.hostname
        new_ip = obj_in.ip_address if obj_in.ip_address is not None else db_obj.ip_address
        
        # Only check if they actually provided new ones in the request that differ, 
        # or just run the check excluding current id.
        if obj_in.hostname is not None or obj_in.ip_address is not None:
            AssetService._check_duplicates(db, db_obj.organization_id, new_hostname, new_ip, exclude_id=db_obj.id)
            
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Asset) -> None:
        """Physical deletion (Use retire for logical deletion)"""
        db.delete(db_obj)
        db.commit()

    @staticmethod
    def retire(db: Session, db_obj: Asset) -> Asset:
        """Logical deletion/retirement workflow"""
        db_obj.status = "retired"
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_posture(db: Session, asset_id: uuid.UUID) -> dict[str, Any]:
        """Aggregate security posture without AI/risk calculations"""
        asset = db.get(Asset, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
            
        open_vulns = db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.asset_id == asset_id, Vulnerability.status == "open")
        ) or 0
        
        critical_vulns = db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.asset_id == asset_id, Vulnerability.status == "open", Vulnerability.severity == "critical")
        ) or 0
        
        # Telemetry in the last 30 days
        telemetry_events = db.scalar(
            select(func.count())
            .select_from(TelemetryEvent)
            .where(TelemetryEvent.asset_id == asset_id)
        ) or 0
        
        return {
            "asset_id": asset.id,
            "asset_name": asset.name,
            "criticality": asset.criticality,
            "internet_exposed": asset.internet_exposed,
            "open_vulnerabilities": open_vulns,
            "critical_vulnerabilities": critical_vulns,
            "recent_telemetry_events": telemetry_events
        }

    @staticmethod
    def get_vulnerabilities(db: Session, asset_id: uuid.UUID, skip: int = 0, limit: int = 100, severity: str | None = None, status: str | None = None) -> Sequence[Vulnerability]:
        query = select(Vulnerability).where(Vulnerability.asset_id == asset_id)
        if severity:
            query = query.where(Vulnerability.severity == severity)
        if status:
            query = query.where(Vulnerability.status == status)
        return db.scalars(query.order_by(desc(Vulnerability.created_at)).offset(skip).limit(limit)).all()

    @staticmethod
    def get_telemetry(db: Session, asset_id: uuid.UUID, skip: int = 0, limit: int = 100, severity: str | None = None, event_type: str | None = None) -> Sequence[TelemetryEvent]:
        query = select(TelemetryEvent).where(TelemetryEvent.asset_id == asset_id)
        if severity:
            query = query.where(TelemetryEvent.severity == severity)
        if event_type:
            query = query.where(TelemetryEvent.event_type == event_type)
        return db.scalars(query.order_by(desc(TelemetryEvent.occurred_at)).offset(skip).limit(limit)).all()

asset_service = AssetService()
