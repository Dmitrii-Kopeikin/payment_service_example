from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType

from app.database.models import UserDb
from app.database.repositories import UserRepository
from app.exceptions import AmountExceedsBalanceError, UserNotFoundError
from app.schemas import UserCreate


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_create(db_session: AsyncSessionType) -> None:
    user_repo = UserRepository(db_session)
    data = UserCreate(
        id="user_id_1",
        name="test_user_1",
    )
    user = await user_repo.create(data)
    await db_session.commit()

    assert user.id == "user_id_1"
    assert user.balance == Decimal("0")

    retrieved_user = await db_session.get(UserDb, "user_id_1")
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_get(db_session: AsyncSessionType) -> None:
    user_repo = UserRepository(db_session)
    data = UserCreate(
        id="user_id_2",
        name="test_user_2",
    )
    user = await user_repo.create(data)
    await db_session.commit()

    retrieved_user = await user_repo.get(user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_update_balance(db_session: AsyncSessionType) -> None:
    user_repo = UserRepository(db_session)
    data = UserCreate(
        id="user_id_3",
        name="test_user_3",
    )
    user = await user_repo.create(data)
    await db_session.commit()
    assert user.id == "user_id_3"
    assert user.name == "test_user_3"

    await user_repo.update_balance(user.id, Decimal("50"))
    await db_session.commit()
    await db_session.refresh(user)
    assert user.balance == Decimal("50")

    await user_repo.update_balance(user.id, Decimal("-25"))
    await db_session.commit()
    await db_session.refresh(user)
    assert user.balance == Decimal("25")

    with pytest.raises(AmountExceedsBalanceError):
        await user_repo.update_balance(user.id, Decimal("-50"))


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_update_balance_user_not_found(db_session: AsyncSessionType) -> None:
    user_repo = UserRepository(db_session)
    with pytest.raises(UserNotFoundError):
        await user_repo.update_balance("non_existent_user", Decimal("50"))


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures("check_database")
async def test_update_balance_amount_exceeds_balance(db_session: AsyncSessionType) -> None:
    user_repo = UserRepository(db_session)
    data = UserCreate(
        id="user_id_4",
        name="test_user_4",
    )
    user = await user_repo.create(data)
    await db_session.commit()
    assert user.id == "user_id_4"
    assert user.name == "test_user_4"

    with pytest.raises(AmountExceedsBalanceError):
        await user_repo.update_balance(user.id, Decimal(-100))
