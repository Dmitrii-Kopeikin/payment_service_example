from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.database.models import TransactionDb
from app.schemas import TransactionAdd
from app.types import TransactionType
from .base_repository import BaseRepository


class TransactionRepository(BaseRepository):
    async def add(self, data: TransactionAdd) -> TransactionDb:
        transaction = TransactionDb(**data.model_dump())
        self.db_session.add(transaction)

        return transaction

    async def get(self, uid: str) -> TransactionDb | None:
        return await self.db_session.get(TransactionDb, uid)

    async def get_total_sum(
        self, user_id: str, after: datetime | None = None, before: datetime | None = None
    ) -> Decimal:
        query_amount_by_type = select(TransactionDb.type, func.sum(TransactionDb.amount)).where(
            TransactionDb.user_id == user_id
        )

        if after is not None:
            query_amount_by_type = query_amount_by_type.where(TransactionDb.created_at >= after)
        if before is not None:
            query_amount_by_type = query_amount_by_type.where(TransactionDb.created_at <= before)

        query_amount_by_type = query_amount_by_type.group_by(TransactionDb.type)

        result = (await self.db_session.execute(query_amount_by_type)).all()

        total_sum = Decimal(0)
        for row in result:
            if row[0] == TransactionType.WITHDRAW:
                total_sum -= row[1]
            elif row[0] == TransactionType.DEPOSIT:
                total_sum += row[1]

        return total_sum
