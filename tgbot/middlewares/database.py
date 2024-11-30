from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from infrastructure.database.models import UserLocal

from infrastructure.database.repositories.users_repo import UsersRepository
from tgbot.keyboards.inline import set_user_language_kb
from tgbot.misc.constants import SET_USER_LANGUAGE_TEXT


class UserExistingMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        event_from_user = data.get("event_from_user")
        if not event_from_user:
            return await handler(event, data)

        container = data["dishka_container"]
        user_repo = await container.get(UsersRepository)

        user = await user_repo.get_user(telegram_id=event.from_user.id)
        if not user:
            await event.answer(SET_USER_LANGUAGE_TEXT, reply_markup=set_user_language_kb())
            return
        if not user.is_active:
            await user_repo.update_user(UserLocal.telegram_id == event_from_user.id, is_active=True)
        data["user"] = user
        return await handler(event, data)
