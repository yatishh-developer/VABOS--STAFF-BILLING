"""initial staff tables

Revision ID: 0001_initial_staff_tables
Revises:
Create Date: 2026-06-06
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial_staff_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'staff_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.String(length=64), nullable=False),
        sa.Column('branch_id', sa.String(length=64), nullable=False, server_default=''),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=False),
        sa.Column('email', sa.String(length=180), nullable=False, server_default=''),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=False, server_default='staff'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_staff_users_business_id', 'staff_users', ['business_id'])
    op.create_index('ix_staff_users_branch_id', 'staff_users', ['branch_id'])
    op.create_index('ix_staff_users_phone', 'staff_users', ['phone'], unique=True)
    op.create_index('ix_staff_users_email', 'staff_users', ['email'], unique=True)

    op.create_table(
        'attendance_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('staff_id', sa.Integer(), sa.ForeignKey('staff_users.id'), nullable=False),
        sa.Column('business_id', sa.String(length=64), nullable=False),
        sa.Column('branch_id', sa.String(length=64), nullable=False, server_default=''),
        sa.Column('event_type', sa.String(length=32), nullable=False),
        sa.Column('note', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('sync_status', sa.String(length=32), nullable=False, server_default='pending'),
    )
    op.create_index('ix_attendance_entries_staff_id', 'attendance_entries', ['staff_id'])
    op.create_index('ix_attendance_entries_business_id', 'attendance_entries', ['business_id'])
    op.create_index('ix_attendance_entries_branch_id', 'attendance_entries', ['branch_id'])

    op.create_table(
        'staff_tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('staff_id', sa.Integer(), sa.ForeignKey('staff_users.id'), nullable=True),
        sa.Column('business_id', sa.String(length=64), nullable=False),
        sa.Column('branch_id', sa.String(length=64), nullable=False, server_default=''),
        sa.Column('title', sa.String(length=220), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(length=32), nullable=False, server_default='normal'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_staff_tasks_staff_id', 'staff_tasks', ['staff_id'])
    op.create_index('ix_staff_tasks_business_id', 'staff_tasks', ['business_id'])
    op.create_index('ix_staff_tasks_branch_id', 'staff_tasks', ['branch_id'])

    op.create_table(
        'staff_notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('staff_id', sa.Integer(), sa.ForeignKey('staff_users.id'), nullable=True),
        sa.Column('business_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=220), nullable=False),
        sa.Column('body', sa.Text(), nullable=False, server_default=''),
        sa.Column('read', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_staff_notifications_staff_id', 'staff_notifications', ['staff_id'])
    op.create_index('ix_staff_notifications_business_id', 'staff_notifications', ['business_id'])


def downgrade() -> None:
    op.drop_table('staff_notifications')
    op.drop_table('staff_tasks')
    op.drop_table('attendance_entries')
    op.drop_table('staff_users')
