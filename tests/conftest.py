from collections.abc import AsyncGenerator, AsyncIterator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
import sqlalchemy_utils
from alembic.command import revision, upgrade
from alembic.config import Config as AlembicConfig
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.models import METADATA
from app.database.repositories import TransactionRepository, UserRepository


class PytestSettings(BaseSettings):
    model_config = {"env_file": ".env.test", "extra": "allow"}
    database__drivername: str = "postgresql+asyncpg"
    database__postgres_username: str = "postgres"
    database__postgres_password: SecretStr = SecretStr("postgres")
    database__host: str = "localhost"
    database__port: int = 5433
    database__db_name: str = "balance_service_db"

    @property
    def db_dsn(self) -> str:
        return (
            f"{self.database__drivername}://{self.database__postgres_username}:"
            f"{self.database__postgres_password.get_secret_value()}@{self.database__host}:{self.database__port}/"
            f"{self.database__db_name}"
        )

    @property
    def db_dsn_sync(self) -> str:
        return (
            f"postgresql://{self.database__postgres_username}:"
            f"{self.database__postgres_password.get_secret_value()}@{self.database__host}:{self.database__port}/"
            f"{self.database__db_name}"
        )


settings = PytestSettings()


DB_CONNECTION_STRING = settings.db_dsn
DB_CONNECTION_STRING_SYNC = settings.db_dsn_sync


def clear_migrations_versions() -> None:
    path = Path("tests/migrations/versions")
    for file in path.glob("*.py"):
        file.unlink()


@pytest.fixture(scope="session", autouse=True)
async def database() -> AsyncGenerator[Any, bool]:
    try:
        if sqlalchemy_utils.database_exists(DB_CONNECTION_STRING_SYNC):
            sqlalchemy_utils.drop_database(DB_CONNECTION_STRING_SYNC)
        sqlalchemy_utils.create_database(DB_CONNECTION_STRING_SYNC)

        alembic_config = AlembicConfig(file_="alembic.ini")
        alembic_config.set_main_option("script_location", "tests/migrations")
        revision(alembic_config, autogenerate=True)
        upgrade(alembic_config, "head")
        clear_migrations_versions()

        database_ok = True
    except Exception:  # noqa: BLE001
        database_ok = False

    yield database_ok

    if database_ok:
        sqlalchemy_utils.drop_database(DB_CONNECTION_STRING_SYNC)


@pytest.fixture(scope="session")
async def check_database(database: bool) -> None:
    def _check_database() -> None:
        if not database:
            pytest.skip("Test database is not available!")

    _check_database()


@pytest.fixture(scope="module")
async def db_sessionmaker() -> AsyncGenerator[Any, Any]:
    async_engine = create_async_engine(DB_CONNECTION_STRING)

    if sqlalchemy_utils.database_exists(DB_CONNECTION_STRING_SYNC):
        async with async_engine.connect() as conn:
            await conn.run_sync(METADATA.drop_all)
            await conn.run_sync(METADATA.create_all)

    session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)
    yield session_maker

    await async_engine.dispose()


@pytest.fixture
async def db_session(db_sessionmaker) -> AsyncIterator[AsyncSessionType]:  # noqa: ANN001
    async with db_sessionmaker() as session:
        yield session


@pytest.fixture(scope="module")
async def db_session_module_scope(db_sessionmaker) -> AsyncIterator[AsyncSessionType]:  # noqa: ANN001
    async with db_sessionmaker() as session:
        yield session


@pytest.fixture
def db_session_mock() -> AsyncMock:
    return AsyncMock(spec=AsyncSessionType)


@pytest.fixture
def user_repo_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def transaction_repo_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionRepository)
