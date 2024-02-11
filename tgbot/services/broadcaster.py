import asyncio
import logging
from datetime import datetime
from typing import List, Tuple

import pytz
from aiogram import Bot
from aiogram import exceptions
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from l10n.translator import TranslatorHub
from tgbot.services.format_functions import format_current_aqi_info


async def send_text(
        bot: Bot,
        user_id: int,
        text: str,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None
) -> Tuple[bool, str]:
    try:
        await bot.send_message(chat_id=user_id, text=text, disable_notification=disable_notification,
                               reply_markup=reply_markup)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return False, "bot_blocked"
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_text(
            bot, user_id, text, disable_notification, reply_markup
        )
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True, "success"
    return False, "other"


async def send_photo(
        bot: Bot,
        user_id: int,
        photo_id: str,
        caption: str = None,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None
) -> Tuple[bool, str]:
    try:
        await bot.send_photo(chat_id=user_id, photo=photo_id, caption=caption,
                             disable_notification=disable_notification)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return False, "bot_blocked"
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_photo(
            bot, user_id, photo_id, caption, disable_notification, reply_markup
        )
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True, "success"
    return False, "other"


async def send_document(
        bot: Bot,
        user_id: int,
        document_id: str,
        caption: str = None,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None
) -> Tuple[bool, str]:
    try:
        await bot.send_document(chat_id=user_id, document=document_id, caption=caption,
                                disable_notification=disable_notification)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return False, "bot_blocked"
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_document(
            bot, user_id, document_id, caption, disable_notification, reply_markup
        )
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True, "success"
    return False, "other"


async def send_audio(
        bot: Bot,
        user_id: int,
        audio_id: str,
        caption: str = None,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None
) -> Tuple[bool, str]:
    try:
        await bot.send_audio(chat_id=user_id, audio=audio_id, caption=caption,
                             disable_notification=disable_notification)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return False, "bot_blocked"
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_audio(
            bot, user_id, audio_id, caption, disable_notification, reply_markup
        )
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True, "success"
    return False, "other"


async def send_animation(
        bot: Bot,
        user_id: int,
        animation_id: str,
        caption: str = None,
        disable_notification: bool = False
) -> Tuple[bool, str]:
    try:
        await bot.send_animation(chat_id=user_id, animation=animation_id, caption=caption,
                                 disable_notification=disable_notification)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return False, "bot_blocked"
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_animation(
            bot, user_id, animation_id, caption, disable_notification
        )
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True, "success"
    return False, "other"


async def send_sticker(
        bot: Bot,
        user_id: int,
        sticker_id: str,
        disable_notification: bool = False
) -> Tuple[bool, str]:
    try:
        await bot.send_sticker(chat_id=user_id, sticker=sticker_id, disable_notification=disable_notification)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return False, "bot_blocked"
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_sticker(
            bot, user_id, sticker_id, disable_notification
        )
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True, "success"
    return False, "other"


async def broadcast(
        bot: Bot,
        users: List[int],
        text,
        disable_notification: bool = False
) -> int:
    """
    Simple broadcaster
    :return: Count of messages
    """
    count = 0
    try:
        for user_id in users:
            success = await send_text(bot, user_id, text, disable_notification)
            if success[0]:
                count += 1
            await asyncio.sleep(0.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")
    return count


async def aqi_users_notifying(
        bot: Bot,
        session_pool: async_sessionmaker,
        translator_hub: TranslatorHub,
):
    async with session_pool() as session:
        repo = RequestsRepo(session)
        current_aqi = await repo.aqi.get_current_aqi()
        if not current_aqi:
            return

        tz = pytz.timezone('Asia/Tashkent')
        current_time = datetime.now(tz)
        hours = current_time.strftime('%H')

        minutes = current_time.strftime("%M")
        if int(minutes) > 50:
            hours = str((int(hours) + 1))

        hours = hours.zfill(2)

        ru_users_ids = await repo.users.get_notifiable_user_ids(language_code="ru", hours=hours)
        uz_users_ids = await repo.users.get_notifiable_user_ids(language_code="uz", hours=hours)
        en_users_ids = await repo.users.get_notifiable_user_ids(language_code="en", hours=hours)

        if not len(ru_users_ids) and not len(uz_users_ids) and not len(en_users_ids):
            return

    count = 0

    try:
        ru_text = format_current_aqi_info(current_aqi=current_aqi, l10n=translator_hub.l10ns.get("ru"))
        for user_id in ru_users_ids:
            success = await send_text(bot=bot, user_id=user_id, text=ru_text, disable_notification=True)
            if not success[0] and success[1] == "bot_blocked":
                await repo.users.update_user(User.telegram_id == user_id, is_active=False)
            count += 1
            await asyncio.sleep(0.05)

        uz_text = format_current_aqi_info(current_aqi=current_aqi, l10n=translator_hub.l10ns.get("uz"))
        for user_id in uz_users_ids:
            success = await send_text(bot=bot, user_id=user_id, text=uz_text, disable_notification=True)
            if not success[0] and success[1] == "bot_blocked":
                await repo.users.update_user(User.telegram_id == user_id, is_active=False)
            count += 1
            await asyncio.sleep(0.05)

        en_text = format_current_aqi_info(current_aqi=current_aqi, l10n=translator_hub.l10ns.get("en"))
        for user_id in en_users_ids:
            success = await send_text(bot=bot, user_id=user_id, text=en_text, disable_notification=True)
            if not success[0] and success[1] == "bot_blocked":
                await repo.users.update_user(User.telegram_id == user_id, is_active=False)
            count += 1
            await asyncio.sleep(0.05)
    finally:
        logging.info(f"{count} messages successful sent.")
