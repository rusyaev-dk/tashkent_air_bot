import asyncio
import logging

from aiogram import Bot
from dishka import AsyncContainer

from infrastructure.database.repositories.aqi_repo import AQIRepository
from infrastructure.database.models import UserLocal
from infrastructure.database.repositories.users_repo import UsersRepository

from datetime import datetime
import pytz

from l10n.translator import Translator
from tgbot.services.broadcaster import send_text
from tgbot.services.format_functions import format_aqi_info


class AQIScheduler:
    @staticmethod
    async def update_aqi(di_container: AsyncContainer):
        async with di_container() as request_container:
            aqi_repo = await request_container.get(AQIRepository)
            await aqi_repo.update_aqi()

    @staticmethod
    async def notify_users(bot: Bot, di_container: AsyncContainer):
        async with di_container() as request_container:
            aqi_repo = await request_container.get(AQIRepository)
            users_repo = await request_container.get(UsersRepository)
            l10n = await request_container.get(Translator)

            aqi = await aqi_repo.get_aqi()

            if not aqi:
                return

            tz = pytz.timezone('Asia/Tashkent')
            current_time = datetime.now(tz)
            hours = current_time.strftime('%H')

            minutes = current_time.strftime("%M")
            if int(minutes) > 50:
                hours = str((int(hours) + 1))

            hours = hours.zfill(2)

            ru_users_ids = await users_repo.get_notifiable_users_ids(language_code="ru", hours=hours)
            uz_users_ids = await users_repo.get_notifiable_users_ids(language_code="uz", hours=hours)
            en_users_ids = await users_repo.get_notifiable_users_ids(language_code="en", hours=hours)

            if not len(ru_users_ids) and not len(uz_users_ids) and not len(en_users_ids):
                return

            count = 0

            try:
                ru_text = format_aqi_info(aqi=aqi, l10n=l10n.l10ns.get("ru"))
                for user_id in ru_users_ids:
                    success = await send_text(bot=bot, user_id=user_id, text=ru_text, disable_notification=True)
                    if not success[0] and success[1] == "bot_blocked":
                        await users_repo.update_user(UserLocal.telegram_id == user_id, is_active=False)
                    count += 1
                    await asyncio.sleep(0.05)

                uz_text = format_aqi_info(aqi=aqi, l10n=l10n.l10ns.get("uz"))
                for user_id in uz_users_ids:
                    success = await send_text(bot=bot, user_id=user_id, text=uz_text, disable_notification=True)
                    if not success[0] and success[1] == "bot_blocked":
                        await users_repo.update_user(UserLocal.telegram_id == user_id, is_active=False)
                    count += 1
                    await asyncio.sleep(0.05)

                en_text = format_aqi_info(aqi=aqi, l10n=l10n.l10ns.get("en"))
                for user_id in en_users_ids:
                    success = await send_text(bot=bot, user_id=user_id, text=en_text, disable_notification=True)
                    if not success[0] and success[1] == "bot_blocked":
                        await users_repo.update_user(UserLocal.telegram_id == user_id, is_active=False)
                    count += 1
                    await asyncio.sleep(0.05)
            finally:
                logging.info(f"{count} messages successful sent.")
