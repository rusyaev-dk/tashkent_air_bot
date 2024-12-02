from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from infrastructure.database.repositories.users_repo import UsersRepository
from l10n.translator import Translator


class L10nMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        container = data["dishka_container"]
        user_repo = await container.get(UsersRepository)
        language_code = await user_repo.get_user_language_code(telegram_id=event.from_user.id)

        translator = await container.get(Translator)
        if language_code in translator.l10ns:
            translator.change_locale(new_locale=language_code)

        await handler(event, data)
