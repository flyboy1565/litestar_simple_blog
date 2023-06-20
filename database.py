from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncGenerator

from litestar import Litestar
from litestar.datastructures import State
from litestar.exceptions import ClientException, NotFoundException
from litestar.status_codes import HTTP_409_CONFLICT

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


from settings import SQLITE_URL


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    # try to get engine state from app
    # if none exists return None
    engine = getattr(app.state, "engine", None)
    if engine is None:
        engine = create_async_engine(SQLITE_URL, echo=True)
        app.state.engine = engine
    try:
        yield
    finally:
        await engine.dispose()


async def provide_transaction(state: State) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker(bind=state.engine) as session:
        try:
            async with session.begin():
                yield session
        except IntegrityError as exc:
            raise ClientException(
                status_code=HTTP_409_CONFLICT,
                detail=str(exc),
            )


sessionmaker = async_sessionmaker(expire_on_commit=False)
