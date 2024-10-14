import logging
import typing
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.types import TransactionType
from .utils import utcnow


logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()


class Base(DeclarativeBase):
    metadata = METADATA


class UserDb(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        sa.DECIMAL(10, 2),
        nullable=False,
        default=Decimal(0),
    )

    __table_args__ = (sa.CheckConstraint("balance >= 0", name="balance_check"),)

    transactions: Mapped["TransactionDb"] = relationship(back_populates="user")


class TransactionDb(Base):
    __tablename__ = "transactions"

    uid: Mapped[str] = mapped_column(sa.String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey(UserDb.id), nullable=False)
    type: Mapped[TransactionType] = mapped_column(sa.Enum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(sa.DECIMAL(10, 2), sa.CheckConstraint("amount >= 0"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=utcnow())

    user: Mapped["UserDb"] = relationship(back_populates="transactions")
