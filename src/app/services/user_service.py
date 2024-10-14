import typing
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType

from app.database.repositories import TransactionRepository, UserRepository
from app.exceptions import UserExistsError, UserNotFoundError, WrongTimeStampError
from app.schemas import User, UserBalance, UserCreate
from app.utils import timezone_validator


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        transaction_repo: TransactionRepository,
        db_session: AsyncSessionType,
    ):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo
        self.db_session = db_session

    async def create_user(self, data: UserCreate) -> User:
        if await self.user_repo.get(user_id=data.id):
            raise UserExistsError

        user = await self.user_repo.create(data)

        return typing.cast(User, user)

    async def get_user(self, user_id: str) -> User | None:
        user_db = await self.user_repo.get(user_id=user_id)
        return typing.cast(User | None, user_db)

    async def get_balance(self, user_id: str, ts: datetime | None = None) -> UserBalance:
        user = await self.user_repo.get(user_id=user_id)
        if not user:
            raise UserNotFoundError

        if ts is None:
            return UserBalance(user_id=user.id, balance=user.balance)

        ts = timezone_validator(ts)

        if ts > datetime.now(tz=UTC):
            raise WrongTimeStampError

        balance = await self.transaction_repo.get_total_sum(user_id=user_id, before=ts)
        return UserBalance(user_id=user.id, balance=balance, ts=ts)
