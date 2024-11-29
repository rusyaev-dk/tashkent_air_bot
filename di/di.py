import os
from pathlib import Path
from typing import AsyncIterable

from dishka import provide, Scope, Provider, make_async_container, AsyncContainer, provide_all
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from infrastructure.api.repositories.aqi_repo import AQIRepository
from infrastructure.api.clients.http_client import HttpClient
from infrastructure.api.clients.aqi_client import AQIClient
from infrastructure.database.models import Base
from infrastructure.database.repositories.users_repo import UsersRepository
from infrastructure.database.setup import create_engine
from l10n.translator import Translator
from tgbot.config import Config, load_config


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def confing(self) -> Config:
        return load_config(".env")


class DBServiceProvider(Provider):

    @provide(scope=Scope.APP)
    async def db_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(config.db)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            yield engine
            await engine.dispose()

    @provide(scope=Scope.APP)
    async def sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session


class RepoProvider(Provider):
    scope = Scope.REQUEST

    default = provide_all(UsersRepository, AQIRepository)


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def http_client(self) -> HttpClient:
        return HttpClient()

    @provide
    async def aqi_client(self, http_client: HttpClient, config: Config) -> AQIClient:
        return AQIClient(
            http_client=http_client,
            base_url="http://api.openweathermap.org",
            token=config.api.api_token
        )


class ServiceProvider(Provider):
    scope = Scope.APP

    def __init__(self, locales_dir_path: str = None):
        super().__init__()
        if not locales_dir_path:
            locales_dir_path = str(Path(__file__).parent.parent.joinpath("l10n/locales"))
        self.__locales_dir_path = locales_dir_path

    @provide
    def scheduler(self) -> AsyncIOScheduler:
        return AsyncIOScheduler()

    @provide
    def translator_hub(self) -> Translator:
        all_files = os.listdir(self.__locales_dir_path + "/ru")
        fluent_files = [file for file in all_files if file.endswith(".ftl")]

        translator = Translator(
            locales_dir_path=str(self.__locales_dir_path), locales=["ru", "uz", "en"],
            resource_ids=fluent_files
        )
        return translator


def setup_dependencies() -> AsyncContainer:
    container = make_async_container(
        ConfigProvider(),
        DBServiceProvider(),
        ServiceProvider(),
        ClientProvider(),
        RepoProvider()
    )

    return container

