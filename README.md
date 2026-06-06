# VABOS Staff Backend

Separate FastAPI backend scaffold for the VABOS Staff app. It is intentionally separate from the billing frontend and ready to share ecosystem auth/sync contracts later.

## Runtime
- Python 3.11

## Stack
- FastAPI
- PostgreSQL via SQLAlchemy async + asyncpg
- Redis
- WebSocket realtime endpoint
- JWT auth structure
- Alembic migrations

## Run
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
docker compose up -d
uvicorn app.main:app --reload --port 8010
```

## Test
```bash
source .venv/bin/activate
pytest -q
```

## Backend TODO
- Connect staff auth to VABOS central identity service.
- Add payroll/role modules only when staff product scope is ready.
- Add shared idempotent sync contracts with billing ecosystem APIs.
