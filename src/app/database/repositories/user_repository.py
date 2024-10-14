from decimal import Decimal

from app.database.models import UserDb
from app.exceptions import AmountExceedsBalanceError, UserNotFoundError
from app.schemas import UserCreate
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, data: UserCreate) -> UserDb:
        user = UserDb(**data.model_dump())
        self.db_session.add(user)

        return user

    async def get(self, user_id: str) -> UserDb | None:
        return await self.db_session.get(UserDb, user_id)

    async def update_balance(self, user_id: str, amount: Decimal) -> None:
        user = await self.db_session.get(UserDb, user_id)
        if user is None:
            raise UserNotFoundError

        if user.balance + amount < 0:
            raise AmountExceedsBalanceError

        user.balance = UserDb.balance + amount
