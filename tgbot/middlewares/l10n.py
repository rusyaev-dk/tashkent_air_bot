from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


from l10n.translator import TranslatorHub


class L10nMiddleware(BaseMiddleware):
    def __init__(self, translator_hub: TranslatorHub):
        self.l10ns = translator_hub.l10ns
        self.default_locale = translator_hub.default_locale

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        repo = data["repo"]
        language_code = await repo.users.get_user_language_code(telegram_id=event.from_user.id)
        if language_code not in self.l10ns:
            language_code = self.default_locale
        data["l10n"] = self.l10ns.get(language_code)
        await handler(event, data)
