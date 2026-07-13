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

## Known limitations & fast-follows
This is a scaffold. Deferred, deliberately:
- **Trailing-truncation detection.** `verify_chain` catches tampered rows and empty chains, but a
  chain with its *last* events deleted (after bypassing the append-only trigger) can't be detected
  without an external anchor. Add a periodic external anchor (e.g. publish the head hash) — see the
  spec's "can add a public anchor later" note.
- **Real offline sync.** `mobile/lib/sync.ts` is a stub; bidirectional sync is Phase-1 farm-app work.
- **CI client-drift check.** CI doesn't yet run `make gen-client` and diff the result against the
  committed `mobile/lib/generated/api-types.ts`; today the one-way contract is kept in sync by hand.
- **CI lint.** The API CI job runs pytest only; no ruff/black step yet.
- **Test schema vs. migration.** Tests build the schema via `Base.metadata.create_all` + a duplicated
  trigger, not the Alembic migration; ORM/migration parity is currently kept in sync manually.
- **Auth, muzzle-print CV, processor QR, consumer scan** — all out of scope for the farm-layer scaffold.
