from typing import AsyncIterable

from dishka import provide, Scope, Provider, make_async_container, AsyncContainer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from infrastructure.api.repositories.aqi_repo import AQIRepositoryI
from infrastructure.api.repositories.aqi_repo_impl import AQIRepository
from infrastructure.clients.http_client import HttpClient
from infrastructure.clients.aqi_client import AQIClient
from infrastructure.database.models import Base
from infrastructure.database.repositories.users_repo import UsersRepositoryI
from infrastructure.database.repositories.users_repo_impl import UsersRepository
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.config import Config, load_config


class ConfigProvider(Provider):

    @provide(scope=Scope.APP)
    def confing(self) -> Config:
        return load_config(".env")


class DBServiceProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_engine(self, config: Config) -> AsyncEngine:
        engine = create_engine(config.db)
        await self.__setup_database(engine)
        return engine

    @provide(scope=Scope.APP)
    async def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_db_session(self, sessionmaker: async_sessionmaker) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @staticmethod
    async def __setup_database(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()


class RepoProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.REQUEST)
    async def users_repo(self, session: AsyncSession) -> UsersRepositoryI:
        return UsersRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def aqi_repo(self, aqi_client: AQIClient, session: AsyncSession) -> AQIRepositoryI:
        return AQIRepository(aqi_client=aqi_client, session=session)


class ClientProvider(Provider):

    @provide(scope=Scope.APP)
    async def http_client(self) -> HttpClient:
        return HttpClient()

    @provide(scope=Scope.APP)
    async def aqi_client(self, http_client: HttpClient, config: Config) -> AQIClient:
        return AQIClient(
            http_client=http_client,
            base_url="http://api.openweathermap.org",
            token=config.api.api_token
        )


def setup_dependencies() -> AsyncContainer:
    container = make_async_container(
        ConfigProvider(),
        DBServiceProvider(),
        ClientProvider(),
        RepoProvider()
    )

    return container

