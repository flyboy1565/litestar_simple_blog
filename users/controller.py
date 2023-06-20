from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel as _BaseModel
from pydantic import parse_obj_as
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from litestar import Litestar, get
from litestar.contrib.repository.filters import LimitOffset

from litestar.controller import Controller
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import delete, patch, post
from litestar.pagination import OffsetPagination
from litestar.params import Parameter

from users.models import (
    UserModel,
    provide_users_repo,
    provide_users_details_repo,
    UsersRepository,
    User,
)


class UserController(Controller):
    """User CRUD"""

    dependencies = {"users_repo": Provide(provide_users_repo, sync_to_thread=True)}

    @get(path="/users")
    def list_users(
        self,
        users_repo: UsersRepository,
        limit_offset: LimitOffset,
    ) -> OffsetPagination[User]:
        """List users."""
        results, total = users_repo.list_and_count(limit_offset)
        return OffsetPagination[User](
            items=parse_obj_as(list[User], results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @post(path="/users")
    def create_user(
        self,
        users_repo: UsersRepository,
        data: User,
    ) -> User:
        """Create a new author."""
        obj = users_repo.add(
            UserModel(
                **data.dict(exclude_unset=True, by_alias=False, exclude_none=True)
            ),
        )
        users_repo.session.commit()
        return User.from_orm(obj)

    # we override the users_repo to use the version that joins the Books in
    @get(
        path="/users/{users_id:uuid}",
        dependencies={
            "users_repo": Provide(provide_users_details_repo, sync_to_thread=True)
        },
    )
    def get_user(
        self,
        users_repo: UsersRepository,
        users_id: UUID = Parameter(
            title="Author ID",
            description="The author to retrieve.",
        ),
    ) -> User:
        """Get an existing author."""
        obj = users_repo.get(users_id)
        return User.from_orm(obj)

    @patch(
        path="/users/{users_id:uuid}",
        dependencies={
            "users_repo": Provide(provide_users_details_repo, sync_to_thread=True)
        },
    )
    def update_user(
        self,
        users_repo: UsersRepository,
        data: User,
        users_id: UUID = Parameter(
            title="Author ID",
            description="The author to update.",
        ),
    ) -> User:
        """Update an author."""
        raw_obj = data.dict(exclude_unset=True, by_alias=False, exclude_none=True)
        raw_obj.update({"id": users_id})
        obj = users_repo.update(UserModel(**raw_obj))
        users_repo.session.commit()
        return User.from_orm(obj)

    @delete(path="/users/{users_id:uuid}")
    def delete_user(
        self,
        users_repo: UsersRepository,
        users_id: UUID = Parameter(
            title="Author ID",
            description="The author to delete.",
        ),
    ) -> None:
        """Delete a author from the system."""
        _ = users_repo.delete(users_id)
        users_repo.session.commit()
