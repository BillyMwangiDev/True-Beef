import uuid
from datetime import date

from app import ledger
from app.hashchain import GENESIS_HASH


def _new_animal(db):
    return ledger.create_animal(
        db, breed="Angus", sex="M", birth_date=date(2025, 3, 1), external_tag="A-100"
    )


def test_create_animal_appends_genesis_event(db):
    animal = _new_animal(db)
    chain = ledger.get_chain(db, animal.id)
    assert len(chain) == 1
    assert chain[0].seq == 0
    assert chain[0].event_type == "ANIMAL_REGISTERED"
    assert chain[0].prev_hash == GENESIS_HASH


def test_append_event_links_to_previous(db):
    animal = _new_animal(db)
    ledger.append_event(db, animal.id, "DIET_LOGGED", {"feed": "grass"})
    chain = ledger.get_chain(db, animal.id)
    assert len(chain) == 2
    assert chain[1].seq == 1
    assert chain[1].prev_hash == chain[0].hash


def test_verify_chain_valid(db):
    animal = _new_animal(db)
    ledger.append_event(db, animal.id, "DIET_LOGGED", {"feed": "grass"})
    ledger.append_event(db, animal.id, "WEIGHT_RECORDED", {"kg": 320})
    assert ledger.verify_chain(db, animal.id) is True


def test_verify_chain_empty_is_false(db):
    # an animal id with no ledger events (e.g. fully truncated) must not verify as valid
    assert ledger.verify_chain(db, uuid.uuid4()) is False
