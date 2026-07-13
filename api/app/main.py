import uuid

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import ledger
from app.db import get_db
from app.models import Animal
from app.schemas import AnimalCreate, AnimalRead, EventCreate, EventRead, VerifyResult

app = FastAPI(title="True Beef API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _get_animal_or_404(db: Session, animal_id: uuid.UUID) -> Animal:
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise HTTPException(status_code=404, detail="animal not found")
    return animal


@app.post("/animals", response_model=AnimalRead, status_code=201)
def create_animal(body: AnimalCreate, db: Session = Depends(get_db)) -> Animal:
    animal = ledger.create_animal(
        db,
        breed=body.breed,
        sex=body.sex,
        birth_date=body.birth_date,
        external_tag=body.external_tag,
        sire_id=body.sire_id,
        dam_id=body.dam_id,
        muzzle_ref=body.muzzle_ref,
        us_born=body.us_born,
        us_raised=body.us_raised,
    )
    db.refresh(animal)
    return animal


@app.get("/animals/{animal_id}", response_model=AnimalRead)
def get_animal(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> Animal:
    return _get_animal_or_404(db, animal_id)


@app.post("/animals/{animal_id}/events", response_model=EventRead, status_code=201)
def add_event(
    animal_id: uuid.UUID, body: EventCreate, db: Session = Depends(get_db)
) -> EventRead:
    _get_animal_or_404(db, animal_id)
    return ledger.append_event(
        db, animal_id, body.event_type, body.payload, body.signature, body.signer_id
    )


@app.get("/animals/{animal_id}/verify", response_model=VerifyResult)
def verify_animal(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> VerifyResult:
    _get_animal_or_404(db, animal_id)
    valid = ledger.verify_chain(db, animal_id)
    return VerifyResult(valid=valid, status="valid" if valid else "tampered")
