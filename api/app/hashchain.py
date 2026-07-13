import hashlib
import json

GENESIS_HASH = "0" * 64


def canonical_json(payload: dict) -> str:
    """Stable, key-order-independent JSON so hashes are reproducible."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(
    animal_id: str, seq: int, event_type: str, payload: dict, prev_hash: str
) -> str:
    material = f"{animal_id}|{seq}|{event_type}|{canonical_json(payload)}|{prev_hash}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
