import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AnimalCreate(BaseModel):
    breed: str
    sex: str
    birth_date: date
    external_tag: str | None = None
    sire_id: uuid.UUID | None = None
    dam_id: uuid.UUID | None = None
    muzzle_ref: str | None = None
    us_born: bool = True
    us_raised: bool = True

    @field_validator("us_born", "us_raised")
    @classmethod
    def must_be_us(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("v1 supports US-born, US-raised animals only")
        return v


class EventCreate(BaseModel):
    event_type: str
    payload: dict = {}
    signature: str | None = None
    signer_id: str | None = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    seq: int
    event_type: str
    payload: dict
    prev_hash: str
    hash: str
    signature: str | None
    signer_id: str | None
    created_at: datetime


class AnimalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_tag: str | None
    breed: str
    sex: str
    birth_date: date
    sire_id: uuid.UUID | None
    dam_id: uuid.UUID | None
    us_born: bool
    us_raised: bool
    muzzle_ref: str | None
    created_at: datetime
    events: list[EventRead]


class VerifyResult(BaseModel):
    valid: bool
    status: str
