from collections.abc import AsyncGenerator
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()
engine_kwargs = {
    'pool_pre_ping': True,
    'pool_recycle': 1800,
}
if settings.database_use_null_pool:
    engine_kwargs['poolclass'] = NullPool

engine = create_async_engine(
    settings.effective_database_url,
    **engine_kwargs,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
_schema_ready = False
_schema_lock = asyncio.Lock()


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def check_database_connection() -> bool:
    async with engine.connect() as connection:
        await connection.execute(text('select 1'))
    return True


async def ensure_database_schema(*, force: bool = False) -> None:
    global _schema_ready
    if _schema_ready and not force:
        return
    async with _schema_lock:
        if _schema_ready and not force:
            return
        async with engine.begin() as connection:
            for schema in ('core', 'staff', 'billing', 'sync'):
                await connection.execute(text(f'create schema if not exists {schema}'))
            await connection.run_sync(Base.metadata.create_all)
        _schema_ready = True
