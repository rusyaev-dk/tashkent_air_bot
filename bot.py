import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from di.di import setup_dependencies
from infrastructure.api.repositories.aqi_repo import AQIRepository
from l10n.translator import Translator
from tgbot.config import Config
from tgbot.handlers import routers_list
from tgbot.middlewares.database import UserExistingMiddleware
from tgbot.middlewares.l10n import L10nMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.constants import DEFAULT_THROTTLE_TIME
from tgbot.services import broadcaster
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
) -> Translator:

    all_files = os.listdir(locales_dir_path + "/ru")
    fluent_files = [file for file in all_files if file.endswith(".ftl")]

    translator_hub = Translator(
        locales_dir_path=str(locales_dir_path), locales=["ru", "uz", "en"],
        resource_ids=fluent_files
    )
    return translator_hub


def register_global_middlewares(
        dp: Dispatcher,
):

    dp.message.middleware(ThrottlingMiddleware(
        default_throttle_time=DEFAULT_THROTTLE_TIME))

    dp.message.middleware(UserExistingMiddleware())

    dp.message.middleware(L10nMiddleware())
    dp.callback_query.middleware(L10nMiddleware())


def setup_scheduling(
        scheduler: AsyncIOScheduler,
        bot: Bot,
        aqi_api: AQIRepository,
        config: Config,
        translator_hub: Translator,
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

    container = setup_dependencies()
    config = await container.get(Config)

    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))

    locales_dir_path = Path(__file__).parent.joinpath("l10n/locales")
    translator_hub = setup_translator(locales_dir_path=str(locales_dir_path))

    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)
    setup_dialogs(dp)
    dp.workflow_data.update(config=config, translator_hub=translator_hub)

    register_global_middlewares(dp=dp)
    # scheduler = AsyncIOScheduler()
    # setup_scheduling(
    #     scheduler=scheduler, bot=bot,
    #     aqi_api=aqi_api, config=config,
    #     translator_hub=translator_hub,
    #     session_pool=session_pool
    # )

    await on_startup(bot, config.tg_bot.admin_ids)
    # scheduler.start()
    setup_dishka(container=container, router=dp)

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.error("Stopping bot")
    finally:
        await container.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
