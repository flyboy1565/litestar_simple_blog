from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel as _BaseModel
from pydantic import parse_obj_as
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from litestar import Litestar, get
from litestar.contrib.repository.filters import LimitOffset
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.plugins.init import (
    SQLAlchemyInitPlugin,
    SQLAlchemySyncConfig,
)
from litestar.contrib.sqlalchemy.repository import SQLAlchemySyncRepository
from litestar.controller import Controller
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import delete, patch, post
from litestar.pagination import OffsetPagination
from litestar.params import Parameter

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from users.controller import UserController


def provide_limit_offset_pagination(
    current_page: int = Parameter(ge=1, query="currentPage", default=1, required=False),
    page_size: int = Parameter(
        query="pageSize",
        ge=1,
        default=10,
        required=False,
    ),
) -> LimitOffset:
    """Add offset/limit pagination.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    current_page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return LimitOffset(page_size, page_size * (current_page - 1))


sqlalchemy_config = SQLAlchemySyncConfig(
    connection_string="sqlite:///test.sqlite"
)  # Create 'db_session' dependency.
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)


def on_startup() -> None:
    """Initializes the database."""
    with sqlalchemy_config.create_engine().begin() as conn:
        UUIDBase.metadata.create_all(conn)


app = Litestar(
    route_handlers=[UserController],
    on_startup=[on_startup],
    plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination)},
    debug=True,
)
