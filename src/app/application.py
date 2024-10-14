import contextlib
import logging
import typing
from collections.abc import AsyncIterator

import fastapi
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from starlette import status

from app.api.base import get_db, get_db_session
from app.api.payments import ROUTER
from app.exceptions import INTERNAL_SERVER_ERROR_MSG
from app.settings import Settings


logger = logging.getLogger(__name__)


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


async def exception_handler(request: fastapi.Request, call_next) -> fastapi.Response:  # noqa: ANN001
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception("Unhandled exception", exc_info=e)
        return fastapi.Response(
            content=f"{{detail: {INTERNAL_SERVER_ERROR_MSG}}}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AppBuilder:
    _async_engine: AsyncEngine
    _session_maker: async_sessionmaker[AsyncSessionType]

    def __init__(self) -> None:
        self.settings = Settings()
        self.app: fastapi.FastAPI = fastapi.FastAPI(
            title=self.settings.service_name,
            debug=self.settings.debug,
            lifespan=self.lifespan_manager,
        )

        self.app.dependency_overrides[get_db] = self.get_async_session_maker
        self.app.dependency_overrides[get_db_session] = self.get_db_session
        self.app.middleware("http")(exception_handler)
        include_routers(self.app)

    async def get_async_session_maker(self) -> async_sessionmaker[AsyncSessionType]:
        return self._session_maker

    async def get_db_session(self) -> AsyncIterator[AsyncSessionType]:
        async with self._session_maker() as session:
            yield session

    async def init_async_resources(self) -> None:
        self._async_engine = create_async_engine(self.settings.db_dsn)
        self._session_maker = async_sessionmaker(bind=self._async_engine, expire_on_commit=False, autoflush=False)

    async def tear_down(self) -> None:
        await self._async_engine.dispose()

    @contextlib.asynccontextmanager
    async def lifespan_manager(self, _: fastapi.FastAPI) -> typing.AsyncIterator[dict[str, typing.Any]]:
        try:
            await self.init_async_resources()
            yield {}
        finally:
            await self.tear_down()


application = AppBuilder().app
