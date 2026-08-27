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
