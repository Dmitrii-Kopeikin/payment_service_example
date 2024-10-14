from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType


class BaseRepository:
    def __init__(self, db_session: AsyncSessionType):
        self.db_session = db_session
