# True Beef — Farm-Layer Scaffold (Design Spec)

**Date:** 2026-07-11
**Status:** Approved for planning
**Scope:** The first sub-project of the True Beef platform — a scaffold (walking skeleton)
for the **farm layer**, the foundation and highest adoption risk per the PRD roadmap
(Phase 1, months 1–4).

## Context & why this first

The PRD describes a five-phase platform (farm capture → immutable ledger → certifier
attestations → processor QR → consumer scan → data SaaS). It is far too large for one
spec. The PRD already fixes the build order: **the farm layer is built first** because it
is both the foundation and the single biggest adoption risk — the exact failure mode that
stalled IBM Food Trust in the US (farmers asked to do extra data entry for a benefit that
accrued to retailers). Nothing downstream has value until real animals are on the ledger.

This spec covers **only the scaffold** for that layer: the chosen stack, the
certification-agnostic ledger schema, project structure, and one thin end-to-end path that
proves the ledger pattern is correct. It is deliberately not a finished farm app.

## Decisions locked during brainstorming

1. **Build goal:** Repo + architecture scaffold (not a runnable feature-complete app, not a
   CV spike, not a clickable prototype).
2. **Ledger implementation:** Append-only Postgres event table with a **hash-chain**
   (each record carries a hash of the prior record) and per-record signatures for
   attestations. Not a distributed ledger — the PRD's central lesson is that blockchain was
   never the source of value; adoption was. Immutability is a required *property*, delivered
   with ordinary, cheap tooling that stays easy to evolve.
3. **Stack:** TypeScript mobile + Python API.
   - **Mobile:** Expo / React Native (TypeScript), offline-first.
   - **API:** Python / FastAPI + Postgres.
   - Chosen so the later muzzle-print CV/ML work lives in the same (Python) ecosystem as
     the API.
4. **Scaffold depth:** A **thin walking skeleton** — one real end-to-end path — not empty
   folders. Rationale: the scaffold's job is to make later work faster *and* prove the
   certification-agnostic ledger schema is right under real constraints. Empty structure
   proves nothing.

## Architecture

### Repo shape (monorepo, no speculative abstractions)

```
True-Beef/
  api/                # FastAPI + Postgres. Owns the ledger schema (Pydantic) — single source of truth
    alembic/          # migrations
    app/
    tests/
  mobile/             # Expo / React Native (TS). TS API client generated from api's OpenAPI
  docker-compose.yml  # Postgres for local dev
  Makefile            # make up / api / mobile / gen-client / test
  docs/
```

The TS/Python language boundary is bridged **one way**: `make gen-client` regenerates the
mobile TS types/client from the API's OpenAPI document, so the app and server cannot
silently drift. There is no shared `packages/` layer — the API is the single source of
truth for the ledger schema.

### Data model (v1, certification-agnostic)

**`animals`**
- `id` (uuid, pk)
- `external_tag` (nullable — e.g. existing ear-tag / RFID)
- `breed`, `sex`, `birth_date`
- `sire_id`, `dam_id` (nullable self-referential FKs — genealogy)
- `us_born`, `us_raised` (boolean; v1 validates both true — US-born/US-raised only)
- `muzzle_ref` (nullable placeholder for the future biometric identity; CV deferred)
- `created_at`

**`ledger_events`** — the append-only, hash-chained log
- `id` (uuid, pk)
- `animal_id` (fk)
- `seq` (per-animal monotonic integer; genesis event is `seq = 0`)
- `event_type` (**string, not a DB enum** — new certification standards must be absorbable
  without a schema migration)
- `payload` (JSONB — certification-agnostic event data)
- `prev_hash` (hash of the prior event for this animal; genesis uses a fixed genesis constant)
- `hash` = `H(animal_id ‖ seq ‖ event_type ‖ canonical_json(payload) ‖ prev_hash)`
- `signature`, `signer_id` (nullable — populated for attestation events)
- `created_at`

**Key modeling decisions**
- **Attestations are not a separate table.** A certifier attestation is a `ledger_event`
  of `event_type = "ATTESTATION_ADDED"` carrying a `signature` + `signer_id`. This keeps
  the ledger certification-agnostic (the PRD's core differentiator) and the schema minimal.
- **Immutability enforced at the DB level:** a Postgres trigger rejects `UPDATE` and
  `DELETE` on `ledger_events`. Writes are append-only.
- **Canonical JSON** (stable key ordering) is used when hashing `payload` so the chain is
  reproducible.

Illustrative `event_type` values (open-ended, not enumerated in the DB):
`ANIMAL_REGISTERED`, `DIET_LOGGED`, `WEIGHT_RECORDED`, `ATTESTATION_ADDED`.

### Vertical slice — what actually runs

**API endpoints**
- `POST /animals` — create an animal and append its genesis `ANIMAL_REGISTERED` event.
- `POST /animals/{id}/events` — append an event (e.g. `DIET_LOGGED`), computing the next
  `seq`, `prev_hash`, and `hash`.
- `GET /animals/{id}` — the animal plus its full ordered event chain.
- `GET /animals/{id}/verify` — recompute the chain from genesis and return
  `valid` / `tampered`.
- `GET /health` — liveness.

**Mobile app (three screens)**
- **Herd list** — `GET` animals.
- **Log animal** — a form that `POST`s a new animal.
- **Animal detail** — the birth-to-now event timeline for one animal.
- Local cache via `expo-sqlite`. **Real bidirectional offline sync is stubbed behind a
  clear interface**, not implemented — that is Phase-1 farm-app work, not scaffold work.

### Testing

- **pytest** for the API, including the **crown-jewel test**: append several events, tamper
  with one stored row, and assert `GET /verify` detects it. This is the certifier-trust
  property, tested from day one.
- Basic React Native test setup (render + one smoke test), not extensive coverage.

### Dev / infra

- `docker-compose.yml` runs Postgres for local dev.
- **Alembic** migrations for schema.
- `.env.example` documenting required config.
- `Makefile` targets: `make up`, `make api`, `make mobile`, `make gen-client`, `make test`.
- **CI** (GitHub Actions): lint + pytest on push.
- **README** with setup/run instructions. On real code landing, update the root `CLAUDE.md`
  to drop the "pre-code" framing and record real build/run/test commands.

## Non-goals (explicitly deferred for this scaffold)

Present only as named stubs/boundaries so the architecture accommodates them; none built:
- Real muzzle-print CV / biometric matching.
- Real bidirectional offline sync.
- Authentication / identity / user accounts.
- Certifier auditor portal, processor QR assignment, consumer scan page.
- Data-insights SaaS / aggregate feeds.
- Production deployment.

## Success criteria

The scaffold is done when, from a clean checkout:
1. `make up && make api` starts Postgres + the API.
2. The vertical slice works end-to-end: create an animal, append an event, read the chain,
   and `/verify` returns `valid`.
3. The tamper test passes (`/verify` returns `tampered` after a row is altered).
4. `make gen-client` produces a TS client the mobile app compiles against.
5. The Expo app runs and shows the herd list, log-animal form, and animal detail against
   the local API.
6. CI is green (lint + pytest).
