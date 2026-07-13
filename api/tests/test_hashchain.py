from app.hashchain import GENESIS_HASH, canonical_json, compute_hash


def test_genesis_hash_is_64_zeros():
    assert GENESIS_HASH == "0" * 64


def test_canonical_json_is_key_order_independent():
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_compute_hash_is_deterministic():
    h1 = compute_hash("animal-1", 0, "ANIMAL_REGISTERED", {"breed": "Angus"}, GENESIS_HASH)
    h2 = compute_hash("animal-1", 0, "ANIMAL_REGISTERED", {"breed": "Angus"}, GENESIS_HASH)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_hash_changes_when_payload_changes():
    base = compute_hash("animal-1", 0, "DIET_LOGGED", {"feed": "grass"}, GENESIS_HASH)
    changed = compute_hash("animal-1", 0, "DIET_LOGGED", {"feed": "grain"}, GENESIS_HASH)
    assert base != changed
