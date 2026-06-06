# Supabase Postgres Tenant Design

Production database is Supabase Postgres, accessed only by FastAPI.

```env
DATABASE_URL=postgresql+asyncpg://postgres.bkbgrgbuxhsykvtgsoez:<PASSWORD>@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?ssl=require
```

The real password must live in backend deployment secrets or local backend
`.env`. It must never be placed in Flutter, checked into Git, or returned by an
API response.

## Flutter Boundary

Flutter apps know only:

- REST API base URL
- WebSocket base URL
- access token / refresh token in secure storage

Flutter apps must never know:

- Supabase password
- Supabase service key
- direct database URL
- SQL connection credentials

## Schemas

- `core`: shared `businesses`, `branches`, `users`
- `staff`: staff billing KOT, bill, payment, product snapshot tables
- `billing`: reserved namespace for admin/full billing tables
- `sync`: idempotent sync queue and realtime event ledger

## Required Tenant Columns

Tenant tables include:

- `business_id`
- `branch_id`
- `created_by`
- `updated_by`
- `deleted_at` where logical delete is needed

## Query Rule

Every FastAPI route must filter by authenticated context:

```python
query = query.where(Model.business_id == current_staff.business_id)
query = query.where(Model.branch_id == current_staff.branch_id)
```

Use `app.db.tenant.tenant_filter` for common staff routes.

## RLS

The migration enables row-level security on tenant tables and intentionally does
not create public unauthenticated access policies. The backend remains
responsible for authenticated tenant filtering.
