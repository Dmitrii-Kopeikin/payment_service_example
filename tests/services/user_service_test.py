from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.database.models import UserDb
from app.exceptions import UserExistsError, UserNotFoundError, WrongTimeStampError
from app.schemas import UserCreate
from app.services import UserService


user_create_schema = UserCreate(
    id="test_id",
    name="test_name",
)

user_with_balance = UserDb(
    id="test_id",
    name="test_name",
    balance=Decimal(100),
)


@pytest.mark.asyncio(loop_scope="session")
async def test_init(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    assert user_service.user_repo is user_repo_mock
    assert user_service.transaction_repo is transaction_repo_mock
    assert user_service.db_session is db_session_mock


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )

    user_repo_mock.get.return_value = None
    user_repo_mock.create.return_value = UserDb(**user_create_schema.model_dump())

    created_user = await user_service.create_user(user_create_schema)
    assert created_user.id == user_create_schema.id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_throws_user_exists(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = UserDb(**user_create_schema.model_dump())
    with pytest.raises(UserExistsError):
        await user_service.create_user(user_create_schema)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = UserDb(**user_create_schema.model_dump())

    retrieved_user = await user_service.get_user("test_id")
    assert retrieved_user is not None
    assert retrieved_user.id == user_create_schema.id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_is_none(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = None

    user = await user_service.get_user("test_id")
    assert user is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_balance(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = user_with_balance

    balance = await user_service.get_balance("test_id")
    assert balance.user_id == user_create_schema.id
    assert balance.balance == Decimal(100)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_balance_with_timestamp(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = user_with_balance
    transaction_repo_mock.get_total_sum.return_value = Decimal(100)
    timestamp = datetime.now(tz=UTC) - timedelta(days=1)

    balance = await user_service.get_balance("test_id", ts=timestamp)
    assert balance.user_id == user_create_schema.id
    assert balance.balance == Decimal(100)
    assert balance.ts == timestamp


@pytest.mark.asyncio(loop_scope="session")
async def test_get_balance_throws_user_not_found(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = None

    with pytest.raises(UserNotFoundError):
        await user_service.get_balance("test_id")


@pytest.mark.asyncio(loop_scope="session")
async def test_get_balance_throws_wrong_timestamp(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    user_service = UserService(
        user_repo=user_repo_mock, transaction_repo=transaction_repo_mock, db_session=db_session_mock
    )
    user_repo_mock.get.return_value = user_with_balance

    with pytest.raises(WrongTimeStampError):
        await user_service.get_balance("test_id", ts=datetime.now(tz=UTC) + timedelta(minutes=1))
    with pytest.raises(WrongTimeStampError):
        await user_service.get_balance("test_id", ts=datetime.now(tz=UTC) + timedelta(days=1000))
