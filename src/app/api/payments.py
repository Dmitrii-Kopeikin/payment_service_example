import typing
from datetime import datetime

import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from starlette import status

from app import schemas
from app.api.base import get_db_session, get_transaction_service, get_user_service
from app.exceptions import (
    TransactionExceedsBalanceError,
    TransactionNotFoundError,
    TransactionProcessedError,
    UserExistsError,
    UserNotFoundError,
    WrongTimeStampError,
)
from app.services import TransactionService, UserService


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.post("/user/")
async def create_user(
    data: schemas.UserCreate,
    user_service: UserService = Depends(get_user_service),
    db_session: AsyncSessionType = Depends(get_db_session),
) -> schemas.User:
    try:
        user = await user_service.create_user(data)
        await db_session.commit()
    except UserExistsError as e:
        await db_session.rollback()
        raise fastapi.HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    else:
        return user


@ROUTER.get("/user/{user_id}/balance/")
async def get_user_balance(
    user_id: str,
    ts: typing.Annotated[
        datetime | None, fastapi.Query(description="Timestamp in ISO format with timezone. Defaults to UTC.")
    ] = None,
    user_service: UserService = Depends(get_user_service),
) -> schemas.UserBalance:
    try:
        balance = await user_service.get_balance(user_id=user_id, ts=ts)
    except UserNotFoundError as e:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except WrongTimeStampError as e:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    else:
        return balance


@ROUTER.put("/transaction/")
async def add_transaction(
    data: schemas.TransactionAdd,
    transaction_service: TransactionService = Depends(get_transaction_service),
    db_session: AsyncSessionType = Depends(get_db_session),
) -> schemas.Transaction:
    try:
        transaction = await transaction_service.add_transaction(data)
        await db_session.commit()
    except UserNotFoundError as e:
        await db_session.rollback()
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except TransactionProcessedError as e:
        await db_session.rollback()
        raise fastapi.HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except TransactionExceedsBalanceError as e:
        await db_session.rollback()
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    else:
        return transaction


@ROUTER.post("/transaction/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> schemas.Transaction:
    try:
        transaction = await transaction_service.get_transaction(transaction_id)
    except TransactionNotFoundError as e:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    else:
        return transaction
