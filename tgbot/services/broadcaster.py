import asyncio
import logging
from typing import List, Tuple

from aiogram import Bot
from aiogram import exceptions
from aiogram.types import InlineKeyboardMarkup


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
