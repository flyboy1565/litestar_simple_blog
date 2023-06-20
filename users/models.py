from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel as _BaseModel
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase

from litestar.contrib.sqlalchemy.repository import SQLAlchemySyncRepository


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    class Config:
        orm_mode = True


# the SQLAlchemy base includes a declarative model for you to use in your models.
# The `Base` class includes a `UUID` based primary key (`id`)
class UserModel(UUIDBase):
    # we can optionally provide the table name instead of auto-generating it
    __tablename__ = "users"  #  type: ignore[assignment]
    username: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]


class User(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str


class UsersRepository(SQLAlchemySyncRepository[UserModel]):
    """Users repository."""

    model_type = UserModel


async def provide_users_repo(db_session: "Session") -> UsersRepository:
    """This provides the default Users repository."""
    return UsersRepository(session=db_session)


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_users_details_repo(db_session: "Session") -> UsersRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return UsersRepository(
        statement=select(UserModel).options(selectinload(UserModel.books)),
        session=db_session,
    )
