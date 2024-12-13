import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from dishka import AsyncContainer

from infrastructure.database.repositories.aqi_repo import AQIRepository
from infrastructure.database.models import UserLocal
from infrastructure.database.repositories.users_repo import UsersRepository

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

            notifiable_users = {}
            for locale in l10n.locales:
                notifiable_users[locale] = await users_repo.get_notifiable_users_ids(
                    language_code=locale,
                    hours=hours
                )

            if all(not len(notifiable_users[locale]) for locale in l10n.locales):
                return

            try:
                c = 0
                for locale in l10n.locales:
                    text = format_aqi_info(aqi=aqi, l10n=l10n, locale=locale)
                    for user_id in notifiable_users[locale]:
                        success = await send_text(bot=bot, user_id=user_id, text=text, disable_notification=True)
                        if not success[0] and success[1] == "bot_blocked":
                            await users_repo.update_user(UserLocal.telegram_id == user_id, is_active=False)
                        c += 1
                        await asyncio.sleep(0.05)
            finally:
                logging.info(f"{c} messages successful sent.")

    @staticmethod
    def get_update_first_run_time(now: datetime = datetime.now()) -> datetime:
        next_minute = (now.minute // 5 + 1) * 5

        if next_minute == 60:
            return now.replace(minute=4, second=30, microsecond=0) + timedelta(hours=1)
        else:
            next_time = now.replace(minute=next_minute, second=0, microsecond=0)
            next_time -= timedelta(seconds=30)
            return next_time

    @staticmethod
    def get_notify_first_run_time(now: datetime = datetime.now()) -> datetime:
        return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
