from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class StaffUser(Base):
    __tablename__ = 'staff_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True, default='')
    name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, default='')
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(64), default='staff')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    attendance: Mapped[list['AttendanceEntry']] = relationship(back_populates='staff')
    tasks: Mapped[list['StaffTask']] = relationship(back_populates='staff')


class AttendanceEntry(Base):
    __tablename__ = 'attendance_entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey('staff_users.id'), index=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True, default='')
    event_type: Mapped[str] = mapped_column(String(32))
    note: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sync_status: Mapped[str] = mapped_column(String(32), default='pending')

    staff: Mapped[StaffUser] = relationship(back_populates='attendance')


class StaffTask(Base):
    __tablename__ = 'staff_tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey('staff_users.id'), nullable=True, index=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True, default='')
    title: Mapped[str] = mapped_column(String(220))
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(32), default='open')
    priority: Mapped[str] = mapped_column(String(32), default='normal')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    staff: Mapped[StaffUser] = relationship(back_populates='tasks')


class StaffNotification(Base):
    __tablename__ = 'staff_notifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey('staff_users.id'), nullable=True, index=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True, default='')
    title: Mapped[str] = mapped_column(String(220))
    body: Mapped[str] = mapped_column(Text, default='')
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CoreBusiness(Base):
    __tablename__ = 'businesses'
    __table_args__ = {'schema': 'core'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(220))
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CoreBranch(Base):
    __tablename__ = 'branches'
    __table_args__ = {'schema': 'core'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(220))
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CoreUser(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'core'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(32), index=True)
    email: Mapped[str] = mapped_column(String(180), index=True, default='')
    role: Mapped[str] = mapped_column(String(64), default='staff')
    permissions: Mapped[dict] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StaffProductSnapshot(Base):
    __tablename__ = 'product_snapshots'
    __table_args__ = {'schema': 'staff'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True)
    product_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(220))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    sync_version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StaffKot(Base):
    __tablename__ = 'kots'
    __table_args__ = {'schema': 'staff'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True)
    staff_id: Mapped[str] = mapped_column(String(64), index=True)
    kot_number: Mapped[str] = mapped_column(String(64), index=True)
    table_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    order_type: Mapped[str] = mapped_column(String(32), default='dine_in')
    status: Mapped[str] = mapped_column(String(32), default='pending')
    items: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default='')
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StaffBill(Base):
    __tablename__ = 'bills'
    __table_args__ = {'schema': 'staff'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True)
    staff_id: Mapped[str] = mapped_column(String(64), index=True)
    linked_kot_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    bill_number: Mapped[str] = mapped_column(String(64), index=True)
    items: Mapped[list] = mapped_column(JSON, default=list)
    payment_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tax: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(32), default='paid')
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SyncQueueItem(Base):
    __tablename__ = 'queue_items'
    __table_args__ = {'schema': 'sync'}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    business_id: Mapped[str] = mapped_column(String(64), index=True)
    branch_id: Mapped[str] = mapped_column(String(64), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default='pending')
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
