from aiogram import Router, flags
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from l10n.translator import Translator
from tgbot.misc.constants import SUPPORT_USERNAME

user_commands_router = Router()


@user_commands_router.message(Command("terms_of_use"))
@flags.rate_limit(key="default")
@inject
async def get_terms_of_use(
        message: Message,
        l10n: FromDishka[Translator]
):
    args = {
        "terms_of_use": f"<a href='{l10n.get_text(key='terms-of-use-link')}'>"
                        f"<b>{l10n.get_text(key='terms-of-use-name')}</b></a>"
    }
    await message.answer(l10n.get_text(key="terms-of-use", args=args), disable_web_page_preview=True)


@user_commands_router.message(Command("help"))
@flags.rate_limit(key="default")
@inject
async def get_help(
        message: Message,
        l10n: FromDishka[Translator]
):
    await message.answer(l10n.get_text(key="help", args={"support_username": SUPPORT_USERNAME}))
