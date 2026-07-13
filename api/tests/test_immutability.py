from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError

from app import ledger


def _animal(db):
    return ledger.create_animal(db, breed="Angus", sex="M", birth_date=date(2025, 3, 1))


def test_update_on_ledger_is_blocked(db):
    animal = _animal(db)
    with pytest.raises(DatabaseError):
        db.execute(text("UPDATE ledger_events SET event_type = 'HACKED'"))
        db.commit()
    db.rollback()


def test_delete_on_ledger_is_blocked(db):
    _animal(db)
    with pytest.raises(DatabaseError):
        db.execute(text("DELETE FROM ledger_events"))
        db.commit()
    db.rollback()


def test_verify_detects_tampering(db):
    """Disable the trigger to simulate a DB-level attacker, corrupt a row,
    and confirm verify_chain catches it."""
    animal = _animal(db)
    ledger.append_event(db, animal.id, "DIET_LOGGED", {"feed": "grass"})
    assert ledger.verify_chain(db, animal.id) is True

    db.execute(text("ALTER TABLE ledger_events DISABLE TRIGGER ledger_events_append_only"))
    db.execute(
        text("UPDATE ledger_events SET payload = '{\"feed\": \"grain\"}' WHERE seq = 1")
    )
    db.execute(text("ALTER TABLE ledger_events ENABLE TRIGGER ledger_events_append_only"))
    db.commit()

    assert ledger.verify_chain(db, animal.id) is False
