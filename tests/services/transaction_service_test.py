from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app import schemas
from app.database.models import TransactionDb
from app.exceptions import (
    AmountExceedsBalanceError,
    TransactionExceedsBalanceError,
    TransactionNotFoundError,
    TransactionProcessedError,
)
from app.services import TransactionService
from app.types import TransactionType


transaction_schema = schemas.TransactionAdd(
    uid="test_uid",
    user_id="test_user_id",
    amount=Decimal("100"),
    type=TransactionType.DEPOSIT,
    created_at=datetime.now(UTC),
)


@pytest.mark.asyncio(loop_scope="session")
async def test_init(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    transaction_service = TransactionService(
        transaction_repo=transaction_repo_mock, user_repo=user_repo_mock, db_session=db_session_mock
    )
    assert transaction_service.transaction_repo is transaction_repo_mock
    assert transaction_service.user_repo is user_repo_mock
    assert transaction_service.db_session is db_session_mock


@pytest.mark.asyncio(loop_scope="session")
async def test_add_transaction(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    transaction_service = TransactionService(
        transaction_repo=transaction_repo_mock, user_repo=user_repo_mock, db_session=db_session_mock
    )

    transaction_repo_mock.get.return_value = None
    user_repo_mock.update_balance.return_value = None
    transaction_repo_mock.add.return_value = TransactionDb(**transaction_schema.model_dump())

    added_transaction = await transaction_service.add_transaction(transaction_schema)
    assert added_transaction.uid == transaction_schema.uid
    assert added_transaction.user_id == transaction_schema.user_id
    assert added_transaction.amount == transaction_schema.amount
    assert added_transaction.type == transaction_schema.type
    assert added_transaction.created_at == transaction_schema.created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_add_transaction_throws_transaction_exceeds_balance(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    transaction_service = TransactionService(
        transaction_repo=transaction_repo_mock, user_repo=user_repo_mock, db_session=db_session_mock
    )

    def raise_amount_exceeds_balance_error(user_id: str, amount: Decimal) -> None:  # noqa: ARG001
        raise AmountExceedsBalanceError

    transaction_repo_mock.get.return_value = None
    user_repo_mock.update_balance.side_effect = raise_amount_exceeds_balance_error
    with pytest.raises(TransactionExceedsBalanceError):
        await transaction_service.add_transaction(transaction_schema)


@pytest.mark.asyncio(loop_scope="session")
async def test_add_transaction_throws_transaction_processed(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    transaction_service = TransactionService(
        transaction_repo=transaction_repo_mock, user_repo=user_repo_mock, db_session=db_session_mock
    )
    transaction_repo_mock.get.return_value = TransactionDb(**transaction_schema.model_dump())
    with pytest.raises(TransactionProcessedError):
        await transaction_service.add_transaction(transaction_schema)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_transaction(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    transaction_service = TransactionService(
        transaction_repo=transaction_repo_mock, user_repo=user_repo_mock, db_session=db_session_mock
    )
    transaction_repo_mock.get.return_value = TransactionDb(**transaction_schema.model_dump())

    retrieved_transaction = await transaction_service.get_transaction("test_uid")
    assert retrieved_transaction.uid == transaction_schema.uid
    assert retrieved_transaction.user_id == transaction_schema.user_id
    assert retrieved_transaction.amount == transaction_schema.amount
    assert retrieved_transaction.type == transaction_schema.type
    assert retrieved_transaction.created_at == transaction_schema.created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_get_transaction_throws_transaction_not_found(
    db_session_mock: AsyncMock,
    user_repo_mock: AsyncMock,
    transaction_repo_mock: AsyncMock,
) -> None:
    transaction_service = TransactionService(
        transaction_repo=transaction_repo_mock, user_repo=user_repo_mock, db_session=db_session_mock
    )
    transaction_repo_mock.get.return_value = None
    with pytest.raises(TransactionNotFoundError):
        await transaction_service.get_transaction("test_uid")
