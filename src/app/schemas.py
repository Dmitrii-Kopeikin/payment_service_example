from datetime import datetime
from decimal import Decimal
from typing import Annotated

import pydantic
from pydantic import AfterValidator, BaseModel, Field

from app.utils import timezone_validator
from .types import TransactionType


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class User(Base):
    id: str
    name: str


class UserCreate(Base):
    id: str
    name: str


class UserBalance(Base):
    user_id: str = Field(description="User ID")
    balance: Decimal = Field(description="User balance")
    ts: datetime | None = Field(exclude=True, default=None, description="Timestamp")


class Transaction(Base):
    uid: str = Field(description="Transaction UID")
    user_id: str = Field(description="User ID")
    amount: Decimal = Field(description="Transaction amount", gt=0)
    created_at: datetime = Field(description="Transaction created at")
    type: TransactionType = Field(description="Transaction type")


class TransactionAdd(Base):
    uid: str = Field(description="Transaction UID")
    user_id: str = Field(description="User ID")
    amount: Decimal = Field(description="Transaction amount", gt=0)
    created_at: Annotated[datetime, AfterValidator(timezone_validator)] = Field(description="Transaction created at")
    type: TransactionType = Field(description="Transaction type")
