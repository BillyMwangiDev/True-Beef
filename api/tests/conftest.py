import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import Base, get_db
import app.models  # noqa: F401 — register tables
from app.main import app

test_engine = create_engine(settings.test_database_url, future=True)
TestSession = sessionmaker(bind=test_engine, autoflush=False, future=True)

APPEND_ONLY_SQL = """
CREATE OR REPLACE FUNCTION ledger_events_no_mutate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'ledger_events is append-only';
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS ledger_events_append_only ON ledger_events;
CREATE TRIGGER ledger_events_append_only
BEFORE UPDATE OR DELETE ON ledger_events
FOR EACH ROW EXECUTE FUNCTION ledger_events_no_mutate();
"""


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    with test_engine.begin() as conn:
        conn.execute(text(APPEND_ONLY_SQL))
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db():
    # truncate before each test for isolation (TRUNCATE is not blocked by the trigger)
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE ledger_events, animals CASCADE"))
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
