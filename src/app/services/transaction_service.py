import typing

from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType

from app import schemas
from app.database.repositories import TransactionRepository
from app.database.repositories.user_repository import UserRepository
from app.exceptions import (
    AmountExceedsBalanceError,
    TransactionExceedsBalanceError,
    TransactionNotFoundError,
    TransactionProcessedError,
)
from app.types import TransactionType


class TransactionService:
    def __init__(
        self, transaction_repo: TransactionRepository, user_repo: UserRepository, db_session: AsyncSessionType
    ):
        self.transaction_repo = transaction_repo
        self.user_repo = user_repo
        self.db_session = db_session

    async def get_transaction(self, uid: str) -> schemas.Transaction:
        transaction = await self.transaction_repo.get(uid=uid)
        if transaction is None:
            raise TransactionNotFoundError

        return typing.cast(schemas.Transaction, transaction)

    async def add_transaction(self, data: schemas.TransactionAdd) -> schemas.Transaction:
        if await self.transaction_repo.get(uid=data.uid):
            raise TransactionProcessedError

        amount = -data.amount if data.type == TransactionType.WITHDRAW else data.amount
        try:
            await self.user_repo.update_balance(user_id=data.user_id, amount=amount)
        except AmountExceedsBalanceError as e:
            raise TransactionExceedsBalanceError from e

        transaction = await self.transaction_repo.add(data)
        return typing.cast(schemas.Transaction, transaction)
