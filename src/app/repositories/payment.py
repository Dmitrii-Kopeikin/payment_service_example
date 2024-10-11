from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession as AsyncSessionType,
)


from app import schemas
from app.models import User


class PaymentRepository:

    def __init__(self, db_session_maker: async_sessionmaker[AsyncSessionType]):
        self.db_session_maker = db_session_maker

    async def create_user(self, data: schemas.UserCreate) -> User:
        ...
