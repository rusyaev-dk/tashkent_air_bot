import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import ErrorEvent, CallbackQuery

from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState, OutdatedIntent, InvalidStackIdError


errors_router = Router()


@errors_router.errors(F.update.callback_query.as_("call"))
async def errors_handler(
        event: ErrorEvent,
        call: CallbackQuery,
):
    if isinstance(event.exception, UnknownIntent):
        logging.error("aiogram_dialog: UnknownIntent: Context not found for intent")
        text = (
            "🇷🇺 Пожалуйста, используйте главное меню\n"
            "🇺🇿 Iltimos, asosiy menyudan foydalaning\n"
            "🇬🇧 Please use the main menu\n"
        )
        await call.answer(text, show_alert=True)
        await call.message.delete()

    elif isinstance(event.exception, UnknownState):
        logging.error(UnknownState)

    elif isinstance(event.exception, OutdatedIntent):
        logging.error(OutdatedIntent)

    elif isinstance(event.exception, InvalidStackIdError):
        logging.error(InvalidStackIdError)

    elif isinstance(event.exception, TelegramNetworkError):
        logging.error("Failed to fetch updates - TelegramNetworkError: HTTP Client says - Request timeout error")
