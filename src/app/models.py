import logging
import typing

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()


class Base(DeclarativeBase):
    metadata = METADATA


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.String(36), primary_key=True)
