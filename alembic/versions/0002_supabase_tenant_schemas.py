"""supabase tenant schemas

Revision ID: 0002_supabase_tenant_schemas
Revises: 0001_initial_staff_tables
Create Date: 2026-06-06
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_supabase_tenant_schemas'
down_revision = '0001_initial_staff_tables'
branch_labels = None
depends_on = None


TENANT_COLUMNS = [
    sa.Column('business_id', sa.String(length=64), nullable=False),
    sa.Column('branch_id', sa.String(length=64), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
]


def _enable_rls(schema: str, table: str) -> None:
    op.execute(f'ALTER TABLE {schema}.{table} ENABLE ROW LEVEL SECURITY')
    op.execute(
        f"COMMENT ON TABLE {schema}.{table} IS "
        "'Tenant isolated. FastAPI must filter by authenticated business_id and branch_id. "
        "No public unauthenticated policies are created.'"
    )


def upgrade() -> None:
    for schema in ('core', 'staff', 'billing', 'sync'):
        op.execute(sa.schema.CreateSchema(schema, if_not_exists=True))

    op.create_table(
        'businesses',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=220), nullable=False),
        sa.Column('created_by', sa.String(length=64), nullable=True),
        sa.Column('updated_by', sa.String(length=64), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema='core',
    )
    op.create_table(
        'branches',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('business_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=220), nullable=False),
        sa.Column('created_by', sa.String(length=64), nullable=True),
        sa.Column('updated_by', sa.String(length=64), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema='core',
    )
    op.create_index('ix_core_branches_tenant', 'branches', ['business_id'], schema='core')
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('business_id', sa.String(length=64), nullable=False),
        sa.Column('branch_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=False),
        sa.Column('email', sa.String(length=180), nullable=False, server_default=''),
        sa.Column('role', sa.String(length=64), nullable=False, server_default='staff'),
        sa.Column('permissions', sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_by', sa.String(length=64), nullable=True),
        sa.Column('updated_by', sa.String(length=64), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema='core',
    )
    op.create_index('ix_core_users_tenant', 'users', ['business_id', 'branch_id'], schema='core')

    op.create_table(
        'product_snapshots',
        sa.Column('id', sa.String(length=64), primary_key=True),
        *TENANT_COLUMNS,
        sa.Column('product_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=220), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('sync_version', sa.Integer(), nullable=False, server_default='1'),
        schema='staff',
    )
    op.create_table(
        'kots',
        sa.Column('id', sa.String(length=64), primary_key=True),
        *TENANT_COLUMNS,
        sa.Column('staff_id', sa.String(length=64), nullable=False),
        sa.Column('kot_number', sa.String(length=64), nullable=False),
        sa.Column('table_number', sa.String(length=64), nullable=True),
        sa.Column('order_type', sa.String(length=32), nullable=False, server_default='dine_in'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('items', sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('idempotency_key', sa.String(length=80), nullable=False, unique=True),
        schema='staff',
    )
    op.create_table(
        'bills',
        sa.Column('id', sa.String(length=64), primary_key=True),
        *TENANT_COLUMNS,
        sa.Column('staff_id', sa.String(length=64), nullable=False),
        sa.Column('linked_kot_id', sa.String(length=64), nullable=True),
        sa.Column('bill_number', sa.String(length=64), nullable=False),
        sa.Column('items', sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('payment_breakdown', sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('subtotal', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('tax', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('discount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='paid'),
        sa.Column('idempotency_key', sa.String(length=80), nullable=False, unique=True),
        schema='staff',
    )
    op.create_table(
        'payments',
        sa.Column('id', sa.String(length=64), primary_key=True),
        *TENANT_COLUMNS,
        sa.Column('bill_id', sa.String(length=64), nullable=False),
        sa.Column('staff_id', sa.String(length=64), nullable=False),
        sa.Column('method', sa.String(length=32), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('idempotency_key', sa.String(length=80), nullable=False, unique=True),
        schema='staff',
    )
    op.create_table(
        'queue_items',
        sa.Column('id', sa.String(length=64), primary_key=True),
        *TENANT_COLUMNS,
        sa.Column('idempotency_key', sa.String(length=80), nullable=False, unique=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('synced_at', sa.DateTime(), nullable=True),
        schema='sync',
    )
    op.create_table(
        'realtime_events',
        sa.Column('id', sa.String(length=64), primary_key=True),
        *TENANT_COLUMNS,
        sa.Column('event_name', sa.String(length=120), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        schema='sync',
    )

    for schema, tables in {
        'core': ('businesses', 'branches', 'users'),
        'staff': ('product_snapshots', 'kots', 'bills', 'payments'),
        'sync': ('queue_items', 'realtime_events'),
    }.items():
        for table in tables:
            _enable_rls(schema, table)


def downgrade() -> None:
    for schema, table in (
        ('sync', 'realtime_events'),
        ('sync', 'queue_items'),
        ('staff', 'payments'),
        ('staff', 'bills'),
        ('staff', 'kots'),
        ('staff', 'product_snapshots'),
        ('core', 'users'),
        ('core', 'branches'),
        ('core', 'businesses'),
    ):
        op.drop_table(table, schema=schema)
    for schema in ('sync', 'billing', 'staff', 'core'):
        op.execute(sa.schema.DropSchema(schema, if_exists=True))
