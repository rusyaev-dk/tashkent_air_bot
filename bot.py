import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.api.aqi_repo import AQIApiRepo
from infrastructure.database.setup import create_session_pool, create_engine
from l10n.translator import TranslatorHub
from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.database import OuterDatabaseMiddleware, InnerDatabaseMiddleware, UserExistingMiddleware
from tgbot.middlewares.l10n import L10nMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.constants import SCHEDULER_AQI_INTERVAL_MINUTES, DEFAULT_THROTTLE_TIME
from tgbot.services import broadcaster
from tgbot.services.broadcaster import aqi_users_notifying
from tgbot.services.micro_functions import get_correct_update_run_time
from tgbot.services.setup_bot_commands import setup_admin_commands


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(
        config: Config
):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


def setup_translator(
    locales_dir_path: str
) -> TranslatorHub:

    all_files = os.listdir(locales_dir_path + "/ru")
    fluent_files = [file for file in all_files if file.endswith(".ftl")]

    translator_hub = TranslatorHub(
        locales_dir_path=str(locales_dir_path), locales=["ru", "uz", "en"],
        resource_ids=fluent_files
    )
    return translator_hub


def register_global_middlewares(
        dp: Dispatcher,
        translator_hub: TranslatorHub,
        session_pool: async_sessionmaker,
):
    dp.message.outer_middleware(OuterDatabaseMiddleware(session_pool))
    dp.callback_query.outer_middleware(OuterDatabaseMiddleware(session_pool))

    dp.message.middleware(ThrottlingMiddleware(
        default_throttle_time=DEFAULT_THROTTLE_TIME))

    dp.message.middleware(InnerDatabaseMiddleware())
    dp.callback_query.middleware(InnerDatabaseMiddleware())

    dp.message.middleware(UserExistingMiddleware())

    dp.message.middleware(L10nMiddleware(translator_hub))
    dp.callback_query.middleware(L10nMiddleware(translator_hub))


def setup_scheduling(
        scheduler: AsyncIOScheduler,
        bot: Bot,
        aqi_api: AQIApiRepo,
        config: Config,
        translator_hub: TranslatorHub,
        session_pool: async_sessionmaker
):
    now = datetime.now()
    update_run_time = get_correct_update_run_time(now=now)

    # scheduler.add_job(
    #     func=aqi_api.update_aqi, trigger='interval',
    #     minutes=SCHEDULER_AQI_INTERVAL_MINUTES, replace_existing=True,
    #     start_date=update_run_time,
    #     args=(bot, config, session_pool)
    # )

    scheduler.add_job(
        func=aqi_api.update_aqi, trigger='interval',
        seconds=5, replace_existing=True,
        args=(bot, config, session_pool)
    )

    first_run_time = None

    if 0 < now.minute < 59:
        first_run_time = now.replace(second=30, microsecond=0, minute=59, hour=now.hour)

    # scheduler.add_job(
    #     func=aqi_users_notifying, trigger="interval", hours=1,
    #     replace_existing=True, start_date=first_run_time,
    #     args=(bot, session_pool, translator_hub)
    # )

    # scheduler.add_job(
    #     func=aqi_users_notifying, trigger='interval', seconds=5,
    #     replace_existing=True, start_date=first_run_time,
    #     args=(bot, session_pool, translator_hub)
    # )


async def on_startup(
        bot: Bot,
        admin_ids: list[int]
):
    await broadcaster.broadcast(bot, admin_ids, "Bot started!")
    await setup_admin_commands(bot, admin_ids)


async def main():
    setup_logging()

    config = load_config(".env")
    aqi_api = AQIApiRepo(api_key=config.api.api_key)
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")

    locales_dir_path = Path(__file__).parent.joinpath("l10n/locales")
    translator_hub = setup_translator(locales_dir_path=str(locales_dir_path))

    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)
    setup_dialogs(dp)
    dp.workflow_data.update(aqi_api=aqi_api, config=config, translator_hub=translator_hub)

    engine = create_engine(db=config.db)
    session_pool = create_session_pool(engine=engine)

    register_global_middlewares(dp=dp, translator_hub=translator_hub, session_pool=session_pool)

    scheduler = AsyncIOScheduler()
    setup_scheduling(
        scheduler=scheduler, bot=bot,
        aqi_api=aqi_api, config=config,
        translator_hub=translator_hub,
        session_pool=session_pool
    )

    await on_startup(bot, config.tg_bot.admin_ids)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Stopping bot")
