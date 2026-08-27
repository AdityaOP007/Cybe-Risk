from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.dashboard import DashboardAlert
from app.schemas.dashboard import ExecutiveDashboardData
from app.services.dashboard.aggregator import DashboardAggregatorService

router = APIRouter()

@router.get("/executive", response_model=ExecutiveDashboardData)
def get_executive_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the massive, unified payload for the Executive Decision Dashboard.
    Aggregates read-only data from Modules 6-11.
    """
    aggregator = DashboardAggregatorService(db, current_user.organization_id)
    return aggregator.get_dashboard()


@router.post("/alerts/{alert_id}/acknowledge", response_model=dict)
def acknowledge_alert(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Acknowledge an executive alert, hiding it from the active queue.
    """
    alert = db.scalars(
        select(DashboardAlert).where(
            DashboardAlert.id == alert_id,
            DashboardAlert.organization_id == current_user.organization_id
        )
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = "acknowledged"
    db.commit()
    
    return {"status": "success", "alert_id": alert_id, "new_status": "acknowledged"}

@router.post("/alerts/{alert_id}/resolve", response_model=dict)
def resolve_alert(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark an executive alert as resolved.
    """
    alert = db.scalars(
        select(DashboardAlert).where(
            DashboardAlert.id == alert_id,
            DashboardAlert.organization_id == current_user.organization_id
        )
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    from app.models.mixins import get_utc_now
    
    alert.status = "resolved"
    alert.resolved_at = get_utc_now()
    db.commit()
    
    return {"status": "success", "alert_id": alert_id, "new_status": "resolved"}
