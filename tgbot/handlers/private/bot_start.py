import html

from aiogram import Router, flags
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from infrastructure.database.repo.requests import RequestsRepo
from l10n.translator import LocalizedTranslator, TranslatorHub
from tgbot.keyboards.inline import SetUserLanguageFactory
from tgbot.keyboards.reply import main_menu_kb
from tgbot.services.setup_bot_commands import update_user_commands

start_router = Router()


@start_router.message(CommandStart())
@flags.rate_limit(key="default")
async def bot_start(
        message: Message,
        state: FSMContext,
        l10n: LocalizedTranslator
):
    await state.clear()
    args = {
        "name": html.escape(message.from_user.full_name),
        "terms_of_use": f"<a href='{l10n.get_text(key='terms-of-use-link')}'>"
                        f"<b>{l10n.get_text(key='terms-of-use-name')}</b></a>"
    }
    text = l10n.get_text(key="hello", args=args)
    await message.answer(text, reply_markup=main_menu_kb(l10n=l10n), disable_web_page_preview=True)


@start_router.callback_query(SetUserLanguageFactory.filter())
async def set_user_language(
        call: CallbackQuery,
        repo: RequestsRepo,
        callback_data: SetUserLanguageFactory,
        translator_hub: TranslatorHub,
):
    language_code = callback_data.language_code

    user = await repo.users.get_user(telegram_id=call.from_user.id)
    if not user:
        await repo.users.setup_default_user_notifications(telegram_id=call.from_user.id)

    await repo.users.add_user(
        telegram_id=call.from_user.id,
        full_name=call.from_user.full_name,
        language=language_code,
        username=call.from_user.username,
    )
    await call.answer()
    await call.message.delete()
    l10n = translator_hub.l10ns.get(language_code)
    await update_user_commands(bot=call.bot, l10n=l10n)
    args = {
        "name": html.escape(call.from_user.full_name),
        "terms_of_use": f"<a href='{l10n.get_text(key='terms-of-use-link')}'>"
                        f"<b>{l10n.get_text(key='terms-of-use-name')}</b></a>"
    }
    text = l10n.get_text(key="hello", args=args)
    await call.message.answer(text, reply_markup=main_menu_kb(l10n=l10n), disable_web_page_preview=True)
