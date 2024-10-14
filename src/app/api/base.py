from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database.repositories import TransactionRepository, UserRepository
from app.services import TransactionService, UserService
from app.settings import Settings


def get_settings() -> Settings:
    raise NotImplementedError


def get_db() -> async_sessionmaker[AsyncSessionType]:
    raise NotImplementedError


def get_db_session() -> AsyncSessionType:
    raise NotImplementedError


def get_user_repo(
    db_session: AsyncSessionType = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(db_session=db_session)


def get_transaction_repo(
    db_session: AsyncSessionType = Depends(get_db_session),
) -> TransactionRepository:
    return TransactionRepository(db_session=db_session)


def get_user_service(
    db_session: AsyncSessionType = Depends(get_db_session),
    user_repo: UserRepository = Depends(get_user_repo),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
) -> UserService:
    return UserService(
        user_repo=user_repo,
        transaction_repo=transaction_repo,
        db_session=db_session,
    )


def get_transaction_service(
    db_session: AsyncSessionType = Depends(get_db_session),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> TransactionService:
    return TransactionService(transaction_repo=transaction_repo, user_repo=user_repo, db_session=db_session)
