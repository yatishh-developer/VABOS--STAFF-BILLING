from functools import lru_cache
import os
from urllib.parse import quote

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'VABOS Staff API'
    environment: str = 'dev'
    database_url: str = 'postgresql+asyncpg://vabos:vabos@localhost:5432/vabos_staff'
    database_use_null_pool: bool = True
    redis_url: str = 'redis://localhost:6379/1'
    redis_host: str = ''
    redis_port: int = 6379
    redis_username: str = ''
    redis_password: str = ''
    redis_db: int = 0
    jwt_secret: str = 'change-me'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1440
    allowed_origins: str = '*'
    create_tables_on_startup: bool = True

    @property
    def effective_database_url(self) -> str:
        """Return async SQLAlchemy URL, preferring Supabase split env values."""
        dotenv = dotenv_values('.env')

        def env_value(prefixed_key: str, legacy_key: str) -> str:
            return (
                os.getenv(prefixed_key)
                or os.getenv(legacy_key)
                or str(dotenv.get(prefixed_key) or '')
                or str(dotenv.get(legacy_key) or '')
            )

        user = env_value('SUPABASE_DB_USER', 'user')
        password = env_value('SUPABASE_DB_PASSWORD', 'password')
        host = env_value('SUPABASE_DB_HOST', 'host')
        port = env_value('SUPABASE_DB_PORT', 'port') or '6543'
        dbname = env_value('SUPABASE_DB_NAME', 'dbname') or 'postgres'

        if any([user, password, host]):
            if not all([user, password, host, port, dbname]):
                raise ValueError('DATABASE_URL or Supabase database env parts are required')
            if password == '[YOUR-PASSWORD]':
                raise ValueError('Supabase database password is still the placeholder value')
            return (
                f'postgresql+asyncpg://{quote(user, safe="")}:'
                f'{quote(password, safe="")}@{host}:{port}/{dbname}?ssl=require'
            )

        explicit_database_url = os.getenv('DATABASE_URL')
        if explicit_database_url:
            return str(explicit_database_url).replace(
                'postgresql+psycopg2://',
                'postgresql+asyncpg://',
            )

        dotenv_database_url = dotenv.get('DATABASE_URL')
        if dotenv_database_url:
            return str(dotenv_database_url).replace(
                'postgresql+psycopg2://',
                'postgresql+asyncpg://',
            )

        return self.database_url

    @property
    def effective_redis_url(self) -> str:
        """Return Redis URL from REDIS_URL or split Redis env settings."""
        dotenv = dotenv_values('.env')
        explicit_redis_url = os.getenv('REDIS_URL')
        if explicit_redis_url:
            return explicit_redis_url

        host = os.getenv('REDIS_HOST') or str(dotenv.get('REDIS_HOST') or self.redis_host)
        password = os.getenv('REDIS_PASSWORD') or str(dotenv.get('REDIS_PASSWORD') or self.redis_password)
        username = os.getenv('REDIS_USERNAME') or str(dotenv.get('REDIS_USERNAME') or self.redis_username)
        port = os.getenv('REDIS_PORT') or str(dotenv.get('REDIS_PORT') or self.redis_port)
        db = os.getenv('REDIS_DB') or str(dotenv.get('REDIS_DB') or self.redis_db)

        if host:
            auth = ''
            if username and password:
                auth = f'{quote(username, safe="")}:{quote(password, safe="")}@'
            elif password:
                auth = f':{quote(password, safe="")}@'
            return f'redis://{auth}{host}:{port}/{db}'

        dotenv_redis_url = dotenv.get('REDIS_URL')
        if dotenv_redis_url:
            return str(dotenv_redis_url)

        return self.redis_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
