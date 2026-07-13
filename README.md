# True Beef — Farm Layer (Scaffold)

Walking-skeleton scaffold: Expo/React Native app + FastAPI/Postgres backend with a
certification-agnostic, append-only, hash-chained animal ledger.

## Prerequisites
- Docker, Python 3.11+, Node 20+

## API — first run
```bash
cp .env.example .env
make up                       # start Postgres
cd api && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
docker compose exec db psql -U truebeef -d truebeef -c "CREATE DATABASE truebeef_test;"
alembic upgrade head
cd .. && make api             # http://localhost:8000/docs
```

## Tests
```bash
make test
```

## Mobile
```bash
make gen-client               # regenerate TS types from the API's OpenAPI
cd mobile && npm install && npx expo start
```

## Ledger model
- `ledger_events` is append-only (Postgres trigger blocks UPDATE/DELETE); each row
  hash-chains to the previous event for its animal.
- Certifier attestations are ledger events of type `ATTESTATION_ADDED` carrying a signature —
  no separate table.
- `event_type` is a free string, not a DB enum, so new certification standards need no migration.
