import asyncio
import logging
from datetime import datetime

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from di.di import setup_dependencies
from infrastructure.api.clients.http_client import HttpClient
from infrastructure.database.models import Base
from infrastructure.database.repositories.users_repo import UsersRepository
from tgbot.config import Config
from tgbot.handlers import routers_list
from tgbot.middlewares.database import UserExistingMiddleware
from tgbot.middlewares.l10n import L10nMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.constants import DEFAULT_THROTTLE_TIME, SCHEDULER_AQI_INTERVAL_MINUTES
from tgbot.services import broadcaster
from tgbot.services.aqi_scheduler import AQIScheduler
from tgbot.services.micro_functions import get_correct_update_run_time
from tgbot.services.setup_bot_commands import setup_admin_commands
from dishka.integrations.aiogram import setup_dishka


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def setup_storage(
        config: Config
):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


def setup_global_middlewares(
        dp: Dispatcher
):
    dp.message.middleware(ThrottlingMiddleware(
        default_throttle_time=DEFAULT_THROTTLE_TIME))

    dp.message.middleware(UserExistingMiddleware())

    dp.message.middleware(L10nMiddleware())
    dp.callback_query.middleware(L10nMiddleware())


async def setup_scheduler(
        bot: Bot,
        di_container: AsyncContainer
):
    scheduler = await di_container.get(AsyncIOScheduler)
    scheduler.start()

    now = datetime.now()
    update_run_time = get_correct_update_run_time(now=now)
    scheduler.add_job(
        func=AQIScheduler.update_aqi, trigger='interval',
        minutes=SCHEDULER_AQI_INTERVAL_MINUTES, replace_existing=True,
        start_date=update_run_time,
        args=(di_container,)
    )

    # scheduler.add_job(
    #     func=AQIScheduler.update_aqi, trigger='interval',
    #     seconds=5, replace_existing=True,
    #     args=(di_container,)
    # )

    first_run_time = None
    if 0 < now.minute < 59:
        first_run_time = now.replace(second=30, microsecond=0, minute=59, hour=now.hour)

    # scheduler.add_job(
    #     func=AQIScheduler.notify_users, trigger="interval", hours=1,
    #     replace_existing=True, start_date=first_run_time,
    #     args=(bot, di_container,)
    # )

    scheduler.add_job(
        func=AQIScheduler.notify_users, trigger='interval',
        seconds=5, replace_existing=True,
        args=(bot, di_container,)
    )


async def establish_db(di_container: AsyncContainer):
    engine: AsyncEngine = await di_container.get(AsyncEngine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with di_container() as request_container:
        users_repo = await request_container.get(UsersRepository)
        try:
            users_count = await users_repo.get_users_count()
            logging.info(f"Database connection established. Users in database: {users_count}.")
        except SQLAlchemyError as e:
            logging.error(f"Database connection failed. Error: {e}")


async def on_startup(
        bot: Bot,
        admin_ids: list[int]
):
    await broadcaster.broadcast(bot, admin_ids, "Bot started!")
    await setup_admin_commands(bot, admin_ids)


async def main():
    setup_logging()

    container = await setup_dependencies()
    http_client: HttpClient = await container.get(HttpClient)
    config = await container.get(Config)
    await establish_db(di_container=container)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode='HTML')
    )

    storage = setup_storage(config)
    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)

    setup_dialogs(dp)
    setup_dishka(container=container, router=dp)

    setup_global_middlewares(dp=dp)
    dp.workflow_data.update(config=config)

    await setup_scheduler(bot, container)
    await on_startup(bot, config.tg_bot.admin_ids)

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.error("Stopping bot...")
    finally:
        await http_client.close()
        await container.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
