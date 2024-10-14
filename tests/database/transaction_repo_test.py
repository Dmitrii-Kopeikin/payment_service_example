from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType

from app.database.models import TransactionDb, UserDb
from app.database.repositories import TransactionRepository
from app.schemas import TransactionAdd
from app.types import TransactionType


@pytest.fixture(scope="module", autouse=True)
async def users(db_session_module_scope: AsyncSessionType) -> None:
    users = [
        UserDb(id="user_id_11", name="test_user_11"),
        UserDb(id="user_id_12", name="test_user_12"),
        UserDb(id="user_id_13", name="test_user_13"),
        UserDb(id="user_id_14", name="test_user_14"),
        UserDb(id="user_id_15", name="test_user_15"),
    ]
    db_session_module_scope.add_all(users)
    await db_session_module_scope.commit()


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_add(db_session: AsyncSessionType) -> None:
    repo = TransactionRepository(db_session)
    data = TransactionAdd(
        uid="tr_uid_11",
        user_id="user_id_11",
        amount=Decimal("100"),
        type=TransactionType.DEPOSIT,
        created_at=datetime.now(UTC),
    )
    transaction = await repo.add(data)
    await db_session.commit()

    assert transaction.user_id == "user_id_11"
    assert transaction.amount == Decimal("100")
    assert transaction.type == TransactionType.DEPOSIT

    query = select(TransactionDb).where(TransactionDb.uid == transaction.uid)
    result = await db_session.execute(query)
    retrieved_transaction = result.scalar_one_or_none()

    assert retrieved_transaction is not None
    assert retrieved_transaction.uid == transaction.uid


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_get(db_session: AsyncSessionType) -> None:
    repo = TransactionRepository(db_session)
    data = TransactionAdd(
        uid="tr_uid_12",
        user_id="user_id_11",
        amount=Decimal("100"),
        type=TransactionType.DEPOSIT,
        created_at=datetime.now(UTC),
    )
    transaction = await repo.add(data)
    await db_session.commit()

    retrieved_transaction = await repo.get(transaction.uid)
    assert retrieved_transaction is not None
    assert retrieved_transaction.uid == transaction.uid


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_get_total_sum_no_filters(db_session: AsyncSessionType) -> None:
    repo = TransactionRepository(db_session)
    await repo.add(
        TransactionAdd(
            uid="tr_uid_13",
            user_id="user_id_12",
            amount=Decimal("100"),
            type=TransactionType.DEPOSIT,
            created_at=datetime.now(UTC),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_14",
            user_id="user_id_12",
            amount=Decimal("50"),
            type=TransactionType.WITHDRAW,
            created_at=datetime.now(UTC),
        )
    )
    await db_session.commit()

    total_sum = await repo.get_total_sum(user_id="user_id_12")
    assert total_sum == Decimal(50)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_get_total_sum_with_before_filter(db_session: AsyncSessionType) -> None:
    repo = TransactionRepository(db_session)
    now = datetime.now(UTC)
    await repo.add(
        TransactionAdd(
            uid="tr_uid_15",
            user_id="user_id_13",
            amount=Decimal(100),
            type=TransactionType.DEPOSIT,
            created_at=now - timedelta(days=2),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_16",
            user_id="user_id_13",
            amount=Decimal(50),
            type=TransactionType.WITHDRAW,
            created_at=now - timedelta(days=1),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_17",
            user_id="user_id_13",
            amount=Decimal(25),
            type=TransactionType.DEPOSIT,
            created_at=now,
        )
    )
    await db_session.commit()

    total_sum = await repo.get_total_sum(user_id="user_id_13", before=now - timedelta(hours=1))
    assert total_sum == Decimal(50)  # 100(deposit) - 50 (withdraw)

    total_sum = await repo.get_total_sum(user_id="user_id_13", before=now)
    assert total_sum == Decimal(75)  # 100(deposit) - 50 (withdraw) + 25 (deposit)

    total_sum = await repo.get_total_sum(user_id="user_id_13", before=now + timedelta(hours=1))
    assert total_sum == Decimal(75)  # 100(deposit) - 50 (withdraw) + 25 (deposit)

    total_sum = await repo.get_total_sum(user_id="user_id_13", before=now - timedelta(days=3))
    assert total_sum == Decimal(0)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_get_total_sum_with_after_filter(db_session: AsyncSessionType) -> None:
    repo = TransactionRepository(db_session)
    now = datetime.now(UTC)
    await repo.add(
        TransactionAdd(
            uid="tr_uid_18",
            user_id="user_id_14",
            amount=Decimal(100),
            type=TransactionType.DEPOSIT,
            created_at=now - timedelta(days=2),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_19",
            user_id="user_id_14",
            amount=Decimal(50),
            type=TransactionType.WITHDRAW,
            created_at=now - timedelta(days=1),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_20",
            user_id="user_id_14",
            amount=Decimal(25),
            type=TransactionType.DEPOSIT,
            created_at=now,
        )
    )
    await db_session.commit()

    total_sum = await repo.get_total_sum(user_id="user_id_14", after=now - timedelta(hours=1))
    assert total_sum == Decimal(25)

    total_sum = await repo.get_total_sum(user_id="user_id_14", after=now)
    assert total_sum == Decimal(25)

    total_sum = await repo.get_total_sum(user_id="user_id_14", after=now - timedelta(days=1))
    assert total_sum == Decimal(-25)

    total_sum = await repo.get_total_sum(user_id="user_id_14", after=now - timedelta(days=3))
    assert total_sum == Decimal(75)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_get_total_sum_with_after_and_before_filter(db_session: AsyncSessionType) -> None:
    repo = TransactionRepository(db_session)
    now = datetime.now(UTC)
    await repo.add(
        TransactionAdd(
            uid="tr_uid_21",
            user_id="user_id_15",
            amount=Decimal(100),
            type=TransactionType.DEPOSIT,
            created_at=now - timedelta(days=2),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_22",
            user_id="user_id_15",
            amount=Decimal(50),
            type=TransactionType.WITHDRAW,
            created_at=now - timedelta(days=1),
        )
    )
    await repo.add(
        TransactionAdd(
            uid="tr_uid_23",
            user_id="user_id_15",
            amount=Decimal(25),
            type=TransactionType.DEPOSIT,
            created_at=now,
        )
    )
    await db_session.commit()

    total_sum = await repo.get_total_sum(
        user_id="user_id_15", after=now - timedelta(days=1, hours=1), before=now - timedelta(hours=1)
    )
    assert total_sum == Decimal(-50)
