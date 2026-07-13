import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.hashchain import GENESIS_HASH, compute_hash
from app.models import Animal, LedgerEvent


def get_chain(db: Session, animal_id: uuid.UUID) -> list[LedgerEvent]:
    stmt = (
        select(LedgerEvent)
        .where(LedgerEvent.animal_id == animal_id)
        .order_by(LedgerEvent.seq)
    )
    return list(db.execute(stmt).scalars().all())


def append_event(
    db: Session,
    animal_id: uuid.UUID,
    event_type: str,
    payload: dict,
    signature: str | None = None,
    signer_id: str | None = None,
) -> LedgerEvent:
    chain = get_chain(db, animal_id)
    if chain:
        seq = chain[-1].seq + 1
        prev_hash = chain[-1].hash
    else:
        seq = 0
        prev_hash = GENESIS_HASH
    event = LedgerEvent(
        animal_id=animal_id,
        seq=seq,
        event_type=event_type,
        payload=payload,
        prev_hash=prev_hash,
        hash=compute_hash(str(animal_id), seq, event_type, payload, prev_hash),
        signature=signature,
        signer_id=signer_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def create_animal(
    db: Session,
    *,
    breed: str,
    sex: str,
    birth_date: date,
    external_tag: str | None = None,
    sire_id: uuid.UUID | None = None,
    dam_id: uuid.UUID | None = None,
    muzzle_ref: str | None = None,
    us_born: bool = True,
    us_raised: bool = True,
) -> Animal:
    animal = Animal(
        breed=breed,
        sex=sex,
        birth_date=birth_date,
        external_tag=external_tag,
        sire_id=sire_id,
        dam_id=dam_id,
        muzzle_ref=muzzle_ref,
        us_born=us_born,
        us_raised=us_raised,
    )
    db.add(animal)
    db.flush()
    db.refresh(animal)
    append_event(
        db,
        animal.id,
        "ANIMAL_REGISTERED",
        {
            "breed": breed,
            "sex": sex,
            "birth_date": birth_date.isoformat(),
            "external_tag": external_tag,
        },
    )
    return animal


def verify_chain(db: Session, animal_id: uuid.UUID) -> bool:
    chain = get_chain(db, animal_id)
    if not chain:
        return False  # no events => no valid provenance (covers a fully-truncated/empty chain)
    expected_prev = GENESIS_HASH
    for event in chain:
        if event.prev_hash != expected_prev:
            return False
        recomputed = compute_hash(
            str(event.animal_id), event.seq, event.event_type, event.payload, event.prev_hash
        )
        if recomputed != event.hash:
            return False
        expected_prev = event.hash
    return True
