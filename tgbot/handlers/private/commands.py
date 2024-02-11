from aiogram import Router, flags
from aiogram.filters import Command
from aiogram.types import Message

from l10n.translator import LocalizedTranslator
from tgbot.misc.constants import SUPPORT_USERNAME

commands_router = Router()


@commands_router.message(Command("terms_of_use"))
@flags.rate_limit(key="default")
async def get_terms_of_use(
        message: Message,
        l10n: LocalizedTranslator,
):
    args = {
        "terms_of_use": f"<a href='{l10n.get_text(key='terms-of-use-link')}'>"
                        f"<b>{l10n.get_text(key='terms-of-use-name')}</b></a>"
    }
    await message.answer(l10n.get_text(key="terms-of-use", args=args), disable_web_page_preview=True)


@commands_router.message(Command("help"))
@flags.rate_limit(key="default")
async def get_help(
        message: Message,
        l10n: LocalizedTranslator
):
    await message.answer(l10n.get_text(key="help", args={"support_username": SUPPORT_USERNAME}))
