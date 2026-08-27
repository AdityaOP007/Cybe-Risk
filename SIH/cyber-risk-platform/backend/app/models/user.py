import uuid
from dataclasses import dataclass

@dataclass
class User:
    """Minimal user stub for demo purposes."""
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str = "admin@demo.bank"
    role: str = "ciso"
