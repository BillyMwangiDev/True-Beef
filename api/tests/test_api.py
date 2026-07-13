def _animal_payload():
    return {
        "breed": "Angus",
        "sex": "M",
        "birth_date": "2025-03-01",
        "external_tag": "A-100",
        "us_born": True,
        "us_raised": True,
    }


def test_create_animal_then_read_chain(client):
    resp = client.post("/animals", json=_animal_payload())
    assert resp.status_code == 201
    animal = resp.json()
    assert animal["breed"] == "Angus"
    assert len(animal["events"]) == 1
    assert animal["events"][0]["event_type"] == "ANIMAL_REGISTERED"

    read = client.get(f"/animals/{animal['id']}")
    assert read.status_code == 200
    assert read.json()["id"] == animal["id"]


def test_append_event_and_verify_valid(client):
    animal = client.post("/animals", json=_animal_payload()).json()
    ev = client.post(
        f"/animals/{animal['id']}/events",
        json={"event_type": "DIET_LOGGED", "payload": {"feed": "grass"}},
    )
    assert ev.status_code == 201
    assert ev.json()["seq"] == 1

    verify = client.get(f"/animals/{animal['id']}/verify")
    assert verify.status_code == 200
    assert verify.json() == {"valid": True, "status": "valid"}


def test_create_animal_rejects_non_us(client):
    payload = _animal_payload()
    payload["us_born"] = False
    resp = client.post("/animals", json=payload)
    assert resp.status_code == 422


def test_get_unknown_animal_404(client):
    resp = client.get("/animals/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
