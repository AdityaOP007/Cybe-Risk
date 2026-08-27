"""
API Dependencies: provides common FastAPI dependencies for injection.
"""
import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization

def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Returns a mock user for the SIH demo.
    Fetches the first organization dynamically to survive db resets.
    """
    org = db.query(Organization).first()
    org_id = org.id if org else uuid.uuid4()
    
    return User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        organization_id=org_id,
    )
