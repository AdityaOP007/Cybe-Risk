import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import Base

@pytest.fixture(scope="session")
def engine():
    return create_engine(str(settings.DATABASE_URL))

@pytest.fixture(scope="function", autouse=True)
def clean_db(engine):
    # This will clear tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    with Session(engine) as session:
        yield session

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
