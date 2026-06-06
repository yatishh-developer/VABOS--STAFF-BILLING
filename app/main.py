from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api import attendance, auth, notifications, realtime, staff, tasks
from app.core.config import get_settings
from app.db.database import check_database_connection, ensure_database_schema
from app.db.redis import check_redis_connection, close_redis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.create_tables_on_startup:
        await ensure_database_schema()
    yield
    await close_redis()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

origins = ['*'] if settings.allowed_origins == '*' else [item.strip() for item in settings.allowed_origins.split(',')]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
app.include_router(realtime.router)
app.include_router(staff.router)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': f'Welcome to {settings.app_name}!'}

@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name}


@app.get('/health/db')
async def database_health() -> dict[str, str]:
    try:
        await ensure_database_schema()
        await check_database_connection()
        return {'status': 'ok', 'database': 'connected'}
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f'database_unavailable: {error.__class__.__name__}',
        ) from None


@app.get('/health/redis')
async def redis_health() -> dict[str, str]:
    try:
        await check_redis_connection()
        return {'status': 'ok', 'redis': 'connected'}
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f'redis_unavailable: {error.__class__.__name__}',
        ) from None
