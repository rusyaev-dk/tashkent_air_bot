from typing import List

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from l10n.translator import LocalizedTranslator


async def update_user_commands(bot: Bot, l10n: LocalizedTranslator):
    default_commands = [
        BotCommand(
            command="start",
            description=l10n.get_text(key="cmd-start-description")
        ),
        BotCommand(
            command="terms_of_use",
            description=l10n.get_text(key="cmd-tou-description")
        ),
        BotCommand(
            command="help",
            description=l10n.get_text(key="cmd-help-description")
        ),
    ]

    await bot.set_my_commands(commands=default_commands, scope=BotCommandScopeDefault())


async def setup_admin_commands(
        bot: Bot,
        admin_ids: List[int]
):
    admin_commands = [
        BotCommand(
            command="start",
            description="Перезапустить бота"
        ),
        BotCommand(
            command="terms_of_use",
            description="Пользовательское соглашение"
        ),
        BotCommand(
            command="statistics",
            description="Статистика"
        ),
    ]

    for admin_id in admin_ids:
        await bot.set_my_commands(commands=admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
